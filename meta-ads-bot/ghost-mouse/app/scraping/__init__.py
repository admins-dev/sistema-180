"""
Outscraper Google Maps API client.

Uses the Outscraper REST API to search Google Maps for businesses.
Free tier: 500 requests/month.

Docs: https://outscraper.com/docs/
"""

from __future__ import annotations

import time
import json
from datetime import datetime, timezone

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import get_settings
from app.observability.logging import get_logger

log = get_logger("outscraper")

OUTSCRAPER_API = "https://api.app.outscraper.com/maps/search-v3"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
def search_google_maps(
    query: str,
    language: str = "es",
    region: str = "ES",
    limit: int = 20,
) -> list[dict]:
    """
    Search Google Maps via Outscraper API.

    Args:
        query: Search query, e.g. "clinica estetica Malaga"
        language: Language code
        region: Region code
        limit: Max results (Outscraper caps at 500 per query)

    Returns:
        List of business dicts with: name, address, phone, website, etc.
    """
    settings = get_settings()

    if not settings.outscraper_api_key:
        raise ValueError("OUTSCRAPER_API_KEY not configured in .env")

    headers = {"X-API-KEY": settings.outscraper_api_key}
    params = {
        "query": query,
        "language": language,
        "region": region,
        "limit": str(limit),
        "async": "false",  # synchronous response
    }

    log.info("outscraper_search", query=query, limit=limit)

    with httpx.Client(timeout=120) as client:
        resp = client.get(OUTSCRAPER_API, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

    # Outscraper returns nested arrays
    results = []
    if isinstance(data, dict) and "data" in data:
        for group in data["data"]:
            if isinstance(group, list):
                results.extend(group)
            elif isinstance(group, dict):
                results.append(group)
    elif isinstance(data, list):
        for group in data:
            if isinstance(group, list):
                results.extend(group)
            elif isinstance(group, dict):
                results.append(group)

    log.info("outscraper_results", query=query, count=len(results))
    return results


def outscraper_to_lead_dict(raw: dict) -> dict:
    """
    Convert an Outscraper result to our standard lead dict format.

    Maps Outscraper fields to our CSV-compatible format.
    """
    return {
        "business_name": raw.get("name", ""),
        "niche": "",  # will be set by the autopilot from the search query
        "city": raw.get("city", raw.get("state", "")),
        "website": raw.get("site", raw.get("website", "")),
        "phone": raw.get("phone", ""),
        "email": raw.get("email", ""),
        "instagram": "",  # extracted from social if available
        "rating": raw.get("rating"),
        "reviews_count": raw.get("reviews"),
        "place_id": raw.get("place_id", ""),
        "address": raw.get("full_address", raw.get("address", "")),
        "maps_url": raw.get("google_maps_url", ""),
    }
