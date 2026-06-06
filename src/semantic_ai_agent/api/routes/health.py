"""Health check route."""

import redis
from dependency_injector.wiring import inject
from fastapi import APIRouter

from semantic_ai_agent.api.dependencies import SettingsDependency
from semantic_ai_agent.api.schema import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
@inject
def health_check(settings: SettingsDependency) -> HealthResponse:
    try:
        client = redis.from_url(settings.REDIS_HOST)
        client.ping()
        is_connected = True
    except Exception:
        is_connected = False
    return HealthResponse(
        status="healthy" if is_connected else "degraded",
        redis_connected=is_connected,
    )
