import redis.asyncio as aioredis

from core.config import config

from .redis import RedisBaseTypes

REDIS_CONNECTION_POOL: aioredis.Redis


async def init_redis_pool():
    global REDIS_CONNECTION_POOL
    REDIS_CONNECTION_POOL = {}
    for redis_base in RedisBaseTypes:
        redis_pool = await aioredis.from_url(config.REDIS_CONNECTION_URL, db=redis_base.value)
        REDIS_CONNECTION_POOL[redis_base.value] = redis_pool


def get_redis_pool(base: int = RedisBaseTypes.DEFAULT.value) -> aioredis.Redis:
    if REDIS_CONNECTION_POOL is None:
        raise RuntimeError("Redis connection pool not initialized")
    return REDIS_CONNECTION_POOL[base]
