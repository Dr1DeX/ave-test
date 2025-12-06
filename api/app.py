from fastapi import FastAPI

from api.base.v1.router import home_router


def include_main_app_routers(app_: FastAPI):
    app_.include_router(home_router)


def init_sub_applications(app_: FastAPI):
    include_main_app_routers(app_)
