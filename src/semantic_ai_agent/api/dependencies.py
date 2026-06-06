"""FastAPI dependency injection providers using dependency-injector."""

from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import Depends

from semantic_ai_agent.services.cache.service import CacheService
from semantic_ai_agent.services.chat.service import ChatService
from semantic_ai_agent.settings import Settings

CacheServiceDependency = Annotated[
    CacheService,
    Depends(Provide["cache_service"]),
]

ChatServiceDependency = Annotated[
    ChatService,
    Depends(Provide["chat_service"]),
]

SettingsDependency = Annotated[
    Settings,
    Depends(Provide["config"]),
]
