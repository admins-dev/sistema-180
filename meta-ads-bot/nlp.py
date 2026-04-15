"""
nlp.py — Clasificador de intents multi-provider
Providers: Anthropic Claude → Groq LLaMA → Gemini → Keywords
Nuevos intents: strategy, general_chat, search_web, generate_image
"""

import os
import re
import json
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

try:
    from shared_state import record_provider_call
    TRACKING = True
except ImportError:
    TRACKING = False

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── Intent cache (evita llamadas repetidas) ──
_intent_cache: dict[str, dict] = {}
CACHE_MAX = 200

SYSTEM_PROMPT = """Eres un clasificador de intenciones para un bot de Meta Ads y marketing digital.
Analiza el mensaje del usuario y responde SOLO con un JSON válido con esta estructura:
{"intent": "...", "action": "...", "params": {...}, "confidence": 0.0}

Intents disponibles:
- "get_metrics": cuando pide datos, métricas, estadísticas, resultados, "dame", "cuánto"
- "create_campaign": cuando quiere crear, nueva, lanzar, iniciar campaña. Extrae params: nombre (string), presupuesto (número o null)
- "pause_campaign": cuando quiere pausar, detener, parar campaña. Extrae params: campaign_id (string o null)
- "report": cuando pide reporte, resumen, informe, análisis
- "list_campaigns": cuando pide listar, mostrar, ver campañas
- "strategy_question": cuando pregunta sobre estrategia de negocio, marketing, ventas, crecimiento
- "search_web": cuando pide buscar información, investigar, "busca", "averigua", "qué es"
- "generate_image": cuando pide crear, generar, dibujar una imagen
- "general_chat": cuando es una conversación general, saludo, pregunta personal
- "unknown": si no encaja en ninguna categoría anterior

Para "create_campaign" extrae del mensaje: nombre de la campaña y presupuesto en euros.
Para "pause_campaign" extrae: campaign_id o nombre de la campaña.
Responde ÚNICAMENTE con el JSON, sin texto adicional."""


def _call_anthropic(user_message: str) -> dict | None:
    """Intenta clasificar usando Claude Haiku."""
    if not ANTHROPIC_API_KEY:
        return None
    t0 = time.time()
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 256,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=10,
        )
        response.raise_for_status()
        raw = response.json()["content"][0]["text"].strip()
        if TRACKING:
            record_provider_call("anthropic_nlp", True, (time.time() - t0) * 1000)
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"[NLP] Anthropic failed: {e}")
        if TRACKING:
            record_provider_call("anthropic_nlp", False)
        return None


def _call_groq(user_message: str) -> dict | None:
    """Intenta clasificar usando Groq (Llama)."""
    if not GROQ_API_KEY:
        return None
    t0 = time.time()
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 256,
                "temperature": 0.0,
            },
            timeout=10,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
        if TRACKING:
            record_provider_call("groq_nlp", True, (time.time() - t0) * 1000)
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"[NLP] Groq failed: {e}")
        if TRACKING:
            record_provider_call("groq_nlp", False)
        return None


def _call_gemini(user_message: str) -> dict | None:
    """Intenta clasificar usando Gemini 2.0 Flash."""
    if not GEMINI_API_KEY:
        return None
    t0 = time.time()
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"parts": [{"text": user_message}]}],
                "generationConfig": {"maxOutputTokens": 256, "temperature": 0.0},
            },
            timeout=10,
        )
        response.raise_for_status()
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Limpiar posible markdown
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        if TRACKING:
            record_provider_call("gemini_nlp", True, (time.time() - t0) * 1000)
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"[NLP] Gemini failed: {e}")
        if TRACKING:
            record_provider_call("gemini_nlp", False)
        return None


def _keyword_fallback(user_message: str) -> dict:
    """Fallback basado en keywords cuando ninguna API está disponible."""
    msg = user_message.lower()

    if any(w in msg for w in ["métrica", "dato", "estadística", "resultado", "cuánto", "gasto", "rendimiento"]):
        return {"intent": "get_metrics", "action": "get_metrics", "params": {}, "confidence": 0.6}

    if any(w in msg for w in ["crear", "nueva", "lanzar", "iniciar", "abrir"]) and "campaña" in msg:
        budget_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:€|euro)", msg)
        params = {}
        if budget_match:
            params["presupuesto"] = float(budget_match.group(1).replace(",", "."))
        return {"intent": "create_campaign", "action": "create_campaign", "params": params, "confidence": 0.5}

    if any(w in msg for w in ["pausar", "parar", "detener", "pausa"]):
        return {"intent": "pause_campaign", "action": "pause_campaign", "params": {}, "confidence": 0.5}

    if any(w in msg for w in ["reporte", "resumen", "informe", "análisis"]):
        return {"intent": "report", "action": "report", "params": {}, "confidence": 0.5}

    if any(w in msg for w in ["listar", "mostrar", "ver", "todas"]) and "campaña" in msg:
        return {"intent": "list_campaigns", "action": "list_campaigns", "params": {}, "confidence": 0.5}

    if any(w in msg for w in ["estrategia", "plan", "crecimiento", "escalar", "objetivo", "meta"]):
        return {"intent": "strategy_question", "action": "strategy_question", "params": {}, "confidence": 0.4}

    if any(w in msg for w in ["busca", "investiga", "averigua", "qué es", "quién es", "dime sobre"]):
        return {"intent": "search_web", "action": "search_web", "params": {}, "confidence": 0.4}

    if any(w in msg for w in ["imagen", "genera", "dibuja", "crea una imagen", "foto"]):
        return {"intent": "generate_image", "action": "generate_image", "params": {}, "confidence": 0.4}

    if any(w in msg for w in ["hola", "buenas", "qué tal", "hey", "gracias", "adiós", "vale"]):
        return {"intent": "general_chat", "action": "general_chat", "params": {}, "confidence": 0.6}

    return {"intent": "unknown", "action": "unknown", "params": {}, "confidence": 0.0}


def process_user_intent(user_message: str) -> dict:
    """
    Multi-provider NLP: Anthropic → Groq → Gemini → Keywords.
    Con cache de intents recientes.
    """
    # Check cache
    cache_key = user_message.lower().strip()[:100]
    if cache_key in _intent_cache:
        logger.info(f"[NLP] Cache hit: {_intent_cache[cache_key]['intent']}")
        return _intent_cache[cache_key]

    # Cascade: Anthropic → Groq → Gemini → Keywords
    for provider_name, provider_fn in [
        ("Anthropic", _call_anthropic),
        ("Groq", _call_groq),
        ("Gemini", _call_gemini),
    ]:
        result = provider_fn(user_message)
        if result:
            result.setdefault("intent", "unknown")
            result.setdefault("action", result["intent"])
            result.setdefault("params", {})
            result.setdefault("confidence", 0.0)
            logger.info(f"[NLP] Processed via {provider_name}: intent={result['intent']}")
            # Cache result
            if len(_intent_cache) < CACHE_MAX:
                _intent_cache[cache_key] = result
            return result

    # Fallback: keyword matching
    logger.info("[NLP] All APIs failed, using keyword fallback")
    result = _keyword_fallback(user_message)
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tests = [
        "Dame las métricas de hoy",
        "Crea una nueva campaña llamada Verano con presupuesto 50 euros",
        "Pausa la campaña 12345",
        "Quiero ver el reporte semanal",
        "Muéstrame todas las campañas activas",
        "Hola qué tal",
        "Busca información sobre el CPC medio en España",
        "Genera una imagen de un logo futurista",
        "Cómo puedo escalar mi negocio a 30 ventas al mes",
    ]
    for msg in tests:
        result = process_user_intent(msg)
        print(f"[{msg[:40]}] → {result['intent']} ({result['confidence']:.0%})")
