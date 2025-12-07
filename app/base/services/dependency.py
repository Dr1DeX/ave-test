from app.base.services.healthcheck import HealthCheckService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from core.db.session import get_db_session
from repositories.cache import CacheRepository
from repositories.dependency import get_cache_repository


async def get_healthcheck_service(
        session: AsyncSession = Depends(get_db_session),
        cache_repository: CacheRepository = Depends(get_cache_repository),
) -> HealthCheckService:
    return HealthCheckService(
        _session=session,
        cache_repository=cache_repository
    )
