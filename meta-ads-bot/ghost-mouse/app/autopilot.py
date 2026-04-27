"""
Ghost Mouse Autopilot — autonomous prospecting loop.

Given a list of target niches and cities, Ghost Mouse will:
1. Search Google Maps for businesses (via Outscraper)
2. Import them into the DB
3. Run the full pipeline (normalize → dedupe → enrich → score → qualify)
4. Move to the next niche/city combo
5. Repeat

Usage:
    ghostmouse autopilot
    ghostmouse autopilot --niches "clinica dental,gimnasio" --cities "Malaga,Sevilla"
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from app.config.settings import get_settings
from app.storage.db import get_session, init_db
from app.domain.models.lead import Lead, LeadContact, SourceSnapshot
from app.domain.models.job import Job
from app.normalizers import normalize_name, normalize_city, normalize_domain, normalize_phone, normalize_niche
from app.dedupe.exact import find_exact_duplicate
from app.dedupe.fuzzy import find_fuzzy_duplicates
from app.scoring.scorer import score_lead
from app.qualification.gate import qualify_lead
from app.scraping import search_google_maps, outscraper_to_lead_dict
from app.observability.logging import get_logger

log = get_logger("autopilot")

# Default targets for Spain B2B prospecting
DEFAULT_NICHES = [
    "clinica estetica",
    "clinica dental",
    "gimnasio",
    "centro de fisioterapia",
    "peluqueria",
    "centro de nutricion",
    "clinica veterinaria",
    "inmobiliaria",
]

DEFAULT_CITIES = [
    "Malaga",
    "Marbella",
    "Sevilla",
    "Granada",
    "Cordoba",
    "Valencia",
    "Barcelona",
    "Madrid",
]


def _import_outscraper_results(results: list[dict], niche: str, city: str, batch_id: str) -> dict:
    """Import Outscraper results into the DB."""
    created = 0
    skipped = 0

    with get_session() as session:
        for raw in results:
            lead_dict = outscraper_to_lead_dict(raw)
            lead_dict["niche"] = niche  # set from search context

            # Skip if no name
            if not lead_dict.get("business_name"):
                skipped += 1
                continue

            # Safe numeric parsing
            try:
                rating = float(lead_dict["rating"]) if lead_dict.get("rating") else None
            except (ValueError, TypeError):
                rating = None
            try:
                reviews = int(lead_dict["reviews_count"]) if lead_dict.get("reviews_count") else None
            except (ValueError, TypeError):
                reviews = None

            lead = Lead(
                business_name=lead_dict["business_name"],
                niche=lead_dict.get("niche") or None,
                city=lead_dict.get("city") or city,
                website=lead_dict.get("website") or None,
                address=lead_dict.get("address") or None,
                place_id=lead_dict.get("place_id") or None,
                maps_url=lead_dict.get("maps_url") or None,
                rating=rating,
                reviews_count=reviews,
                pipeline_stage="raw",
            )

            # Snapshot
            lead.source_snapshots.append(SourceSnapshot(
                batch_id=batch_id,
                source_type="outscraper",
                raw_data=json.dumps(raw, ensure_ascii=False, default=str),
            ))

            # Contacts
            if lead_dict.get("phone"):
                lead.contacts.append(LeadContact(
                    contact_type="phone", value=lead_dict["phone"],
                    source="outscraper", extracted_by="outscraper_import",
                ))
            if lead_dict.get("email"):
                lead.contacts.append(LeadContact(
                    contact_type="email", value=lead_dict["email"],
                    source="outscraper", extracted_by="outscraper_import",
                ))

            session.add(lead)
            created += 1

    return {"created": created, "skipped": skipped}


def _run_pipeline_for_raw() -> dict:
    """Run normalize → dedupe → score → qualify on all raw leads."""
    normalized = 0
    exact_dupes = 0
    fuzzy_dupes = 0
    scored = 0
    grades: dict[str, int] = {}

    with get_session() as session:
        # ── Normalize ──
        raw_leads = session.query(Lead).filter(Lead.pipeline_stage == "raw").all()
        for lead in raw_leads:
            lead.normalized_name = normalize_name(lead.business_name)
            lead.city_normalized = normalize_city(lead.city)
            lead.normalized_domain = normalize_domain(lead.website)
            lead.niche = normalize_niche(lead.niche)
            for contact in lead.contacts:
                if contact.contact_type == "phone":
                    contact.normalized = normalize_phone(contact.value)
                elif contact.contact_type == "email":
                    contact.normalized = contact.value.strip().lower() if contact.value else None
            lead.pipeline_stage = "normalized"
            normalized += 1

    with get_session() as session:
        # ── Dedupe ──
        norm_leads = session.query(Lead).filter(
            Lead.pipeline_stage == "normalized", Lead.is_duplicate == False
        ).all()
        for lead in norm_leads:
            phone_c = next((c for c in lead.contacts if c.contact_type == "phone" and c.normalized), None)
            result = find_exact_duplicate(
                session=session, place_id=lead.place_id,
                normalized_domain=lead.normalized_domain,
                normalized_phone=phone_c.normalized if phone_c else None,
                exclude_id=lead.id,
            )
            if result.is_duplicate:
                lead.is_duplicate = True
                lead.duplicate_of = result.duplicate_of_id
                lead.duplicate_type = result.duplicate_type
                lead.duplicate_reason = result.reason
                exact_dupes += 1
                continue
            fuzzy = find_fuzzy_duplicates(
                session=session, normalized_name=lead.normalized_name,
                city_normalized=lead.city_normalized, exclude_id=lead.id,
            )
            if fuzzy:
                best = fuzzy[0]
                lead.is_duplicate = True
                lead.duplicate_of = best.duplicate_of_id
                lead.duplicate_type = best.duplicate_type
                lead.duplicate_reason = best.reason
                fuzzy_dupes += 1
                continue
            lead.pipeline_stage = "deduped"

    with get_session() as session:
        # ── Score ──
        deduped = session.query(Lead).filter(
            Lead.pipeline_stage.in_(["deduped", "enriched"]),
            Lead.is_duplicate == False,
        ).all()
        for lead in deduped:
            results = score_lead(lead, lead.contacts)
            for r in results:
                setattr(lead, f"{r.score_type}_score", r.score)
            lead.last_scored_at = datetime.now(timezone.utc)
            lead.pipeline_stage = "scored"
            scored += 1

    with get_session() as session:
        # ── Qualify ──
        scored_leads = session.query(Lead).filter(
            Lead.pipeline_stage == "scored", Lead.is_duplicate == False,
        ).all()
        for lead in scored_leads:
            result = qualify_lead(lead, lead.contacts, lead.outreach_readiness_score or 0.0)
            lead.lead_grade = result.grade
            lead.pipeline_stage = "qualified"
            grades[result.grade] = grades.get(result.grade, 0) + 1

    return {
        "normalized": normalized,
        "exact_dupes": exact_dupes,
        "fuzzy_dupes": fuzzy_dupes,
        "scored": scored,
        "grades": grades,
    }


def run_autopilot(
    niches: list[str] | None = None,
    cities: list[str] | None = None,
    leads_per_search: int = 20,
    delay_between_searches: float = 3.0,
) -> dict:
    """
    Run the full autonomous prospecting loop.

    For each niche × city combination:
      1. Search Google Maps via Outscraper
      2. Import results
      3. Run full pipeline

    Args:
        niches: List of business niches to target
        cities: List of cities to search
        leads_per_search: Max results per search query
        delay_between_searches: Seconds to wait between API calls

    Returns:
        Summary dict with totals
    """
    settings = get_settings()
    init_db()

    if not niches:
        niches = DEFAULT_NICHES
    if not cities:
        cities = DEFAULT_CITIES

    total_searches = 0
    total_imported = 0
    total_skipped = 0
    errors = []

    log.info("autopilot_start", niches=len(niches), cities=len(cities),
             total_combos=len(niches) * len(cities))

    for niche in niches:
        for city in cities:
            query = f"{niche} {city}"
            batch_id = f"AP_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{niche[:10]}_{city[:10]}"

            # Create job record
            with get_session() as session:
                job = Job(
                    job_name=f"autopilot_{query}",
                    status="running",
                    config=json.dumps({"niche": niche, "city": city, "limit": leads_per_search}),
                    started_at=datetime.now(timezone.utc),
                )
                session.add(job)
                session.flush()
                job_id = job.id

            try:
                # Search
                log.info("autopilot_search", query=query)
                results = search_google_maps(
                    query=query,
                    limit=leads_per_search,
                )

                # Import
                import_result = _import_outscraper_results(results, niche, city, batch_id)
                total_imported += import_result["created"]
                total_skipped += import_result["skipped"]
                total_searches += 1

                # Update job
                with get_session() as session:
                    job = session.query(Job).filter(Job.id == job_id).first()
                    if job:
                        job.status = "completed"
                        job.records_processed = len(results)
                        job.records_created = import_result["created"]
                        job.finished_at = datetime.now(timezone.utc)

                log.info("autopilot_imported", query=query,
                         created=import_result["created"], skipped=import_result["skipped"])

            except Exception as e:
                log.error("autopilot_error", query=query, error=str(e))
                errors.append({"query": query, "error": str(e)})

                with get_session() as session:
                    job = session.query(Job).filter(Job.id == job_id).first()
                    if job:
                        job.status = "failed"
                        job.error_message = str(e)
                        job.finished_at = datetime.now(timezone.utc)

            # Respectful delay
            time.sleep(delay_between_searches)

    # Run pipeline on all new raw leads
    log.info("autopilot_pipeline_start")
    pipeline_result = _run_pipeline_for_raw()

    summary = {
        "searches": total_searches,
        "imported": total_imported,
        "skipped": total_skipped,
        "errors": len(errors),
        "error_details": errors,
        **pipeline_result,
    }

    log.info("autopilot_done", **{k: v for k, v in summary.items() if k != "error_details"})
    return summary
