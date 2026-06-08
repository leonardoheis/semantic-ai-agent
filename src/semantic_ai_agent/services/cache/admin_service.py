"""Cache admin service — lifecycle management (clear, stats)."""

from pydantic import ConfigDict, Field
from redisvl.extensions.cache.llm import SemanticCache

from semantic_ai_agent.domain.cache_stats import CacheStats
from semantic_ai_agent.domain.base import DomainBase
from semantic_ai_agent.services.cache.exceptions import CacheStatsError


class CacheAdminService(DomainBase):
    """Responsible for cache lifecycle management."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)

    cache: SemanticCache = Field(..., description="The shared semantic cache instance.")

    def clear(self) -> None:
        """Remove all entries from the semantic cache."""
        self.cache.clear()

    def stats(self) -> CacheStats:
        """Return current cache index statistics."""
        try:
            index_info = self.cache.index.info()
        except Exception as exc:
            raise CacheStatsError(detail=f"Failed to retrieve stats: {exc}") from exc
        return CacheStats(
            total_entries=int(index_info.get("num_docs", 0)),
            index_name=self.cache.index.name,
            distance_threshold=self.cache._distance_threshold,
            ttl_seconds=self.cache.ttl or 0,
        )
