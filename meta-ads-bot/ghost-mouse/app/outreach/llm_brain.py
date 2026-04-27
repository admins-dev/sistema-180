"""
LLM Brain — generates personalized outreach drafts using AI.

Uses Groq (free, fast) or Gemini as LLM backend.
Generates drafts for HUMAN REVIEW — never sends autonomously.

Every generated draft is stored with the prompt version for auditability.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from app.config.settings import get_settings
from app.domain.models.lead import Lead, LeadContact
from app.observability.logging import get_logger

log = get_logger("llm_brain")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

PROMPT_VERSION = "v1.0"

SYSTEM_PROMPT = """Eres un experto en ventas B2B para negocios locales en España.
Tu trabajo es escribir emails de prospección CORTOS, DIRECTOS y PERSONALIZADOS.

Reglas:
- Máximo 5 frases
- Tono profesional pero cercano (tuteo)
- Menciona algo ESPECÍFICO del negocio (su nicho, su ciudad, su web)
- NO uses palabras como "increíble", "revolucionario", "disruptivo"
- NO prometas resultados concretos (no "duplicaremos tus clientes")
- Incluye una pregunta abierta al final para provocar respuesta
- Escribe en español de España (no latinoamericano)
- NO incluyas asunto, solo el cuerpo del email
"""


def _build_user_prompt(lead: Lead, contacts: list[LeadContact]) -> str:
    """Build a context-rich prompt for the LLM."""
    has_web = bool(lead.website)
    has_email = any(c.contact_type == "email" for c in contacts)
    has_ig = any(c.contact_type == "instagram" for c in contacts)

    context = f"""Genera un email de primer contacto para este negocio:

- Nombre: {lead.business_name}
- Nicho: {lead.niche or 'desconocido'}
- Ciudad: {lead.city or 'desconocida'}
- Web: {lead.website or 'no tiene'}
- Rating Google: {lead.rating or 'sin datos'} ({lead.reviews_count or 0} reseñas)
- Tiene Instagram: {'sí' if has_ig else 'no'}
- Score de oportunidad: {lead.redesign_opportunity_score or 'no calculado'}

Servicio que ofrecemos: marketing digital y rediseño web para negocios locales."""

    return context


def generate_draft_groq(lead: Lead, contacts: list[LeadContact]) -> dict:
    """Generate a personalized email draft using Groq (free, fast)."""
    settings = get_settings()

    if not settings.groq_api_key:
        return {"error": "GROQ_API_KEY not configured"}

    user_prompt = _build_user_prompt(lead, contacts)

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                GROQ_API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        draft = data["choices"][0]["message"]["content"].strip()

        log.info("draft_generated", lead_id=lead.id, model="groq", prompt_version=PROMPT_VERSION)

        return {
            "draft": draft,
            "model": "llama-3.3-70b-versatile",
            "provider": "groq",
            "prompt_version": PROMPT_VERSION,
            "tokens_used": data.get("usage", {}).get("total_tokens", 0),
        }

    except Exception as e:
        log.error("draft_failed", lead_id=lead.id, error=str(e))
        return {"error": str(e)}


def generate_draft_gemini(lead: Lead, contacts: list[LeadContact]) -> dict:
    """Generate a personalized email draft using Gemini (free tier)."""
    settings = get_settings()

    if not settings.gemini_api_key:
        return {"error": "GEMINI_API_KEY not configured"}

    user_prompt = _build_user_prompt(lead, contacts)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300},
    }

    try:
        url = f"{GEMINI_API_URL}?key={settings.gemini_api_key}"
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        draft = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        log.info("draft_generated", lead_id=lead.id, model="gemini", prompt_version=PROMPT_VERSION)

        return {
            "draft": draft,
            "model": "gemini-2.0-flash",
            "provider": "gemini",
            "prompt_version": PROMPT_VERSION,
        }

    except Exception as e:
        log.error("draft_failed", lead_id=lead.id, error=str(e))
        return {"error": str(e)}


def generate_draft(lead: Lead, contacts: list[LeadContact]) -> dict:
    """Generate draft using best available LLM (Groq first, Gemini fallback)."""
    settings = get_settings()

    if settings.groq_api_key:
        result = generate_draft_groq(lead, contacts)
        if "error" not in result:
            return result

    if settings.gemini_api_key:
        result = generate_draft_gemini(lead, contacts)
        if "error" not in result:
            return result

    return {"error": "No LLM API key configured (need GROQ_API_KEY or GEMINI_API_KEY)"}
