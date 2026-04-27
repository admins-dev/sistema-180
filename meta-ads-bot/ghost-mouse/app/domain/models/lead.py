"""
Lead domain model — the heart of Ghost Mouse.

Tables:
  - leads: canonical business identity (one row per unique business)
  - lead_contacts: multiple contact channels per lead (email, phone, IG, etc.)
  - source_snapshots: immutable raw data as captured (never modified)
"""

from __future__ import annotations

from sqlalchemy import (
    String, Text, Float, Integer, Boolean, DateTime, Index,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base


class Lead(Base):
    """Canonical business identity — one row per unique business."""

    __tablename__ = "leads"

    # ── Identity ─────────────────────────
    business_name: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(500))
    place_id: Mapped[str | None] = mapped_column(String(200), index=True)

    # ── Classification ───────────────────
    niche: Mapped[str | None] = mapped_column(String(200))
    subniche: Mapped[str | None] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(5), default="ES")
    region: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(200))
    city_normalized: Mapped[str | None] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(Text)

    # ── Web presence ─────────────────────
    website: Mapped[str | None] = mapped_column(String(500))
    normalized_domain: Mapped[str | None] = mapped_column(String(300))
    maps_url: Mapped[str | None] = mapped_column(String(500))

    # ── Reputation ───────────────────────
    rating: Mapped[float | None] = mapped_column(Float)
    reviews_count: Mapped[int | None] = mapped_column(Integer)

    # ── Pipeline ─────────────────────────
    pipeline_stage: Mapped[str] = mapped_column(
        String(50),
        default="raw",
        doc="raw → normalized → deduped → enriched → scored → qualified → outreach → closed",
    )

    # ── Deduplication ────────────────────
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("leads.id"), nullable=True
    )
    duplicate_type: Mapped[str | None] = mapped_column(
        String(50), doc="exact | probable | possible"
    )
    duplicate_reason: Mapped[str | None] = mapped_column(Text)

    # ── Scores ───────────────────────────
    data_quality_score: Mapped[float | None] = mapped_column(Float)
    contactability_score: Mapped[float | None] = mapped_column(Float)
    website_quality_score: Mapped[float | None] = mapped_column(Float)
    social_dependency_score: Mapped[float | None] = mapped_column(Float)
    redesign_opportunity_score: Mapped[float | None] = mapped_column(Float)
    commercial_fit_score: Mapped[float | None] = mapped_column(Float)
    outreach_readiness_score: Mapped[float | None] = mapped_column(Float)
    lead_grade: Mapped[str | None] = mapped_column(
        String(20), doc="HOT | WARM | COLD | NURTURE | DISCARD"
    )

    # ── Timestamps ───────────────────────
    last_enriched_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    last_scored_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    last_outreach_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    # ── Relationships ────────────────────
    contacts: Mapped[list[LeadContact]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    source_snapshots: Mapped[list[SourceSnapshot]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_leads_normalized_domain", "normalized_domain"),
        Index("idx_leads_pipeline_stage", "pipeline_stage"),
        Index("idx_leads_city_normalized", "city_normalized"),
        Index("idx_leads_niche", "niche"),
        Index("idx_leads_lead_grade", "lead_grade"),
        Index("idx_leads_is_duplicate", "is_duplicate"),
    )

    def __repr__(self) -> str:
        return f"<Lead {self.business_name!r} [{self.pipeline_stage}]>"


class LeadContact(Base):
    """Multiple contact channels per lead, each with confidence score."""

    __tablename__ = "lead_contacts"

    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id"), nullable=False
    )
    contact_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc="email | phone | whatsapp | instagram | facebook | linkedin",
    )
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized: Mapped[str | None] = mapped_column(String(500))
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str | None] = mapped_column(String(200))
    extracted_by: Mapped[str | None] = mapped_column(String(100))

    # ── Relationship ─────────────────────
    lead: Mapped[Lead] = relationship(back_populates="contacts")

    __table_args__ = (
        Index("idx_contacts_lead_id", "lead_id"),
        Index("idx_contacts_normalized", "normalized"),
        Index("idx_contacts_type", "contact_type"),
    )

    def __repr__(self) -> str:
        return f"<LeadContact {self.contact_type}={self.value!r} conf={self.confidence}>"


class SourceSnapshot(Base):
    """Immutable raw data as captured from source — NEVER modified after creation."""

    __tablename__ = "source_snapshots"

    lead_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("leads.id"), nullable=True
    )
    batch_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc="google_maps | paginas_amarillas | cylex | infoIsInfo | outscraper | manual",
    )
    source_url: Mapped[str | None] = mapped_column(String(1000))
    raw_data: Mapped[str] = mapped_column(Text, nullable=False, doc="JSON blob")
    job_run_id: Mapped[str | None] = mapped_column(String(36))

    # ── Relationship ─────────────────────
    lead: Mapped[Lead | None] = relationship(back_populates="source_snapshots")

    __table_args__ = (
        Index("idx_snapshots_batch_id", "batch_id"),
        Index("idx_snapshots_source_type", "source_type"),
    )

    def __repr__(self) -> str:
        return f"<SourceSnapshot {self.source_type} batch={self.batch_id}>"
