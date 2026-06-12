"""Cache store — writes entries to the semantic cache."""

from pydantic import ConfigDict, Field
from redisvl.extensions.cache.llm import SemanticCache

from semantic_ai_agent.domain.base import DomainBase
from semantic_ai_agent.services.cache.exceptions import CacheStoreError


class CacheStoreService(DomainBase):
    """Responsible for storing new entries in the cache."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)

    cache: SemanticCache = Field(..., description="The shared semantic cache instance.")

    def store(self, prompt: str, response: str, **kwargs: object) -> None:
        """Store a prompt-response pair in the cache.

        Raises:
            CacheStoreError: If the entry cannot be stored.
        """
        try:
            self.cache.store(prompt=prompt, response=response, **kwargs)
        except Exception as exc:
            raise CacheStoreError(detail=f"Failed to store entry: {exc}") from exc
