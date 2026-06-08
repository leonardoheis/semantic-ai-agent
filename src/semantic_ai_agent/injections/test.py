"""Test dependency bindings — mocked services and LLM for testing without external services."""

from typing import Any, Optional
from unittest.mock import MagicMock

from dependency_injector import containers, providers

from pathlib import Path

from semantic_ai_agent.domain.cache_result import CacheResult, CacheResults
from semantic_ai_agent.domain.hydrate_result import HydrateResult
from semantic_ai_agent.services.cache.exceptions import FaqFileNotFoundError
from semantic_ai_agent.services.chat.service import ChatService
from semantic_ai_agent.settings import SettingsType


class MockCacheQueryService:
    """In-memory mock of CacheQueryService for testing."""

    def __init__(self) -> None:
        self.entries: dict[str, str] = {}

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

    def check_many(self, queries: list[str], **kwargs: Any) -> list[CacheResults]:
        return [self.check(q) for q in queries]

    def register_reranker(self, reranker: Any) -> None:
        pass

    def clear_reranker(self) -> None:
        pass

    def has_reranker(self) -> bool:
        return False


class MockCacheHydrationService:
    """In-memory mock of CacheHydrationService for testing."""

    def __init__(self) -> None:
        self.entries: dict[str, str] = {}

    def hydrate(self, faq_path: Optional[str] = None) -> HydrateResult:
        if faq_path and not Path(faq_path).exists():
            raise FaqFileNotFoundError(detail=f"FAQ file not found: {faq_path}")
        return HydrateResult(entries_loaded=0, categories=[])

    def hydrate_from_df(
        self, df: Any, *, q_col: str = "question", a_col: str = "answer", **kw: Any
    ) -> None:
        for _, row in df.iterrows():
            self.entries[row[q_col]] = row[a_col]

    def hydrate_from_pairs(self, pairs: Any, **kw: Any) -> None:
        for q, a in pairs:
            self.entries[q] = a


class MockCacheAdminService:
    """In-memory mock of CacheAdminService for testing."""

    def __init__(self, query_service: MockCacheQueryService) -> None:
        self._query_service = query_service

    def clear(self) -> None:
        self._query_service.entries.clear()

    def stats(self) -> Any:
        from semantic_ai_agent.domain.cache_stats import CacheStats

        return CacheStats(
            total_entries=len(self._query_service.entries),
            index_name="test-cache",
            distance_threshold=0.3,
            ttl_seconds=60,
        )


class MockLLM:
    """Mock LLM that returns a fixed response."""

    def invoke(self, messages: list[dict[str, str]]) -> MagicMock:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        mock_resp = MagicMock()
        mock_resp.content = f"[Mock LLM response for: {last_user}]"
        return mock_resp


_test_settings = SettingsType(
    OPENAI_API_KEY="test-key",
    CACHE_NAME="test-cache",
    CACHE_DISTANCE_THRESHOLD=0.3,
    CACHE_TTL_SECONDS=60,
    OPENAI_MODEL="gpt-test",
    REDIS="localhost",
    REDIS_PORT=6379,
)

_mock_query = MockCacheQueryService()
_mock_hydration = MockCacheHydrationService()
_mock_admin = MockCacheAdminService(query_service=_mock_query)


class TestContainer(containers.DeclarativeContainer):
    """Test container that overrides production with mocks."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "semantic_ai_agent.api.routes.chat.chat",
            "semantic_ai_agent.api.routes.cache.cache",
            "semantic_ai_agent.api.routes.health.health",
        ]
    )

    config: providers.Provider[SettingsType] = providers.Object(_test_settings)

    cache_query_service = providers.Object(_mock_query)
    cache_hydration_service = providers.Object(_mock_hydration)
    cache_admin_service = providers.Object(_mock_admin)

    llm = providers.Singleton(MockLLM)

    chat_service = providers.Factory(
        ChatService,
        cache=cache_query_service,
        llm=llm,
        system_prompt="You are a test HR assistant.",
    )


def create_mock_chat_service() -> ChatService:
    query_svc = MockCacheQueryService()
    llm = MockLLM()
    return ChatService(
        cache=query_svc,  # type: ignore[arg-type]
        llm=llm,  # type: ignore[arg-type]
        system_prompt="You are a test HR assistant.",
    )
