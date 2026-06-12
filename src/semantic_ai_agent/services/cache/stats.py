"""Cache stats — read-only index statistics."""

from pydantic import ConfigDict, Field
from redisvl.extensions.cache.llm import SemanticCache

from semantic_ai_agent.domain.base import DomainBase
from semantic_ai_agent.domain.cache_stats import CacheStats
from semantic_ai_agent.services.cache.exceptions import CacheStatsError


class CacheStatsService(DomainBase):
    """Responsible for reporting cache index statistics."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)

    cache: SemanticCache = Field(..., description="The shared semantic cache instance.")

    def stats(self) -> CacheStats:
        """Return current cache index statistics.

        Returns:
            CacheStats object containing total entries, index name, distance threshold, and TTL.
        Raises:
            CacheStatsError: If the cache index statistics cannot be retrieved.
        """
        try:
            index_info = self.cache.index.info()
        except Exception as exc:
            raise CacheStatsError(detail=f"Failed to retrieve stats: {exc}") from exc
        return CacheStats(
            total_entries=int(index_info.get("num_docs", 0)),
            index_name=self.cache.index.name,
            distance_threshold=self.cache.distance_threshold,
            ttl_seconds=self.cache.ttl or 0,
        )
