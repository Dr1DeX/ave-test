from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.public.v1.request.help_desk import CreateHelpDeskDataModel, UpdateHelpDeskModel
from api.public.v1.response.help_desk import GetHelpDeskResponseModel, CreateHelpDeskResponseModel, \
    GetListHelpDeskResponseModel, UpdateHelpDeskResponseModel, DeleteHelpDeskResponseModel
from app.public.services.dependency import get_help_desk_service
from app.public.services.help_desk import HelpDeskService
from core.exceptions.service import ServiceAPIResponseStatus
from core.fastapi.decorators.service import service_response_decorator

public_router = APIRouter(prefix="/v1/contacts", tags=["Public"])


@public_router.get(
    "",
    response_model=GetListHelpDeskResponseModel,
    description="Получить все контакты"
)
@service_response_decorator(status_response=ServiceAPIResponseStatus.SUCCESS)
async def get_all_contacts(
        help_desk_service: Annotated[HelpDeskService, Depends(get_help_desk_service)]
):
    return await help_desk_service.get_all_contacts()


@public_router.get(
    "/search",
    response_model=GetHelpDeskResponseModel,
    description="Получить контакт по фильтру phone или address"
)
@service_response_decorator(status_response=ServiceAPIResponseStatus.SUCCESS)
async def get_contact_by_filter_search(
        help_desk_service: Annotated[HelpDeskService, Depends(get_help_desk_service)],
        phone: str | None = Query(default=None),
        address: str | None = Query(default=None),
):
    return await help_desk_service.filter_contact_by_phone_or_address(
        phone=phone,
        address=address
    )


@public_router.post(
    "",
    response_model=CreateHelpDeskResponseModel,
    description="Создать контакт телефон+адрес"
)
@service_response_decorator(status_response=ServiceAPIResponseStatus.CREATED)
async def create_contact(
        body: CreateHelpDeskDataModel,
        help_desk_service: Annotated[HelpDeskService, Depends(get_help_desk_service)]
):
    return await help_desk_service.create_contact(phone=body.phone, address=body.address)


@public_router.put(
    "/update/{address_id}",
    response_model=UpdateHelpDeskResponseModel,
    description="Обновить контакты телефона или адреса"
)
@service_response_decorator(status_response=ServiceAPIResponseStatus.SUCCESS)
async def update_contact_by_address_id(
        address_id: int,
        body: UpdateHelpDeskModel,
        help_desk_service: Annotated[HelpDeskService, Depends(get_help_desk_service)]
):
    return await help_desk_service.update_contact_by_address_id(
        address_id=address_id,
        phone=body.phone,
        address=body.address
    )


@public_router.delete(
    "/delete/{phone}",
    response_model=DeleteHelpDeskResponseModel,
    description="Удаление данных из системы по телефону"
)
@service_response_decorator(status_response=ServiceAPIResponseStatus.DELETED)
async def delete_contact_by_phone(
        phone: str,
        help_desk_service: Annotated[HelpDeskService, Depends(get_help_desk_service)]
):
    return await help_desk_service.delete_by_phone(phone=phone)
