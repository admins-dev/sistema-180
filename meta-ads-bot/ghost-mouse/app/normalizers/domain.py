"""
Domain normalizer.

Extracts clean domain from URLs using tldextract.
Handles www, http/https, paths, query strings.
"""

from __future__ import annotations

import tldextract


def normalize_domain(url: str | None) -> str | None:
    """
    Extract clean domain from a URL.

    Examples:
        "https://www.clinica-estetica.es/servicios" → "clinica-estetica.es"
        "http://www.EXAMPLE.COM"                    → "example.com"
        "example.es"                                → "example.es"
        None                                        → None

    Uses tldextract to handle edge cases properly.
    """
    if not url:
        return None

    url = url.strip()
    if not url:
        return None

    extracted = tldextract.extract(url)

    if not extracted.domain or not extracted.suffix:
        return None

    domain = f"{extracted.domain}.{extracted.suffix}".lower()
    return domain


def domains_match(url1: str | None, url2: str | None) -> bool:
    """Check if two URLs point to the same domain."""
    d1 = normalize_domain(url1)
    d2 = normalize_domain(url2)
    if d1 is None or d2 is None:
        return False
    return d1 == d2
