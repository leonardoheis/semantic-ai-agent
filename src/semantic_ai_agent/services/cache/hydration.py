"""Cache hydration — populates the semantic cache from FAQ data."""

from collections.abc import Iterable

import pandas as pd
from pydantic import ConfigDict, Field
from redisvl.extensions.cache.llm import SemanticCache

from semantic_ai_agent.domain.base import DomainBase
from semantic_ai_agent.domain.hydrate_result import HydrateResult
from semantic_ai_agent.services.cache.exceptions import CacheHydrationError
from semantic_ai_agent.services.helper import load_faq_json
from semantic_ai_agent.settings import Settings


class CacheHydrationService(DomainBase):
    """Responsible for populating the cache from FAQ data."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)

    cache: SemanticCache = Field(..., description="The shared semantic cache instance.")

    def hydrate(self) -> HydrateResult:
        """Load FAQ data from disk and populate the semantic cache.

        Returns:
            HydrateResult with the number of entries loaded and category list.
        """
        try:
            entries = load_faq_json(Settings.DEFAULT_FAQ_PATH)
            df = pd.DataFrame([e.model_dump() for e in entries])
            self._load_df(df, q_col="question", a_col="response")
        except Exception as exc:
            raise CacheHydrationError(detail=f"Hydration failed: {exc}") from exc

        categories = sorted(df["category"].unique().tolist()) if "category" in df.columns else []
        return HydrateResult(entries_loaded=len(df), categories=categories)

    def hydrate_from_df(
        self,
        df: pd.DataFrame,
        *,
        q_col: str = "question",
        a_col: str = "answer",
        clear: bool = True,
        ttl_override: int | None = None,
    ) -> None:
        """Populate the cache from a DataFrame."""
        try:
            if clear:
                self.cache.clear()
            self._load_df(df, q_col=q_col, a_col=a_col, ttl_override=ttl_override)
        except Exception as exc:
            raise CacheHydrationError(detail=f"Hydration from DataFrame failed: {exc}") from exc

    def hydrate_from_pairs(
        self,
        pairs: Iterable[tuple[str, str]],
        *,
        clear: bool = True,
        ttl_override: int | None = None,
    ) -> None:
        """Populate the cache from an iterable of (question, answer) pairs."""
        try:
            if clear:
                self.cache.clear()
            for q, a in pairs:
                self.cache.store(prompt=q, response=a, ttl=ttl_override)
        except Exception as exc:
            raise CacheHydrationError(detail=f"Hydration from pairs failed: {exc}") from exc

    def _load_df(
        self,
        df: pd.DataFrame,
        *,
        q_col: str,
        a_col: str,
        ttl_override: int | None = None,
    ) -> None:
        for row in df[[q_col, a_col]].itertuples(index=False, name=None):
            q, a = row
            self.cache.store(prompt=q, response=a, ttl=ttl_override)
