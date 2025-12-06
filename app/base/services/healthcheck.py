from logging import getLogger
from typing import Tuple

from sqlalchemy import select

from core.db.session import session
from repositories.cache import CacheManager

logger = getLogger(__name__)


class HealthCheckService:
    """
    Сервис healthcheck проверяет статус инфрастуктурных модулей Postgresql/Redis
    """

    @staticmethod
    async def is_db_healthy():
        try:
            async with session() as db_connection:
                await db_connection.execute(select(1))
                return True
        except Exception as exc:
            logger.error(f"Database is unhealthy: {exc}")
            return False

    @staticmethod
    async def is_redis_healthy():
        try:
            await CacheManager.ping()
            return True
        except Exception as exc:
            logger.error(f"Redis is unhealthy: {exc}")
            return False

    @classmethod
    async def is_application_healthy(cls) -> Tuple[bool, list]:
        unavailable_modules = []
        if not await cls.is_db_healthy():
            unavailable_modules.append("PostgreSQL")
        if not await cls.is_redis_healthy():
            unavailable_modules.append("Redis")

        is_ok_flag = True if not unavailable_modules else False
        return is_ok_flag, unavailable_modules
