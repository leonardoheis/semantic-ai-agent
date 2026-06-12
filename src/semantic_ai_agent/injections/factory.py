"""Container factory and wiring."""

from functools import cache

from .production import Container


@cache
def configure_container() -> Container:
    """Configure the dependency injection container for production.

    Returns:
        The configured dependency injection container.
    """
    container = Container()
    container.wire(packages=["semantic_ai_agent"])
    return container
