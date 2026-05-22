"""Chat error handler functions."""

from fastapi import Request
from fastapi.responses import JSONResponse

from semantic_ai_agent.services.chat.exceptions import CacheConnectionError, LLMError


async def cache_connection_handler(_: Request, exc: CacheConnectionError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": exc.detail})


async def llm_error_handler(_: Request, exc: LLMError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": exc.detail})
