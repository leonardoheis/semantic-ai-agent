"""Health check route."""

from dependency_injector.wiring import inject
from fastapi import APIRouter

from .schema import HealthResponse
from semantic_ai_agent.utils import ping_redis

from semantic_ai_agent.settings import Settings

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse)
@inject
def health_check() -> HealthResponse:
    client = ping_redis(Settings.REDIS_URL)
    is_connected = client is not None
    return HealthResponse(
        status="healthy" if is_connected else "degraded",
        redis_connected=is_connected,
    )
