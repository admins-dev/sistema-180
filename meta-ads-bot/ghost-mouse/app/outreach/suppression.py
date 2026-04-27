"""
Suppression List — prevents re-sending to unsubscribed/bounced contacts.

GDPR/LOPD compliant:
- Stores unsubscribe requests permanently
- Checks before every send
- Supports manual additions and bulk imports
- Tracks reason (unsubscribe, bounce, complaint, manual)
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base
from app.storage.db import get_session
from app.observability.logging import get_logger

log = get_logger("suppression")


class SuppressedEmail(Base):
    """Email addresses that must NEVER be contacted again."""

    __tablename__ = "suppressed_emails"

    email: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc="unsubscribe | bounce | complaint | manual | spam_trap",
    )
    source: Mapped[str | None] = mapped_column(String(200))
    suppressed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index("idx_suppressed_email", "email"),
    )


def is_suppressed(email: str) -> bool:
    """Check if an email is in the suppression list."""
    if not email:
        return True  # no email = suppressed by default
    with get_session() as session:
        exists = session.query(SuppressedEmail).filter(
            SuppressedEmail.email == email.lower().strip()
        ).first()
        return exists is not None


def add_suppression(email: str, reason: str, source: str | None = None, notes: str | None = None):
    """Add an email to the suppression list."""
    email = email.lower().strip()
    with get_session() as session:
        existing = session.query(SuppressedEmail).filter(
            SuppressedEmail.email == email
        ).first()
        if existing:
            log.info("already_suppressed", email=email)
            return
        session.add(SuppressedEmail(
            email=email, reason=reason, source=source, notes=notes,
        ))
    log.info("email_suppressed", email=email, reason=reason)


def remove_suppression(email: str) -> bool:
    """Remove an email from suppression (rare — use carefully)."""
    with get_session() as session:
        record = session.query(SuppressedEmail).filter(
            SuppressedEmail.email == email.lower().strip()
        ).first()
        if record:
            session.delete(record)
            log.info("suppression_removed", email=email)
            return True
    return False


def get_suppression_count() -> int:
    """Total suppressed emails."""
    with get_session() as session:
        return session.query(SuppressedEmail).count()


def bulk_suppress(emails: list[str], reason: str = "manual"):
    """Add multiple emails to suppression list."""
    added = 0
    for email in emails:
        if email and not is_suppressed(email):
            add_suppression(email, reason=reason)
            added += 1
    log.info("bulk_suppressed", count=added, reason=reason)
    return added
