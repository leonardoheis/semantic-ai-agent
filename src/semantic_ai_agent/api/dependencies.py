"""FastAPI dependency injection providers using dependency-injector."""

from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import Depends

from semantic_ai_agent.services.cache.admin_service import CacheAdminService
from semantic_ai_agent.services.cache.hydration_service import CacheHydrationService
from semantic_ai_agent.services.cache.query_service import CacheQueryService
from semantic_ai_agent.services.chat.service import ChatService
from semantic_ai_agent.settings import SettingsType

CacheAdminServiceDependency = Annotated[
    CacheAdminService,
    Depends(Provide["cache_admin_service"]),
]

CacheHydrationServiceDependency = Annotated[
    CacheHydrationService,
    Depends(Provide["cache_hydration_service"]),
]

CacheQueryServiceDependency = Annotated[
    CacheQueryService,
    Depends(Provide["cache_query_service"]),
]

ChatServiceDependency = Annotated[
    ChatService,
    Depends(Provide["chat_service"]),
]

SettingsDependency = Annotated[
    SettingsType,
    Depends(Provide["config"]),
]
