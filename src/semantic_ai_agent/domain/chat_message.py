"""Chat message domain model."""

from datetime import datetime, timezone
from typing import Literal

from .base import DomainBase


class ChatMessage(DomainBase):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = datetime.now(tz=timezone.utc)
