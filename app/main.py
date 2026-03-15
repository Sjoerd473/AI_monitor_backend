from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
import hmac, hashlib
import json
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apscheduler.schedulers.asyncio import AsyncIOScheduler


from db.promptdb import PromptDB
from db.pool import pool  # psycopg_pool.ConnectionPool
from services.ingestion import Ingestion
from scripts.energy_calc import compute_environmental_impact
from caching.cache import redis_client
from caching.prompt_data_caching import prompt_dump
from caching.db_caching import db_dump

# Logging setup
# uses the built-in python logging module
# __name__ is equal to the module name
# this all makes debugging easier
logger = logging.getLogger(__name__)
# this means to only show log messages with severity INFO or higher (INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# FastAPI app
app = FastAPI()

scheduler = AsyncIOScheduler()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# Initialize PromptDB + Ingestion
prompt_db = PromptDB(pool)
ingestion = Ingestion()  # ingestion.db is already PromptDB(pool)

# Buffer for batching events
buffer = []
# because we are running async, more than one function might be trying to access the buffer at the same time
# the lock will allow only one coroutine to access the buffer at a time
# thus preventing race conditions (reading the buffer while it is being wiped, etc.)
buffer_lock = asyncio.Lock()
flush_interval = 0.2  # seconds

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
    try:
        while not stop_event.is_set():

            batch = []

            # Wait for at least one event
            
            _, event = await redis_client.blpop("event_queue") # type: ignore
            batch.append(json.loads(event))

            # After first event, drain more quickly
            for _ in range(99):
                event = await redis_client.lpop("event_queue") # type: ignore
                if not event:
                    break
                batch.append(json.loads(event)) # type: ignore

            try:
                ingestion.batch_insert(batch)
                logger.info(f"[FlushWorker] Inserted {len(batch)} events")

            except Exception as e:
                logger.error(f"[FlushWorker] DB error: {e}", exc_info=True)

    except asyncio.CancelledError:
        logger.info("[FlushWorker] Cancelled")

async def generate_prompt_data():
    prompt_dump()

async def generate_db_dump():
    db_dump()



# FastAPI lifespan manager for startup/shutdown

# this turns the function into an asynchronous context manager
@asynccontextmanager
# run automatically, the part before yield on server start,
# the part after yield on server stop
async def lifespan(app: FastAPI):
    # Startup: launch flush worker
    worker_task = asyncio.create_task(flush_worker())
    logger.info("[Lifespan] Flush worker started")

    logger.info("Generating DB dump...")
    await generate_db_dump()
    logger.info("DB dump complete")

    logger.info("Generating prompt dump...")
    await generate_prompt_data()
    logger.info("Prompt dump complete")

    scheduler.add_job(generate_prompt_data, 'cron', minute=1)
    scheduler.add_job(generate_db_dump, 'cron', hour=0, minute=0)
    scheduler.start()
    # yield pauses the execution of this function until it is called again
    # at that point the part after yield is exectuted
    yield
    # Shutdown: stop flush worker
    # this tells the worker to stop
    stop_event.set()
    # and cancels the worker
    worker_task.cancel()
    scheduler.shutdown()
    try:
        # this makes sure the program cannot stop while the worker is still running
        await worker_task

        # when awaiting a cancelled task Python will throw the error again, so this ignores it
    except asyncio.CancelledError:
        pass

    # Close the pool cleanly

    # this checks if the DB pool exists
    if hasattr(prompt_db, "pool") and prompt_db.pool:
        # and closes it
        # connection pools hold open database connections, so this way we avoid connection leaks
        prompt_db.pool.close()  # Correct method for psycopg_pool
        logger.info("[Lifespan] PromptDB pool closed")

# this tells FastAPI to use this function to manage application lifecycle
app.router.lifespan_context = lifespan


# Shared secret for HMAC
SECRET_KEY = b"super_secret_key_here"


# @app.post("/events")
# # request allows us to access body, headers and client info
# # Header(...) means this header (x_signature) is required, otherwise error 422
# async def receive_event(request: Request, x_signature: str = Header(...)):
#     """Receive an event from the plugin and append it to the buffer."""
#     global buffer

#     # Read raw body
#     # the raw body is required for verifying the signature
#     raw_body = await request.body()
#     # convert from bytes to string
#     payload_string = raw_body.decode("utf-8")

#     # Verify HMAC
#     # this creates the expected signature as it was in the extension
#     computed_hmac = hmac.new(SECRET_KEY, payload_string.encode("utf-8"), hashlib.sha256).hexdigest()
#     # if they don't match, raise an error and return 403
#     if not hmac.compare_digest(computed_hmac, x_signature):
#         raise HTTPException(status_code=403, detail="Invalid signature")

#     # Parse JSON
#     data = await request.json()

#     # Compute environmental impact
#     impact_values = compute_environmental_impact(data)

#     # we merge the extra values into the object for ease of use
#     data["prompt"].update(impact_values)

#     # Add to buffer
#     async with buffer_lock:
#         buffer.append(data)
#     # we return a message to the extension to confirm we received the data
#     return {"status": "received"}


@app.post("/events")
async def receive_event(request: Request, x_signature: str = Header(...)):
    raw_body = await request.body()
    payload_string = raw_body.decode("utf-8")

    computed_hmac = hmac.new(
        SECRET_KEY,
        payload_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hmac, x_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()

    impact_values = compute_environmental_impact(data)
    data["prompt"].update(impact_values)

    # Push event to Redis queue
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
