"""Health check route."""

from dependency_injector.wiring import inject
from fastapi import APIRouter

from semantic_ai_agent.settings import Settings
from semantic_ai_agent.utils import ping_redis

from .schema import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/")
@router.get("/health")
@inject
def health_check() -> HealthResponse:
    client = ping_redis(Settings.REDIS_URL)
    is_connected = client is not None
    return HealthResponse(
        status="healthy" if is_connected else "degraded",
        redis_connected=is_connected,
    )
