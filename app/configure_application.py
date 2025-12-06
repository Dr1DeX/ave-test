from core.cache.pool import init_redis_pool


async def configure_application_for_run():
    await init_redis_pool()
