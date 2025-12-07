from pydantic import BaseModel

from api.base.v1.response.base import BaseResponseModel


class HelpDeskResponseSchema(BaseModel):
    phone: str | None
    address: str | None


class DeleteHelpDeskResponseSchema(BaseModel):
    delete_contact_id: int | None


class GetHelpDeskResponseModel(BaseResponseModel):
    result: HelpDeskResponseSchema


class GetListHelpDeskResponseModel(BaseResponseModel):
    result: list[HelpDeskResponseSchema]


class CreateHelpDeskResponseModel(BaseResponseModel):
    result: HelpDeskResponseSchema


class UpdateHelpDeskResponseModel(BaseResponseModel):
    result: HelpDeskResponseSchema


class DeleteHelpDeskResponseModel(BaseResponseModel):
    result: DeleteHelpDeskResponseSchema
