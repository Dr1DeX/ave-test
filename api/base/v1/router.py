from fastapi import APIRouter, Response
from fastapi import status

from app.base.services.healthcheck import HealthCheckService

home_router = APIRouter()


@home_router.get("/healthcheck")
async def home():
    is_ok, unhealthy_services = await HealthCheckService.is_application_healthy()

    response_data = "OK" if is_ok else f"Unavailable services: {','.join(unhealthy_services)}"
    return Response(
        status_code=status.HTTP_200_OK if is_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=response_data,
        headers={"Content-Type": "text/plain"},
    )
