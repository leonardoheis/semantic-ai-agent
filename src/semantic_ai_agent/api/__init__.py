"""API package — exposes create_app factory and run_api entry point."""

import uvicorn

from semantic_ai_agent.settings import Settings

from .app import create_app


def run_api() -> None:
    settings = Settings()
    uvicorn.run(
        "semantic_ai_agent.api.app:app",
        host=settings.host,
        port=settings.api_port,
        reload=True,
    )


__all__ = ["create_app", "run_api"]
