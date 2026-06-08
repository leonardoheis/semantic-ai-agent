"""Health route response schema."""

from semantic_ai_agent.api.schema import BaseSchema


class HealthResponse(BaseSchema):
    status: str
    redis_connected: bool
