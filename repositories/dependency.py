from core.db.session import get_db_session
from repositories.cache import CacheRepository
from repositories.help_desk import HelpDeskRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


async def get_help_desk_repository(session: AsyncSession = Depends(get_db_session)) -> HelpDeskRepository:
    return HelpDeskRepository(_session=session)


async def get_cache_repository() -> CacheRepository:
    # TODO: статический объект да, мэйби в будущем пригодиться?
    return CacheRepository()
