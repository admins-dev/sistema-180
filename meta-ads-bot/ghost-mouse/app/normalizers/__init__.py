"""Normalizers package — pure functions that convert chaos into clean data."""

from app.normalizers.name import normalize_name
from app.normalizers.city import normalize_city
from app.normalizers.domain import normalize_domain, domains_match
from app.normalizers.phone import normalize_phone
from app.normalizers.niche import normalize_niche

__all__ = [
    "normalize_name",
    "normalize_city",
    "normalize_domain",
    "domains_match",
    "normalize_phone",
    "normalize_niche",
]
