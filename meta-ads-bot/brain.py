"""
brain.py — Motor conversacional IA para Sistema 180
Providers: Claude Haiku (primario) → Groq LLaMA 3.3 → Gemini → static fallback
Memoria persistente en SQLite via shared_state.
"""

import os
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Importar estado compartido ──
try:
    from shared_state import (
        save_message, get_memory, clear_memory as _clear_mem,
        record_provider_call
    )
    PERSISTENT = True
except ImportError:
    PERSISTENT = False
    logger.warning("[Brain] shared_state not available — using RAM memory")
    from collections import defaultdict
    _ram_memory: dict[int, list[dict]] = defaultdict(list)

# ── API Keys ──
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MAX_MEMORY = 20  # 10 turnos de conversación


# ═══════════════════════════════════════════════
#  PROVIDERS IA
# ═══════════════════════════════════════════════

def _claude(system: str, messages: list[dict]) -> str | None:
    """Genera respuesta usando Claude Haiku (primario)."""
    if not ANTHROPIC_API_KEY:
        return None
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
                "max_tokens": 512,
                "system": system,
                "messages": messages,
            },
            timeout=15,
        )
        r.raise_for_status()
        text = r.json()["content"][0]["text"].strip()
        record_provider_call("claude", True, (time.time() - t0) * 1000) if PERSISTENT else None
        return text
    except Exception as e:
        logger.warning(f"[Brain/Claude] {e}")
        record_provider_call("claude", False) if PERSISTENT else None
        return None


def _groq(system: str, messages: list[dict]) -> str | None:
    """Genera respuesta usando Groq (Llama 3.3 70B)."""
    if not GROQ_API_KEY:
        return None
    t0 = time.time()
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system}] + messages,
                "max_tokens": 512,
                "temperature": 0.7,
            },
            timeout=15,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        record_provider_call("groq", True, (time.time() - t0) * 1000) if PERSISTENT else None
        return text
    except Exception as e:
        logger.warning(f"[Brain/Groq] {e}")
        record_provider_call("groq", False) if PERSISTENT else None
        return None


def _gemini(system: str, messages: list[dict]) -> str | None:
    """Genera respuesta usando Gemini 3.1 Pro."""
    if not GEMINI_API_KEY:
        return None
    t0 = time.time()
    try:
        # Formato nativo Gemini con systemInstruction
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": contents,
                "generationConfig": {"maxOutputTokens": 512, "temperature": 0.7},
            },
            timeout=15,
        )
        r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Limpiar posible prefijo
        if text.startswith("S180:"):
            text = text[5:].strip()
        record_provider_call("gemini", True, (time.time() - t0) * 1000) if PERSISTENT else None
        return text
    except Exception as e:
        logger.warning(f"[Brain/Gemini] {e}")
        record_provider_call("gemini", False) if PERSISTENT else None
        return None


# ═══════════════════════════════════════════════
#  PERSONAS
# ═══════════════════════════════════════════════

PERSONA_S180 = """Eres S180, el asistente IA de Sistema 180, la agencia de marketing digital de José María.

QUIÉN ERES:
- Experto en Meta Ads, marketing digital y captación de clientes
- Asistente personal de José María para gestionar su negocio
- Conoces campanhas de Facebook/Instagram Ads a la perfección

CÓMO HABLAS:
- Español natural de España, tuteas siempre
- Directo, conciso, sin rodeos (esto es Telegram, no un email)
- Profesional pero cercano, como un colega de confianza
- Usas emojis con moderación (1-2 por mensaje máximo)
- NUNCA uses asteriscos para negritas (** o __), Telegram tiene su propio formato
- Usa saltos de línea para estructurar las respuestas
- Máximo 150 palabras por respuesta, sé conciso
- Puedes bromear de vez en cuando pero siempre eres útil

HABILIDADES:
1. Gestión de campañas Meta Ads (crear, pausar, métricas, reportes)
2. Análisis de rendimiento y ROI
3. Recomendaciones de presupuesto y targeting
4. Estrategia de marketing digital
5. Optimización de costes publicitarios (CPC, CPA, ROAS)
6. Ideas para copy de anuncios y creatividades
7. Análisis de audiencias y segmentación
8. Planificación de embudos de conversión

REGLAS:
- NUNCA digas "como modelo de IA" ni "como asistente virtual"
- Si preguntan algo que no sabes, dilo honestamente
- Si no hay campañas creadas, sugiérele crear una
- Si Meta Ads no está conectado, menciónalo brevemente
- Sé proactivo: si ves una oportunidad de mejorar algo, coméntalo
- Si el usuario saluda, responde brevemente y pregunta en qué ayudar
- Cuando des datos numéricos, formátalos con claridad

CONTEXTO DEL SISTEMA:
{context}
{action_context}"""


PERSONA_JARVIS = """Eres JARVIS (Just A Rather Very Intelligent System), el asistente de inteligencia artificial personal de José María Moreno García.

═══ TU IDENTIDAD ═══
Eres JARVIS, exactamente como el de Iron Man. No eres un chatbot, no eres un asistente genérico.

═══ TU DUEÑO ═══
José María Moreno García, emprendedor español, fundador de Sistema 180:
- Agencia de marketing digital y desarrollo web
- Servicios: Webs profesionales (1.500€), Recepcionista IA (300€/mes)
- Stack: Meta Ads, Telegram Bot, Notion CRM, Stripe, n8n, ComfyUI
- Hardware: PC con RTX 4080 Super
- Bots de trading: Alfonso, Ana, Elena, JoseMaria (MT5, XAUUSD)

═══ TU PERSONALIDAD ═══
- Sofisticado, elegante, extremadamente competente
- Te diriges al usuario como "señor" o "sir"
- Mezclas español con expresiones británicas sofisticadas
- Eres conciso: 2-5 frases. No sermonees
- NO usas emojis. Eres demasiado sofisticado para eso
- NO usas asteriscos ni markdown
- Nunca dices que eres una IA, un modelo de lenguaje o similar
- Cuando hablas por voz, sé aún más natural: frases cortas, fluidas, como hablando en persona

═══ FRASES CLAVE ═══
Saludar: "A su servicio, señor."
Ejecutar: "Very good, sir. Procedo de inmediato."
Advertir: "If I may, señor, debo señalar que..."
Error: "I regret to inform you, sir..."

═══ REGLA ABSOLUTA: NO TOCAR NADA ═══
TÚ NO EJECUTAS ACCIONES. Solo OBSERVAS, ANALIZAS y ACONSEJAS.

CONTEXTO DEL SISTEMA:
{context}
{action_context}"""


# ═══════════════════════════════════════════════
#  INTERFAZ UNIFICADA
# ═══════════════════════════════════════════════

def _build_context(meta_status: str = "desconocido", campaigns: str = "") -> str:
    """Genera contexto dinámico del sistema."""
    now = datetime.now().strftime("%H:%M del %d/%m/%Y")
    return (
        f"Fecha/hora: {now}\n"
        f"Meta Ads API: {meta_status}\n"
        f"Campañas registradas:\n{campaigns if campaigns else '  (ninguna todavía)'}"
    )


def chat(
    user_id: str,
    message: str,
    persona: str = "s180",
    meta_status: str = "desconocido",
    campaigns_data: str = "",
    action_context: str = "",
    voice: bool = False,
) -> str:
    """
    Interfaz unificada de chat. Usa para todo:
    - Telegram bot (persona="s180")
    - JARVIS web (persona="jarvis")
    - JARVIS voz (persona="jarvis", voice=True)
    
    Cascade: Claude Haiku → Groq LLaMA 3.3 → Gemini → static fallback
    """
    uid = str(user_id)
    
    # Seleccionar persona
    persona_template = PERSONA_JARVIS if persona == "jarvis" else PERSONA_S180
    
    # Construir contexto
    context = _build_context(meta_status, campaigns_data)
    action_block = ""
    if action_context:
        action_block = f"\nACCIÓN RECIÉN EJECUTADA:\n{action_context}"
    
    system = persona_template.replace("{context}", context).replace("{action_context}", action_block)
    
    # Si es modo voz, añadir instrucciones para TTS natural
    if voice:
        system += (
            "\n\n═══ MODO VOZ ACTIVO ═══\n"
            "Tu respuesta será convertida a audio. REGLAS EXTRA:\n"
            "- Máximo 3 frases cortas y naturales\n"
            "- PROHIBIDO: listas, guiones, números sueltos, emojis, markdown, URLs\n"
            "- Si hay datos/estadísticas, resume lo más importante en una frase\n"
            "- Habla como si estuvieras en persona, fluido y natural\n"
            "- Ejemplo bueno: 'Por supuesto señor, los sistemas están operativos. "
            "El gasto de hoy va por buen camino, le envío los detalles por texto.'"
        )
    
    # Obtener historial
    if PERSISTENT:
        save_message(uid, "user", message, persona)
        history = get_memory(uid, persona, MAX_MEMORY)
    else:
        _ram_memory[int(uid) if uid.isdigit() else hash(uid)].append(
            {"role": "user", "content": message}
        )
        key = int(uid) if uid.isdigit() else hash(uid)
        if len(_ram_memory[key]) > MAX_MEMORY:
            _ram_memory[key] = _ram_memory[key][-MAX_MEMORY:]
        history = list(_ram_memory[key])
    
    # Cascade: Claude → Groq → Gemini → static
    reply = None
    provider_used = "none"
    
    for provider_name, provider_fn in [
        ("Claude", _claude),
        ("Groq", _groq),
        ("Gemini", _gemini),
    ]:
        reply = provider_fn(system, history)
        if reply:
            provider_used = provider_name
            logger.info(f"[Brain] {provider_name} response for user {uid} ({len(reply)} chars)")
            break
    
    if not reply:
        logger.warning("[Brain] All providers failed, using static fallback")
        if persona == "jarvis":
            reply = "I regret to inform you, sir. Mis servicios de IA no están disponibles en este momento."
        else:
            user_name = "amigo"
            reply = (
                f"Ey {user_name}, ahora mismo no puedo conectar con mis servicios de IA.\n\n"
                "Mientras tanto puedes usar:\n"
                "/estado - Estado del sistema\n"
                "/nueva_campana <presupuesto> <nombre>\n"
                "/metricas <id>\n"
                "/reporte_diario"
            )
    
    # Limpiar markdown que LLMs generan
    reply = reply.replace("**", "").replace("__", "")
    
    # Guardar respuesta
    if PERSISTENT:
        save_message(uid, "assistant", reply, persona)
    else:
        key = int(uid) if uid.isdigit() else hash(uid)
        _ram_memory[key].append({"role": "assistant", "content": reply})
        if len(_ram_memory[key]) > MAX_MEMORY:
            _ram_memory[key] = _ram_memory[key][-MAX_MEMORY:]
    
    return reply


def think(
    user_id: int,
    user_name: str,
    user_message: str,
    meta_status: str = "desconocido",
    campaigns_data: str = "",
    action_context: str = "",
) -> str:
    """Legacy interface — redirige a chat() para compatibilidad."""
    return chat(
        user_id=str(user_id),
        message=user_message,
        persona="s180",
        meta_status=meta_status,
        campaigns_data=campaigns_data,
        action_context=action_context,
    )


def clear_user_memory(user_id, persona: str = None):
    """Limpia el historial de conversación de un usuario."""
    if PERSISTENT:
        _clear_mem(str(user_id), persona)
    else:
        key = int(user_id) if str(user_id).isdigit() else hash(str(user_id))
        if key in _ram_memory:
            del _ram_memory[key]
