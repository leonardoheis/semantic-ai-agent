"""Cache result domain models."""

from typing import Optional

from .base import DomainBase


class CacheResult(DomainBase):
    prompt: str
    response: str
    vector_distance: float
    cosine_similarity: float
    reranker_type: Optional[str] = None
    reranker_score: Optional[float] = None
    reranker_reason: Optional[str] = None


class CacheResults(DomainBase):
    query: str
    matches: list[CacheResult]

    def __repr__(self) -> str:
        return f"(Query: '{self.query}', Matches: {[m.prompt for m in self.matches]})"
