# src/semantic_ai_agent/domain/chat_result.py

"""Chat result domain model."""

from typing import Literal, Optional

from .base import DomainBase


class ChatResult(DomainBase):
    session_id: str
    answer: str
    source: Literal["cache_hit", "llm_generated"]
    latency_ms: float
    distance: Optional[float] = None
