"""API route definitions."""

from .cache import CacheStatsResponse, HydrateRequest, HydrateResponse, cache_router
from .chat import ChatRequest, ChatResponse, ErrorResponse, chat_router
from .health import health_router
from .registry import ROUTERS

__all__ = [
    "ROUTERS",
    "CacheStatsResponse",
    "ChatRequest",
    "ChatResponse",
    "ErrorResponse",
    "HydrateRequest",
    "HydrateResponse",
    "cache_router",
    "chat_router",
    "health_router",
]
