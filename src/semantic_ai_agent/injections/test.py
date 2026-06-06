"""Test dependency bindings — mocked cache and LLM for testing without external services."""

from typing import Any, Optional
from unittest.mock import MagicMock

from dependency_injector import containers, providers

from semantic_ai_agent.cache.wrapper import CacheResult, CacheResults
from semantic_ai_agent.services.cache.service import CacheService
from semantic_ai_agent.services.chat.service import ChatService
from semantic_ai_agent.settings import Settings


class MockCacheWrapper:
    """In-memory mock of SemanticCacheWrapper for testing."""

    def __init__(self):
        self.entries: dict[str, str] = {}
        self._name = "test-cache"

    def check(
        self,
        query: str,
        distance_threshold: Optional[float] = None,
        num_results: int = 1,
        use_reranker_distance: bool = False,
    ) -> CacheResults:
        if query in self.entries:
            return CacheResults(
                query=query,
                matches=[
                    CacheResult(
                        prompt=query,
                        response=self.entries[query],
                        vector_distance=0.0,
                        cosine_similarity=1.0,
                    )
                ],
            )
        return CacheResults(query=query, matches=[])

    def store(self, prompt: str, response: str, **kwargs: Any) -> None:
        self.entries[prompt] = response

    def clear(self) -> None:
        self.entries.clear()

    def hydrate_from_df(
        self, df: Any, *, q_col: str = "question", a_col: str = "answer", **kw: Any
    ):
        for _, row in df.iterrows():
            self.entries[row[q_col]] = row[a_col]


class MockLLM:
    """Mock LLM that returns a fixed response."""

    def invoke(self, messages: list[dict[str, str]]) -> MagicMock:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        mock_resp = MagicMock()
        mock_resp.content = f"[Mock LLM response for: {last_user}]"
        return mock_resp


class TestContainer(containers.DeclarativeContainer):
    """Test container that overrides production with mocks."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "semantic_ai_agent.api.routes.chat",
            "semantic_ai_agent.api.routes.cache",
            "semantic_ai_agent.api.routes.health",
        ]
    )

    config = providers.Singleton(
        Settings,
        OPENAI_API_KEY="test-key",
        CACHE_NAME="test-cache",
        CACHE_DISTANCE_THRESHOLD=0.3,
        CACHE_TTL_SECONDS=60,
        OPENAI_MODEL="gpt-test",
        REDIS="localhost",
        REDIS_PORT=6379,
    )

    cache = providers.Singleton(MockCacheWrapper)

    llm = providers.Singleton(MockLLM)

    cache_service = providers.Singleton(CacheService, cache=cache)

    chat_service = providers.Singleton(
        ChatService,
        cache=cache,
        llm=llm,
        system_prompt="You are a test HR assistant.",
    )


def create_mock_chat_service() -> ChatService:
    cache = MockCacheWrapper()
    llm = MockLLM()
    return ChatService(
        cache=cache,  # type: ignore[arg-type]
        llm=llm,  # type: ignore[arg-type]
        system_prompt="You are a test HR assistant.",
    )
