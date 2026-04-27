"""
Ghost Mouse V2 — CLI (Command Line Interface).

All operational commands for the pipeline.
Usage: ghostmouse <command> [options]
"""

from __future__ import annotations

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from app.config.settings import get_settings
from app.storage.db import init_db, get_session, get_db_stats
from app.domain.models.lead import Lead, LeadContact, SourceSnapshot
from app.normalizers import (
    normalize_name, normalize_city, normalize_domain,
    normalize_phone, normalize_niche,
)
from app.dedupe.exact import find_exact_duplicate
from app.dedupe.fuzzy import find_fuzzy_duplicates
from app.scoring.scorer import score_lead
from app.qualification.gate import qualify_lead
from app.observability.logging import setup_logging, get_logger

app = typer.Typer(
    name="ghostmouse",
    help="🐭 Ghost Mouse V2 — B2B Prospecting Engine",
    rich_markup_mode="rich",
)
console = Console()


@app.callback()
def _startup():
    """Initialize logging on every command."""
    setup_logging()


# ═══════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════

@app.command()
def init():
    """🏗️  Initialize the database (create all tables)."""
    settings = get_settings()
    console.print(f"[bold cyan]Mode:[/] {settings.gm_mode.value}")
    console.print(f"[bold cyan]Database:[/] {settings.db_path}")

    init_db()
    console.print("[bold green]✓ Database initialized successfully![/]")

    # Show table counts
    stats = get_db_stats()
    table = Table(title="Tables Created")
    table.add_column("Table", style="cyan")
    table.add_column("Rows", justify="right")
    for name, count in stats.items():
        table.add_row(name, str(count))
    console.print(table)


# ═══════════════════════════════════════════
# IMPORT
# ═══════════════════════════════════════════

@app.command()
def import_csv(
    file: Path = typer.Argument(..., help="CSV file to import"),
    source: str = typer.Option("manual", help="Source type"),
    batch_id: str | None = typer.Option(None, help="Batch ID (auto-generated if empty)"),
):
    """📥 Import leads from a CSV file."""
    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/]")
        raise typer.Exit(1)

    if batch_id is None:
        batch_id = f"B{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    log = get_logger("import", batch_id=batch_id, source=source)
    settings = get_settings()

    with open(file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    console.print(f"[cyan]Found {len(rows)} rows in {file.name}[/]")

    created = 0
    skipped = 0

    with get_session() as session:
        for row in rows:
            # Safe numeric parsing
            try:
                rating = float(row["rating"]) if row.get("rating") else None
            except (ValueError, TypeError):
                rating = None
            try:
                reviews = int(row["reviews_count"]) if row.get("reviews_count") else None
            except (ValueError, TypeError):
                reviews = None

            # Create lead
            lead = Lead(
                business_name=row.get("business_name", row.get("nombre", "")),
                niche=row.get("niche", row.get("nicho", "")) or None,
                city=row.get("city", row.get("ciudad", "")) or None,
                website=row.get("website", row.get("web", "")) or None,
                address=row.get("address", row.get("direccion", "")) or None,
                place_id=row.get("place_id") or None,
                rating=rating,
                reviews_count=reviews,
                pipeline_stage="raw",
            )

            # Create source snapshot (immutable)
            snapshot = SourceSnapshot(
                batch_id=batch_id,
                source_type=source,
                raw_data=json.dumps(row, ensure_ascii=False),
            )
            lead.source_snapshots.append(snapshot)

            # Add contacts if present
            for ctype, keys in [
                ("email", ["email"]),
                ("phone", ["phone", "telefono"]),
                ("instagram", ["instagram"]),
            ]:
                for key in keys:
                    if row.get(key):
                        lead.contacts.append(LeadContact(
                            contact_type=ctype,
                            value=row[key],
                            source=source,
                            extracted_by="csv_import",
                        ))

            session.add(lead)
            created += 1
            log.info("lead_imported", lead_name=lead.business_name)

    console.print(Panel(
        f"[green]✓ Imported {created} leads[/]\n"
        f"[dim]Batch: {batch_id} | Source: {source}[/]",
        title="Import Complete",
    ))


# ═══════════════════════════════════════════
# NORMALIZE
# ═══════════════════════════════════════════

@app.command()
def normalize(
    batch_id: str | None = typer.Option(None, help="Only normalize this batch"),
):
    """🧹 Normalize all lead fields (name, city, domain, phone, niche)."""
    log = get_logger("normalize", batch_id=batch_id)

    with get_session() as session:
        query = session.query(Lead).filter(Lead.pipeline_stage == "raw")
        leads = query.all()

        console.print(f"[cyan]Normalizing {len(leads)} raw leads...[/]")
        count = 0

        for lead in leads:
            lead.normalized_name = normalize_name(lead.business_name)
            lead.city_normalized = normalize_city(lead.city)
            lead.normalized_domain = normalize_domain(lead.website)
            lead.niche = normalize_niche(lead.niche)

            # Normalize contacts
            for contact in lead.contacts:
                if contact.contact_type == "phone":
                    contact.normalized = normalize_phone(contact.value)
                elif contact.contact_type == "email":
                    contact.normalized = contact.value.strip().lower() if contact.value else None

            lead.pipeline_stage = "normalized"
            count += 1
            log.info("normalized", lead_id=lead.id, name=lead.normalized_name)

    console.print(f"[green]✓ Normalized {count} leads[/]")


# ═══════════════════════════════════════════
# DEDUPE
# ═══════════════════════════════════════════

@app.command()
def dedupe():
    """🔍 Run deduplication (exact + fuzzy)."""
    log = get_logger("dedupe")

    with get_session() as session:
        leads = session.query(Lead).filter(
            Lead.pipeline_stage == "normalized",
            Lead.is_duplicate == False,
        ).all()

        console.print(f"[cyan]Checking {len(leads)} leads for duplicates...[/]")
        exact_count = 0
        fuzzy_count = 0

        for lead in leads:
            # Get primary phone from contacts
            phone_contact = next(
                (c for c in lead.contacts if c.contact_type == "phone" and c.normalized),
                None,
            )

            # Exact dedup
            result = find_exact_duplicate(
                session=session,
                place_id=lead.place_id,
                normalized_domain=lead.normalized_domain,
                normalized_phone=phone_contact.normalized if phone_contact else None,
                exclude_id=lead.id,
            )

            if result.is_duplicate:
                lead.is_duplicate = True
                lead.duplicate_of = result.duplicate_of_id
                lead.duplicate_type = result.duplicate_type
                lead.duplicate_reason = result.reason
                exact_count += 1
                log.info("exact_duplicate", lead_id=lead.id, reason=result.reason)
                continue

            # Fuzzy dedup
            fuzzy_matches = find_fuzzy_duplicates(
                session=session,
                normalized_name=lead.normalized_name,
                city_normalized=lead.city_normalized,
                exclude_id=lead.id,
            )

            if fuzzy_matches:
                best = fuzzy_matches[0]
                lead.is_duplicate = True
                lead.duplicate_of = best.duplicate_of_id
                lead.duplicate_type = best.duplicate_type
                lead.duplicate_reason = best.reason
                fuzzy_count += 1
                log.info("fuzzy_duplicate", lead_id=lead.id, score=best.score)
                continue

            # Not a duplicate — advance pipeline
            lead.pipeline_stage = "deduped"

    console.print(Panel(
        f"[yellow]Exact duplicates:[/] {exact_count}\n"
        f"[yellow]Fuzzy duplicates:[/] {fuzzy_count}\n"
        f"[green]Clean leads:[/] {len(leads) - exact_count - fuzzy_count}",
        title="Deduplication Complete",
    ))


# ═══════════════════════════════════════════
# SCORE
# ═══════════════════════════════════════════

@app.command()
def score():
    """📊 Calculate all 7 scores for deduped leads."""
    log = get_logger("scoring")

    with get_session() as session:
        leads = session.query(Lead).filter(
            Lead.pipeline_stage.in_(["deduped", "enriched"]),
            Lead.is_duplicate == False,
        ).all()

        console.print(f"[cyan]Scoring {len(leads)} leads...[/]")

        for lead in leads:
            results = score_lead(lead, lead.contacts)

            # Store scores on the lead
            for r in results:
                setattr(lead, f"{r.score_type}_score", r.score)

            lead.last_scored_at = datetime.now(timezone.utc)
            lead.pipeline_stage = "scored"
            log.info("scored", lead_id=lead.id, readiness=lead.outreach_readiness_score)

    console.print(f"[green]✓ Scored {len(leads)} leads[/]")


# ═══════════════════════════════════════════
# QUALIFY
# ═══════════════════════════════════════════

@app.command()
def qualify():
    """🎯 Run qualification gate (assign grades: HOT/WARM/COLD/NURTURE/DISCARD)."""
    log = get_logger("qualification")

    with get_session() as session:
        leads = session.query(Lead).filter(
            Lead.pipeline_stage == "scored",
            Lead.is_duplicate == False,
        ).all()

        console.print(f"[cyan]Qualifying {len(leads)} scored leads...[/]")
        grades: dict[str, int] = {}

        for lead in leads:
            result = qualify_lead(
                lead, lead.contacts, lead.outreach_readiness_score or 0.0
            )
            lead.lead_grade = result.grade
            lead.pipeline_stage = "qualified"
            grades[result.grade] = grades.get(result.grade, 0) + 1
            log.info("qualified", lead_id=lead.id, grade=result.grade)

    # Display results
    table = Table(title="Qualification Results")
    table.add_column("Grade", style="bold")
    table.add_column("Count", justify="right")
    for grade in ["HOT", "WARM", "COLD", "NURTURE", "DISCARD", "BLOCKED"]:
        count = grades.get(grade, 0)
        style = {"HOT": "red", "WARM": "yellow", "COLD": "blue", "BLOCKED": "dim"}.get(grade)
        label = f"[{style}]{grade}[/{style}]" if style else grade
        table.add_row(label, str(count))
    console.print(table)


# ═══════════════════════════════════════════
# PIPELINE (run all stages)
# ═══════════════════════════════════════════

@app.command()
def pipeline():
    """🚀 Run the full pipeline: normalize → dedupe → score → qualify."""
    console.print(Panel("[bold cyan]Ghost Mouse V2 — Full Pipeline[/]"))

    normalize()
    dedupe()
    score()
    qualify()

    console.print("[bold green]✓ Pipeline complete![/]")


# ═══════════════════════════════════════════
# STATUS / REPORT
# ═══════════════════════════════════════════

@app.command()
def status():
    """📋 Show system status and lead counts."""
    settings = get_settings()

    console.print(Panel(
        f"[bold]Mode:[/] {settings.gm_mode.value}\n"
        f"[bold]Database:[/] {settings.db_path}\n"
        f"[bold]Dry Run:[/] {settings.is_dry_run}",
        title="🐭 Ghost Mouse V2",
    ))

    stats = get_db_stats()
    table = Table(title="Database Stats")
    table.add_column("Table", style="cyan")
    table.add_column("Rows", justify="right", style="green")
    for name, count in stats.items():
        table.add_row(name, str(count))
    console.print(table)

    # Pipeline stage breakdown
    with get_session() as session:
        from sqlalchemy import func
        stages = session.query(
            Lead.pipeline_stage, func.count(Lead.id)
        ).group_by(Lead.pipeline_stage).all()

        if stages:
            stage_table = Table(title="Pipeline Stages")
            stage_table.add_column("Stage", style="cyan")
            stage_table.add_column("Count", justify="right", style="green")
            for stage, count in stages:
                stage_table.add_row(stage, str(count))
            console.print(stage_table)

        # Grade breakdown
        grades = session.query(
            Lead.lead_grade, func.count(Lead.id)
        ).filter(Lead.lead_grade.isnot(None)).group_by(Lead.lead_grade).all()

        if grades:
            grade_table = Table(title="Lead Grades")
            grade_table.add_column("Grade", style="bold")
            grade_table.add_column("Count", justify="right")
            for grade, count in grades:
                grade_table.add_row(grade, str(count))
            console.print(grade_table)


# ═══════════════════════════════════════════
# SERVE (Dashboard)
# ═══════════════════════════════════════════

@app.command()
def serve(
    port: int = typer.Option(8180, help="Port number"),
    host: str = typer.Option("0.0.0.0", help="Host"),
):
    """🌐 Launch the real-time dashboard (FastAPI + HTML)."""
    import uvicorn
    from app.storage.db import init_db as _init

    _init()  # ensure tables exist
    console.print(Panel(
        f"[bold green]Dashboard:[/] http://{host}:{port}\n"
        f"[bold cyan]API:[/] http://{host}:{port}/api/stats\n"
        f"[dim]Press Ctrl+C to stop[/]",
        title="Ghost Mouse V2 — Dashboard",
    ))
    uvicorn.run("app.server:api", host=host, port=port, reload=False)


# ═══════════════════════════════════════════
# ENRICH
# ═══════════════════════════════════════════

@app.command()
def enrich(
    limit: int = typer.Option(50, help="Max leads to enrich"),
):
    """🔬 Enrich deduped leads (web signals, emails, social)."""
    from app.enrichment.web_enricher import enrich_leads_batch

    console.print(f"[cyan]Enriching up to {limit} leads...[/]")
    results = enrich_leads_batch(limit=limit)
    console.print(Panel(
        f"[green]Enriched:[/] {results['enriched']}\n"
        f"[yellow]Skipped:[/] {results['skipped']}\n"
        f"[red]Failed:[/] {results['failed']}",
        title="Enrichment Complete",
    ))


# ═══════════════════════════════════════════
# OUTREACH (Brevo Email)
# ═══════════════════════════════════════════

@app.command()
def outreach(
    campaign_name: str = typer.Option("intro_v1", help="Campaign name"),
    subject: str = typer.Option(
        "Propuesta para {business_name}",
        help="Email subject (supports {business_name}, {niche}, {city})",
    ),
    max_sends: int = typer.Option(10, help="Max emails to send"),
    grade: str = typer.Option("HOT,WARM", help="Comma-separated grades to target"),
):
    """📧 Send email campaign via Brevo (checks DRY_RUN + feature flag)."""
    from app.outreach.brevo import send_campaign, TEMPLATE_INTRO_ES

    settings = get_settings()
    if settings.is_dry_run:
        console.print("[yellow]DRY_RUN mode: emails will be simulated, not sent[/]")

    grade_list = [g.strip().upper() for g in grade.split(",")]
    result = send_campaign(
        campaign_name=campaign_name,
        subject=subject,
        template=TEMPLATE_INTRO_ES,
        max_sends=max_sends,
        grade_filter=grade_list,
    )

    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[green]Sent:[/] {result['sent']}\n"
        f"[yellow]Skipped:[/] {result['skipped']}\n"
        f"[red]Failed:[/] {result['failed']}",
        title=f"Campaign: {campaign_name}",
    ))


# ═══════════════════════════════════════════
# AUTOPILOT (autonomous prospecting)
# ═══════════════════════════════════════════

@app.command()
def autopilot(
    niches: str = typer.Option(
        "clinica estetica,clinica dental,gimnasio",
        help="Comma-separated niches to prospect",
    ),
    cities: str = typer.Option(
        "Malaga,Marbella,Sevilla",
        help="Comma-separated cities to search",
    ),
    leads_per_search: int = typer.Option(20, help="Max leads per niche+city search"),
):
    """🤖 Autonomous prospecting: search Google Maps → import → pipeline."""
    from app.autopilot import run_autopilot

    niche_list = [n.strip() for n in niches.split(",")]
    city_list = [c.strip() for c in cities.split(",")]
    total_combos = len(niche_list) * len(city_list)

    console.print(Panel(
        f"[bold]Niches:[/] {', '.join(niche_list)}\n"
        f"[bold]Cities:[/] {', '.join(city_list)}\n"
        f"[bold]Searches:[/] {total_combos}\n"
        f"[bold]Leads/search:[/] {leads_per_search}\n"
        f"[dim]Max potential leads: {total_combos * leads_per_search}[/]",
        title="Ghost Mouse Autopilot",
    ))

    result = run_autopilot(
        niches=niche_list,
        cities=city_list,
        leads_per_search=leads_per_search,
    )

    # Display results
    console.print(Panel(
        f"[cyan]Searches:[/] {result['searches']}\n"
        f"[green]Imported:[/] {result['imported']}\n"
        f"[yellow]Skipped:[/] {result['skipped']}\n"
        f"[red]Errors:[/] {result['errors']}\n"
        f"[dim]---[/]\n"
        f"[cyan]Normalized:[/] {result['normalized']}\n"
        f"[yellow]Exact dupes:[/] {result['exact_dupes']}\n"
        f"[yellow]Fuzzy dupes:[/] {result['fuzzy_dupes']}\n"
        f"[green]Scored:[/] {result['scored']}\n"
        f"[bold]Grades:[/] {result.get('grades', {})}",
        title="Autopilot Complete",
    ))

    if result.get("errors"):
        for err in result.get("error_details", []):
            console.print(f"  [red]Error:[/] {err['query']} → {err['error']}")


if __name__ == "__main__":
    app()
