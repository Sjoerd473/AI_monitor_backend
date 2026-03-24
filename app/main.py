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
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.asyncio import AsyncIOScheduler







from services.ingestion import Ingestion
from services.retrieval import Retrieval
from caching.cache import redis_client
from caching.prompt_data_caching import prompt_dump
from caching.db_caching import db_dump
from security_headers import SecurityHeadersMiddleware

# Logging setup
# uses the built-in python logging module
# __name__ is equal to the module name
# this all makes debugging easier
logger = logging.getLogger(__name__)
# this means to only show log messages with severity INFO or higher (INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# FastAPI app
app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)

scheduler = AsyncIOScheduler()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# Initialize PromptDB + Ingestion

ingestion = Ingestion()  # ingestion.db is already PromptDB(pool)
retrieval = Retrieval()

# Buffer for batching events
# buffer = []
# because we are running async, more than one function might be trying to access the buffer at the same time
# the lock will allow only one coroutine to access the buffer at a time
# thus preventing race conditions (reading the buffer while it is being wiped, etc.)
# buffer_lock = asyncio.Lock()
# flush_interval = 0.2  # seconds

# Event to signal shutdown
stop_event = asyncio.Event()


# async def flush_worker():
#     """Background task to flush buffer to the database."""
#     # must be global as it lives outside the function, and has to
#     global buffer
#     try:
#         # this mean run forever until the server sends a stop signal
#         # stop_event is an async signal for shutdown
#         while not stop_event.is_set():
#             # asyncio.sleep() to wake up every 0.2 seconds > micro-batches
#             await asyncio.sleep(flush_interval)
#             # here it acquires the lock
#             async with buffer_lock:
#                 # if the buffer is empty skip the cycle
#                 if not buffer:
#                     continue
#                 # the buffer is copied to a flush_buffer so we don't block incoming requests
#                 # while processing the batch
#                 flush_buffer = buffer
#                 buffer = []

#             # Insert batch
#             try:
#                 # then we send the whole batch on to the DB
#                 ingestion.batch_insert(flush_buffer)
#                 logger.info(f"[FlushWorker] Inserted {len(flush_buffer)} events")
#             except Exception as e:
#                 # print the error with full stack trace
#                 logger.error(f"[FlushWorker] Failed to insert batch: {e}", exc_info=True)
#     except asyncio.CancelledError:
#         # this happens when the server is shut down == worker_task.cancel raises this error
#         logger.info("[FlushWorker] Cancelled")


async def flush_worker():
    logger.info("[FlushWorker] Started")

    while not stop_event.is_set():
        try:
            result = await redis_client.blpop("event_queue", timeout=5) # type: ignore

            if result is None:
                continue

            _, event = result

            data = json.loads(event)

            ingestion.batch_insert([data])

            logger.info(f"{datetime.now()}[FlushWorker] Inserted 1 event")

        except Exception as e:
            logger.error(f"[FlushWorker] Error: {e}", exc_info=True)



async def generate_prompt_data():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, prompt_dump)


async def generate_db_dump():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, db_dump)

def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    raw_token = authorization.removeprefix("Bearer ")
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    row = retrieval.get_token(token_hash)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid token")

    ingestion.update_token_last_used(token_hash)
    return row["user_id"]

async def rate_limit(user_id: str = Depends(verify_token)):
    key = f"rate_limit:{user_id}"
    window = 60        # seconds
    max_requests = 60  # requests per window

    now = asyncio.get_event_loop().time()
    window_start = now - window

    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)       # drop old entries
    pipe.zadd(key, {str(now): now})                   # add current request
    pipe.zcard(key)                                   # count requests in window
    pipe.expire(key, window)                          # auto-cleanup key
    results = await pipe.execute()

    request_count = results[2]
    if request_count > max_requests:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    return user_id



# FastAPI lifespan manager for startup/shutdown

# this turns the function into an asynchronous context manager
@asynccontextmanager
# run automatically, the part before yield on server start,
# the part after yield on server stop
async def lifespan(app: FastAPI):

    logger.info("Opening DB connection pool...")
    pool.open()
    logger.info("DB pool opened")

    worker_task = asyncio.create_task(flush_worker())
    logger.info("[Lifespan] Flush worker started")

    # Only one worker runs scheduler + dumps
    if os.getenv("GUNICORN_WORKER_ID", "0") == "0":

        logger.info("Generating DB dump...")
        asyncio.create_task(generate_db_dump())

        logger.info("Generating prompt dump...")
        asyncio.create_task(generate_prompt_data())

        scheduler.add_job(generate_prompt_data, "cron", minute=1)
        scheduler.add_job(generate_db_dump, "cron", hour=0, minute=0)

        scheduler.start()
        logger.info("Scheduler started")

    yield

    stop_event.set()
    worker_task.cancel()

    try:
        await worker_task
    except asyncio.CancelledError:
        pass

    if scheduler.running:
        scheduler.shutdown()

    # always close the pool, no conditions
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




@app.post("/events")
async def receive_event(request: Request, user_id: str = Depends(rate_limit)):
    data = await request.json()
    data["user_id"] = user_id  # now server-authoritative, not from payload
    await redis_client.rpush("event_queue", json.dumps(data)) # type: ignore
    return {"status": "queued"}


@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse("index.html",  {"request": request,})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    import time
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "reload_timestamp": int(time.time())  # Unique per request
    })


@app.get("/data/dashboard.json")
async def get_dashboard_data():
    # Option 1: Serve static JSON file
    file_path = "static/data/dashboard.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
        


@app.post("/register")
async def register(request: Request):
    data = await request.json()
    user_id = data.get("user_id")  # the stable ID from the extension

    # Generate a raw token — this is the ONLY time it exists in plaintext
    raw_token = secrets.token_hex(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    ingestion.insert_user(user_id)
    ingestion.insert_token(user_id, token_hash) # type: ignore
    

    return {"token": raw_token}


@app.get("/download/dataset")
async def download_dataset(user_id: str = Depends(verify_token)):
    
    # Check if user has already downloaded today
    last_download = retrieval.get_last_download(user_id)
    
    if last_download:
        last_dt = last_download["downloaded_at"]
        today = datetime.now(timezone.utc).date()
        if last_dt.date() == today:
            raise HTTPException(status_code=429, detail="Daily download limit reached")

    # Log the download
    ingestion.log_download(user_id)

    # Build zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write("protected/AI_monitor_dataset.json", "AI_monitor_dataset.json")
        zf.write("protected/README.md", "README.md")
        zf.write("protected/schema.sql", "schema.sql")
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=AI_monitor_dataset.zip"}
    )
