"""FastAPI application factory with lifespan management."""

from fastapi import FastAPI

from .error_handlers import EXCEPTION_HANDLERS
from .routes import ROUTERS


def create_app() -> FastAPI:
    app = FastAPI(
        title="HR Policy FAQ Chatbot",
        description="Semantic-cache-backed chatbot for HR policy questions using redisvl.",
        version="0.1.0",
    )

    for router in ROUTERS:
        app.include_router(router)

    for exception, exception_handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception, exception_handler)

    return app


app = create_app()
