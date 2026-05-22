"""FastAPI dependency injection providers using dependency-injector."""

from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import Depends

from semantic_ai_agent.services.chat.service import ChatService
from semantic_ai_agent.settings import Settings

ChatServiceDependency = Annotated[
    ChatService,
    Depends(Provide["chat_service"]),
]

SettingsDependency = Annotated[
    Settings,
    Depends(Provide["config"]),
]
