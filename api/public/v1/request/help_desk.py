from pydantic import BaseModel


class CreateHelpDeskDataModel(BaseModel):
    phone: str
    address: str


class UpdateHelpDeskModel(BaseModel):
    phone: str | None = None
    address: str | None = None


class DeleteHelpDeskModel(BaseModel):
    phone: str
