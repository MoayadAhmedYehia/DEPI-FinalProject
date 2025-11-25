"""Redis client for caching"""
import redis.asyncio as redis
from typing import Optional
from src.config.settings import get_settings

settings = get_settings()

redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    redis_client = await redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> redis.Redis:
    """Get Redis client"""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client
