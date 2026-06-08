"""Cache management routes."""

from typing import Annotated

from dependency_injector.wiring import inject
from fastapi import APIRouter, HTTPException, Body

from semantic_ai_agent.api.dependencies import (
    CacheAdminServiceDependency,
    CacheHydrationServiceDependency,
)
from .schema import CacheStatsResponse, HydrateRequest, HydrateResponse
from semantic_ai_agent.services.cache.exceptions import FaqFileNotFoundError
from .examples import EXAMPLES

router = APIRouter(prefix="/cache", tags=["cache"])


@router.post("/hydrate", response_model=HydrateResponse)
@inject
def hydrate_cache(
    body: Annotated[HydrateRequest, Body(openapi_examples=EXAMPLES)],
    svc: CacheHydrationServiceDependency,
) -> HydrateResponse:
    try:
        result = svc.hydrate(body.faq_path)
    except FaqFileNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail)
    return HydrateResponse(entries_loaded=result.entries_loaded, categories=result.categories)


@router.delete("")
@inject
def clear_cache(svc: CacheAdminServiceDependency) -> dict[str, str]:
    svc.clear()
    return {"detail": "Cache cleared"}


@router.get("/stats", response_model=CacheStatsResponse)
@inject
def cache_stats(svc: CacheAdminServiceDependency) -> CacheStatsResponse:
    s = svc.stats()
    return CacheStatsResponse(
        total_entries=s.total_entries,
        index_name=s.index_name,
        distance_threshold=s.distance_threshold,
        ttl_seconds=s.ttl_seconds,
    )
