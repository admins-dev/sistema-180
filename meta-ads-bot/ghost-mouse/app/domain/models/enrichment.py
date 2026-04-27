"""
Enrichment model — traceable data enrichments.

Every enrichment records WHAT was found, WHERE it came from,
HOW confident we are, and WHAT evidence backs it up.
"""

from __future__ import annotations

from sqlalchemy import String, Text, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base


class Enrichment(Base):
    """A single enrichment fact attached to a lead."""

    __tablename__ = "enrichments"

    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id"), nullable=False
    )
    enricher: Mapped[str] = mapped_column(
        String(100), nullable=False,
        doc="Module that produced this: email_extractor | social_finder | web_enricher",
    )
    field: Mapped[str] = mapped_column(
        String(100), nullable=False,
        doc="Field enriched: email | phone | instagram | has_booking | etc.",
    )
    value: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(
        Float, default=0.5,
        doc="0.0 = guessing, 1.0 = confirmed",
    )
    evidence: Mapped[str | None] = mapped_column(
        Text,
        doc="JSON: where exactly this came from (URL, CSS selector, page section)",
    )
    job_run_id: Mapped[str | None] = mapped_column(String(36))

    __table_args__ = (
        Index("idx_enrichments_lead_id", "lead_id"),
        Index("idx_enrichments_enricher", "enricher"),
        Index("idx_enrichments_field", "field"),
    )

    def __repr__(self) -> str:
        return f"<Enrichment {self.field}={self.value!r} conf={self.confidence}>"
