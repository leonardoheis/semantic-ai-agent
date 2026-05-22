"""Shared service helpers."""

import json
from pathlib import Path
from typing import Any


def load_faq_json(faq_path: str | None = None) -> list[dict[str, Any]]:
    """Load FAQ data from a JSON file."""
    path = Path(faq_path) if faq_path else Path("data/raw/faq_data.json")
    if not path.exists():
        raise FileNotFoundError(f"FAQ file not found: {path}")
    with open(path) as f:
        return json.load(f)
