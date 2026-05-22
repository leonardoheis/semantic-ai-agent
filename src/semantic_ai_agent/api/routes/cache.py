"""Cache management routes."""

import pandas as pd
from dependency_injector.wiring import inject
from fastapi import APIRouter, HTTPException

from semantic_ai_agent.api.dependencies import ChatServiceDependency
from semantic_ai_agent.api.schema import (
    CacheStatsResponse,
    HydrateRequest,
    HydrateResponse,
)
from semantic_ai_agent.services.helper import load_faq_json

router = APIRouter(prefix="/cache", tags=["cache"])


@router.post("/hydrate", response_model=HydrateResponse)
@inject
def hydrate_cache(body: HydrateRequest, svc: ChatServiceDependency) -> HydrateResponse:
    try:
        faq_data = load_faq_json(body.faq_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    df = pd.DataFrame(faq_data)
    svc.cache.hydrate_from_df(df, q_col="question", a_col="response")
    categories = sorted(df["category"].unique().tolist()) if "category" in df.columns else []
    return HydrateResponse(entries_loaded=len(df), categories=categories)


@router.delete("")
@inject
def clear_cache(svc: ChatServiceDependency) -> dict[str, str]:
    svc.cache.clear()
    return {"detail": "Cache cleared"}


@router.get("/stats", response_model=CacheStatsResponse)
@inject
def cache_stats(svc: ChatServiceDependency) -> CacheStatsResponse:
    cache_obj = svc.cache.cache
    info = cache_obj.index.info()
    num_docs = int(info.get("num_docs", 0))
    return CacheStatsResponse(
        total_entries=num_docs,
        index_name=cache_obj.index.name,
        distance_threshold=cache_obj._distance_threshold,
        ttl_seconds=cache_obj.ttl or 0,
    )
