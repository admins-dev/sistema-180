"""
Outreach models — campaigns and contact events.

Unified history of ALL touchpoints across ALL channels.
Every email sent, every DM, every open, every reply — tracked here.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base


class OutreachCampaign(Base):
    """A named outreach campaign grouping multiple messages."""

    __tablename__ = "outreach_campaigns"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    channel: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc="email | instagram_dm | whatsapp | linkedin",
    )
    status: Mapped[str] = mapped_column(
        String(20), default="draft",
        doc="draft | active | paused | completed",
    )
    template_content: Mapped[str | None] = mapped_column(Text)
    template_version: Mapped[str | None] = mapped_column(String(50))
    config: Mapped[str | None] = mapped_column(
        Text, doc="JSON: sequence config, delays, max sends, etc."
    )

    def __repr__(self) -> str:
        return f"<Campaign {self.name!r} [{self.channel}/{self.status}]>"


class OutreachEvent(Base):
    """A single touchpoint in the outreach lifecycle."""

    __tablename__ = "outreach_events"

    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id"), nullable=False
    )
    campaign_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("outreach_campaigns.id")
    )
    channel: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc="email | instagram_dm | whatsapp",
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc="sent | opened | clicked | replied | bounced | unsubscribed",
    )
    message_id: Mapped[str | None] = mapped_column(String(200))
    account_used: Mapped[str | None] = mapped_column(String(200))
    event_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[str | None] = mapped_column(Text, doc="JSON with extra details")

    __table_args__ = (
        Index("idx_outreach_lead_id", "lead_id"),
        Index("idx_outreach_campaign_id", "campaign_id"),
        Index("idx_outreach_event_type", "event_type"),
    )

    def __repr__(self) -> str:
        return f"<OutreachEvent {self.channel}/{self.event_type} lead={self.lead_id[:8]}>"
