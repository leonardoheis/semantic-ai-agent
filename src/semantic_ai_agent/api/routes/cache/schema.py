"""Cache route request/response schemas."""

from typing import Optional

from pydantic import Field

from semantic_ai_agent.api.schema import BaseSchema


class HydrateRequest(BaseSchema):
    faq_path: Optional[str] = Field(
        default=None,
        description="Path to FAQ JSON file. Defaults to data/raw/faq_data.json.",
    )

    @classmethod
    def create_example(cls, faq_path: Optional[str] = None) -> "HydrateRequest":
        return cls(faq_path=faq_path)


class HydrateResponse(BaseSchema):
    entries_loaded: int
    categories: list[str]


class CacheStatsResponse(BaseSchema):
    total_entries: int
    index_name: str
    distance_threshold: float
    ttl_seconds: int
