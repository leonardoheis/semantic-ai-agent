"""Test dependency bindings — mocked services and LLM for testing without external services."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from dependency_injector import containers, providers

from semantic_ai_agent.domain.cache_result import CacheResult, CacheResults
from semantic_ai_agent.domain.cache_stats import CacheStats
from semantic_ai_agent.domain.hydrate_result import HydrateResult
from semantic_ai_agent.services.cache.exceptions import FaqFileNotFoundError
from semantic_ai_agent.services.chat.chat import ChatService


class MockCacheQueryService:
    """In-memory mock of CacheQueryService for testing."""

    def __init__(self) -> None:
        self.entries: dict[str, str] = {}

    def check(
        self,
        query: str,
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

    def check_many(self, queries: list[str]) -> list[CacheResults]:
        return [self.check(q) for q in queries]


class MockCacheStoreService:
    """In-memory mock of CacheStoreService for testing."""

    def __init__(self, query_service: MockCacheQueryService) -> None:
        self._query_service = query_service

    def store(self, prompt: str, response: str) -> None:
        self._query_service.entries[prompt] = response


class MockCacheHydrationService:
    """In-memory mock of CacheHydrationService for testing."""

    def __init__(self) -> None:
        self.entries: dict[str, str] = {}

    @staticmethod
    def hydrate(
        faq_path: str | None = None,
    ) -> HydrateResult:
        if faq_path and not Path(faq_path).exists():
            raise FaqFileNotFoundError(detail=f"FAQ file not found: {faq_path}")
        return HydrateResult(entries_loaded=0, categories=[])

    def hydrate_from_df(self, df: Any, *, q_col: str = "question", a_col: str = "answer") -> None:
        for _, row in df.iterrows():
            self.entries[row[q_col]] = row[a_col]

    def hydrate_from_pairs(self, pairs: Any) -> None:
        for q, a in pairs:
            self.entries[q] = a


class MockCacheAdminService:
    """In-memory mock of CacheAdminService for testing."""

    def __init__(self, query_service: MockCacheQueryService) -> None:
        self._query_service = query_service

    def clear(self) -> None:
        self._query_service.entries.clear()


class MockCacheStatsService:
    """In-memory mock of CacheStatsService for testing."""

    def __init__(self, query_service: MockCacheQueryService) -> None:
        self._query_service = query_service

    def stats(self) -> CacheStats:
        return CacheStats(
            total_entries=len(self._query_service.entries),
            index_name="test-cache",
            distance_threshold=0.3,
            ttl_seconds=60,
        )


class MockLLM:
    """Mock LLM that returns a fixed response."""

    @staticmethod
    def invoke(
        messages: list[dict[str, str]],
    ) -> MagicMock:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        mock_resp = MagicMock()
        mock_resp.content = f"[Mock LLM response for: {last_user}]"
        return mock_resp


_mock_query = MockCacheQueryService()
_mock_store = MockCacheStoreService(query_service=_mock_query)
_mock_hydration = MockCacheHydrationService()
_mock_admin = MockCacheAdminService(query_service=_mock_query)
_mock_stats = MockCacheStatsService(query_service=_mock_query)


class TestContainer(containers.DeclarativeContainer):
    """Test container that overrides production with mocks."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "semantic_ai_agent.api.routes.chat.chat",
            "semantic_ai_agent.api.routes.cache.cache",
            "semantic_ai_agent.api.routes.health.health",
        ]
    )

    cache_query_service = providers.Object(_mock_query)
    cache_store_service = providers.Object(_mock_store)
    cache_hydration_service = providers.Object(_mock_hydration)
    cache_admin_service = providers.Object(_mock_admin)
    cache_stats_service = providers.Object(_mock_stats)

    llm = providers.Singleton(MockLLM)

    chat_service = providers.Factory(
        ChatService,
        cache=cache_query_service,
        store=cache_store_service,
        llm=llm,
        system_prompt="You are a test HR assistant.",
    )


def create_mock_chat_service() -> ChatService:
    query_svc = MockCacheQueryService()
    store_svc = MockCacheStoreService(query_service=query_svc)
    llm = MockLLM()
    return ChatService(
        cache=query_svc,  # type: ignore[arg-type]
        store=store_svc,  # type: ignore[arg-type]
        llm=llm,  # type: ignore[arg-type]
        system_prompt="You are a test HR assistant.",
    )
