from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware import Middleware
from contextlib import asynccontextmanager
from typing import AsyncIterator

from api import init_sub_applications
from app.configure_application import configure_application_for_run
from core.config import config
from core.fastapi.middlewares import SQLAlchemyMiddleware


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(SQLAlchemyMiddleware),
        Middleware(CorrelationIdMiddleware, header_name="X-Request-ID", validator=None),
    ]

    return middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await configure_application_for_run()

    # отдаём управление приложению
    try:
        yield
    finally:
        # TODO: разместить shutdown-логику?
        pass


def create_app() -> FastAPI:
    app_ = FastAPI(
        title=f"{config.MICROSERVICE_NAME}-service",
        description=f"{config.MICROSERVICE_NAME} Service API",
        version="1.0.0",
        docs_url=None if config.ENV == "production" else "/docs",
        redoc_url=None if config.ENV == "production" else "/redoc",
        middleware=make_middleware(),
        lifespan=lifespan,
    )
    init_sub_applications(app_=app_)
    return app_


app = create_app()
