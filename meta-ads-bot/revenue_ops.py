"""
revenue_ops.py — Sistema 180
Revenue Ops autónomo: leads, clasificación, scoring, copy, follow-ups
Control via Telegram. Gmail-ready.
"""

import os
import json
import logging
import sqlite3
import requests
from datetime import datetime, date, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ─── Config from env ───
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_USER_IDS = set(
    int(uid.strip()) for uid in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
    if uid.strip().isdigit()
)

DB_PATH = os.path.join(os.path.dirname(__file__), "leads.db")

VALID_STATUSES = ("new", "qualified", "proposal", "followup", "closed", "lost", "donotcontact")
VALID_INTENTS = ("buying_signal", "info_request", "objection", "irrelevant", "spam")

AVG_LEAD_VALUE = 500  # euros


# ─────────────────────────────────────────────────────────────────────────────
# LeadsDB
# ─────────────────────────────────────────────────────────────────────────────

class LeadsDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT NOT NULL,
                    company         TEXT NOT NULL,
                    email           TEXT,
                    phone           TEXT,
                    source          TEXT NOT NULL DEFAULT 'manual',
                    status          TEXT NOT NULL DEFAULT 'new',
                    score           INTEGER NOT NULL DEFAULT 0,
                    created_at      TEXT NOT NULL,
                    last_contact    TEXT,
                    next_action     TEXT,
                    consent         INTEGER NOT NULL DEFAULT 0,
                    notes           TEXT,
                    email_thread_id TEXT,
                    channel         TEXT
                )
            """)
            # Index for fast hot-lead queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)
            """)
            conn.commit()

    def add_lead(self, name: str, company: str, email: str, source: str, notes: str = "") -> int:
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO leads (name, company, email, source, status, score, created_at, notes)
                VALUES (?, ?, ?, ?, 'new', 0, ?, ?)
                """,
                (name, company, email, source, now, notes),
            )
            conn.commit()
            return cursor.lastrowid

    def get_lead(self, lead_id: int) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
            return dict(row) if row else None

    def get_leads_by_status(self, status: str) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM leads WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_hot_leads(self) -> list[dict]:
        excluded = ("closed", "lost", "donotcontact")
        placeholders = ",".join("?" * len(excluded))
        with self._get_conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM leads WHERE score >= 60 AND status NOT IN ({placeholders}) ORDER BY score DESC",
                excluded,
            ).fetchall()
            return [dict(r) for r in rows]

    def update_lead(self, lead_id: int, **fields):
        if not fields:
            return
        allowed = {
            "name", "company", "email", "phone", "source", "status", "score",
            "last_contact", "next_action", "consent", "notes", "email_thread_id", "channel",
        }
        safe_fields = {k: v for k, v in fields.items() if k in allowed}
        if not safe_fields:
            return
        set_clause = ", ".join(f"{k} = ?" for k in safe_fields)
        values = list(safe_fields.values()) + [lead_id]
        with self._get_conn() as conn:
            conn.execute(f"UPDATE leads SET {set_clause} WHERE id = ?", values)
            conn.commit()

    def mark_do_not_contact(self, email: str):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE leads SET status = 'donotcontact' WHERE lower(email) = lower(?)",
                (email,),
            )
            conn.commit()

    def is_do_not_contact(self, email: str) -> bool:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM leads WHERE lower(email) = lower(?) AND status = 'donotcontact'",
                (email,),
            ).fetchone()
            return row is not None

    def get_stats(self) -> dict:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM leads GROUP BY status"
            ).fetchall()
            counts = {r["status"]: r["cnt"] for r in rows}
            total = sum(counts.values())
            # Pipeline value = leads not lost/donotcontact * avg value
            pipeline_count = sum(
                v for k, v in counts.items() if k not in ("lost", "donotcontact")
            )
            return {
                "total": total,
                "by_status": counts,
                "pipeline_value_eur": pipeline_count * AVG_LEAD_VALUE,
            }

    def get_leads_created_today(self) -> list[dict]:
        today = date.today().isoformat()
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM leads WHERE created_at LIKE ? ORDER BY created_at DESC",
                (f"{today}%",),
            ).fetchall()
            return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# AI helpers — Groq primary, Claude Haiku fallback
# ─────────────────────────────────────────────────────────────────────────────

def _call_groq(prompt: str, system: str, model: str = "llama-3.1-8b-instant") -> str:
    """Call Groq API via raw requests. Raises on failure."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 1024,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _call_claude_haiku(prompt: str, system: str) -> str:
    """Call Anthropic Claude Haiku as fallback."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "claude-haiku-4-5",
        "max_tokens": 1024,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"].strip()


def _call_ai(prompt: str, system: str) -> str:
    """Try Groq first, fall back to Claude Haiku."""
    if GROQ_API_KEY:
        try:
            return _call_groq(prompt, system)
        except Exception as e:
            logger.warning(f"Groq failed, falling back to Claude: {e}")
    if ANTHROPIC_API_KEY:
        return _call_claude_haiku(prompt, system)
    raise RuntimeError("No AI provider configured (GROQ_API_KEY or ANTHROPIC_API_KEY required)")


def _extract_json(text: str) -> dict:
    """Extract first JSON object from AI response."""
    import re
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"No valid JSON found in AI response: {text[:200]}")


# ─────────────────────────────────────────────────────────────────────────────
# ClassificationAgent
# ─────────────────────────────────────────────────────────────────────────────

class ClassificationAgent:
    SYSTEM = (
        "Eres un agente de clasificacion de leads B2B para una agencia digital espanola. "
        "Tu objetivo: analizar un mensaje entrante y devolver JSON con la clasificacion del lead. "
        "Responde SOLO con JSON valido, sin texto adicional."
    )

    def classify_lead(self, text: str, source: str) -> dict:
        """
        Classify a lead from raw text.
        Returns: {intent, score, pain_point, urgency, summary, next_action}
        """
        prompt = f"""Analiza este mensaje de un potencial cliente y clasifícalo.
Fuente: {source}
Mensaje: {text}

Devuelve JSON con estos campos exactos:
{{
  "intent": "<buying_signal|info_request|objection|irrelevant|spam>",
  "score": <0-100 entero, probabilidad de cierre>,
  "pain_point": "<problema principal detectado, en espanol, max 80 chars>",
  "urgency": "<alta|media|baja>",
  "summary": "<resumen 1 frase en espanol>",
  "next_action": "<accion recomendada, ej: llamar hoy, enviar propuesta, no contactar>"
}}

Criterios de score:
- 80-100: quiere contratar ya, pide precio o demo
- 60-79: interes claro, hace preguntas concretas
- 40-59: curiosidad, pide informacion general
- 20-39: objecion o duda fuerte
- 0-19: irrelevante o spam"""

        try:
            raw = _call_ai(prompt, self.SYSTEM)
            result = _extract_json(raw)
            # Validate and sanitize
            if result.get("intent") not in VALID_INTENTS:
                result["intent"] = "info_request"
            result["score"] = max(0, min(100, int(result.get("score", 0))))
            result.setdefault("pain_point", "")
            result.setdefault("urgency", "baja")
            result.setdefault("summary", "")
            result.setdefault("next_action", "revisar manualmente")
            return result
        except Exception as e:
            logger.error(f"ClassificationAgent error: {e}")
            return {
                "intent": "info_request",
                "score": 30,
                "pain_point": "desconocido",
                "urgency": "baja",
                "summary": "Error al clasificar automaticamente",
                "next_action": "revisar manualmente",
            }


# ─────────────────────────────────────────────────────────────────────────────
# CopywriterAgent
# ─────────────────────────────────────────────────────────────────────────────

class CopywriterAgent:
    SYSTEM = (
        "Eres el closer de Sistema 180, una agencia digital espanola para negocios locales. "
        "Escribes emails de ventas B2B en espanol: directos, humanos, sin robotismo. "
        "Framework: DOLOR → CLARIDAD → RESULTADO → CTA simple. "
        "Objetivo: conseguir una llamada o un pago. Sin parrafadas, sin relleno. "
        "Responde SOLO con JSON valido."
    )

    PRODUCTS = (
        "Web profesional: 297€ pago unico (posicionamiento Google Maps + Bot IA WhatsApp 24/7). "
        "Recepcionista IA WhatsApp: 300€/mes (atiende clientes, cierra citas automaticamente)."
    )

    def _lead_context(self, lead: dict) -> str:
        return (
            f"Nombre: {lead.get('name', '')}\n"
            f"Empresa: {lead.get('company', '')}\n"
            f"Email: {lead.get('email', '')}\n"
            f"Score: {lead.get('score', 0)}/100\n"
            f"Notas: {lead.get('notes', '')}\n"
            f"Canal: {lead.get('channel', lead.get('source', ''))}"
        )

    def draft_email_reply(self, lead: dict, original_email: str) -> dict:
        prompt = f"""Lead info:
{self._lead_context(lead)}

Email original que enviaron:
{original_email[:800]}

Productos Sistema 180:
{self.PRODUCTS}

Escribe una respuesta de email que:
1. Reconoce su problema especifico (dolor)
2. Da claridad de que existe solucion
3. Muestra resultado concreto (ejemplo real de cliente)
4. CTA simple: "15 min de llamada esta semana?"

JSON de respuesta:
{{
  "subject": "<asunto del email, max 60 chars>",
  "body": "<cuerpo del email, tono cercano B2B, max 250 palabras, sin formatos markdown>"
}}"""
        return self._generate(prompt)

    def draft_followup(self, lead: dict, attempt_number: int) -> dict:
        angles = {
            1: "Angulo: recordatorio suave. Preguntar si recibio el mensaje anterior. Ofrecer demo gratis.",
            2: "Angulo: caso de exito. Mencionar un cliente similar que ya usa el sistema. Resultados concretos.",
            3: "Angulo: urgencia real. Plazas limitadas este mes. Oferta especial si cierra esta semana.",
        }
        angle = angles.get(attempt_number, angles[3])

        prompt = f"""Lead info:
{self._lead_context(lead)}

Este es el seguimiento numero {attempt_number}.
{angle}

Productos Sistema 180:
{self.PRODUCTS}

Escribe un email de seguimiento corto (max 120 palabras). CTA claro al final.

JSON:
{{
  "subject": "<asunto>",
  "body": "<cuerpo>"
}}"""
        return self._generate(prompt)

    def draft_proposal(self, lead: dict) -> dict:
        prompt = f"""Lead info:
{self._lead_context(lead)}

Este lead tiene score alto. Escribe una propuesta comercial personalizada.

Incluye:
1. Diagnostico de su situacion (basado en notas/canal)
2. Solucion propuesta de Sistema 180 con precio
3. Que ocurre si no actuan (coste de oportunidad)
4. Garantia: si no ven resultados en 30 dias, devolvemos el dinero
5. CTA: "Firma el acuerdo hoy y empezamos manana"

Productos: {self.PRODUCTS}

JSON:
{{
  "subject": "<asunto propuesta>",
  "body": "<propuesta completa, max 400 palabras, tono profesional pero cercano>"
}}"""
        return self._generate(prompt)

    def _generate(self, prompt: str) -> dict:
        try:
            raw = _call_ai(prompt, self.SYSTEM)
            result = _extract_json(raw)
            result.setdefault("subject", "Propuesta Sistema 180")
            result.setdefault("body", "")
            return result
        except Exception as e:
            logger.error(f"CopywriterAgent error: {e}")
            return {
                "subject": "Propuesta Sistema 180",
                "body": (
                    "Hola,\n\nGracias por tu interes en Sistema 180. "
                    "Me gustaria explicarte como podemos ayudarte. "
                    "Tienes 15 minutos esta semana para una llamada rapida?\n\nSaludos"
                ),
            }


# ─────────────────────────────────────────────────────────────────────────────
# FollowUpEngine
# ─────────────────────────────────────────────────────────────────────────────

class FollowUpEngine:
    MAX_ATTEMPTS = 3

    def __init__(self, db: LeadsDB):
        self.db = db

    def get_pending_followups(self) -> list[dict]:
        """Returns leads where next_action date is today or in the past."""
        today = date.today().isoformat()
        with self.db._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM leads
                WHERE status = 'followup'
                  AND next_action IS NOT NULL
                  AND next_action <= ?
                ORDER BY next_action ASC
                """,
                (today,),
            ).fetchall()
            return [dict(r) for r in rows]

    def mark_followup_done(self, lead_id: int, attempt: int):
        """Schedule next follow-up or mark as lost after max attempts."""
        if attempt >= self.MAX_ATTEMPTS:
            self.db.update_lead(lead_id, status="lost", notes="Max follow-ups reached — no response")
            logger.info(f"Lead {lead_id} marked as lost after {attempt} attempts")
        else:
            next_date = (date.today() + timedelta(days=3 + attempt)).isoformat()
            self.db.update_lead(
                lead_id,
                next_action=next_date,
                last_contact=datetime.utcnow().isoformat(),
            )
            logger.info(f"Lead {lead_id} follow-up {attempt} done, next: {next_date}")

    def schedule_followup(self, lead_id: int, days_from_now: int = 2):
        """Put a lead into followup queue."""
        next_date = (date.today() + timedelta(days=days_from_now)).isoformat()
        self.db.update_lead(lead_id, status="followup", next_action=next_date)


# ─────────────────────────────────────────────────────────────────────────────
# ReportingAgent
# ─────────────────────────────────────────────────────────────────────────────

class ReportingAgent:
    def __init__(self, db: LeadsDB, followup_engine: FollowUpEngine):
        self.db = db
        self.fe = followup_engine

    def generate_daily_report(self) -> str:
        stats = self.db.get_stats()
        new_today = self.db.get_leads_created_today()
        hot = self.db.get_hot_leads()
        pending_followups = self.fe.get_pending_followups()
        by_status = stats.get("by_status", {})

        lines = [
            f"REPORTE DIARIO — {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            f"Leads nuevos hoy: {len(new_today)}",
            f"Leads calientes (score>=60): {len(hot)}",
            f"Follow-ups pendientes: {len(pending_followups)}",
            "",
            "Pipeline por estado:",
        ]
        for status in VALID_STATUSES:
            count = by_status.get(status, 0)
            if count:
                lines.append(f"  {status}: {count}")

        lines += [
            "",
            f"Valor pipeline estimado: {stats['pipeline_value_eur']:,}€",
            f"Leads totales en DB: {stats['total']}",
        ]

        if hot:
            lines.append("")
            lines.append("Top leads calientes:")
            for lead in hot[:5]:
                lines.append(
                    f"  [{lead['score']}] {lead['name']} — {lead['company']} ({lead['status']})"
                )

        if pending_followups:
            lines.append("")
            lines.append("Follow-ups de hoy:")
            for lead in pending_followups[:5]:
                lines.append(f"  {lead['name']} — {lead['company']} ({lead['next_action']})")

        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# GmailOps — stub ready for OAuth (works standalone)
# ─────────────────────────────────────────────────────────────────────────────

class GmailOps:
    """
    Thin wrapper that integrates Gmail emails into the lead pipeline.
    Actual Gmail API calls are handled by GmailClient in gmail_ops.py.
    This class processes emails and adds them to the DB.
    """

    def __init__(self, db: LeadsDB, classifier: ClassificationAgent, copywriter: CopywriterAgent):
        self.db = db
        self.classifier = classifier
        self.copywriter = copywriter

    def add_email_lead(
        self,
        from_email: str,
        from_name: str,
        subject: str,
        body: str,
    ) -> dict:
        """
        Classify an inbound email and add to leads DB.
        GDPR: only process emails from businesses (not personal).
        Returns: {lead_id, classification}
        """
        if self.db.is_do_not_contact(from_email):
            logger.info(f"GmailOps: skipping do-not-contact email {from_email}")
            return {"lead_id": None, "classification": None, "skipped": "do_not_contact"}

        text = f"Asunto: {subject}\n\n{body}"
        classification = self.classifier.classify_lead(text, source="gmail")

        # Skip spam
        if classification.get("intent") == "spam":
            logger.info(f"GmailOps: skipping spam from {from_email}")
            return {"lead_id": None, "classification": classification, "skipped": "spam"}

        notes = (
            f"Asunto: {subject} | "
            f"Score AI: {classification['score']} | "
            f"Pain: {classification.get('pain_point', '')} | "
            f"Urgencia: {classification.get('urgency', '')}"
        )

        lead_id = self.db.add_lead(
            name=from_name or from_email.split("@")[0],
            company=from_email.split("@")[-1].split(".")[0].capitalize(),
            email=from_email,
            source="gmail",
            notes=notes,
        )

        self.db.update_lead(
            lead_id,
            score=classification["score"],
            status="qualified" if classification["score"] >= 60 else "new",
            channel="email",
            last_contact=datetime.utcnow().isoformat(),
        )

        logger.info(f"GmailOps: added lead {lead_id} from {from_email} score={classification['score']}")
        return {"lead_id": lead_id, "classification": classification}

    def draft_reply(self, lead_id: int) -> Optional[dict]:
        """
        Generate an AI draft reply for a lead.
        Human must approve before sending.
        Returns: {subject, body} or None
        """
        lead = self.db.get_lead(lead_id)
        if not lead:
            return None

        original = lead.get("notes", "")
        draft = self.copywriter.draft_email_reply(lead, original)
        logger.info(f"GmailOps: draft created for lead {lead_id}")
        return draft


# ─────────────────────────────────────────────────────────────────────────────
# Convenience factory
# ─────────────────────────────────────────────────────────────────────────────

def get_revenue_ops() -> tuple[LeadsDB, ClassificationAgent, CopywriterAgent, FollowUpEngine, ReportingAgent, GmailOps]:
    """Return fully wired Revenue Ops components."""
    db = LeadsDB()
    classifier = ClassificationAgent()
    copywriter = CopywriterAgent()
    followup = FollowUpEngine(db)
    reporter = ReportingAgent(db, followup)
    gmail_ops = GmailOps(db, classifier, copywriter)
    return db, classifier, copywriter, followup, reporter, gmail_ops
