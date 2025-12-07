from fastapi import FastAPI

from api.base.v1.router import home_router
from api.public.app import public_subapi


def include_main_app_routers(app_: FastAPI):
    app_.include_router(home_router)


def init_sub_applications(app_: FastAPI):
    app_.mount("/api/public", public_subapi)
    include_main_app_routers(app_)
