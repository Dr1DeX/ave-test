from .enum import ServiceAPIResponseMessage, ServiceAPIResponseStatus


class ServiceAPIException(Exception):
    def __init__(
        self,
        status: int = ServiceAPIResponseStatus.GENERAL_ERROR,
        message: str = ServiceAPIResponseMessage.GENERAL_ERROR,
        extra_data=None,
    ):
        if extra_data is None:
            extra_data = dict()

        self.status = status
        self.message = message
        self.extra_data = extra_data
