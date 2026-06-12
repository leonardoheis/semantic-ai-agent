"""Production dependency injection container."""

import redis
from dependency_injector import containers, providers
from langchain_openai import ChatOpenAI
from redisvl.extensions.cache.embeddings import EmbeddingsCache
from redisvl.extensions.cache.llm import SemanticCache
from redisvl.utils.vectorize import HFTextVectorizer

from semantic_ai_agent.services.cache.admin import CacheAdminService
from semantic_ai_agent.services.cache.hydration import CacheHydrationService
from semantic_ai_agent.services.cache.query import CacheQueryService
from semantic_ai_agent.services.cache.stats import CacheStatsService
from semantic_ai_agent.services.cache.store import CacheStoreService
from semantic_ai_agent.services.chat.chat import ChatService
from semantic_ai_agent.settings import Settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "semantic_ai_agent.api.routes.chat.chat",
            "semantic_ai_agent.api.routes.cache.cache",
            "semantic_ai_agent.api.routes.health.health",
        ]
    )

    # --- Infrastructure: Singletons (expensive, shared connection) ---

    redis_client = providers.Singleton(redis.Redis.from_url, Settings.REDIS_HOST)

    embeddings_cache = providers.Singleton(
        EmbeddingsCache,
        redis_client=redis_client,
        ttl=Settings.CACHE_TTL_SECONDS,
    )

    vectorizer = providers.Singleton(
        HFTextVectorizer,
        model="redis/langcache-embed-v1",
        cache=embeddings_cache,
    )

    semantic_cache = providers.Singleton(
        SemanticCache,
        name=Settings.CACHE_NAME,
        vectorizer=vectorizer,
        redis_client=redis_client,
        distance_threshold=Settings.CACHE_DISTANCE_THRESHOLD,
        ttl=Settings.CACHE_TTL_SECONDS,
    )

    llm = providers.Singleton(
        ChatOpenAI,
        model=Settings.OPENAI_MODEL,
        temperature=0,
        api_key=Settings.OPENAI_API_KEY,
    )

    # --- Services: Factories (stateless, new instance per injection) ---

    cache_query_service = providers.Factory(CacheQueryService, cache=semantic_cache)
    cache_store_service = providers.Factory(CacheStoreService, cache=semantic_cache)
    cache_hydration_service = providers.Factory(CacheHydrationService, cache=semantic_cache)
    cache_admin_service = providers.Factory(CacheAdminService, cache=semantic_cache)
    cache_stats_service = providers.Factory(CacheStatsService, cache=semantic_cache)

    chat_service = providers.Factory(
        ChatService,
        cache=cache_query_service,
        store=cache_store_service,
        llm=llm,
        system_prompt=Settings.HR_SYSTEM_PROMPT,
    )
