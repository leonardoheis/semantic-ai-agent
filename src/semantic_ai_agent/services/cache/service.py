"""Cache service — hydrate, clear, and inspect the semantic cache."""

from pathlib import Path

import pandas as pd

from pydantic import BaseModel, ConfigDict, Field

from semantic_ai_agent.cache.wrapper import SemanticCacheWrapper
from semantic_ai_agent.domain.cache_stats import CacheStats
from semantic_ai_agent.settings import Settings
from semantic_ai_agent.services.helper import load_faq_json

_DEFAULT_FAQ_PATH = Path("data/raw/faq_data.json")


class CacheService:
    faq_path: Path = Field(default=Settings.DEFAULT_FAQ_PATH)
    
    cache_service_config = ConfigDict(arbitrary_types_allowed=True)
          
    @property
    def cache(self) -> SemanticCacheWrapper:
        return self.cache

    def hydrate(self, faq_path: str | None = None) -> tuple[int, list[str]]:
        """Load FAQ data from disk and hydrate the semantic cache."""
        entries = load_faq_json(self.faq_path)
        df = pd.DataFrame([e.model_dump() for e in entries])
        self.cache.hydrate_from_df(df, q_col="question", a_col="response")
        categories = sorted(df["category"].unique().tolist()) if "category" in df.columns else []
        return len(df), categories

    def clear(self) -> None:
        """Remove all entries from the semantic cache."""
        self.cache.clear()

    def stats(self) -> CacheStats:
        """Return current cache index statistics."""
        index_info = self.cache.cache.index.info()
        return CacheStats(
            total_entries=int(index_info.get("num_docs", 0)),
            index_name=self.cache.cache.index.name,
            distance_threshold=self.cache.cache._distance_threshold,
            ttl_seconds=self.cache.cache.ttl or 0,
        )
