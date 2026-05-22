"""Production dependency injection container."""

from dependency_injector import containers, providers
from langchain_openai import ChatOpenAI

from semantic_ai_agent.cache.wrapper import SemanticCacheWrapper
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
        name=config.provided.cache_name,
        distance_threshold=config.provided.distance_threshold,
        ttl=config.provided.ttl_seconds,
        redis_url=config.provided.redis_url,
    )

    llm = providers.Singleton(
        ChatOpenAI,
        model=config.provided.openai_model,
        temperature=0,
        api_key=config.provided.openai_api_key,
    )

    chat_service = providers.Singleton(
        ChatService,
        cache=cache,
        llm=llm,
        system_prompt=config.provided.hr_system_prompt,
    )
