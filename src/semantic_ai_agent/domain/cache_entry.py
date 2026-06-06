"""Cache entry domain model."""

from .base import DomainBase


class CacheEntry(DomainBase):
    prompt: str
    response: str
    distance: float = 0.0
    similarity: float = 1.0
