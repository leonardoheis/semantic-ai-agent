"""Chat service exceptions."""

from dataclasses import dataclass


@dataclass
class CacheConnectionError(Exception):
    detail: str = "Cannot connect to Redis cache"


@dataclass
class LLMError(Exception):
    detail: str = "LLM API call failed"
