import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Header, HTTPException
import hmac, hashlib

from db.promptdb import PromptDB
from db.pool import pool  # psycopg_pool.ConnectionPool
from services.ingestion import Ingestion
from scripts.energy_calc import compute_environmental_impact

# Logging setup
# uses the built-in python logging module
# __name__ is equal to the module name
# this all makes debugging easier
logger = logging.getLogger(__name__)
# this means to only show log messages with severity INFO or higher (INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# FastAPI app
app = FastAPI()

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


async def flush_worker():
    """Background task to flush buffer to the database."""
    # must be global as it lives outside the function, and has to
    global buffer
    try:
        # this mean run forever until the server sends a stop signal
        # stop_event is an async signal for shutdown
        while not stop_event.is_set():
            # asyncio.sleep() to wake up every 0.2 seconds > micro-batches
            await asyncio.sleep(flush_interval)
            # here it acquires the lock
            async with buffer_lock:
                # if the buffer is empty skip the cycle
                if not buffer:
                    continue
                # the buffer is copied to a flush_buffer so we don't block incoming requests
                # while processing the batch
                flush_buffer = buffer
                buffer = []

            # Insert batch
            try:
                # then we send the whole batch on to the DB
                ingestion.batch_insert(flush_buffer)
                logger.info(f"[FlushWorker] Inserted {len(flush_buffer)} events")
            except Exception as e:
                # print the error with full stack trace
                logger.error(f"[FlushWorker] Failed to insert batch: {e}", exc_info=True)
    except asyncio.CancelledError:
        # this happens when the server is shut down == worker_task.cancel raises this error
        logger.info("[FlushWorker] Cancelled")


# FastAPI lifespan manager for startup/shutdown

# this turns the function into an asynchronous context manager
@asynccontextmanager
# run automatically, the part before yield on server start,
# the part after yield on server stop
async def lifespan(app: FastAPI):
    # Startup: launch flush worker
    worker_task = asyncio.create_task(flush_worker())
    logger.info("[Lifespan] Flush worker started")
    # yield pauses the execution of this function until it is called again
    # at that point the part after yield is exectuted
    yield
    # Shutdown: stop flush worker
    # this tells the worker to stop
    stop_event.set()
    # and cancels the worker
    worker_task.cancel()
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


@app.post("/events")
# request allows us to access body, headers and client info
# Header(...) means this header (x_signature) is required, otherwise error 422
async def receive_event(request: Request, x_signature: str = Header(...)):
    """Receive an event from the plugin and append it to the buffer."""
    global buffer

    # Read raw body
    # the raw body is required for verifying the signature
    raw_body = await request.body()
    # convert from bytes to string
    payload_string = raw_body.decode("utf-8")

    # Verify HMAC
    # this creates the expected signature as it was in the extension
    computed_hmac = hmac.new(SECRET_KEY, payload_string.encode("utf-8"), hashlib.sha256).hexdigest()
    # if they don't match, raise an error and return 403
    if not hmac.compare_digest(computed_hmac, x_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse JSON
    data = await request.json()

    # Compute environmental impact
    impact_values = compute_environmental_impact(data)

    # we merge the extra values into the object for ease of use
    data["prompt"].update(impact_values)

    # Add to buffer
    async with buffer_lock:
        buffer.append(data)
    # we return a message to the extension to confirm we received the data
    return {"status": "received"}