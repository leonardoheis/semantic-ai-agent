"""API route definitions."""

from .cache import cache_router
from .chat import chat_router
from .health import health_router

ROUTERS = [health_router, chat_router, cache_router]

__all__ = ["ROUTERS"]
