"""
Cache helper utilities for Redis Semantic Caching project.

SemanticCacheWrapper has been replaced by focused services:
  - CacheQueryService     (services/cache/query_service.py)
  - CacheHydrationService (services/cache/hydration_service.py)
  - CacheAdminService     (services/cache/admin_service.py)

CacheResult and CacheResults are domain models (domain/cache_result.py).
"""

from semantic_ai_agent.services.cache import CacheQueryService, CacheHydrationService
from .config import config, load_openai_key
from .evals import CacheEvaluator, PerfEval
from semantic_ai_agent.domain.cache_result import CacheResult, CacheResults
from semantic_ai_agent.utils import try_connect_to_redis

__all__ = [
    "CacheEvaluator",
    "CacheResult",
    "CacheResults",
    "CacheQueryService",
    "CacheHydrationService",
    "PerfEval",
    "config",
    "load_openai_key",
    "try_connect_to_redis",
]
