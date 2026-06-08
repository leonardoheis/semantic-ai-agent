"""Cache query service — reads and writes entries to the semantic cache."""

from typing import Callable, Optional

from pydantic import ConfigDict, Field
from redisvl.extensions.cache.llm import SemanticCache
from tqdm.auto import tqdm

from semantic_ai_agent.domain.base import DomainBase
from semantic_ai_agent.domain.cache_result import CacheResult, CacheResults
from semantic_ai_agent.services.cache.exceptions import CacheQueryError, CacheStoreError

RerankerFn = Callable[[str, list[dict]], list[dict]]


class CacheQueryService(DomainBase):
    """Responsible for cache lookups and storing new answers."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)

    cache: SemanticCache = Field(..., description="The shared semantic cache instance.")
    reranker: Optional[RerankerFn] = Field(default=None, description="Optional reranking function.")

    def check(
        self,
        query: str,
        distance_threshold: Optional[float] = None,
        num_results: int = 1,
        use_reranker_distance: bool = False,
    ) -> CacheResults:
        """Check the semantic cache for a matching entry."""
        try:
            _num = num_results if self.reranker is None else max(10, 3 * num_results)
            candidates = self.cache.check(
                query, distance_threshold=distance_threshold, num_results=_num
            )
        except Exception as exc:
            raise CacheQueryError(detail=f"Cache query failed: {exc}") from exc

        if not candidates:
            return CacheResults(query=query, matches=[])

        if self.reranker is not None:
            candidates = self.reranker(query, candidates)

        results: list[CacheResult] = []
        for item in candidates[:num_results]:
            result = dict(item)
            result["vector_distance"] = float(result.get("vector_distance", 0.0))
            result["cosine_similarity"] = float((2 - result["vector_distance"]) / 2)
            result["query"] = query
            if self.reranker is not None:
                result["reranker_type"] = result.get("reranker_type")
                result["reranker_score"] = result.get("reranker_score")
                result["reranker_reason"] = result.get("reranker_reason")
                if use_reranker_distance:
                    result["vector_distance"] = result.get(
                        "reranker_distance", result["vector_distance"]
                    )
            results.append(CacheResult(**result))

        return CacheResults(query=query, matches=results)

    def check_many(
        self,
        queries: list[str],
        distance_threshold: Optional[float] = None,
        show_progress: bool = False,
        num_results: int = 1,
        use_reranker_distance: bool = False,
    ) -> list[CacheResults]:
        """Check the semantic cache for multiple queries."""
        return [
            self.check(q, distance_threshold, num_results, use_reranker_distance)
            for q in tqdm(queries, disable=not show_progress)
        ]

    def store(self, prompt: str, response: str, **kwargs: object) -> None:
        """Store a prompt-response pair in the cache."""
        try:
            self.cache.store(prompt=prompt, response=response, **kwargs)
        except Exception as exc:
            raise CacheStoreError(detail=f"Failed to store entry: {exc}") from exc

    def register_reranker(self, reranker: RerankerFn) -> None:
        """Register an optional reranking function."""
        if not callable(reranker):
            raise TypeError("Reranker must be a callable")
        self.reranker = reranker

    def clear_reranker(self) -> None:
        """Remove the registered reranker."""
        self.reranker = None

    def has_reranker(self) -> bool:
        """Return True if a reranker is registered."""
        return self.reranker is not None
