"""Production dependency injection container."""

from dependency_injector import containers, providers
from langchain_openai import ChatOpenAI

from semantic_ai_agent.cache.wrapper import SemanticCacheWrapper
from semantic_ai_agent.services.cache.service import CacheService
from semantic_ai_agent.services.chat.service import ChatService
from semantic_ai_agent.settings import Settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "semantic_ai_agent.api.routes.chat",
            "semantic_ai_agent.api.routes.cache",
            "semantic_ai_agent.api.routes.health",
        ]
    )

    config = providers.Singleton(Settings)

    cache = providers.Singleton(
        SemanticCacheWrapper,
        name=config.provided.CACHE_NAME,
        distance_threshold=config.provided.CACHE_DISTANCE_THRESHOLD,
        ttl=config.provided.CACHE_TTL_SECONDS,
        redis_url=config.provided.REDIS_HOST,
    )

    llm = providers.Singleton(
        ChatOpenAI,
        model=config.provided.OPENAI_MODEL,
        temperature=0,
        api_key=config.provided.OPENAI_API_KEY,
    )

    cache_service = providers.Singleton(CacheService, cache=cache)

    chat_service = providers.Singleton(
        ChatService,
        cache=cache,
        llm=llm,
        system_prompt=config.provided.HR_SYSTEM_PROMPT,
    )
