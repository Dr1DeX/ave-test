from typing import Any

from pydantic import BaseModel


class BaseResponseModel(BaseModel):
    """
    Базовая респонс модель
    """

    result: Any = {}
    status: int = 0
    error_message: str = ""
