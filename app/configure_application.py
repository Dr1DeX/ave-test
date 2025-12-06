from core.cache.pool import init_redis_pool
from core.db.session import init_db


async def configure_application_for_run():
    await init_redis_pool()
    await init_db()
