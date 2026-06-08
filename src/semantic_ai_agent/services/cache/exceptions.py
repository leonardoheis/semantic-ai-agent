"""Cache service exceptions."""

from dataclasses import dataclass


@dataclass
class CacheConnectionError(Exception):
    detail: str = "Cannot connect to Redis cache"


@dataclass
class CacheQueryError(Exception):
    detail: str = "Cache query failed"


@dataclass
class CacheStoreError(Exception):
    detail: str = "Failed to store entry in cache"


@dataclass
class FaqFileNotFoundError(Exception):
    detail: str = "FAQ file not found"


@dataclass
class CacheHydrationError(Exception):
    detail: str = "Failed to load entries into the cache"


@dataclass
class CacheStatsError(Exception):
    detail: str = "Failed to retrieve cache index statistics"
