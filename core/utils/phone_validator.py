import re

from core.exceptions.service import ServiceAPIException, ServiceAPIResponseStatus


def validate_phone(phone: str) -> bool:
    if not phone:
        return False

    phone_clean = phone.replace(" ", "").replace("-", "")
    pattern = r'^(\+7|7|8)\d{10}$'

    return bool(re.match(pattern, phone_clean))


def normalize_phone(phone: str) -> str:
    if not phone:
        return phone

    phone_clean = phone.replace(" ", "").replace("-", "")

    if phone_clean.startswith("+7"):
        return phone_clean
    elif phone_clean.startswith("7"):
        return "+7" + phone_clean[1:]
    elif phone_clean.startswith("8"):
        return "+7" + phone_clean[1:]


def phone_validator_by_query_param(phone: str) -> str:
    if phone is not None:
        if not validate_phone(phone):
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.BAD_REQUEST,
                message=f"Invalid phone number format. Expected: +71234567890, 71234567890 or 81234567890",
                extra_data={"field": "phone", "value": phone}
            )
        return normalize_phone(phone)
