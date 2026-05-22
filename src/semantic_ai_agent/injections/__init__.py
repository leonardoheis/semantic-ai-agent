"""Dependency injection containers for production and testing."""

from functools import cache

from .production import Container
from .test import TestContainer


@cache
def configure_container() -> Container:
    container = Container()
    container.wire(packages=["semantic_ai_agent"])
    return container


__all__ = ["Container", "TestContainer", "configure_container"]
