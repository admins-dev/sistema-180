"""
Google Maps Official API extractor.

Uses the Google Places API (New) for reliable, ban-free business search.
Pricing: $17 per 1000 searches (Place Search), $5 per 1000 details.
Free tier: $200/month credit = ~11,700 searches free.

Alternative to Outscraper for more reliable, official data.
"""

from __future__ import annotations

import time
import json
from datetime import datetime, timezone

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import get_settings
from app.observability.logging import get_logger

log = get_logger("gmaps_official")

PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PLACES_DETAIL_URL = "https://places.googleapis.com/v1/places"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def search_places(
    query: str,
    max_results: int = 20,
) -> list[dict]:
    """
    Search Google Maps via Places API (New).

    Args:
        query: e.g. "clinica estetica Malaga"
        max_results: cap at 20 per request (API limit)

    Returns:
        List of place dicts with name, address, phone, website, rating, etc.
    """
    settings = get_settings()

    if not settings.google_maps_api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not configured in .env")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.google_maps_api_key,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,"
            "places.nationalPhoneNumber,places.internationalPhoneNumber,"
            "places.websiteUri,places.rating,places.userRatingCount,"
            "places.googleMapsUri,places.businessStatus,"
            "places.primaryType,places.location"
        ),
    }

    body = {
        "textQuery": query,
        "languageCode": "es",
        "maxResultCount": min(max_results, 20),
    }

    log.info("gmaps_search", query=query, max_results=max_results)

    with httpx.Client(timeout=30) as client:
        resp = client.post(PLACES_SEARCH_URL, json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    places = data.get("places", [])
    log.info("gmaps_results", query=query, count=len(places))
    return places


def gmaps_to_lead_dict(place: dict, niche: str = "") -> dict:
    """Convert Google Places API result to our standard lead dict."""
    display_name = place.get("displayName", {})
    location = place.get("location", {})

    return {
        "business_name": display_name.get("text", ""),
        "niche": niche,
        "city": "",  # extracted from formattedAddress
        "website": place.get("websiteUri", ""),
        "phone": place.get("internationalPhoneNumber", place.get("nationalPhoneNumber", "")),
        "email": "",
        "instagram": "",
        "rating": place.get("rating"),
        "reviews_count": place.get("userRatingCount"),
        "place_id": place.get("id", ""),
        "address": place.get("formattedAddress", ""),
        "maps_url": place.get("googleMapsUri", ""),
    }
