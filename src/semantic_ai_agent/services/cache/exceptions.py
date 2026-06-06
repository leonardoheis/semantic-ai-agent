"""Cache service exceptions."""
from dataclasses import dataclass


@dataclass
class FaqFileNotFoundError(Exception):
    detail: str = "Cannot connect to Redis cache"

@dataclass
class CacheHydrationError(Exception):
    detail: str = "Failed to load entries into the cache"

@dataclass
class CacheStatsError(Exception):
    detail: str = "Failed to retrieve cache index statistics"