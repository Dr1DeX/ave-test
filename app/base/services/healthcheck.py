from logging import getLogger
from typing import Tuple
from dataclasses import dataclass
from sqlalchemy import select

from repositories.cache import CacheRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = getLogger(__name__)


@dataclass
class HealthCheckService:
    _session: AsyncSession
    cache_repository: CacheRepository

    """
    Сервис healthcheck проверяет статус инфрастуктурных модулей Postgresql/Redis
    """

    async def is_db_healthy(self):
        try:
            await self._session.execute(select(1))
            return True
        except Exception as exc:
            logger.error(f"Database is unhealthy: {exc}")
            return False

    async def is_redis_healthy(self):
        try:
            await self.cache_repository.ping()
            return True
        except Exception as exc:
            logger.error(f"Redis is unhealthy: {exc}")
            return False

    async def is_application_healthy(self) -> Tuple[bool, list]:
        unavailable_modules = []
        if not await self.is_db_healthy():
            unavailable_modules.append("PostgreSQL")
        if not await self.is_redis_healthy():
            unavailable_modules.append("Redis")

        is_ok_flag = True if not unavailable_modules else False
        return is_ok_flag, unavailable_modules
