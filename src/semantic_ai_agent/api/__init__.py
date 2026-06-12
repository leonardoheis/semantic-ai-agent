"""API package — exposes create_app factory and run_api entry point."""

import uvicorn

from semantic_ai_agent.settings import Settings

from .app import create_app


def run_api() -> None:  # noqa: RUF067
    uvicorn.run(
        "semantic_ai_agent.api.app:app",
        host=Settings.HOST,
        port=Settings.API_PORT,
        reload=True,
    )


__all__ = ["create_app", "run_api"]
