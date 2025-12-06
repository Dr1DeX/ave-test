from functools import wraps
from logging import getLogger
from traceback import print_exc

from fastapi import status
from fastapi.responses import ORJSONResponse

from api.base.v1.response import BaseResponseModel
from core.exceptions.service import ServiceAPIResponseStatus, ServiceAPIException

logger = getLogger(__name__)


def service_response_decorator(handler):
    """
    дефолтный респонс декоратор используется в public рутах
    """

    @wraps(handler)
    async def wrapper(*args, **kwargs):
        try:
            response = await handler(*args, **kwargs)
            return BaseResponseModel(result=response)

        except ServiceAPIException as err:
            response_body = BaseResponseModel(result=err.extra_data, error_message=err.message, status=err.status)
            return ORJSONResponse(
                content=response_body.dict(),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            # да я злодей )
            print_exc()
            response_body = BaseResponseModel(
                result={},
                error_message="Unexpected error.",
                status=ServiceAPIResponseStatus.GENERAL_ERROR,
            )
            return ORJSONResponse(content=response_body.dict(), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper
