"""
Brevo Email Outreach — transactional email sending via Brevo API.

Free tier: 300 emails/day.
Uses the Brevo REST API (v3) for sending.

Safety:
  - Only sends to HOT/WARM qualified leads
  - Checks DRY_RUN mode before any send
  - Records every send as an OutreachEvent
  - Won't re-send to already-contacted leads
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import get_settings
from app.storage.db import get_session
from app.domain.models.lead import Lead, LeadContact
from app.domain.models.outreach import OutreachCampaign, OutreachEvent
from app.observability.logging import get_logger

log = get_logger("brevo_outreach")

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _build_email_content(lead: Lead, template: str) -> dict:
    """
    Build personalized email content.

    Template variables:
      {business_name} — Lead's business name
      {niche} — Lead's niche
      {city} — Lead's city
      {website} — Lead's website
    """
    body = template
    replacements = {
        "{business_name}": lead.business_name or "tu negocio",
        "{niche}": lead.niche or "tu sector",
        "{city}": lead.city or "tu zona",
        "{website}": lead.website or "tu web",
    }
    for key, value in replacements.items():
        body = body.replace(key, value)
    return body


@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=10))
def _send_via_brevo(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    from_email: str,
    from_name: str,
    api_key: str,
) -> dict:
    """Send a single email via Brevo API."""
    payload = {
        "sender": {"name": from_name, "email": from_email},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content,
    }
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=30) as client:
        resp = client.post(BREVO_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


def send_campaign(
    campaign_name: str,
    subject: str,
    template: str,
    from_name: str = "Sistema 180",
    max_sends: int = 10,
    grade_filter: list[str] | None = None,
) -> dict:
    """
    Send a campaign to qualified leads.

    Args:
        campaign_name: Name for tracking
        subject: Email subject (can use {business_name} etc.)
        template: HTML email body (can use template variables)
        from_name: Sender display name
        max_sends: Max emails to send in this batch
        grade_filter: Only send to these grades (default: HOT, WARM)

    Returns:
        Summary dict with sent/skipped/failed counts
    """
    settings = get_settings()

    if not grade_filter:
        grade_filter = ["HOT", "WARM"]

    # Safety gates
    if not settings.ff_enable_email_outreach:
        log.warning("email_outreach_disabled")
        return {"error": "Email outreach is disabled. Set FF_ENABLE_EMAIL_OUTREACH=true"}

    if settings.is_dry_run:
        log.warning("dry_run_mode", msg="Would send emails but DRY_RUN is active")

    if not settings.brevo_api_key:
        return {"error": "BREVO_API_KEY not configured"}

    sent = 0
    skipped = 0
    failed = 0

    with get_session() as session:
        # Create campaign record
        campaign = OutreachCampaign(
            name=campaign_name,
            channel="email",
            status="active",
            template_content=template,
            template_version="v1",
            config=json.dumps({
                "subject": subject,
                "from_name": from_name,
                "max_sends": max_sends,
                "grade_filter": grade_filter,
            }),
        )
        session.add(campaign)
        session.flush()  # get campaign.id

        # Get qualified leads with email
        leads = (
            session.query(Lead)
            .filter(
                Lead.lead_grade.in_(grade_filter),
                Lead.is_duplicate == False,
            )
            .limit(max_sends * 2)  # over-fetch to account for skips
            .all()
        )

        for lead in leads:
            if sent >= max_sends:
                break

            # Get best email contact
            email_contact = next(
                (c for c in lead.contacts if c.contact_type == "email" and c.value),
                None,
            )
            if not email_contact:
                skipped += 1
                continue

            # Check if already contacted in this campaign
            already_sent = session.query(OutreachEvent).filter(
                OutreachEvent.lead_id == lead.id,
                OutreachEvent.campaign_id == campaign.id,
                OutreachEvent.event_type == "sent",
            ).first()
            if already_sent:
                skipped += 1
                continue

            # Personalize content
            personalized_subject = _build_email_content(lead, subject)
            personalized_body = _build_email_content(lead, template)

            if settings.is_dry_run:
                log.info("dry_run_send", to=email_contact.value, subject=personalized_subject)
                # Record as dry_run event
                session.add(OutreachEvent(
                    lead_id=lead.id,
                    campaign_id=campaign.id,
                    channel="email",
                    event_type="dry_run",
                    account_used=settings.email_from,
                    event_at=datetime.now(timezone.utc),
                    metadata_json=json.dumps({"subject": personalized_subject}),
                ))
                sent += 1
                continue

            # Actually send
            try:
                result = _send_via_brevo(
                    to_email=email_contact.value,
                    to_name=lead.business_name or "",
                    subject=personalized_subject,
                    html_content=personalized_body,
                    from_email=settings.email_from,
                    from_name=from_name,
                    api_key=settings.brevo_api_key,
                )
                # Record success
                session.add(OutreachEvent(
                    lead_id=lead.id,
                    campaign_id=campaign.id,
                    channel="email",
                    event_type="sent",
                    message_id=result.get("messageId"),
                    account_used=settings.email_from,
                    event_at=datetime.now(timezone.utc),
                    metadata_json=json.dumps(result),
                ))
                lead.last_outreach_at = datetime.now(timezone.utc)
                sent += 1
                log.info("email_sent", lead_id=lead.id, to=email_contact.value)

            except Exception as e:
                session.add(OutreachEvent(
                    lead_id=lead.id,
                    campaign_id=campaign.id,
                    channel="email",
                    event_type="failed",
                    event_at=datetime.now(timezone.utc),
                    metadata_json=json.dumps({"error": str(e)}),
                ))
                failed += 1
                log.error("email_failed", lead_id=lead.id, error=str(e))

        # Update campaign status
        campaign.status = "completed"

    summary = {"sent": sent, "skipped": skipped, "failed": failed, "campaign": campaign_name}
    log.info("campaign_done", **summary)
    return summary


# ── Default templates ──

TEMPLATE_INTRO_ES = """
<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
<p>Hola {business_name},</p>

<p>He estado investigando negocios de <strong>{niche}</strong> en <strong>{city}</strong>
y me ha llamado la atencion vuestro perfil.</p>

<p>Trabajo con negocios como el vuestro ayudandoles a conseguir mas clientes
a traves de su presencia digital. Nada de promesas vacias: resultados medibles.</p>

<p>Me encantaria comentar como podriamos trabajar juntos.
Un simple "me interesa" basta para que te cuente mas.</p>

<p>Un saludo,<br>
<strong>Jose</strong><br>
<em>Sistema 180</em></p>
</div>
"""

TEMPLATE_FOLLOWUP_ES = """
<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
<p>Hola {business_name},</p>

<p>Os escribi hace unos dias sobre vuestra presencia digital.
Entiendo que estais ocupados, solo queria asegurarme de que lo habiais visto.</p>

<p>Si no es el momento, ningun problema. Pero si os interesa explorar
como conseguir mas clientes online, estoy aqui.</p>

<p>Un saludo,<br>
<strong>Jose</strong></p>
</div>
"""
