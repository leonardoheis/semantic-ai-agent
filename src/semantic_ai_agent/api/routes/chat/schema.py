"""Chat route request/response schemas."""

from typing import Literal

from pydantic import Field

from semantic_ai_agent.api.schema import BaseSchema


class ChatRequest(BaseSchema):
    session_id: str | None = Field(
        default=None,
        description="Session ID for multi-turn conversation. Null to start a new session.",
    )
    message: str = Field(..., min_length=1, description="The user's question.")

    @classmethod
    def create_example(cls, message: str = "What is the remote work policy?") -> "ChatRequest":
        return cls(message=message)


class ChatResponse(BaseSchema):
    session_id: str
    answer: str
    source: Literal["cache_hit", "llm_generated"]
    latency_ms: float
    distance: float | None = None


class ErrorResponse(BaseSchema):
    detail: str
