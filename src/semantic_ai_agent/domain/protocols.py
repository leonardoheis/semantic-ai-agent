"""Structural protocols for service dependencies."""

from typing import Protocol, runtime_checkable

from semantic_ai_agent.domain.cache_result import CacheResults


@runtime_checkable
class CacheReader(Protocol):
    def check(
        self,
        query: str,
        distance_threshold: float | None = None,
        num_results: int = 1,
        use_reranker_distance: bool = False,
    ) -> CacheResults: ...


@runtime_checkable
class CacheWriter(Protocol):
    def store(self, prompt: str, response: str, **kwargs: object) -> None: ...
