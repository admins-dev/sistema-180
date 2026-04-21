"""
llm_brain.py — Cerebro LLM para generar DMs personalizados
Cascade: Groq (gratis) → Claude Haiku → Gemini Flash → Fallback
"""
import os
import logging
import aiohttp
from config import ANTHROPIC_KEY, GEMINI_KEY, GROQ_KEY

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Eres un vendedor consultivo experto para negocios locales en España. "
    "Escribes DMs de Instagram de MÁXIMO 2-3 líneas. Reglas estrictas:\n"
    "- Naturalidad total, como si lo escribiera un humano con el móvil\n"
    "- NUNCA 'Hola equipo de X' ni emojis de relleno\n"
    "- Menciona algo ESPECÍFICO de su perfil/bio para demostrar que lo miraste\n"
    "- Termina SIEMPRE con una pregunta abierta breve\n"
    "- Solo el texto del DM, nada más"
)

FALLBACKS = {
    "peluqueria": "Vi tu pelu y me surgió una pregunta — ¿cuántos clientes pierdes por no contestar fuera de horario? Hay algo que puede ayudarte.",
    "barberia": "¿Cuántas llamadas para cita no puedes atender? Hay una forma sencilla de no perder ninguna.",
    "estetica": "Tus fotos están muy bien. ¿Tienes citas entrando solas por Instagram? Se puede automatizar sin complicaciones.",
    "clinica": "He visto tu clínica. ¿Cuántos pacientes pierdes por no contestar a tiempo? Tengo algo que puede ayudarte.",
    "default": "Vi tu negocio — ¿cuántos clientes pierdes porque no contestas rápido? Tengo una solución sencilla.",
}


def _detect_business_type(username: str, bio: str = "") -> str:
    text = (username + " " + bio).lower()
    types = {
        "barberia": ["barberia", "barber", "barbershop", "barbero", "fade"],
        "estetica": ["estetica", "beauty", "spa", "uñas", "nail", "laser", "belleza"],
        "clinica": ["clinica", "dental", "fisio", "medico", "salud", "doctor"],
        "peluqueria": ["peluqueria", "peluquer", "salon", "hair", "stylist"],
    }
    for btype, keywords in types.items():
        if any(kw in text for kw in keywords):
            return btype
    return "default"


async def generate_dm(
    business_name: str,
    username: str = "",
    bio: str = "",
    followers: int = 0,
    city: str = "",
) -> str:
    """
    Genera un DM personalizado usando la cascada de LLMs.
    Prioridad: Groq (gratis, rápido) → Claude Haiku → Gemini Flash → fallback.
    """
    tipo = _detect_business_type(username, bio)
    user_prompt = (
        f"Negocio: {business_name}"
        + (f" (@{username})" if username else "")
        + (f" en {city}" if city else "")
        + f"\nTipo: {tipo}"
        + (f"\nBio: {bio[:150]}" if bio else "")
        + (f"\nSeguidores: {followers}" if followers else "")
        + "\nEscribe el DM:"
    )

    # ── 1. Groq / LLaMA (gratis, ultra rápido) ──────────────────────
    if GROQ_KEY:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "max_tokens": 120,
                        "temperature": 0.85,
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    data = await resp.json()
                    text = data["choices"][0]["message"]["content"].strip()
                    if text and len(text) > 20:
                        logger.info("[LLM] DM generado con Groq/LLaMA")
                        return text
        except Exception as e:
            logger.warning(f"[LLM] Groq falló: {e}")

    # ── 2. Claude Haiku (backup barato) ──────────────────────────────
    if ANTHROPIC_KEY:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": ANTHROPIC_KEY,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "claude-haiku-4-5-20251001",
                        "max_tokens": 120,
                        "system": SYSTEM_PROMPT,
                        "messages": [{"role": "user", "content": user_prompt}],
                    },
                    timeout=aiohttp.ClientTimeout(total=12),
                ) as resp:
                    data = await resp.json()
                    text = data["content"][0]["text"].strip()
                    if text:
                        logger.info("[LLM] DM generado con Claude Haiku")
                        return text
        except Exception as e:
            logger.warning(f"[LLM] Claude falló: {e}")

    # ── 3. Gemini Flash (backup) ─────────────────────────────────────
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_prompt}]}],
                        "generationConfig": {"maxOutputTokens": 120, "temperature": 0.85},
                    },
                    timeout=aiohttp.ClientTimeout(total=12),
                ) as resp:
                    data = await resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text:
                        logger.info("[LLM] DM generado con Gemini Flash")
                        return text
        except Exception as e:
            logger.warning(f"[LLM] Gemini falló: {e}")

    # ── 4. Fallback hardcoded ────────────────────────────────────────
    logger.warning("[LLM] Usando fallback estático")
    return FALLBACKS.get(tipo, FALLBACKS["default"])
