"""
Web Enricher — visits websites and extracts business signals.

Extracts:
  - Emails from the page
  - Phone numbers
  - Social media links (Instagram, Facebook, LinkedIn)
  - Has booking system
  - Has HTTPS
  - Has contact form
  - CMS detection (WordPress, Wix, Squarespace)

Every finding is stored as a traceable Enrichment record.
"""

from __future__ import annotations

import re
import time
import json
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import get_settings
from app.storage.db import get_session
from app.domain.models.lead import Lead, LeadContact
from app.domain.models.enrichment import Enrichment
from app.observability.logging import get_logger

log = get_logger("web_enricher")

# ── Patterns ──
EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
)
PHONE_ES_RE = re.compile(
    r"(?:\+34[\s\-]?)?(?:6\d{1,2}[\s\-]?\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{0,2}"
    r"|9\d{1,2}[\s\-]?\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{0,2})",
)
IG_RE = re.compile(r"(?:instagram\.com|instagr\.am)/([a-zA-Z0-9_\.]{1,30})")
FB_RE = re.compile(r"facebook\.com/([a-zA-Z0-9\.\-]+)")
LI_RE = re.compile(r"linkedin\.com/(?:company|in)/([a-zA-Z0-9\-]+)")

# Noise emails to filter out
NOISE_EMAILS = {
    "info@sentry.io", "noreply@github.com", "support@wix.com",
    "support@squarespace.com", "support@wordpress.com",
}
NOISE_DOMAINS = {
    "sentry.io", "github.com", "wix.com", "squarespace.com",
    "wordpress.com", "google.com", "facebook.com", "twitter.com",
    "schema.org", "w3.org",
}

# CMS signatures
CMS_SIGNATURES = {
    "wordpress": ["wp-content", "wp-includes", "wordpress"],
    "wix": ["wix.com", "wixsite.com", "wix-code"],
    "squarespace": ["squarespace.com", "sqsp.net"],
    "shopify": ["shopify.com", "myshopify.com"],
    "webflow": ["webflow.io", "webflow.com"],
}

# Booking platform keywords
BOOKING_KEYWORDS = [
    "reservar", "cita", "booking", "calendly", "appointy",
    "doctolib", "treatwell", "mindbody", "reserve",
]


def _is_valid_email(email: str, lead_domain: str | None) -> bool:
    """Filter noise emails."""
    email = email.lower()
    domain = email.split("@")[-1]
    if domain in NOISE_DOMAINS:
        return False
    if email in NOISE_EMAILS:
        return False
    if email.startswith("noreply") or email.startswith("no-reply"):
        return False
    return True


@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
def _fetch_page(url: str) -> tuple[str, int]:
    """Fetch a webpage with timeout and retry."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-ES,es;q=0.9",
    }
    with httpx.Client(timeout=15, follow_redirects=True, verify=False) as client:
        resp = client.get(url, headers=headers)
        return resp.text, resp.status_code


def extract_signals(url: str) -> dict:
    """
    Visit a URL and extract all business signals.

    Returns a dict with all findings + evidence.
    """
    if not url:
        return {"error": "No URL provided"}

    if not url.startswith("http"):
        url = f"https://{url}"

    try:
        html, status = _fetch_page(url)
    except Exception as e:
        return {"error": str(e), "status": None}

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True).lower()
    html_lower = html.lower()

    signals: dict = {
        "url": url,
        "status": status,
        "has_https": url.startswith("https"),
    }

    # ── Emails ──
    raw_emails = EMAIL_RE.findall(html)
    emails = list({e.lower() for e in raw_emails if _is_valid_email(e, None)})
    signals["emails"] = emails[:5]  # cap at 5

    # ── Phones ──
    phones = list({p.strip() for p in PHONE_ES_RE.findall(html) if len(p.strip()) >= 9})
    signals["phones"] = phones[:3]

    # ── Social ──
    ig_matches = IG_RE.findall(html)
    fb_matches = FB_RE.findall(html)
    li_matches = LI_RE.findall(html)
    signals["instagram"] = list(set(ig_matches))[:2]
    signals["facebook"] = list(set(fb_matches))[:2]
    signals["linkedin"] = list(set(li_matches))[:2]

    # ── CMS ──
    detected_cms = None
    for cms, sigs in CMS_SIGNATURES.items():
        if any(s in html_lower for s in sigs):
            detected_cms = cms
            break
    signals["cms"] = detected_cms

    # ── Booking ──
    signals["has_booking"] = any(kw in text for kw in BOOKING_KEYWORDS)

    # ── Contact form ──
    forms = soup.find_all("form")
    signals["has_contact_form"] = any(
        "contact" in str(f).lower() or "email" in str(f).lower()
        for f in forms
    )

    # ── Title ──
    title_tag = soup.find("title")
    signals["page_title"] = title_tag.get_text(strip=True) if title_tag else None

    # ── Meta description ──
    meta_desc = soup.find("meta", attrs={"name": "description"})
    signals["meta_description"] = meta_desc.get("content", "")[:200] if meta_desc else None

    return signals


def _store_enrichment(session, lead_id: str, field: str, value, enricher: str, confidence: float, evidence: str | None = None):
    """Create a traceable enrichment record."""
    session.add(Enrichment(
        lead_id=lead_id,
        enricher=enricher,
        field=field,
        value=str(value) if value else None,
        confidence=confidence,
        evidence=evidence,
    ))


def enrich_single_lead(lead: Lead, session) -> dict:
    """
    Enrich a single lead by visiting its website.

    Stores all findings as Enrichment records and adds new contacts.
    """
    if not lead.website:
        return {"status": "skipped", "reason": "no_website"}

    settings = get_settings()
    signals = extract_signals(lead.website)

    if "error" in signals:
        log.warning("enrich_failed", lead_id=lead.id, error=signals["error"])
        return {"status": "failed", "error": signals["error"]}

    evidence_json = json.dumps(signals, ensure_ascii=False, default=str)
    enricher = "web_enricher"

    # ── Store enrichments ──
    _store_enrichment(session, lead.id, "has_https", signals["has_https"], enricher, 1.0, evidence_json)
    _store_enrichment(session, lead.id, "cms", signals.get("cms"), enricher, 0.9 if signals.get("cms") else 0.0)
    _store_enrichment(session, lead.id, "has_booking", signals["has_booking"], enricher, 0.8)
    _store_enrichment(session, lead.id, "has_contact_form", signals["has_contact_form"], enricher, 0.8)

    if signals.get("page_title"):
        _store_enrichment(session, lead.id, "page_title", signals["page_title"], enricher, 1.0)

    # ── Add new contacts ──
    existing_contacts = {c.value.lower() for c in lead.contacts}

    for email in signals.get("emails", []):
        if email.lower() not in existing_contacts:
            session.add(LeadContact(
                lead_id=lead.id, contact_type="email", value=email,
                normalized=email.lower(), confidence=0.7,
                source=lead.website, extracted_by=enricher,
            ))
            _store_enrichment(session, lead.id, "email_found", email, enricher, 0.7, f"Found on {lead.website}")

    for phone in signals.get("phones", []):
        if phone not in existing_contacts:
            session.add(LeadContact(
                lead_id=lead.id, contact_type="phone", value=phone,
                confidence=0.6, source=lead.website, extracted_by=enricher,
            ))

    for ig in signals.get("instagram", []):
        ig_val = f"@{ig}" if not ig.startswith("@") else ig
        if ig_val.lower() not in existing_contacts:
            session.add(LeadContact(
                lead_id=lead.id, contact_type="instagram", value=ig_val,
                confidence=0.8, source=lead.website, extracted_by=enricher,
            ))

    # Update lead
    lead.last_enriched_at = datetime.now(timezone.utc)
    lead.pipeline_stage = "enriched"

    log.info("enriched", lead_id=lead.id, emails=len(signals.get("emails", [])),
             phones=len(signals.get("phones", [])), cms=signals.get("cms"))

    return {"status": "enriched", "signals": signals}


def enrich_leads_batch(limit: int = 50) -> dict:
    """Enrich a batch of deduped leads."""
    settings = get_settings()
    enriched = 0
    skipped = 0
    failed = 0

    with get_session() as session:
        leads = (
            session.query(Lead)
            .filter(
                Lead.pipeline_stage == "deduped",
                Lead.is_duplicate == False,
                Lead.website.isnot(None),
            )
            .limit(limit)
            .all()
        )

        log.info("enrich_batch_start", count=len(leads))

        for lead in leads:
            result = enrich_single_lead(lead, session)

            if result["status"] == "enriched":
                enriched += 1
            elif result["status"] == "skipped":
                skipped += 1
            else:
                failed += 1

            # Respectful delay between requests
            time.sleep(settings.scrape_delay_min)

    log.info("enrich_batch_done", enriched=enriched, skipped=skipped, failed=failed)
    return {"enriched": enriched, "skipped": skipped, "failed": failed}
