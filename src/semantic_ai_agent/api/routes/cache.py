"""Cache management routes."""

from dependency_injector.wiring import inject
from fastapi import APIRouter, HTTPException

from semantic_ai_agent.api.dependencies import CacheServiceDependency
from semantic_ai_agent.api.schema import CacheStatsResponse, HydrateRequest, HydrateResponse

router = APIRouter(prefix="/cache", tags=["cache"])


@router.post("/hydrate", response_model=HydrateResponse)
@inject
def hydrate_cache(body: HydrateRequest, svc: CacheServiceDependency) -> HydrateResponse:
    try:
        count, categories = svc.hydrate(body.faq_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return HydrateResponse(entries_loaded=count, categories=categories)


@router.delete("")
@inject
def clear_cache(svc: CacheServiceDependency) -> dict[str, str]:
    svc.clear()
    return {"detail": "Cache cleared"}


@router.get("/stats", response_model=CacheStatsResponse)
@inject
def cache_stats(svc: CacheServiceDependency) -> CacheStatsResponse:
    s = svc.stats()
    return CacheStatsResponse(
        total_entries=s.total_entries,
        index_name=s.index_name,
        distance_threshold=s.distance_threshold,
        ttl_seconds=s.ttl_seconds,
    )
