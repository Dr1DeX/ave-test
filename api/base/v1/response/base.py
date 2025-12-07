from typing import Any

from pydantic import BaseModel


class BaseResponseModel(BaseModel):
    """
    Базовая респонс модель
    """

    result: Any = {}
    status: int = 200
    error_message: str = ""
