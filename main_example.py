import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Header, HTTPException

from db.promptdb import PromptDB
from db.pool import pool  # psycopg_pool.ConnectionPool
from services.ingestion import Ingestion
from scripts.energy_calc import compute_environmental_impact

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# FastAPI app
app = FastAPI()

# Initialize PromptDB + Ingestion
prompt_db = PromptDB(pool)
ingestion = Ingestion()  # ingestion.db is already PromptDB(pool)

# Buffer for batching events
buffer = []
buffer_lock = asyncio.Lock()
flush_interval = 0.2  # seconds

# Event to signal shutdown
stop_event = asyncio.Event()


async def flush_worker():
    """Background task to flush buffer to the database."""
    global buffer
    try:
        while not stop_event.is_set():
            await asyncio.sleep(flush_interval)
            async with buffer_lock:
                if not buffer:
                    continue
                flush_buffer = buffer
                buffer = []

            # Insert batch
            try:
                ingestion.batch_insert(flush_buffer)
                logger.info(f"[FlushWorker] Inserted {len(flush_buffer)} events")
            except Exception as e:
                logger.error(f"[FlushWorker] Failed to insert batch: {e}", exc_info=True)
    except asyncio.CancelledError:
        logger.info("[FlushWorker] Cancelled")


# FastAPI lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch flush worker
    worker_task = asyncio.create_task(flush_worker())
    logger.info("[Lifespan] Flush worker started")
    yield
    # Shutdown: stop flush worker
    stop_event.set()
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

    # Close the pool cleanly
    if hasattr(prompt_db, "pool") and prompt_db.pool:
        prompt_db.pool.close()  # Correct method for psycopg_pool
        logger.info("[Lifespan] PromptDB pool closed")


app.router.lifespan_context = lifespan


# Shared secret for HMAC
SECRET_KEY = b"super_secret_key_here"


@app.post("/events")
async def receive_event(request: Request, x_signature: str = Header(...)):
    """Receive an event from the plugin and append it to the buffer."""
    global buffer

    # Read raw body
    raw_body = await request.body()
    payload_string = raw_body.decode("utf-8")

    # Verify HMAC
    import hmac, hashlib
    computed_hmac = hmac.new(SECRET_KEY, payload_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_hmac, x_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse JSON
    data = await request.json()

    # Compute environmental impact
    impact_values = compute_environmental_impact(data)
    data["prompt"].update(impact_values)

    # Add to buffer
    async with buffer_lock:
        buffer.append(data)

    return {"status": "received"}