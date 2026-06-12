"""Cache management routes."""

from typing import Annotated

from dependency_injector.wiring import inject
from fastapi import APIRouter, Body, HTTPException

from semantic_ai_agent.api.dependencies import (
    CacheAdminServiceDependency,
    CacheHydrationServiceDependency,
    CacheStatsServiceDependency,
)
from semantic_ai_agent.services.cache.exceptions import FaqFileNotFoundError

from .examples import EXAMPLES
from .schema import CacheStatsResponse, HydrateRequest, HydrateResponse

router = APIRouter(prefix="/cache", tags=["cache"])


@router.post("/hydrate")
@inject
def hydrate_cache(
    _body: Annotated[HydrateRequest, Body(openapi_examples=EXAMPLES)],
    svc: CacheHydrationServiceDependency,
) -> HydrateResponse:
    try:
        result = svc.hydrate()
    except FaqFileNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e
    return HydrateResponse(entries_loaded=result.entries_loaded, categories=result.categories)


@router.delete("")
@inject
def clear_cache(svc: CacheAdminServiceDependency) -> dict[str, str]:
    svc.clear()
    return {"detail": "Cache cleared"}


@router.get("/stats")
@inject
def cache_stats(svc: CacheStatsServiceDependency) -> CacheStatsResponse:
    s = svc.stats()
    return CacheStatsResponse(
        total_entries=s.total_entries,
        index_name=s.index_name,
        distance_threshold=s.distance_threshold,
        ttl_seconds=s.ttl_seconds,
    )
