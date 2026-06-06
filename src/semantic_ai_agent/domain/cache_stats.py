"""Cache statistics domain model."""

from .base import DomainBase


class CacheStats(DomainBase):
    total_entries: int
    index_name: str
    distance_threshold: float
    ttl_seconds: int
