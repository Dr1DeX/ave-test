import logging
import time
from contextvars import ContextVar
from logging import Filter, LogRecord
from logging import config, Formatter

from core.config import config as app_config

app_unique_id: ContextVar[str] = ContextVar("app_unique_id")
app_unique_id.set(app_config.APP_UNIQUE_ID)


class UniqueAppIDFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        record.app_unique_id = app_unique_id.get()

        return True


class GMTFormatter(Formatter):
    converter = time.gmtime


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "correlation_id": {
            "()": "asgi_correlation_id.CorrelationIdFilter",
            "uuid_length": 32 if not app_config.ENV == "local" else 10,
        },
        "app_unique_id": {"()": "core.utils.logging.UniqueAppIDFilter"},
    },
    "formatters": {
        "lines": {
            "format": "%(asctime)s [%(levelname)s] %(pathname)s %(lineno)d %(message)s [%(app_unique_id)s] "
            "[%(correlation_id)s]",
            "()": GMTFormatter,
        },
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(message)s [%(app_unique_id)s] [%(correlation_id)s] ",
            "()": GMTFormatter,
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "filters": ["correlation_id", "app_unique_id"],
            "formatter": "simple",
        },
        "debug": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["correlation_id", "app_unique_id"],
            "formatter": "simple",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "filters": ["correlation_id", "app_unique_id"],
            "level": logging.DEBUG,
            "propagate": False,
        },
        "asgi_correlation_id": {"handlers": ["default"], "level": logging.WARNING},
    },
}


def config_logging():
    config.dictConfig(LOGGING)
