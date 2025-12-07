from fastapi import FastAPI

from api.base.v1.response.base import BaseResponseModel
from core.exceptions.service import ServiceAPIException
from core.fastapi.exceptions.handlers import service_api_exception_handler
from .router import public_router

public_subapi = FastAPI()

public_subapi.include_router(public_router, responses={
    "default": {
        "model": BaseResponseModel
    }
})
public_subapi.add_exception_handler(ServiceAPIException, service_api_exception_handler)
