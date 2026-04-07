from dotenv import load_dotenv
from db.pool import pool  # psycopg_pool.ConnectionPool
load_dotenv()

import asyncio
import logging
import secrets, hashlib
import json
from contextlib import asynccontextmanager
import os
import zipfile
import io
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.asyncio import AsyncIOScheduler







from services.ingestion import Ingestion
from services.retrieval import Retrieval
from caching.cache import redis_client
from caching.prompt_data_caching import prompt_dump
from caching.db_caching import db_dump
# from security_headers import SecurityHeadersMiddleware

# Logging setup
# uses the built-in python logging module
# __name__ is equal to the module name
# this all makes debugging easier
logger = logging.getLogger(__name__)
# this means to only show log messages with severity INFO or higher (INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# FastAPI app
app = FastAPI()
# app.add_middleware(SecurityHeadersMiddleware)

scheduler = AsyncIOScheduler()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# Initialize PromptDB + Ingestion

ingestion = Ingestion()  # ingestion.db is already PromptDB(pool)
retrieval = Retrieval()



# Event to signal shutdown
stop_event = asyncio.Event()





# This runs permanently in the background, awaiting incoming prompt data
# in order to gather it all into a buffer and create a big INSERT statement
# which is much more efficient than many single statements.
async def flush_worker():
    logger.info("[FlushWorker] Started")
    buffer = []
    MAX_BATCH_SIZE = 50
    FLUSH_INTERVAL = 10  # seconds

    # while loop that keeps running until it receives a shutdown signal
    while not stop_event.is_set():
        try:
            # We try to get an item from Redis, but we timeout based on our flush interval
            try:
                # blpop = blocking left pop, waits 5 seconds for something to arrive
                # incase the queue is empty. A normal lpop would poll the CPU constantly
                # which is less efficient

                # this keeps repeating until the FLUSH_INTERVAL has passed, or the buffer
                # is full
                result = await asyncio.wait_for(
                    redis_client.blpop("event_queue", timeout=5),  # type: ignore
                    timeout=FLUSH_INTERVAL
                )
            except asyncio.TimeoutError:
                result = None # Trigger a manual flush check

            if result:
                # blpop returns a tuple: ('name of queue', {data_inserted})
                # we discard the name of the queue as we don't need it
                # BLpop can listen to more than one queue simultaneously 
                _, event = result
                buffer.append(json.loads(event))

            # Flush Logic: If buffer is full OR time has passed and buffer isn't empty
            if len(buffer) >= MAX_BATCH_SIZE or (len(buffer) > 0 and result is None):
                
                
                
                batch_to_insert = list(buffer)
                buffer.clear()

                # This is safe because Ingestion.batch_insert 
                # requests its own connection from the pool.
                await asyncio.to_thread(ingestion.batch_insert, batch_to_insert)
                logger.info(f"{datetime.now()} [FlushWorker] Inserted {len(batch_to_insert)} events")

        except Exception as e:
            logger.error(f"[FlushWorker] Error: {e}", exc_info=True)
            # Optional: Sleep briefly on error to avoid rapid-fire failure loops
            await asyncio.sleep(1)


# these sync functions are made to run on a different thread too.
async def generate_prompt_data():
    await asyncio.to_thread(prompt_dump)


# async def generate_db_dump():
#     loop = asyncio.get_event_loop()
#     await loop.run_in_executor(None, db_dump)

def verify_token(authorization: str = Header(...)):
    # This matches how we send the API key from the plugin, the message, per standard
    # practice starts with 'Bearer'
    # if it does not match, return an error
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    
    # trim the message and hash it
    raw_token = authorization.removeprefix("Bearer ")
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    # We look for the exact hash in the DB, and throw an error
    # if it is not found
    row = retrieval.get_token(token_hash)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid token")

    # We then update when the token was last used, and return
    # the connected user_id
    ingestion.update_token_last_used(token_hash)
    return row["user_id"]

# This is a sliding window rate limiter, using redis. Thus the 60 seconds are relative
# to the exact moment a user sends a prompt. This is instead of resetting a counter every fixed minute.
async def rate_limit(user_id: str = Depends(verify_token)):
    # the key is a unique identifier redis uses to bucket the data
    key = f"rate_limit:{user_id}"
    window = 60        # seconds
    max_requests = 20  # requests per window

    now = asyncio.get_event_loop().time()
    window_start = now - window

    # a pipeline allows us to bundle commands into a 'package'
    # thus only one network trip, instead of four.
    # Uses a redis ZSET (Sorted Set) as a data structure
    pipe = redis_client.pipeline()

    pipe.zremrangebyscore(key, 0, window_start)       # drop old entries, slides the window forward
    pipe.zadd(key, {str(now): now})                   # add current request
    pipe.zcard(key)                                   # count requests in window
    pipe.expire(key, window)                          # auto-cleanup key
    results = await pipe.execute()

    request_count = results[2]                        # [2] is what zcard returns
    if request_count > max_requests:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    return user_id
# The same idea as rate_limit, but more strict
# this limits the amount of times a user can register per IP per minute.
async def rate_limit_ip(request: Request):
    if request.client is None:
        raise HTTPException(status_code=400, detail="Could not determine client IP")
    
    ip = request.client.host
    key = f"rate_limit_ip:{ip}"
    window = 60
    max_requests = 5  # stricter than the token limit

    now = asyncio.get_event_loop().time()
    window_start = now - window

    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)
    results = await pipe.execute()

    request_count = results[2]
    if request_count > max_requests:
        raise HTTPException(status_code=429, detail="Too many registration attempts")


# FastAPI lifespan manager for startup/shutdown

# this turns the function into an asynchronous context manager
@asynccontextmanager
# run automatically, the part before yield on server start,
# the part after yield on server stop
async def lifespan(app: FastAPI):
    # we open the pool/connect to the database to ensure readiness
    logger.info("Opening DB connection pool...")
    pool.open()
    logger.info("DB pool opened")
    # we start the aforementioned flushworker
    worker_task = asyncio.create_task(flush_worker())
    logger.info("[Lifespan] Flush worker started")

    # Only one worker runs scheduler + dumps
    if os.getenv("GUNICORN_WORKER_ID", "0") == "0":

        # logger.info("Generating DB dump...")
        # asyncio.create_task(generate_db_dump())

        logger.info("Generating prompt dump...")
        asyncio.create_task(generate_prompt_data())
        # we add a cronjob to dump the prompt data every hour one minute after the hour.
        scheduler.add_job(generate_prompt_data, "cron", minute=1)
        # scheduler.add_job(generate_db_dump, "cron", hour=0, minute=0)

        scheduler.start()
        logger.info("Scheduler started")

    yield
    # these two ensure a 'graceful exit' = finish what you are doing then terminate.
    stop_event.set()
    worker_task.cancel()
    # server shutdown without ugly logs
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    # no new cronjobs as the server is dying
    if scheduler.running:
        scheduler.shutdown()

    # always close the pool, no conditions
    # this ensures we don't end up with 'zombie' connections on the DB
    try:
        pool.close()
        logger.info("[Lifespan] Pool closed")
    except Exception as e:
        logger.error(f"[Lifespan] Pool close failed: {e}")
# this tells FastAPI to use this function to manage application lifecycle
app.router.lifespan_context = lifespan

# JUST FOR TESTING
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
    "chrome-extension://enhmgcekbcibpljmgkpiljjfcnhljgdc"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# endpoint for collecting prompt data
@app.post("/events")
# Depends is like a gatekeeper, the function will only go ahead if it returns a user_id
# and we u
async def receive_event(request: Request, user_id: str = Depends(rate_limit)):
    data = await request.json()
    data["user_id"] = user_id  # now server-authoritative, not from payload but from our DB
    # rpush adds the data to the end(right side) of a list in redis named 'event_queue'
    # the same event queue that our flush worker is watching
    await redis_client.rpush("event_queue", json.dumps(data)) # type: ignore
    return {"status": "queued"}


@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse("index.html",  {"request": request,})

@app.get("/co2", response_class=HTMLResponse)
async def co2(request:Request):
    return templates.TemplateResponse("co2.html",  {"request": request,})

@app.get("/energy", response_class=HTMLResponse)
async def energy(request:Request):
    return templates.TemplateResponse("energy.html",  {"request": request,})

@app.get("/", response_class=HTMLResponse)
async def water(request:Request):
    return templates.TemplateResponse("water.html",  {"request": request,})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    import time
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "reload_timestamp": int(time.time())  # Unique per request
    })

@app.get('/privacy', response_class=HTMLResponse)
async def privacy(request:Request):
    return templates.TemplateResponse('privacy-policy.html', {'request': request})

# This endpoint is needed to get the json data to the frontend
@app.get("/data/dashboard.json")
async def get_dashboard_data():
    file_path = "protected/data/dashboard.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return data  # FastAPI automatically returns this as application/json
    
    raise HTTPException(status_code=404, detail="Data not ready yet")

# this function too only runs if Depends returns no error
@app.post("/register")
async def register(request: Request,  _: None = Depends(rate_limit_ip)):
    data = await request.json()
    user_id = data.get("user_id")  # the stable ID from the extension

    # Generate a raw token — this is the ONLY time it exists in plaintext
    raw_token = secrets.token_hex(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    ingestion.insert_user(user_id)
    ingestion.insert_token(user_id, token_hash) # type: ignore
    
    # this is sent back to the plugin user
    return {"token": raw_token}


# @app.get("/download/dataset")
# async def download_dataset(user_id: str = Depends(verify_token)):
    
#     # Check if user has already downloaded today
#     last_download = retrieval.get_last_download(user_id)
    
#     if last_download:
#         last_dt = last_download["downloaded_at"]
#         today = datetime.now(timezone.utc).date()
#         if last_dt.date() == today:
#             raise HTTPException(status_code=429, detail="Daily download limit reached")

#     # Log the download
#     ingestion.log_download(user_id)

#     # Build zip in memory
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
#         zf.write("protected/AI_monitor_dataset.json", "AI_monitor_dataset.json")
#         zf.write("protected/README.md", "README.md")
#         zf.write("protected/schema.sql", "schema.sql")
#     zip_buffer.seek(0)

#     return StreamingResponse(
#         zip_buffer,
#         media_type="application/zip",
#         headers={"Content-Disposition": "attachment; filename=AI_monitor_dataset.zip"}
#     )
