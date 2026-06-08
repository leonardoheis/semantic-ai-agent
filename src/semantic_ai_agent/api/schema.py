"""Pydantic v2 API request/response schemas."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, arbitrary_types_allowed=True)


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for multi-turn conversation. Null to start a new session.",
    )
    message: str = Field(..., min_length=1, description="The user's question.")

    @classmethod
    def create_example(cls, message: str = "What is the remote work policy?") -> "ChatRequest":
        return cls(message=message)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    source: Literal["cache_hit", "llm_generated"]
    latency_ms: float
    distance: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    redis_connected: bool


class HydrateRequest(BaseModel):
    faq_path: Optional[str] = Field(
        default=None,
        description="Path to FAQ JSON file. Defaults to data/raw/faq_data.json.",
    )

    @classmethod
    def create_example(cls, faq_path: Optional[str] = None) -> "HydrateRequest":
        return cls(faq_path=faq_path)


class HydrateResponse(BaseModel):
    entries_loaded: int
    categories: list[str]


class CacheStatsResponse(BaseModel):
    total_entries: int
    index_name: str
    distance_threshold: float
    ttl_seconds: int


class ErrorResponse(BaseModel):
    detail: str
