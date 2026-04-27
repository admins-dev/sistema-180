"""
City normalizer.

Handles accents, aliases, and common misspellings for Spanish cities.
"""

from __future__ import annotations

import unicodedata

# Alias map: variant → canonical form
_CITY_ALIASES: dict[str, str] = {
    "barna": "barcelona",
    "bcn": "barcelona",
    "mad": "madrid",
    "vlc": "valencia",
    "agp": "malaga",
    "svq": "sevilla",
    "bilbo": "bilbao",
    "donosti": "san sebastian",
    "san sebastian": "san sebastian",
    "sant sebastia": "san sebastian",
    "palma de mallorca": "palma",
    "las palmas de gran canaria": "las palmas",
    "sta cruz de tenerife": "santa cruz de tenerife",
    "sta. cruz de tenerife": "santa cruz de tenerife",
    "benalmadena": "benalmadena",
    "fuengirola": "fuengirola",
    "marbella": "marbella",
    "torremolinos": "torremolinos",
    "estepona": "estepona",
}


def _strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_city(city: str | None) -> str | None:
    """
    Normalize a city name for consistent matching.

    - Lowercase, strip accents
    - Apply alias mapping
    - Collapse whitespace

    Returns None if input is None or empty.
    """
    if not city:
        return None

    result = city.strip().lower()
    result = _strip_accents(result)
    result = " ".join(result.split())  # collapse whitespace

    # Check alias map
    return _CITY_ALIASES.get(result, result)
