"""
Job model — operational control and checkpoints.

Every pipeline run creates a Job record so you can always answer:
  - what ran
  - when it ran
  - how much it processed
  - where it failed
  - what config was used
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base


class Job(Base):
    """A single pipeline execution with progress tracking."""

    __tablename__ = "jobs"

    job_name: Mapped[str] = mapped_column(String(100), nullable=False)
    batch_id: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(
        String(20), default="pending",
        doc="pending | running | completed | failed | cancelled",
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text)
    config_snapshot: Mapped[str | None] = mapped_column(
        Text, doc="JSON of the config used for this run"
    )
    last_checkpoint: Mapped[str | None] = mapped_column(
        Text, doc="JSON checkpoint for resuming interrupted jobs"
    )

    __table_args__ = (
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_batch_id", "batch_id"),
    )

    def __repr__(self) -> str:
        return f"<Job {self.job_name} [{self.status}] processed={self.records_processed}>"
