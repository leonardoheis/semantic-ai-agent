"""FastAPI application factory with lifespan management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from semantic_ai_agent.injections import configure_container

from .error_handlers import EXCEPTION_HANDLERS
from .routes import ROUTERS


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = configure_container()
    app.state.container = container
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="HR Policy FAQ Chatbot",
        description="Semantic-cache-backed chatbot for HR policy questions using redisvl.",
        version="0.1.0",
        lifespan=lifespan,
    )

    for router in ROUTERS:
        app.include_router(router)

    for exception, exception_handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception, exception_handler)

    return app


app = create_app()
