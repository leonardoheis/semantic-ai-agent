"""Cache admin — lifecycle management (clear only)."""

from pydantic import ConfigDict, Field
from redisvl.extensions.cache.llm import SemanticCache

from semantic_ai_agent.domain.base import DomainBase


class CacheAdminService(DomainBase):
    """Responsible for cache lifecycle management."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)

    cache: SemanticCache = Field(..., description="The shared semantic cache instance.")

    def clear(self) -> None:
        """Remove all entries from the semantic cache."""
        self.cache.clear()
