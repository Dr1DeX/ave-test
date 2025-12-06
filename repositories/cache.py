from core.cache.pool import get_redis_pool as redis


class CacheRepository:
    @classmethod
    async def ping(cls):
        await redis().ping()
