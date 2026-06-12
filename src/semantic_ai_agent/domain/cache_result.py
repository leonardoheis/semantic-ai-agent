"""Cache result domain models."""

from .base import DomainBase


class CacheResult(DomainBase):
    prompt: str
    response: str
    vector_distance: float
    cosine_similarity: float
    reranker_type: str | None = None
    reranker_score: float | None = None
    reranker_reason: str | None = None


class CacheResults(DomainBase):
    query: str
    matches: list[CacheResult]

    def __repr__(self) -> str:
        return f"(Query: '{self.query}', Matches: {[m.prompt for m in self.matches]})"
