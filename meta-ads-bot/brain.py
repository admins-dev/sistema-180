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

# ── Importar doctrina del Cerebro S180 ──
try:
    from doctrina_s180 import (
        SYSTEM_PROMPT_JARVIS, SYSTEM_PROMPT_S180,
        detect_module, detect_operator_state, detect_natural_entry,
        PROTOCOLO_REGULACION_RAPIDA, PROTOCOLO_DIARIO_CAJA,
        PROTOCOLO_CAJA_URGENTE, REGLA_MADRE_CAJA,
    )
    DOCTRINA_LOADED = True
    logger.info("[Brain] Doctrina S180 cargada correctamente")
except ImportError:
    DOCTRINA_LOADED = False
    logger.warning("[Brain] doctrina_s180 no disponible — usando prompts base")

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

# Personas: importadas de doctrina_s180.py si disponible, fallback inline
if DOCTRINA_LOADED:
    PERSONA_S180 = SYSTEM_PROMPT_S180
else:
    PERSONA_S180 = """Eres S180, asistente de marketing digital de Sistema 180.
    Doctrina: Verdad, Foco, Caja, Ejecución limpia.
    Español de España. Directo. Máximo 150 palabras.
    {context}
    {action_context}"""


if DOCTRINA_LOADED:
    PERSONA_JARVIS = SYSTEM_PROMPT_JARVIS
else:
    PERSONA_JARVIS = """Eres JARVIS, capa ejecutora del cerebro de Sistema 180.
    Doctrina: Verdad, Foco, Caja, Ejecución limpia.
    Voz: premium, afilada, humor seco, cero humo. Máximo 3-5 frases.
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
    Interfaz unificada de chat con doctrina CEREBRO S180 inyectada.
    
    Flujo:
    1. Detectar estado del operador (Doc 02)
    2. Detectar módulo doctrinal (Doc 00 triggers)
    3. Inyectar contexto de módulo en el system prompt
    4. Cascade: Claude Haiku → Groq LLaMA 3.3 → Gemini → static fallback
    """
    uid = str(user_id)
    
    # ── 1. Seleccionar persona base ──
    persona_template = PERSONA_JARVIS if persona == "jarvis" else PERSONA_S180
    
    # ── 2. Detectar estado del operador (Doc 02) ──
    operator_guard = ""
    if DOCTRINA_LOADED:
        op_state = detect_operator_state(message)
        if op_state == "bajo":
            operator_guard = (
                "\n\nALERTA OPERADOR ESTADO BAJO DETECTADO.\n"
                "El operador muestra señales de estado bajo (ansiedad, agotamiento, impulso).\n"
                "PROTOCOLO OBLIGATORIO: FRENA. No empujes. No ejecutes. Primero regula.\n"
                f"Aplica esto:\n{PROTOCOLO_REGULACION_RAPIDA}\n"
                "Solo después de regular, pregunta cuál es la próxima acción de caja concreta."
            )
    
    # ── 3. Detectar módulo doctrinal (Doc 00 triggers) ──
    module_context = ""
    if DOCTRINA_LOADED:
        active_module = detect_module(message)
        if active_module:
            if "Caja" in active_module:
                module_context = (
                    f"\n\nMÓDULO ACTIVO: {active_module}\n"
                    f"Regla madre: {REGLA_MADRE_CAJA}\n"
                    f"Prioridades: 1.Cobro 2.Cierre 3.Seguimiento 4.Prospección 5.Percepción\n"
                    f"Protocolo diario:\n{PROTOCOLO_DIARIO_CAJA}"
                )
            elif "Operador" in active_module:
                module_context = (
                    f"\n\nMÓDULO ACTIVO: {active_module}\n"
                    f"El operador necesita regulación ANTES de decidir.\n"
                    f"Protocolo:\n{PROTOCOLO_REGULACION_RAPIDA}"
                )
            else:
                module_context = f"\n\nMÓDULO ACTIVO: {active_module}. Responde según doctrina de ese módulo."
    
    # ── 4. Construir system prompt con contexto ──
    context = _build_context(meta_status, campaigns_data)
    action_block = ""
    if action_context:
        action_block = f"\nACCIÓN RECIÉN EJECUTADA:\n{action_context}"
    
    system = persona_template.replace("{context}", context).replace("{action_context}", action_block)
    system += operator_guard + module_context
    
    # Si es modo voz, añadir instrucciones para TTS natural
    if voice:
        system += (
            "\n\nMODO VOZ ACTIVO: Tu respuesta será audio.\n"
            "Máximo 3 frases cortas. PROHIBIDO: listas, guiones, emojis, markdown, URLs.\n"
            "Habla fluido y natural."
        )
    
    # ── 5. Obtener historial ──
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
    
    # ── 6. Cascade: Claude → Groq → Gemini → static ──
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
            logger.info(f"[Brain] {provider_name} ({active_module if DOCTRINA_LOADED and active_module else 'general'}) for user {uid}")
            break
    
    if not reply:
        logger.warning("[Brain] All providers failed, using static fallback")
        if persona == "jarvis":
            reply = "Mis servicios no están disponibles ahora mismo, señor. Pero el sistema sigue operativo. Usa /estado para verificar."
        else:
            reply = (
                "Ahora mismo no puedo conectar con IA.\n\n"
                "Comandos disponibles:\n"
                "/caja - Protocolo de caja\n"
                "/regulacion - Regulación rápida\n"
                "/precios - Escalera de precios\n"
                "/estado - Estado del sistema"
            )
    
    # Limpiar markdown que LLMs generan
    reply = reply.replace("**", "").replace("__", "")
    
    # ── 7. Guardar respuesta ──
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
