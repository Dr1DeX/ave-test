from app.public.services.help_desk import HelpDeskService
from repositories.cache import CacheRepository
from repositories.dependency import get_cache_repository, get_help_desk_repository
from repositories.help_desk import HelpDeskRepository

from fastapi import Depends


async def get_help_desk_service(
        cache_repository: CacheRepository = Depends(get_cache_repository),
        help_desk_repository: HelpDeskRepository = Depends(get_help_desk_repository)
) -> HelpDeskService:
    return HelpDeskService(
        cache_repository=cache_repository,
        help_desk_repository=help_desk_repository
    )
