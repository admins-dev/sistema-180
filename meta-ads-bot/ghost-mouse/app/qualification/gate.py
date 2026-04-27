"""
Qualification gate — decides if a lead can proceed to outreach.

Rules:
  - outreach_readiness_score >= 0.50 → HOT
  - outreach_readiness_score >= 0.35 → WARM
  - outreach_readiness_score >= 0.20 → COLD
  - outreach_readiness_score >= 0.10 → NURTURE
  - below 0.10 → DISCARD

Hard blocks (regardless of score):
  - No email AND no phone → BLOCKED
  - No niche → BLOCKED
  - Already marked as duplicate → SKIP
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.lead import Lead, LeadContact


# Grade thresholds
THRESHOLD_HOT = 0.50
THRESHOLD_WARM = 0.35
THRESHOLD_COLD = 0.20
THRESHOLD_NURTURE = 0.10


@dataclass
class QualificationResult:
    """Result of the qualification gate."""
    lead_id: str
    grade: str  # HOT | WARM | COLD | NURTURE | DISCARD | BLOCKED
    reason: str
    can_outreach: bool
    outreach_readiness: float


def qualify_lead(
    lead: Lead,
    contacts: list[LeadContact],
    outreach_readiness_score: float,
) -> QualificationResult:
    """
    Run the qualification gate on a lead.

    Hard blocks override any score:
      - Duplicate leads are skipped
      - Leads without any contact channel are blocked
      - Leads without a niche are blocked (can't personalize)
    """
    # Hard block: duplicate
    if lead.is_duplicate:
        return QualificationResult(
            lead_id=lead.id,
            grade="SKIP",
            reason="Lead is a duplicate",
            can_outreach=False,
            outreach_readiness=outreach_readiness_score,
        )

    # Hard block: no contact channel
    has_email = any(c.contact_type == "email" for c in contacts)
    has_phone = any(c.contact_type == "phone" for c in contacts)
    has_instagram = any(c.contact_type == "instagram" for c in contacts)

    if not has_email and not has_phone and not has_instagram:
        return QualificationResult(
            lead_id=lead.id,
            grade="BLOCKED",
            reason="No contact channel available (no email, phone, or Instagram)",
            can_outreach=False,
            outreach_readiness=outreach_readiness_score,
        )

    # Hard block: no niche
    if not lead.niche:
        return QualificationResult(
            lead_id=lead.id,
            grade="BLOCKED",
            reason="No niche defined — cannot personalize outreach",
            can_outreach=False,
            outreach_readiness=outreach_readiness_score,
        )

    # Grade by score
    if outreach_readiness_score >= THRESHOLD_HOT:
        grade = "HOT"
        can_outreach = True
    elif outreach_readiness_score >= THRESHOLD_WARM:
        grade = "WARM"
        can_outreach = True
    elif outreach_readiness_score >= THRESHOLD_COLD:
        grade = "COLD"
        can_outreach = False  # Needs more enrichment first
    elif outreach_readiness_score >= THRESHOLD_NURTURE:
        grade = "NURTURE"
        can_outreach = False
    else:
        grade = "DISCARD"
        can_outreach = False

    return QualificationResult(
        lead_id=lead.id,
        grade=grade,
        reason=f"Score {outreach_readiness_score:.2f} → {grade}",
        can_outreach=can_outreach,
        outreach_readiness=outreach_readiness_score,
    )
