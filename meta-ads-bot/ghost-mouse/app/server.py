"""
Ghost Mouse V2 — Dashboard API Server.

FastAPI backend that serves the real-time dashboard and provides
JSON endpoints reading directly from the SQLite database.

Usage:
    ghostmouse serve
    # or
    uvicorn app.server:app --reload --port 8180
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, text

from app.config.settings import get_settings
from app.storage.db import get_session, get_db_stats, init_db
from app.domain.models.lead import Lead, LeadContact
from app.domain.models.enrichment import Enrichment
from app.domain.models.scoring import ScoringRecord
from app.domain.models.job import Job
from app.domain.models.outreach import OutreachCampaign, OutreachEvent


api = FastAPI(
    title="Ghost Mouse V2",
    description="B2B Prospecting Engine — Real-time Dashboard API",
    version="2.0.0",
)


# ═══════════════════════════════════════════
# DASHBOARD HTML
# ═══════════════════════════════════════════

@api.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard HTML."""
    dashboard_path = Path(__file__).parent.parent / "dashboard" / "index.html"
    if not dashboard_path.exists():
        return HTMLResponse("<h1>Dashboard not found</h1><p>Run ghostmouse init first.</p>")
    return HTMLResponse(dashboard_path.read_text(encoding="utf-8"))


# ═══════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════

@api.get("/api/stats")
async def api_stats():
    """Global system stats."""
    stats = get_db_stats()
    with get_session() as session:
        # Pipeline stages
        stages = dict(
            session.query(Lead.pipeline_stage, func.count(Lead.id))
            .group_by(Lead.pipeline_stage).all()
        )
        # Lead grades
        grades = dict(
            session.query(Lead.lead_grade, func.count(Lead.id))
            .filter(Lead.lead_grade.isnot(None))
            .group_by(Lead.lead_grade).all()
        )
        # Duplicates
        dupes = session.query(func.count(Lead.id)).filter(Lead.is_duplicate == True).scalar()
        total = session.query(func.count(Lead.id)).scalar()
        # Avg scores
        avg_quality = session.query(func.avg(Lead.data_quality_score)).filter(
            Lead.data_quality_score.isnot(None)
        ).scalar()
        avg_readiness = session.query(func.avg(Lead.outreach_readiness_score)).filter(
            Lead.outreach_readiness_score.isnot(None)
        ).scalar()

    return {
        "tables": stats,
        "pipeline_stages": stages,
        "lead_grades": grades,
        "total_leads": total,
        "duplicates": dupes,
        "unique_leads": (total or 0) - (dupes or 0),
        "avg_data_quality": round(avg_quality, 3) if avg_quality else 0,
        "avg_outreach_readiness": round(avg_readiness, 3) if avg_readiness else 0,
    }


@api.get("/api/leads")
async def api_leads(
    stage: str | None = None,
    grade: str | None = None,
    niche: str | None = None,
    city: str | None = None,
    limit: int = 100,
    offset: int = 0,
    include_dupes: bool = False,
):
    """List leads with filters."""
    with get_session() as session:
        query = session.query(Lead)

        if not include_dupes:
            query = query.filter(Lead.is_duplicate == False)
        if stage:
            query = query.filter(Lead.pipeline_stage == stage)
        if grade:
            query = query.filter(Lead.lead_grade == grade)
        if niche:
            query = query.filter(Lead.niche == niche)
        if city:
            query = query.filter(Lead.city_normalized == city)

        total = query.count()
        leads = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()

        results = []
        for lead in leads:
            contacts = session.query(LeadContact).filter(
                LeadContact.lead_id == lead.id
            ).all()

            results.append({
                "id": lead.id,
                "business_name": lead.business_name,
                "niche": lead.niche,
                "city": lead.city,
                "city_normalized": lead.city_normalized,
                "website": lead.website,
                "normalized_domain": lead.normalized_domain,
                "place_id": lead.place_id,
                "rating": lead.rating,
                "reviews_count": lead.reviews_count,
                "pipeline_stage": lead.pipeline_stage,
                "lead_grade": lead.lead_grade,
                "is_duplicate": lead.is_duplicate,
                "scores": {
                    "data_quality": lead.data_quality_score,
                    "contactability": lead.contactability_score,
                    "website_quality": lead.website_quality_score,
                    "social_dependency": lead.social_dependency_score,
                    "redesign_opportunity": lead.redesign_opportunity_score,
                    "commercial_fit": lead.commercial_fit_score,
                    "outreach_readiness": lead.outreach_readiness_score,
                },
                "contacts": [
                    {
                        "type": c.contact_type,
                        "value": c.value,
                        "confidence": c.confidence,
                        "verified": c.verified,
                    }
                    for c in contacts
                ],
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
            })

    return {"total": total, "leads": results}


@api.get("/api/leads/{lead_id}")
async def api_lead_detail(lead_id: str):
    """Single lead with full details."""
    with get_session() as session:
        lead = session.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return JSONResponse({"error": "Lead not found"}, status_code=404)

        contacts = session.query(LeadContact).filter(LeadContact.lead_id == lead_id).all()
        enrichments = session.query(Enrichment).filter(Enrichment.lead_id == lead_id).all()
        scores = session.query(ScoringRecord).filter(ScoringRecord.lead_id == lead_id).all()
        events = session.query(OutreachEvent).filter(OutreachEvent.lead_id == lead_id).all()

        return {
            "id": lead.id,
            "business_name": lead.business_name,
            "niche": lead.niche,
            "city": lead.city,
            "website": lead.website,
            "pipeline_stage": lead.pipeline_stage,
            "lead_grade": lead.lead_grade,
            "contacts": [{"type": c.contact_type, "value": c.value, "confidence": c.confidence} for c in contacts],
            "enrichments": [{"field": e.field, "value": e.value, "confidence": e.confidence, "enricher": e.enricher} for e in enrichments],
            "scores": [{"type": s.score_type, "score": s.score, "factors": json.loads(s.factors) if s.factors else {}} for s in scores],
            "outreach_events": [{"channel": e.channel, "event_type": e.event_type, "event_at": e.event_at.isoformat() if e.event_at else None} for e in events],
        }


@api.get("/api/pipeline")
async def api_pipeline_overview():
    """Pipeline stage funnel data."""
    stage_order = ["raw", "normalized", "deduped", "enriched", "scored", "qualified", "outreach", "closed"]
    with get_session() as session:
        counts = dict(
            session.query(Lead.pipeline_stage, func.count(Lead.id))
            .filter(Lead.is_duplicate == False)
            .group_by(Lead.pipeline_stage).all()
        )
    return {
        "stages": [
            {"name": s, "count": counts.get(s, 0)}
            for s in stage_order
        ]
    }


@api.get("/api/niches")
async def api_niches():
    """Niche distribution."""
    with get_session() as session:
        niches = (
            session.query(Lead.niche, func.count(Lead.id))
            .filter(Lead.is_duplicate == False, Lead.niche.isnot(None))
            .group_by(Lead.niche)
            .order_by(func.count(Lead.id).desc())
            .limit(20)
            .all()
        )
    return {"niches": [{"name": n, "count": c} for n, c in niches]}


@api.get("/api/cities")
async def api_cities():
    """City distribution."""
    with get_session() as session:
        cities = (
            session.query(Lead.city_normalized, func.count(Lead.id))
            .filter(Lead.is_duplicate == False, Lead.city_normalized.isnot(None))
            .group_by(Lead.city_normalized)
            .order_by(func.count(Lead.id).desc())
            .limit(20)
            .all()
        )
    return {"cities": [{"name": c, "count": cnt} for c, cnt in cities]}


@api.get("/api/jobs")
async def api_jobs(limit: int = 20):
    """Recent job runs."""
    with get_session() as session:
        jobs = (
            session.query(Job)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .all()
        )
    return {
        "jobs": [
            {
                "id": j.id,
                "job_name": j.job_name,
                "status": j.status,
                "records_processed": j.records_processed,
                "records_created": j.records_created,
                "records_failed": j.records_failed,
                "started_at": j.started_at.isoformat() if j.started_at else None,
                "finished_at": j.finished_at.isoformat() if j.finished_at else None,
            }
            for j in jobs
        ]
    }


@api.get("/api/health")
async def api_health():
    """System health check."""
    settings = get_settings()
    return {
        "status": "ok",
        "mode": settings.gm_mode.value,
        "db_path": str(settings.db_path),
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
