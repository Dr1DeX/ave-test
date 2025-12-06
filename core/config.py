import os
from uuid import uuid4

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Конфиг для приложения, подбирает .env файл и перезаписывает переменные, если имеются такие же тут,
    """

    # APP
    ENV: str = "development"

    # # FastAPI
    MICROSERVICE_NAME: str = "ave"  # CHANGEME
    APP_HOST: str = "localhost"
    APP_PORT: int = 8889

    APP_UNIQUE_ID: str = str(uuid4().hex[:10])

    # # LOGGING
    DEBUG: bool = True

    # Databases
    # # Postgresql
    DATABASE_CONNECTION_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ave"
    DATABASE_MAX_OVERFLOW: int = 15
    DATABASE_POOL_SIZE: int = 30
    DATABASE_ECHO: bool = False

    # # Redis
    REDIS_CONNECTION_URL: str = "redis://default:redis12345@localhost:6390"


class DevelopmentConfig(Config):
    DATABASE_ECHO: bool = True


class ProductionConfig(Config):
    DEBUG: bool = False


def get_config() -> Config:
    env = os.getenv("ENV", "local")
    config_type = {
        "local": DevelopmentConfig(),
        "production": ProductionConfig(),
    }

    return config_type[env]


config: Config = get_config()
