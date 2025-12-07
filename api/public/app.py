from fastapi import FastAPI

from api.base.v1.response.base import BaseResponseModel
from .router import public_router

public_subapi = FastAPI()

public_subapi.include_router(public_router, responses={
    "default": {
        "model": BaseResponseModel
    }
})
