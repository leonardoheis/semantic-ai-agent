"""Hydrate result domain model."""

from .base import DomainBase


class HydrateResult(DomainBase):
    entries_loaded: int
    categories: list[str]
