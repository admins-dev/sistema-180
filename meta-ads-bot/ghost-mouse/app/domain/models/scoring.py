"""
Scoring model — auditable, explainable scores.

Each scoring record stores the score TYPE, the numeric VALUE,
and a JSON breakdown of FACTORS that contributed to it.
"""

from __future__ import annotations

from sqlalchemy import String, Text, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base


class ScoringRecord(Base):
    """One score for one lead. Scores are recalculable and versioned."""

    __tablename__ = "scoring_records"

    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id"), nullable=False
    )
    model_version: Mapped[str] = mapped_column(
        String(50), nullable=False, default="v1",
    )
    score_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc=(
            "data_quality | contactability | website_quality | "
            "social_dependency | redesign_opportunity | "
            "commercial_fit | outreach_readiness"
        ),
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    factors: Mapped[str | None] = mapped_column(
        Text,
        doc="JSON object explaining what contributed to this score",
    )

    __table_args__ = (
        Index("idx_scoring_lead_id", "lead_id"),
        Index("idx_scoring_type", "score_type"),
    )

    def __repr__(self) -> str:
        return f"<ScoringRecord {self.score_type}={self.score:.2f}>"
