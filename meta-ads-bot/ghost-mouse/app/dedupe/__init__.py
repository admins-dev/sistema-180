"""Deduplication package."""

from app.dedupe.exact import find_exact_duplicate
from app.dedupe.fuzzy import find_fuzzy_duplicates

__all__ = ["find_exact_duplicate", "find_fuzzy_duplicates"]
