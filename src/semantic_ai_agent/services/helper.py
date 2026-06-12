"""Shared service helpers."""

import json
from pathlib import Path

from semantic_ai_agent.domain.faq_data import FaqEntry
from semantic_ai_agent.settings import Settings


def load_faq_json(faq_path: Path = Settings.DEFAULT_FAQ_PATH) -> list[FaqEntry]:
    """Load FAQ data from a JSON file and return typed domain objects.
    Returns:
        List of FaqEntry objects loaded from the JSON file.
    """
    if not faq_path.exists():
        msg = f"FAQ file not found: {faq_path}"
        raise FileNotFoundError(msg)
    with Path(faq_path).open(encoding="utf-8") as f:
        raw: list[dict[str, object]] = json.load(f)
    return [FaqEntry.model_validate(item) for item in raw]
