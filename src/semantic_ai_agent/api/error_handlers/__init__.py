"""Exception handler registry."""

from collections.abc import Callable

from fastapi import Request, Response

from semantic_ai_agent.services.chat.exceptions import CacheConnectionError, LLMError

from .chat import cache_connection_handler, llm_error_handler

ExceptionHandler = Callable[[Request, Exception], Response]

EXCEPTION_HANDLERS: dict[type[Exception], ExceptionHandler] = {
    CacheConnectionError: cache_connection_handler,  # type: ignore[dict-item]
    LLMError: llm_error_handler,  # type: ignore[dict-item]
}

__all__ = ["EXCEPTION_HANDLERS"]
