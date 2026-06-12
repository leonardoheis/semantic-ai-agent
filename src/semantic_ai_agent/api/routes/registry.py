"""Registered API routers."""

from collections.abc import Iterable

from fastapi import APIRouter

from .cache import cache_router
from .chat import chat_router
from .health import health_router

ROUTERS: Iterable[APIRouter] = (
    health_router,
    chat_router,
    cache_router,
)
