"""
Exact deduplication — multicriterio matching.

Priority order:
  1. place_id (strongest — Google's own stable ID)
  2. normalized_domain (one domain = one business, usually)
  3. normalized_phone (same phone = same business)

Each match is classified and explained.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.lead import Lead, LeadContact


@dataclass
class DuplicateMatch:
    """Result of a deduplication check."""
    is_duplicate: bool
    duplicate_type: str | None  # exact | probable | possible
    duplicate_of_id: str | None
    reason: str | None
    matched_field: str | None
    confidence: float  # 0.0 - 1.0


def _check_place_id(session: Session, place_id: str | None, exclude_id: str | None) -> DuplicateMatch | None:
    """Check for exact match by Google Maps place_id."""
    if not place_id:
        return None

    stmt = select(Lead).where(
        Lead.place_id == place_id,
        Lead.is_duplicate == False,
    )
    if exclude_id:
        stmt = stmt.where(Lead.id != exclude_id)

    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        return DuplicateMatch(
            is_duplicate=True,
            duplicate_type="exact",
            duplicate_of_id=existing.id,
            reason=f"Same place_id: {place_id}",
            matched_field="place_id",
            confidence=1.0,
        )
    return None


def _check_domain(session: Session, domain: str | None, exclude_id: str | None) -> DuplicateMatch | None:
    """Check for exact match by normalized domain."""
    if not domain:
        return None

    stmt = select(Lead).where(
        Lead.normalized_domain == domain,
        Lead.is_duplicate == False,
    )
    if exclude_id:
        stmt = stmt.where(Lead.id != exclude_id)

    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        return DuplicateMatch(
            is_duplicate=True,
            duplicate_type="exact",
            duplicate_of_id=existing.id,
            reason=f"Same domain: {domain}",
            matched_field="normalized_domain",
            confidence=0.95,
        )
    return None


def _check_phone(session: Session, phone: str | None, exclude_id: str | None) -> DuplicateMatch | None:
    """Check for exact match by normalized phone in contacts."""
    if not phone:
        return None

    stmt = (
        select(LeadContact)
        .join(Lead, Lead.id == LeadContact.lead_id)
        .where(
            LeadContact.normalized == phone,
            LeadContact.contact_type == "phone",
            Lead.is_duplicate == False,
        )
    )
    if exclude_id:
        stmt = stmt.where(Lead.id != exclude_id)

    existing_contact = session.execute(stmt).scalar_one_or_none()
    if existing_contact:
        return DuplicateMatch(
            is_duplicate=True,
            duplicate_type="exact",
            duplicate_of_id=existing_contact.lead_id,
            reason=f"Same phone: {phone}",
            matched_field="phone",
            confidence=0.90,
        )
    return None


def find_exact_duplicate(
    session: Session,
    place_id: str | None = None,
    normalized_domain: str | None = None,
    normalized_phone: str | None = None,
    exclude_id: str | None = None,
) -> DuplicateMatch:
    """
    Check for exact duplicates using multicriterio matching.

    Priority: place_id → domain → phone
    Returns the FIRST match found (highest confidence).
    """
    # Check in priority order
    for checker in [
        lambda: _check_place_id(session, place_id, exclude_id),
        lambda: _check_domain(session, normalized_domain, exclude_id),
        lambda: _check_phone(session, normalized_phone, exclude_id),
    ]:
        result = checker()
        if result:
            return result

    return DuplicateMatch(
        is_duplicate=False,
        duplicate_type=None,
        duplicate_of_id=None,
        reason=None,
        matched_field=None,
        confidence=0.0,
    )
