"""Tests for scoring logic."""

import pytest

from app.domain.models.lead import Lead, LeadContact
from app.scoring.scorer import (
    score_data_quality,
    score_contactability,
    score_website_quality,
    score_commercial_fit,
    score_outreach_readiness,
    score_lead,
)


def _make_lead(**kwargs) -> Lead:
    """Helper to create a Lead with defaults (uses proper constructor)."""
    defaults = {
        "business_name": "Test Business",
        "niche": "estetica",
        "city": "Malaga",
        "website": "https://test.es",
        "normalized_domain": "test.es",
        "pipeline_stage": "raw",
        "is_duplicate": False,
        "country": "ES",
    }
    defaults.update(kwargs)
    return Lead(**defaults)


def _make_contact(contact_type: str, value: str, **kwargs) -> LeadContact:
    """Helper to create a LeadContact (uses proper constructor)."""
    return LeadContact(
        contact_type=contact_type,
        value=value,
        normalized=kwargs.get("normalized", value),
        confidence=kwargs.get("confidence", 0.5),
        verified=kwargs.get("verified", False),
        source=kwargs.get("source", "test"),
        extracted_by=kwargs.get("extracted_by", "test"),
    )


class TestDataQualityScore:
    def test_complete_lead_scores_high(self):
        lead = _make_lead(rating=4.5, reviews_count=50, place_id="ChIJ123")
        contacts = [
            _make_contact("email", "info@test.es"),
            _make_contact("phone", "+34612345678"),
        ]
        result = score_data_quality(lead, contacts)
        assert result.score >= 0.90

    def test_empty_lead_scores_low(self):
        lead = _make_lead(
            business_name="", niche=None, city=None,
            website=None, normalized_domain=None,
            rating=None, reviews_count=None, place_id=None,
        )
        result = score_data_quality(lead, [])
        assert result.score < 0.20

    def test_factors_are_present(self):
        lead = _make_lead()
        result = score_data_quality(lead, [])
        assert "has_name" in result.factors
        assert "has_email" in result.factors


class TestContactabilityScore:
    def test_verified_email_scores_highest(self):
        lead = _make_lead()
        contacts = [_make_contact("email", "info@test.es", verified=True)]
        result = score_contactability(lead, contacts)
        assert result.score >= 0.50

    def test_no_contacts_scores_zero(self):
        lead = _make_lead()
        result = score_contactability(lead, [])
        assert result.score == 0.0


class TestWebsiteQualityScore:
    def test_https_website(self):
        lead = _make_lead(website="https://test.es")
        result = score_website_quality(lead)
        assert result.score == 1.0

    def test_no_website(self):
        lead = _make_lead(website=None, normalized_domain=None)
        result = score_website_quality(lead)
        assert result.score == 0.0


class TestCommercialFitScore:
    def test_premium_niche_scores_higher(self):
        lead = _make_lead(niche="estetica", rating=4.5, reviews_count=50, city="Malaga")
        result = score_commercial_fit(lead)
        assert result.score >= 0.80


class TestOutreachReadinessScore:
    def test_high_scores_produce_high_readiness(self):
        result = score_outreach_readiness(0.9, 0.8, 0.7)
        assert result.score >= 0.70

    def test_low_scores_produce_low_readiness(self):
        result = score_outreach_readiness(0.1, 0.1, 0.1)
        assert result.score <= 0.15


class TestScoreLeadIntegration:
    def test_returns_7_scores(self):
        lead = _make_lead()
        contacts = [_make_contact("email", "info@test.es")]
        results = score_lead(lead, contacts)
        assert len(results) == 7
        types = {r.score_type for r in results}
        assert "data_quality" in types
        assert "outreach_readiness" in types
