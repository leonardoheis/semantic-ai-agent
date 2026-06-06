"""Faq data domain model."""

from .base import DomainBase


class FaqEntry(DomainBase):
    question: str
    response: str
    category: str
