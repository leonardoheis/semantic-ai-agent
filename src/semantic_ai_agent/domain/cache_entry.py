"""Cache entry domain model."""

from typing import Optional

from .base import DomainBase


class CacheEntry(DomainBase):
    prompt: str
    response: str
    category: Optional[str] = None
    distance: float = 0.0
    similarity: float = 1.0
