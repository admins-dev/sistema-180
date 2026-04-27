"""
Business name normalizer.

Strips legal suffixes (SL, SA, SLU, S.L., etc.), lowercases, removes accents.
"""

from __future__ import annotations

import re
import unicodedata

# Spanish legal suffixes to strip
_LEGAL_SUFFIXES = re.compile(
    r"\b(s\.?l\.?u?\.?|s\.?a\.?|s\.?c\.?|s\.?l\.?l\.?|sociedad\s+limitada|"
    r"sociedad\s+anonima|comunidad\s+de\s+bienes|c\.?b\.?)\s*$",
    re.IGNORECASE,
)

# Common noise words at the end
_NOISE = re.compile(
    r"\b(centro|clinica|clínica|grupo|the|&|y)\s*$",
    re.IGNORECASE,
)


def _strip_accents(text: str) -> str:
    """Remove diacritical marks: á→a, ñ→n, ü→u."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_name(name: str | None) -> str | None:
    """
    Normalize a business name for deduplication matching.

    - Lowercase
    - Strip accents
    - Remove legal suffixes (SL, SA, SLU, etc.)
    - Collapse whitespace
    - Strip leading/trailing punctuation

    Returns None if input is None or empty after normalization.
    """
    if not name:
        return None

    result = name.strip().lower()
    result = _strip_accents(result)

    # Remove legal suffixes
    result = _LEGAL_SUFFIXES.sub("", result).strip()

    # Remove trailing punctuation
    result = re.sub(r"[,.\-–—]+$", "", result).strip()

    # Collapse whitespace
    result = re.sub(r"\s+", " ", result)

    return result if result else None
