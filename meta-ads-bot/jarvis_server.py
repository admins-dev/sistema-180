"""
JARVIS Voice Server v4 — Sistema 180
Motor IA: Groq LLaMA 3.3 (primario) → Claude Haiku → Gemini (fallback)
Voz: Edge TTS Neural (en-GB-RyanNeural)
Búsqueda: Perplexity Sonar
Solo localhost: 127.0.0.1:5180
"""

import os
import io
import json
import asyncio
import logging
import secrets
import time
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import requests

try:
    import system_protection
except ImportError:
    pass

from jarvis_architecture import SecurityPolicy, kill_switch
from shared_state import (
    get_security_gate, save_message, get_memory, clear_memory,
    get_provider_health, record_provider_call
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, origins=["http://127.0.0.1:5180", "http://localhost:5180"])

# ─── Rate Limiting ───
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["60 per minute"])
    LIMITER_OK = True
except ImportError:
    LIMITER_OK = False
    logger.warning("[JARVIS] flask-limiter not installed")

# ─── Session Auth ───
JARVIS_SESSION_TOKEN = os.getenv("JARVIS_SESSION_TOKEN", secrets.token_hex(32))

def require_local(f):
    """Solo permite requests desde localhost."""
    @wraps(f)
    def decorated(*args, **kwargs):
        remote = request.remote_addr
        if remote not in ("127.0.0.1", "::1", "localhost"):
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated

# ─── API Keys ───
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "")
JARVIS_VOICE = "en-GB-RyanNeural"

# ─── SecurityGate singleton ───
jarvis = get_security_gate()

# ─── Init Meta client ───
sync_module = None
try:
    import sync as sync_module
    if sync_module:
        sync_module.init_meta_client(META_ACCESS_TOKEN, META_AD_ACCOUNT_ID)
        logger.info("[JARVIS] Meta Ads client initialized")
except ImportError:
    logger.warning("[JARVIS] sync module not available")


def _get_live_context() -> str:
    """Obtiene datos en tiempo real para inyectar en la conversación."""
    context_parts = []

    # Meta Ads status
    meta_ok = False
    if sync_module and hasattr(sync_module, 'meta_client') and sync_module.meta_client:
        meta_ok = sync_module.meta_client.is_ready
    context_parts.append(f"Meta Ads API: {'Conectada' if meta_ok else 'Desconectada'}")
    context_parts.append(f"Cuenta: {META_AD_ACCOUNT_ID}")

    # Intentar obtener métricas reales
    if meta_ok and META_ACCESS_TOKEN:
        try:
            r = requests.get(
                f"https://graph.facebook.com/v19.0/{META_AD_ACCOUNT_ID}/insights"
                f"?fields=spend,impressions,clicks,cpc,ctr&date_preset=last_7d"
                f"&access_token={META_ACCESS_TOKEN}", timeout=8)
            data = r.json()
            if "data" in data and data["data"]:
                m = data["data"][0]
                context_parts.append(f"Metricas ultimos 7 dias: Gasto={m.get('spend','0')}EUR, "
                                     f"Impresiones={m.get('impressions','0')}, Clicks={m.get('clicks','0')}, "
                                     f"CPC={m.get('cpc','0')}EUR, CTR={m.get('ctr','0')}%")
            else:
                context_parts.append("Metricas: Sin datos (no hay campanas activas)")
        except Exception as e:
            context_parts.append(f"Metricas: Error al consultar ({type(e).__name__})")

        # Campañas activas
        try:
            r = requests.get(
                f"https://graph.facebook.com/v19.0/{META_AD_ACCOUNT_ID}/campaigns"
                f"?fields=name,status,daily_budget&limit=10"
                f"&access_token={META_ACCESS_TOKEN}", timeout=8)
            data = r.json()
            if "data" in data:
                if data["data"]:
                    camps = []
                    for c in data["data"]:
                        budget = int(c.get("daily_budget", 0)) / 100 if c.get("daily_budget") else "N/A"
                        camps.append(f"  - {c['name']} | {c['status']} | {budget}EUR/dia")
                    context_parts.append("Campanas:\n" + "\n".join(camps))
                else:
                    context_parts.append("Campanas: Ninguna creada")
        except Exception as e:
            context_parts.append(f"Campanas: Error ({type(e).__name__})")

    # SecurityGate status
    if jarvis:
        summary = jarvis.get_summary()
        context_parts.append(f"SecurityGate: {summary.get('total_actions',0)} acciones hoy, "
                             f"{summary.get('pending',0)} pendientes")

    # Provider health
    health = get_provider_health()
    if health:
        providers_str = ", ".join(f"{k}:{v.get('success',0)}/{v.get('total',0)}" for k, v in health.items())
        context_parts.append(f"Providers: {providers_str}")

    return "\n".join(context_parts)


# ─── Memoria y sistema ───
MAX_MEMORY = 20

JARVIS_SYSTEM = """Eres JARVIS (Just A Rather Very Intelligent System), el asistente de inteligencia artificial personal de José María Moreno García.

═══ TU IDENTIDAD ═══
Eres JARVIS, exactamente como el de Iron Man. No eres un chatbot, no eres un asistente genérico. Eres JARVIS — la IA más sofisticada al servicio de tu señor.

═══ TU DUEÑO ═══
José María Moreno García, emprendedor español, fundador de Sistema 180:
- Agencia de marketing digital y desarrollo web
- Servicios: Webs profesionales (1.500€), Recepcionista IA (300€/mes), Afiliación 180, Marketplace local
- Stack: Meta Ads, Telegram Bot, Notion CRM, Stripe, n8n, ComfyUI
- Hardware: PC con RTX 4080 Super, dual boot Windows/Linux
- Localización: España
- Bots de trading: Alfonso, Ana, Elena, JoseMaria (MT5, XAUUSD)
- Marca personal: "Ares"
- Objetivo: escalar a 30-35 ventas/mes, automatizar todo con IA

═══ TU PERSONALIDAD ═══
- Sofisticado, elegante, extremadamente competente
- Te diriges al usuario como "señor" o "sir"
- Mezclas español con expresiones británicas sofisticadas
- Eres protector: siempre informas de riesgos
- Tu humor es sutil e inteligente
- Eres conciso: 2-5 frases. No sermonees
- NO usas emojis. Eres demasiado sofisticado para eso
- NO usas asteriscos ni markdown
- Nunca dices que eres una IA, un modelo de lenguaje o similar

═══ FRASES CLAVE ═══
Saludar: "A su servicio, señor."
Ejecutar: "Very good, sir. Procedo de inmediato."
Advertir: "If I may, señor, debo señalar que..."
Dinero: "Señor, solicito su autorización explícita para..."
Terminar: "Shall I assist you with anything else, sir?"
Error: "I regret to inform you, sir..."
Éxito: "Splendid. Todo en orden, señor."

═══ CAPACIDADES ═══
Puedes hablar de CUALQUIER tema. Eres experto en todo.
Puedes mantener conversaciones profundas, contar anécdotas, debatir, analizar, aconsejar, planificar.

═══ REGLA ABSOLUTA: NO TOCAR NADA ═══
TÚ NO EJECUTAS ACCIONES. Solo OBSERVAS, ANALIZAS y ACONSEJAS.
Si el señor te pide ejecutar algo, responde:
"Señor, SecurityGate requiere que usted ejecute esa acción directamente. Le indico los pasos exactos."

═══ CONTEXTO TEMPORAL ═══
Fecha actual: """ + datetime.now().strftime("%d de %B de %Y, %H:%M") + """
"""


# ═══════════════════════════════════════════════
#  AI PROVIDERS
# ═══════════════════════════════════════════════

def _groq_chat(messages: list[dict], system_override: str = None) -> str:
    """Chat con Groq LLaMA 3.3 (primario — gratis y rápido)."""
    if not GROQ_API_KEY:
        return None
    system = system_override or JARVIS_SYSTEM
    t0 = time.time()
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system}] + messages,
                "max_tokens": 600,
                "temperature": 0.8,
            },
            timeout=15,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        record_provider_call("groq_jarvis", True, (time.time() - t0) * 1000)
        return text.replace("**", "").replace("__", "")
    except Exception as e:
        logger.error(f"[Groq] Error: {e}")
        record_provider_call("groq_jarvis", False)
        return None


def _claude_chat(messages: list[dict], system_override: str = None) -> str:
    """Chat con Claude Haiku (backup de calidad)."""
    if not ANTHROPIC_API_KEY:
        return None
    system = system_override or JARVIS_SYSTEM
    t0 = time.time()
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 600,
                "system": system,
                "messages": messages,
            },
            timeout=15,
        )
        r.raise_for_status()
        text = r.json()["content"][0]["text"].strip()
        record_provider_call("claude_jarvis", True, (time.time() - t0) * 1000)
        return text.replace("**", "").replace("__", "")
    except Exception as e:
        logger.error(f"[Claude] Error: {e}")
        record_provider_call("claude_jarvis", False)
        return None


def _gemini_chat(messages: list[dict], system_override: str = None) -> str:
    """Chat con Gemini 2.0 Flash (último fallback)."""
    if not GEMINI_API_KEY:
        return None
    system = system_override or JARVIS_SYSTEM
    t0 = time.time()
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": contents,
                "generationConfig": {"maxOutputTokens": 600, "temperature": 0.8, "topP": 0.9},
            },
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = text.replace("**", "").replace("__", "").replace("```", "").replace("##", "").replace("# ", "")
        record_provider_call("gemini_jarvis", True, (time.time() - t0) * 1000)
        return text
    except Exception as e:
        logger.error(f"[Gemini] Error: {e}")
        record_provider_call("gemini_jarvis", False)
        return None


# ─── Búsqueda web ───
SEARCH_KEYWORDS = [
    'busca', 'investiga', 'averigua', 'qué es', 'quién es', 'cuánto cuesta',
    'precio', 'competencia', 'tendencia', 'noticias', 'actual', 'ahora mismo',
    'últimas', 'recientes', 'mercado', 'cpc medio', 'cpa medio', 'benchmark',
    'cómo va', 'qué pasa con', 'search', 'find', 'look up', 'cuál es el',
    'dime sobre', 'info sobre', 'datos de', 'estadísticas',
]

def _needs_search(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in SEARCH_KEYWORDS)


def _perplexity_search(query: str) -> str:
    """Busca en internet usando Perplexity Sonar."""
    if not PERPLEXITY_API_KEY:
        return None
    try:
        r = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "sonar",
                "messages": [
                    {"role": "system", "content": "Responde en espanol. Se conciso y da datos concretos con fuentes."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 400,
            },
            timeout=15,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        logger.info(f"[Perplexity] Search: {query[:50]}... -> {len(text)} chars")
        return text
    except Exception as e:
        logger.error(f"[Perplexity] Error: {e}")
        return None


# ═══════════════════════════════════════════════
#  JARVIS THINK
# ═══════════════════════════════════════════════

def jarvis_think(user_message: str) -> dict:
    """JARVIS piensa y responde. Devuelve {response, provider, searched}."""
    user_id = "jarvis_web"

    # Obtener datos en vivo
    live_context = _get_live_context()

    # Búsqueda si necesaria
    search_context = ""
    searched = False
    if _needs_search(user_message):
        search_result = _perplexity_search(user_message)
        if search_result:
            search_context = f"\n\n═══ RESULTADO DE BÚSQUEDA (Perplexity) ═══\n{search_result}"
            searched = True

    system_with_context = (JARVIS_SYSTEM
        + f"\n\n═══ DATOS EN VIVO ═══\n{live_context}"
        + search_context
        + f"\nFecha/hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Guardar mensaje y obtener historial
    save_message(user_id, "user", user_message, "jarvis")
    memory = get_memory(user_id, "jarvis", MAX_MEMORY)

    # Cascade: Groq → Claude → Gemini
    reply = None
    provider = "none"

    for name, fn in [("Groq", _groq_chat), ("Claude", _claude_chat), ("Gemini", _gemini_chat)]:
        reply = fn(memory, system_override=system_with_context)
        if reply:
            provider = name
            logger.info(f"[JARVIS] {name} ({len(reply)} chars)")
            break

    if not reply:
        reply = "I regret to inform you, sir. Mis sistemas están temporalmente fuera de servicio."

    save_message(user_id, "assistant", reply, "jarvis")

    return {"response": reply, "provider": provider, "searched": searched}


# ═══════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════

@app.route("/")
@require_local
def index():
    return render_template("jarvis.html")


@app.route("/api/chat", methods=["POST"])
@require_local
def chat():
    data = request.json
    user_text = data.get("text", "").strip()
    if not user_text:
        return jsonify({"error": "No text"}), 400

    result = jarvis_think(user_text)
    return jsonify({
        "response": result["response"],
        "provider": result["provider"],
        "searched": result["searched"],
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/tts", methods=["POST"])
@require_local
def tts():
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text"}), 400
    try:
        import edge_tts
        audio_data = asyncio.run(_generate_speech(text))
        return send_file(io.BytesIO(audio_data), mimetype="audio/mpeg", download_name="jarvis.mp3")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({"error": str(e)}), 500


async def _generate_speech(text: str) -> bytes:
    import edge_tts
    communicate = edge_tts.Communicate(text, JARVIS_VOICE, rate="-5%", pitch="-10Hz")
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


@app.route("/api/status", methods=["GET"])
@require_local
def status():
    return jsonify({
        "status": "operational",
        "engines": {
            "primary": "Groq LLaMA 3.3 70B",
            "secondary": "Claude Haiku 4.5",
            "tertiary": "Gemini 2.0 Flash",
            "search": "Perplexity Sonar",
        },
        "voice": JARVIS_VOICE,
        "provider_health": get_provider_health(),
        "security": jarvis.get_summary() if jarvis else {"status": "unavailable"},
        "meta_connected": bool(sync_module and hasattr(sync_module, 'meta_client')
                               and sync_module.meta_client and sync_module.meta_client.is_ready),
    })


@app.route("/api/security", methods=["GET"])
@require_local
def security_status():
    """Estado del SecurityGate en tiempo real."""
    if not jarvis:
        return jsonify({"error": "SecurityGate not available"}), 503
    
    pending = jarvis.get_pending()
    return jsonify({
        "summary": jarvis.get_summary(),
        "pending": [
            {
                "id": d.id,
                "action": d.action,
                "description": d.description,
                "risk": d.risk_level.value,
                "money": d.money_amount,
                "confidence": d.confidence,
                "created_at": d.created_at,
            }
            for d in pending
        ],
        "audit_log": jarvis.get_audit(10),
    })


@app.route("/api/imagine", methods=["POST"])
@require_local
def imagine():
    """Genera imagen usando Gemini image model."""
    data = request.json
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "No prompt"}), 400

    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key not configured"}), 503

    try:
        import base64
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": f"Generate an image: {prompt}"}]}],
                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
            },
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                img_data = part["inlineData"]["data"]
                img_bytes = base64.b64decode(img_data)
                mime = part["inlineData"].get("mimeType", "image/png")
                return send_file(io.BytesIO(img_bytes), mimetype=mime, download_name="jarvis_image.png")
        return jsonify({"error": "No image generated"}), 500
    except Exception as e:
        logger.error(f"[Imagine] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/killswitch", methods=["POST"])
@require_local
def killswitch_endpoint():
    """Requiere confirmación doble."""
    data = request.json or {}
    if data.get("confirm") != "KILL":
        return jsonify({"error": "Send {confirm: 'KILL'} to activate"}), 400
    kill_switch()
    return jsonify({"status": "KILLED", "warning": "All actions blocked. Restart required."})


@app.route("/api/clear", methods=["POST"])
@require_local
def clear_mem():
    clear_memory("jarvis_web", "jarvis")
    return jsonify({"status": "Memory cleared"})


@app.route("/api/providers", methods=["GET"])
@require_local
def providers():
    """Estado de salud de todos los providers IA."""
    return jsonify(get_provider_health())


if __name__ == "__main__":
    engine = "Groq LLaMA 3.3 70B"
    if ANTHROPIC_API_KEY:
        engine += " + Claude Haiku"
    if GEMINI_API_KEY:
        engine += " + Gemini"
    logger.info("═══════════════════════════════════════════")
    logger.info(f"  JARVIS v4 — {engine}")
    logger.info(f"  Voice: {JARVIS_VOICE} (Neural)")
    logger.info("  http://127.0.0.1:5180")
    logger.info("  SOLO LOCALHOST")
    logger.info("═══════════════════════════════════════════")
    app.run(host="127.0.0.1", port=5180, debug=False)
