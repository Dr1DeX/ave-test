from typing import Annotated

from fastapi import APIRouter, Response, Depends
from fastapi import status

from app.base.services.dependency import get_healthcheck_service
from app.base.services.healthcheck import HealthCheckService

home_router = APIRouter()


@home_router.get("/healthcheck")
async def home(
        health_check_service: Annotated[HealthCheckService, Depends(get_healthcheck_service)]
):
    is_ok, unhealthy_services = await health_check_service.is_application_healthy()

    response_data = "OK" if is_ok else f"Unavailable services: {','.join(unhealthy_services)}"
    return Response(
        status_code=status.HTTP_200_OK if is_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=response_data,
        headers={"Content-Type": "text/plain"},
    )
