"""API route definitions."""

from .cache import router as cache_router
from .chat import router as chat_router
from .health import router as health_router

ROUTERS = [health_router, chat_router, cache_router]

__all__ = ["ROUTERS"]
