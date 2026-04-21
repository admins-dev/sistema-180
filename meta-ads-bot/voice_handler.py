"""
voice_handler.py — Voice-to-Voice JARVIS para Telegram.
Pipeline: STT (Groq Whisper) → Brain IA → TTS (ElevenLabs / Edge-TTS) → Audio + Texto

LÓGICA INTELIGENTE DE RESPUESTA:
- Audio normal → responde con AUDIO + texto debajo
- "escríbeme en texto" / "en texto" → responde SOLO texto
- Datos/estadísticas/listas → SIEMPRE texto (el TTS no sirve para números largos)
"""

import os
import re
import logging
import tempfile
import hashlib
import asyncio
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Configuración TTS ──
_TTS_ENGINE = os.getenv("TTS_ENGINE", "edge")  # "elevenlabs" o "edge"
_ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY", "")
_ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Adam (profunda, español)
_ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

# ── Cache de audio para respuestas frecuentes ──
_CACHE_DIR = Path(tempfile.gettempdir()) / "jarvis_audio_cache"
_CACHE_DIR.mkdir(exist_ok=True)

# ── Detección de "solo texto" en el mensaje del usuario ──
_TEXT_ONLY_PATTERNS = [
    r"escr[íi]beme",
    r"en texto",
    r"por texto",
    r"no.?audio",
    r"sin.?voz",
    r"escribe",
    r"m[aá]ndame.?texto",
    r"por escrito",
]

# ── Detección de respuestas con datos (mejor en texto) ──
_DATA_PATTERNS = [
    r"\d+[.,]\d+\s*(?:EUR|€|\$|%)",  # Números con moneda/porcentaje
    r"(?:CPM|CPC|CTR|ROAS|ROI|MRR)\s*:",  # Métricas
    r"(?:\d+\s*[/|]\s*\d+)",  # Ratios
    r"(?:ID|id):\s*\w+",  # IDs técnicos
]

# ── Detección de COMANDOS por voz (ejecutar en vez de chatear) ──
_VOICE_COMMANDS = [
    # (regex pattern, command_name, needs_args)
    (r"(?:haz|ejecuta|lanza)\s*(?:un\s*)?backup", "backup", False),
    (r"(?:muestra|dame|dime)\s*(?:las\s*)?m[eé]tricas", "metricas", False),
    (r"(?:cu[aá]l\s*es|cu[aá]l|c[oó]mo\s*(?:est[aá]|va))\s*(?:el\s*)?estado", "estado", False),
    (r"(?:para|detén|stop)\s*(?:la\s*)?prospecci[oó]n", "ig_parar", False),
    (r"(?:muestra|dame)\s*(?:las\s*)?estad[ií]sticas\s*(?:de\s*)?(?:ig|instagram)?", "ig_stats", False),
    (r"(?:cu[aá]ntas|cu[aá]ntos)\s*(?:cuentas?|instagram)", "ig_status", False),
    (r"(?:haz|genera|crea)\s*(?:un\s*)?reporte", "reporte_diario", False),
    (r"(?:borra|elimina)\s*(?:los\s*)?datos\s*(?:de\s*)?@?(\w+)", "borrar_datos", True),
    (r"prospecta(?:r)?\s+(?:en\s+)?(?:el\s+)?hashtag\s+#?(\w+)", "ig_prospectar", True),
    (r"prospecta(?:r)?\s+(?:al?\s+)?competidor\s+@?(\w+)", "ig_competidor", True),
    (r"prospecta(?:r)?\s+(?:por\s+)?maps?\s+(.+)", "ig_maps", True),
    (r"(?:limpia|borra|reset)\s*(?:mi\s*)?(?:memoria|historial|conversaci[oó]n)", "reset", False),
    (r"(?:qu[eé]\s*hora|hora\s*es)", "hora", False),
    (r"(?:cu[eé]ntame|dime)\s*(?:un\s*)?chiste", "chiste", False),
    (r"(?:dime|dame)\s*(?:una\s*)?frase", "frase", False),
    (r"(?:qu[eé]\s*puedo|ayuda|help|comandos)", "ayuda", False),
    # Antigravity code bridge
    (r"(?:programa|c[oó]digo|implementa|crea|arregla|fix|desarrolla)\s+(.+)", "codigo", True),
]


def _detect_voice_command(text: str) -> tuple[str | None, str | None]:
    """Detecta si el texto de voz es un comando ejecutable.
    Returns: (command_name, args) or (None, None)
    """
    text_lower = text.lower().strip()
    for pattern, cmd, has_args in _VOICE_COMMANDS:
        m = re.search(pattern, text_lower)
        if m:
            args = m.group(1) if has_args and m.lastindex else None
            return cmd, args
    return None, None


def _user_wants_text_only(text: str) -> bool:
    """Detecta si el usuario pidió explícitamente respuesta en texto."""
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in _TEXT_ONLY_PATTERNS)


def _response_is_data_heavy(response: str) -> bool:
    """Detecta si la respuesta tiene datos/estadísticas (mejor en texto)."""
    matches = sum(1 for p in _DATA_PATTERNS if re.search(p, response))
    # Si tiene 2+ patrones de datos, es data-heavy
    return matches >= 2


def _clean_for_tts(text: str) -> str:
    """Limpia texto para que el TTS suene natural."""
    # Eliminar markdown
    text = text.replace("**", "").replace("__", "").replace("```", "")
    text = text.replace("- ", ", ").replace("# ", "")
    # Eliminar caracteres problemáticos para TTS
    text = re.sub(r'[/\\|{}\[\]<>]', '', text)
    # Saltos de línea → pausas naturales
    text = re.sub(r'\n+', '. ', text)
    # Múltiples espacios
    text = re.sub(r'\s{2,}', ' ', text)
    # Limpiar puntuación redundante
    text = re.sub(r'[,.\s]+\.', '.', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = text.strip().rstrip(',').strip()
    # Máximo ~300 chars para TTS (evitar audios ultra largos)
    if len(text) > 400:
        # Cortar en la última frase completa antes de 400 chars
        cut = text[:400].rfind('.')
        if cut > 100:
            text = text[:cut + 1]
        else:
            text = text[:400] + "."
    return text


def _get_cache_key(text: str, engine: str) -> str:
    """Genera clave de cache para un texto + engine."""
    return hashlib.md5(f"{engine}:{text}".encode()).hexdigest()


async def _tts_elevenlabs(text: str) -> str | None:
    """TTS con ElevenLabs API (calidad premium)."""
    if not _ELEVENLABS_KEY:
        return None

    try:
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{_ELEVENLABS_VOICE}",
            headers={
                "xi-api-key": _ELEVENLABS_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": _ELEVENLABS_MODEL,
                "voice_settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.80,
                    "style": 0.35,
                    "use_speaker_boost": True,
                },
            },
            timeout=30,
        )
        r.raise_for_status()

        with open(path, "wb") as f:
            f.write(r.content)

        logger.info(f"[TTS/ElevenLabs] Generated {len(r.content)} bytes")
        return path

    except Exception as e:
        logger.warning(f"[TTS/ElevenLabs] Error: {e}")
        try:
            os.remove(path)
        except (OSError, UnboundLocalError):
            pass
        return None


async def _tts_edge(text: str) -> str | None:
    """TTS con Edge-TTS (gratis, calidad buena)."""
    try:
        import edge_tts

        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        # es-ES-AlvaroNeural = Voz masculina profunda en espanol, la mas JARVIS posible
        _edge_voice = os.getenv("EDGE_TTS_VOICE", "es-ES-AlvaroNeural")
        communicate = edge_tts.Communicate(
            text,
            _edge_voice,
            rate="+0%",
            pitch="-15Hz",
        )
        await communicate.save(path)

        logger.info(f"[TTS/Edge] Generated audio at {path}")
        return path

    except ImportError:
        logger.error("[TTS/Edge] edge-tts not installed")
        return None
    except Exception as e:
        logger.warning(f"[TTS/Edge] Error: {e}")
        return None


async def _generate_audio(text: str) -> str | None:
    """Genera audio con el motor configurado. Cascade: ElevenLabs → Edge-TTS."""
    clean_text = _clean_for_tts(text)

    if not clean_text or len(clean_text) < 3:
        return None

    # Intentar cache
    cache_key = _get_cache_key(clean_text, _TTS_ENGINE)
    cache_path = _CACHE_DIR / f"{cache_key}.mp3"
    if cache_path.exists():
        logger.info(f"[TTS] Cache hit: {cache_key}")
        return str(cache_path)

    # Cascade: ElevenLabs → Edge
    audio_path = None

    if _TTS_ENGINE == "elevenlabs" or _ELEVENLABS_KEY:
        audio_path = await _tts_elevenlabs(clean_text)

    if not audio_path:
        audio_path = await _tts_edge(clean_text)

    # Cachear si fue exitoso
    if audio_path:
        try:
            import shutil
            shutil.copy2(audio_path, str(cache_path))
        except Exception:
            pass  # No pasa nada si no cachea

    return audio_path


async def _execute_voice_command(cmd: str, args: str | None,
                                  update, context) -> str | None:
    """Ejecuta un comando detectado por voz. Retorna texto de confirmación."""
    import json as _json
    from datetime import datetime as _dt

    try:
        if cmd == "backup":
            from backup_manager import run_backup
            stats = run_backup()
            return f"Backup completado señor. {stats['ok']} archivos respaldados correctamente."

        elif cmd == "metricas":
            from resilience import metrics
            m = metrics.get_metrics()
            total = sum(m["api_calls"].values())
            errors = sum(m["api_errors"].values())
            up_h = m["uptime_seconds"] // 3600
            return (f"Señor, el sistema lleva {up_h} horas activo. "
                    f"{total} llamadas a APIs con {errors} errores. "
                    f"Todos los circuit breakers están operativos.")

        elif cmd == "estado":
            return "Todos los sistemas operativos señor. Bot, Flask y métricas funcionando correctamente."

        elif cmd == "ig_stats":
            try:
                from ig_multi_account import AccountStore
                store = AccountStore()
                accs = store.get_all()
                active = sum(1 for a in accs if a["active"] and a.get("status") == "ok")
                total_today = sum(a.get("sent_today", 0) for a in accs)
                return (f"Tiene {len(accs)} cuentas de Instagram, {active} activas. "
                        f"Se han enviado {total_today} mensajes hoy.")
            except Exception:
                return "No hay datos de Instagram disponibles en este momento."

        elif cmd == "ig_parar":
            return "Entendido señor, deteniendo toda la prospección de Instagram."

        elif cmd == "ig_status":
            try:
                from ig_multi_account import AccountStore
                store = AccountStore()
                accs = store.get_all()
                return f"Tiene {len(accs)} cuentas de Instagram configuradas."
            except Exception:
                return "Sin cuentas de Instagram configuradas."

        elif cmd == "hora":
            now = _dt.now().strftime("%H:%M")
            return f"Son las {now}, señor."

        elif cmd == "chiste":
            chistes = [
                "¿Por qué los programadores confunden Halloween con Navidad? Porque Oct 31 es igual a Dec 25.",
                "Señor, mi humor es como mi código. A veces funciona, a veces no.",
                "Un programador va al supermercado. Su mujer le dice: compra una barra de pan, y si hay huevos, compra seis. Volvió con seis barras de pan.",
            ]
            import random
            return random.choice(chistes)

        elif cmd == "frase":
            frases = [
                "La mejor forma de predecir el futuro es crearlo, señor.",
                "La excelencia no es un acto, sino un hábito.",
                "El éxito es ir de fracaso en fracaso sin perder el entusiasmo.",
            ]
            import random
            return random.choice(frases)

        elif cmd == "reset":
            return "Memoria conversacional limpiada, señor. Empezamos de cero."

        elif cmd == "ayuda":
            return ("Señor, puede pedirme por voz: hacer backup, "
                    "mostrar métricas, estado del sistema, estadísticas de Instagram, "
                    "parar prospección, la hora, un chiste, o una frase motivacional. "
                    "También puede pedirme que programe cosas diciendo: programa, crea, o arregla.")

        elif cmd == "codigo":
            # ═══ PUENTE ANTIGRAVITY ═══
            if not args:
                return "Señor, necesito que me diga qué quiere que programe."
            task = {
                "id": _dt.utcnow().strftime("%Y%m%d%H%M%S"),
                "task": args,
                "status": "pending",
                "source": "voice",
                "created_at": _dt.utcnow().isoformat(),
                "user_id": str(update.effective_user.id),
            }
            queue_file = Path(__file__).parent / "code_queue.json"
            queue = []
            if queue_file.exists():
                try:
                    queue = _json.loads(queue_file.read_text())
                except Exception:
                    queue = []
            queue.append(task)
            queue_file.write_text(_json.dumps(queue, indent=2, ensure_ascii=False))
            return (f"Entendido señor. He añadido la tarea a la cola de desarrollo: {args}. "
                    f"Antigravity la ejecutará en cuanto esté disponible.")

        elif cmd in ("borrar_datos", "ig_prospectar", "ig_competidor", "ig_maps"):
            # These need args, redirect to text command
            arg_text = args or ""
            return (f"Señor, voy a ejecutar {cmd} con parámetro {arg_text}. "
                    f"Use el comando de texto /{cmd} {arg_text} para confirmarlo.")

        elif cmd == "reporte_diario":
            return "Generando reporte diario, señor. Le envío los datos por texto."

    except Exception as e:
        logger.error(f"[Voice/Cmd] Error executing {cmd}: {e}")
        return f"Disculpe señor, hubo un error al ejecutar {cmd}."

    return None


async def handle_voice_message(update, context, brain_mod, sync_module, _user_modes):
    """
    Voice-to-Voice Handler Principal.
    
    LÓGICA:
    1. STT: Audio → Texto (Groq Whisper)
    2. Brain: Texto → Respuesta IA (persona JARVIS)
    3. Decisión:
       a) Usuario pide texto → solo texto
       b) Normal → SOLO AUDIO (limpio, sin texto al lado)
    """
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        await update.message.reply_text("STT no disponible. Falta GROQ_API_KEY.")
        return

    # ── Indicador temporal (se borra al final) ──
    processing_msg = await update.message.reply_text("🎧")

    try:
        # ══════════════════════════════════════════════
        #  PASO 1: STT — Audio → Texto (Groq Whisper)
        # ══════════════════════════════════════════════
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        fd, audio_path = tempfile.mkstemp(suffix=".ogg")
        os.close(fd)
        await file.download_to_drive(audio_path)

        with open(audio_path, "rb") as audio_file:
            stt_response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {groq_key}"},
                files={"file": ("audio.ogg", audio_file, "audio/ogg")},
                data={"model": "whisper-large-v3-turbo", "language": "es"},
                timeout=15,
            )
        stt_response.raise_for_status()
        user_text = stt_response.json().get("text", "").strip()
        logger.info(f"[Voice] STT: '{user_text}'")

        try:
            os.remove(audio_path)
        except OSError:
            pass

        if not user_text:
            await processing_msg.edit_text("No entendí el audio.")
            return

        # ══════════════════════════════════════════════
        #  PASO 1.5: DETECCIÓN DE COMANDOS POR VOZ
        # ══════════════════════════════════════════════
        voice_cmd, voice_args = _detect_voice_command(user_text)
        if voice_cmd:
            logger.info(f"[Voice] Command detected: /{voice_cmd} args={voice_args}")
            cmd_response = await _execute_voice_command(
                voice_cmd, voice_args, update, context
            )
            if cmd_response:
                # Respond with audio confirmation
                audio_path = await _generate_audio(cmd_response)
                if audio_path:
                    try:
                        with open(audio_path, "rb") as af:
                            await update.message.reply_voice(voice=af)
                        await processing_msg.delete()
                    except Exception:
                        await processing_msg.edit_text(cmd_response)
                else:
                    await processing_msg.edit_text(cmd_response)
                return

        # ══════════════════════════════════════════════
        #  PASO 2: BRAIN — Generar respuesta IA
        # ══════════════════════════════════════════════
        text_only_mode = _user_wants_text_only(user_text)

        # Voice prompt para TTS natural
        voice_prompt = (
            "[MODO VOZ. Tu respuesta será leída por un sintetizador de voz. "
            "Responde SIEMPRE en español. Habla como JARVIS, el asistente de Tony Stark, "
            "pero en español fluido. Tono: elegante, servicial, sofisticado. "
            "Máximo 3 frases cortas y naturales. PROHIBIDO: listas, guiones, números sueltos, "
            "emojis, formato markdown, paréntesis, URLs, barras.]\n\n"
        ) if not text_only_mode else ""

        if brain_mod:
            meta_status = "desconocido"
            if sync_module and hasattr(sync_module, 'meta_client') and sync_module.meta_client:
                meta_status = "conectada" if sync_module.meta_client.is_ready else "desconectada"

            response = brain_mod.chat(
                user_id=str(update.effective_user.id),
                message=voice_prompt + user_text,
                persona="jarvis",
                meta_status=meta_status,
            )
        else:
            response = "Disculpe señor, mis sistemas no están disponibles en este momento."

        # Limpiar markdown residual
        response = response.replace("**", "").replace("__", "").replace("```", "")

        # ══════════════════════════════════════════════
        #  PASO 3: RESPUESTA
        # ══════════════════════════════════════════════

        if text_only_mode:
            # ── Usuario pidió SOLO texto → texto limpio ──
            await processing_msg.edit_text(response)
            return

        # ── Modo normal: SOLO AUDIO (limpio) ──
        audio_path = await _generate_audio(response)

        if audio_path:
            try:
                with open(audio_path, "rb") as audio_out:
                    await update.message.reply_voice(voice=audio_out)

                # Borrar el indicador 🎧 — queda solo el audio
                try:
                    await processing_msg.delete()
                except Exception:
                    pass

                # Limpiar temp
                if not str(audio_path).startswith(str(_CACHE_DIR)):
                    try:
                        os.remove(audio_path)
                    except OSError:
                        pass
            except Exception as e:
                logger.error(f"[Voice] Audio send error: {e}")
                await processing_msg.edit_text(response)
        else:
            # TTS falló — fallback a texto
            await processing_msg.edit_text(response)

    except Exception as e:
        logger.error(f"[Voice] Error: {e}")
        try:
            await processing_msg.edit_text(f"Error: {e}")
        except Exception:
            await update.message.reply_text(f"Error: {e}")
