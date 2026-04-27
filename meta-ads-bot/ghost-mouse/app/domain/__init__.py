"""Domain models package."""

from app.domain.models.lead import Lead, LeadContact, SourceSnapshot
from app.domain.models.enrichment import Enrichment
from app.domain.models.scoring import ScoringRecord
from app.domain.models.job import Job
from app.domain.models.outreach import OutreachCampaign, OutreachEvent

__all__ = [
    "Lead",
    "LeadContact",
    "SourceSnapshot",
    "Enrichment",
    "ScoringRecord",
    "Job",
    "OutreachCampaign",
    "OutreachEvent",
]
