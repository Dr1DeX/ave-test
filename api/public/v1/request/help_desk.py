from pydantic import BaseModel, field_validator

from core.exceptions.service import ServiceAPIException, ServiceAPIResponseStatus
from core.utils.phone_validator import validate_phone, normalize_phone


class BaseValidatorModel(BaseModel):
    @field_validator("phone", check_fields=False)
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if v is None:
            return v

        if not validate_phone(v):
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.BAD_REQUEST,
                message=f"Invalid phone number format. Expected: +71234567890, 71234567890 or 81234567890",
                extra_data={"field": "phone", "value": v}
            )
        return normalize_phone(v)


class CreateHelpDeskDataModel(BaseValidatorModel):
    phone: str
    address: str


class UpdateHelpDeskModel(BaseValidatorModel):
    phone: str | None = None
    address: str | None = None


class DeleteHelpDeskModel(BaseValidatorModel):
    phone: str
