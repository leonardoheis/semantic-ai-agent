"""Domain models — pure Pydantic v2 objects with no framework dependencies."""

from .base import DomainBase
from .cache_entry import CacheEntry
from .cache_result import CacheResult, CacheResults
from .cache_stats import CacheStats
from .chat_message import ChatMessage
from .chat_result import ChatResult
from .faq_data import FaqEntry
from .hydrate_result import HydrateResult
from .protocols import CacheReader, CacheWriter

__all__ = [
    "CacheEntry",
    "CacheReader",
    "CacheResult",
    "CacheResults",
    "CacheStats",
    "CacheWriter",
    "ChatMessage",
    "ChatResult",
    "DomainBase",
    "FaqEntry",
    "HydrateResult",
]
