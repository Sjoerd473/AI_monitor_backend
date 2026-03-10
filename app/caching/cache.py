from config import settings
import redis.asyncio as redis


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# CHANGE THE REDIS HOST IN .ENV FOR CONTAINER, NEEDS TO BE redis