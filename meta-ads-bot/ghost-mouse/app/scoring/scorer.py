"""
Lead scorer — 7 auditable scores with explainable factors.

No LLM needed. Pure rule-based scoring on observed facts.
Every score has a JSON breakdown of what contributed to it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from app.domain.models.lead import Lead, LeadContact


@dataclass
class ScoreResult:
    """Single score with its explanation."""
    score_type: str
    score: float  # 0.0 - 1.0
    factors: dict = field(default_factory=dict)

    @property
    def factors_json(self) -> str:
        return json.dumps(self.factors, ensure_ascii=False)


def score_data_quality(lead: Lead, contacts: list[LeadContact]) -> ScoreResult:
    """
    Score 1/7: How complete is the lead's data?

    Factors:
      - has_name (0.15)
      - has_city (0.10)
      - has_niche (0.10)
      - has_website (0.15)
      - has_email (0.20)
      - has_phone (0.15)
      - has_rating (0.05)
      - has_reviews (0.05)
      - has_place_id (0.05)
    """
    factors = {}
    total = 0.0

    checks = [
        ("has_name", 0.15, bool(lead.business_name)),
        ("has_city", 0.10, bool(lead.city)),
        ("has_niche", 0.10, bool(lead.niche)),
        ("has_website", 0.15, bool(lead.website)),
        ("has_email", 0.20, any(c.contact_type == "email" for c in contacts)),
        ("has_phone", 0.15, any(c.contact_type == "phone" for c in contacts)),
        ("has_rating", 0.05, lead.rating is not None),
        ("has_reviews", 0.05, lead.reviews_count is not None and lead.reviews_count > 0),
        ("has_place_id", 0.05, bool(lead.place_id)),
    ]

    for name, weight, present in checks:
        val = weight if present else 0.0
        factors[name] = {"present": present, "weight": weight, "contributed": val}
        total += val

    return ScoreResult(score_type="data_quality", score=round(total, 3), factors=factors)


def score_contactability(lead: Lead, contacts: list[LeadContact]) -> ScoreResult:
    """
    Score 2/7: Can we actually reach this business?

    Factors:
      - has_verified_email (0.35)
      - has_any_email (0.15)
      - has_phone (0.20)
      - has_instagram (0.15)
      - has_multiple_channels (0.15)
    """
    factors = {}
    total = 0.0

    emails = [c for c in contacts if c.contact_type == "email"]
    phones = [c for c in contacts if c.contact_type == "phone"]
    instagrams = [c for c in contacts if c.contact_type == "instagram"]
    verified_emails = [c for c in emails if c.verified]

    channels_count = sum([
        len(emails) > 0,
        len(phones) > 0,
        len(instagrams) > 0,
    ])

    checks = [
        ("has_verified_email", 0.35, len(verified_emails) > 0),
        ("has_any_email", 0.15, len(emails) > 0),
        ("has_phone", 0.20, len(phones) > 0),
        ("has_instagram", 0.15, len(instagrams) > 0),
        ("has_multiple_channels", 0.15, channels_count >= 2),
    ]

    for name, weight, present in checks:
        val = weight if present else 0.0
        factors[name] = {"present": present, "weight": weight, "contributed": val}
        total += val

    return ScoreResult(score_type="contactability", score=round(total, 3), factors=factors)


def score_website_quality(lead: Lead) -> ScoreResult:
    """
    Score 3/7: How good is their web presence?

    Low score = they need our services = opportunity.
    """
    factors = {}
    total = 0.0

    has_website = bool(lead.website)
    has_https = lead.website.startswith("https") if lead.website else False
    has_domain = bool(lead.normalized_domain)

    checks = [
        ("has_website", 0.40, has_website),
        ("has_https", 0.20, has_https),
        ("has_own_domain", 0.40, has_domain),
    ]

    for name, weight, present in checks:
        val = weight if present else 0.0
        factors[name] = {"present": present, "weight": weight, "contributed": val}
        total += val

    return ScoreResult(score_type="website_quality", score=round(total, 3), factors=factors)


def score_social_dependency(lead: Lead, contacts: list[LeadContact]) -> ScoreResult:
    """
    Score 4/7: Does this business depend too much on social media?

    High score = heavily dependent on Instagram without proper web.
    This is an OPPORTUNITY indicator — they need a real web presence.
    """
    factors = {}

    has_instagram = any(c.contact_type == "instagram" for c in contacts)
    has_website = bool(lead.website)
    has_domain = bool(lead.normalized_domain)

    # High dependency = has IG but no proper website
    dependency = 0.0
    if has_instagram and not has_website:
        dependency = 0.90
        factors["pattern"] = "Instagram only, no website"
    elif has_instagram and has_website and not has_domain:
        dependency = 0.60
        factors["pattern"] = "Instagram + weak web (no own domain)"
    elif has_instagram and has_website:
        dependency = 0.30
        factors["pattern"] = "Instagram + website (balanced)"
    elif not has_instagram and not has_website:
        dependency = 0.50
        factors["pattern"] = "No web presence at all"
    else:
        dependency = 0.10
        factors["pattern"] = "Has website, no Instagram dependency"

    factors["has_instagram"] = has_instagram
    factors["has_website"] = has_website
    factors["has_own_domain"] = has_domain

    return ScoreResult(
        score_type="social_dependency",
        score=round(dependency, 3),
        factors=factors,
    )


def score_redesign_opportunity(lead: Lead) -> ScoreResult:
    """
    Score 5/7: How much would this business benefit from a web redesign?

    Based on observable signals, not LLM guesswork.
    """
    factors = {}
    opportunity = 0.0

    has_website = bool(lead.website)
    has_reviews = lead.reviews_count is not None and lead.reviews_count > 5
    good_rating = lead.rating is not None and lead.rating >= 4.0

    if not has_website:
        # No website at all — maximum opportunity
        opportunity = 0.95
        factors["reason"] = "No website — full build opportunity"
    elif has_reviews and good_rating and not has_website:
        opportunity = 0.90
        factors["reason"] = "Good reviews but no web — needs digital presence"
    elif has_website:
        # Has website — moderate opportunity (potential redesign)
        opportunity = 0.40
        factors["reason"] = "Has website — potential redesign"
    else:
        opportunity = 0.20
        factors["reason"] = "Low signals"

    factors["has_website"] = has_website
    factors["has_reviews"] = has_reviews
    factors["good_rating"] = good_rating

    return ScoreResult(
        score_type="redesign_opportunity",
        score=round(opportunity, 3),
        factors=factors,
    )


def score_commercial_fit(lead: Lead) -> ScoreResult:
    """
    Score 6/7: Does this business match our ideal customer profile?

    Factors: niche profitability, reviews volume, rating, location.
    """
    factors = {}
    total = 0.0

    # Premium niches (higher willingness to pay)
    premium_niches = {
        "estetica", "dental", "inmobiliaria", "fisioterapia", "psicologia",
    }
    is_premium = lead.niche in premium_niches if lead.niche else False

    has_reviews = lead.reviews_count is not None and lead.reviews_count > 10
    high_rating = lead.rating is not None and lead.rating >= 4.0
    has_city = bool(lead.city)

    checks = [
        ("premium_niche", 0.35, is_premium),
        ("has_reviews", 0.20, has_reviews),
        ("high_rating", 0.20, high_rating),
        ("has_city", 0.10, has_city),
        ("has_niche", 0.15, bool(lead.niche)),
    ]

    for name, weight, present in checks:
        val = weight if present else 0.0
        factors[name] = {"present": present, "weight": weight, "contributed": val}
        total += val

    return ScoreResult(score_type="commercial_fit", score=round(total, 3), factors=factors)


def score_outreach_readiness(
    data_quality: float,
    contactability: float,
    commercial_fit: float,
) -> ScoreResult:
    """
    Score 7/7: Is this lead ready for outreach?

    Weighted combination of the key scores.
    This is the GATE score — below threshold = blocked from outreach.
    """
    weights = {
        "data_quality": 0.25,
        "contactability": 0.40,
        "commercial_fit": 0.35,
    }

    scores = {
        "data_quality": data_quality,
        "contactability": contactability,
        "commercial_fit": commercial_fit,
    }

    total = sum(scores[k] * weights[k] for k in weights)

    factors = {
        k: {"score": scores[k], "weight": weights[k], "contributed": round(scores[k] * weights[k], 3)}
        for k in weights
    }

    return ScoreResult(
        score_type="outreach_readiness",
        score=round(total, 3),
        factors=factors,
    )


def score_lead(lead: Lead, contacts: list[LeadContact]) -> list[ScoreResult]:
    """
    Run ALL 7 scores on a lead.

    Returns a list of ScoreResult objects, one per score type.
    """
    s1 = score_data_quality(lead, contacts)
    s2 = score_contactability(lead, contacts)
    s3 = score_website_quality(lead)
    s4 = score_social_dependency(lead, contacts)
    s5 = score_redesign_opportunity(lead)
    s6 = score_commercial_fit(lead)
    s7 = score_outreach_readiness(s1.score, s2.score, s6.score)

    return [s1, s2, s3, s4, s5, s6, s7]
