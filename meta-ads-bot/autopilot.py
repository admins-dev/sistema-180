"""
autopilot.py — Sistema 180
SDR Bot completamente autónomo.
Busca negocios → detecta dolor → envía DM → gestiona respuestas → cierra cita.
Sin intervención humana.
"""
import os, json, asyncio, logging, random, re, time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import requests

try:
    from shared_state import atomic_write_json, safe_read_json
    ATOMIC = True
except ImportError:
    ATOMIC = False

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_KEY  = os.getenv('GEMINI_API_KEY', '')
GROQ_KEY    = os.getenv('GROQ_API_KEY', '')
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY', '')
MAPS_KEY    = os.getenv('GOOGLE_MAPS_KEY', '')
BOT_TOKEN   = os.getenv('TELEGRAM_BOT_TOKEN', '')
NOTIFY_CHAT = os.getenv('TELEGRAM_ALLOWED_USER_IDS', '').split(',')[0]

# Validate critical keys
if not MAPS_KEY:
    logger.warning('[Autopilot] GOOGLE_MAPS_KEY not set — lead search disabled')
if not any([GROQ_KEY, ANTHROPIC_KEY, GEMINI_KEY]):
    logger.warning('[Autopilot] No AI API keys set — using fallback messages')

# Archivos de estado
STATE_FILE     = 'autopilot_state.json'
SENT_FILE      = 'ig_sent.json'
PIPELINE_FILE  = 'pipeline.json'   # leads que respondieron

# Límites anti-ban
DAILY_DM_LIMIT   = 25   # semana 1: conservador
DELAY_MIN        = 30
DELAY_MAX        = 70

# Zonas a prospectar (empezamos por las más cercanas)
ZONES_PRIORITY = [
    ('Alhaurín el Grande', 36.6453, -4.6984),
    ('Coín',               36.6603, -4.7597),
    ('Mijas',              36.5965, -4.6378),
    ('Alhaurín de la Torre', 36.6667, -4.5667),
    ('Fuengirola',         36.5403, -4.6250),
    ('Benalmádena',        36.5997, -4.5169),
    ('Torremolinos',       36.6219, -4.4997),
    ('Málaga',             36.7213, -4.4214),
]

BUSINESS_TARGETS = [
    'peluquería', 'barbería', 'centro estética',
    'clínica dental', 'fisioterapia', 'centro belleza',
    'academia', 'taller mecánico', 'restaurante',
]

# ── Telegram notify ────────────────────────────────────────────────────────
def telegram_notify(msg: str):
    if not BOT_TOKEN or not NOTIFY_CHAT:
        return
    try:
        # Sanitize: never log the bot token
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': NOTIFY_CHAT, 'text': msg, 'parse_mode': 'HTML'},
            timeout=5,
        )
    except Exception as e:
        logger.warning(f'[Autopilot] Telegram notify error: {type(e).__name__}')


# ── Google Maps Lead Search ────────────────────────────────────────────────
# Circuit breaker for Google Maps
_maps_failures = 0
_maps_backoff_until = 0

def find_leads_without_web(city: str, lat: float, lng: float,
                            business_type: str, limit: int = 15) -> list[dict]:
    global _maps_failures, _maps_backoff_until
    if not MAPS_KEY:
        logger.warning('[Autopilot] Maps key not set')
        return []
    if time.time() < _maps_backoff_until:
        logger.info('[Autopilot] Maps in backoff, skipping')
        return []
    """Busca negocios SIN WEB — son los más calientes."""
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    results = []
    try:
        r = requests.get(url, params={
            'query': f'{business_type} {city}',
            'location': f'{lat},{lng}',
            'radius': 8000,
            'language': 'es',
            'key': MAPS_KEY,
        }, timeout=10)
        places = r.json().get('results', [])[:limit*2]

        for place in places:
            pid = place.get('place_id', '')
            # Obtener detalles
            det = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params={
                'place_id': pid,
                'fields': 'name,website,formatted_phone_number,rating,user_ratings_total',
                'key': MAPS_KEY,
            }, timeout=8).json().get('result', {})
            time.sleep(0.2)

            has_web = bool(det.get('website', ''))
            rating  = det.get('rating', 5.0)
            reviews = det.get('user_ratings_total', 0)

            # Priorizar: sin web O rating bajo
            score = 0
            if not has_web:        score += 3
            if rating < 4.2:       score += 2
            if reviews < 20:       score += 1

            if score < 1:
                continue  # tienen todo, no los necesitan

            # Detectar Instagram en su web
            ig_handle = ''
            if has_web:
                try:
                    html = requests.get(det['website'], timeout=6,
                                        headers={'User-Agent': 'Mozilla/5.0'}).text
                    m = re.search(r'instagram\.com/([a-zA-Z0-9_.]{2,30})', html)
                    if m and m.group(1) not in ('p', 'reel', 'explore', 'sharer'):
                        ig_handle = f'@{m.group(1)}'
                except Exception:
                    pass

            pain = []
            if not has_web:   pain.append('sin página web')
            if rating < 4.0:  pain.append('reseñas bajas')
            if reviews < 10:  pain.append('poca visibilidad en Maps')

            results.append({
                'name':     det.get('name', place.get('name', '')),
                'city':     city,
                'type':     business_type,
                'has_web':  has_web,
                'website':  det.get('website', ''),
                'phone':    det.get('formatted_phone_number', ''),
                'rating':   rating,
                'reviews':  reviews,
                'pain':     ', '.join(pain) or 'no contestan clientes',
                'instagram': ig_handle,
                'score':    score,
                'place_id': pid,
            })

            if len(results) >= limit:
                break

    except Exception as e:
        _maps_failures += 1
        if _maps_failures >= 3:
            _maps_backoff_until = time.time() + 300  # 5 min backoff
            logger.error(f'[Autopilot] Maps circuit breaker: {_maps_failures} failures, backing off 5min')
            _maps_failures = 0
        logger.error(f'Maps error en {city}: {e}')

    return sorted(results, key=lambda x: x['score'], reverse=True)


# ── Gemini: Generar DM de venta ────────────────────────────────────────────
def generate_sales_dm(lead: dict) -> str:
    """
    DM de venta personalizado.
    Prioridad: Meta LLaMA (Groq) → Claude Haiku → Gemini → Fallback
    """
    pain     = lead.get('pain', '')
    name     = lead.get('name', 'tu negocio')
    city     = lead.get('city', '')
    has_web  = lead.get('has_web', True)
    GROQ_KEY      = os.getenv('GROQ_API_KEY', '')
    ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY', '')

    angle = "no tienen web y pierden clientes que los buscan en Google" if not has_web \
            else f"el problema es: {pain}"
    prompt_text = (
        f"Eres el SDR de una agencia digital en España (Sistema 180). "
        f"Vendes: 1) Webs profesionales 297€ pago único 2) Bot IA WhatsApp 300€/mes "
        f"que atiende clientes y cierra citas automáticamente.\n\n"
        f"Escribe un DM de Instagram para este negocio. "
        f"REGLAS ESTRICTAS: máximo 3 líneas, directo, natural, sin emojis de relleno, "
        f"sin 'Hola equipo de', menciona su problema concreto, "
        f"termina con pregunta que invite a responder.\n\n"
        f"Negocio: {name}\nCiudad: {city}\nTipo: {lead.get('type','')}\n"
        f"Problema detectado: {angle}\n\n"
        f"Solo el mensaje. Nada más."
    )

    # 1. Meta LLaMA 3 vía Groq (gratis, rápido)
    if GROQ_KEY:
        try:
            r = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f'Bearer {GROQ_KEY}', 'Content-Type': 'application/json'},
                json={
                    'model': 'llama-3.1-8b-instant',
                    'messages': [{'role': 'user', 'content': prompt_text}],
                    'max_tokens': 130,
                    'temperature': 0.75,
                },
                timeout=10,
            )
            return r.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.warning(f'Groq/LLaMA error: {e}')

    # 2. Claude Haiku (backup)
    if ANTHROPIC_KEY:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_KEY)
            msg = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=130,
                messages=[{'role': 'user', 'content': prompt_text}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            logger.warning(f'Claude error: {e}')

    # 3. Gemini (backup)
    if GEMINI_KEY:
        try:
            r = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}',
                json={'contents': [{'parts': [{'text': prompt_text}]}],
                      'generationConfig': {'maxOutputTokens': 130, 'temperature': 0.75}},
                timeout=12,
            )
            return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            logger.warning(f'Gemini error: {e}')

    # 4. Fallback
    return (
        f"Vi {name} en Maps — ¿cuántos clientes pierdes por no contestar a tiempo? "
        f"Tengo algo que puede ayudarte. ¿Hablamos?"
    )


# ── Gemini: Gestionar respuestas entrantes ─────────────────────────────────
def handle_response_with_ai(prospect_name: str, message: str) -> str:
    """Genera respuesta automática a un lead que contestó."""
    if not GEMINI_KEY:
        return (
            "¡Perfecto! Te explico en 5 minutos cómo funciona. "
            "¿Cuándo tienes un momento para una llamada rápida? "
            "Puedo mostrarte exactamente cómo quedaría tu negocio."
        )
    try:
        prompt = (
            f"Eres el closer de Sistema 180, agencia digital en España.\n"
            f"Vendes: Web 297€ + Bot WhatsApp 300€/mes que atiende clientes 24h.\n"
            f"Un prospecto ({prospect_name}) te respondió: '{message}'\n\n"
            f"Escribe la respuesta perfecta para:\n"
            f"1. Mantener la conversación viva\n"
            f"2. Resolver su objeción si la hay\n"
            f"3. Intentar cerrar una llamada de 5 minutos\n\n"
            f"Máximo 3 líneas. Natural. Sin emojis de relleno. Solo el texto."
        )
        r = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}',
            json={'contents': [{'parts': [{'text': prompt}]}],
                  'generationConfig': {'maxOutputTokens': 150, 'temperature': 0.6}},
            timeout=12,
        )
        return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        logger.error(f'Gemini response error: {e}')
        return "¡Perfecto! ¿Cuándo tienes 5 minutos para una llamada? Te lo muestro en directo."


# ── State management ───────────────────────────────────────────────────────
def load_state() -> dict:
    default = {
        'running': False,
        'total_sent': 0,
        'total_leads': 0,
        'started_at': None,
        'last_run': None,
        'zone_index': 0,
        'type_index': 0,
        'daily_sent': 0,
        'daily_reset': str(datetime.now().date()),
    }
    if ATOMIC:
        return safe_read_json(STATE_FILE, default)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default
    return default

def save_state(state: dict):
    if ATOMIC:
        atomic_write_json(STATE_FILE, state)
    else:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)

def load_sent() -> set:
    if ATOMIC:
        data = safe_read_json(SENT_FILE, [])
        return set(data) if isinstance(data, list) else set()
    if os.path.exists(SENT_FILE):
        try:
            with open(SENT_FILE) as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()

def mark_sent(ig_handle: str, lead: dict):
    sent = load_sent()
    sent.add(ig_handle)
    if ATOMIC:
        atomic_write_json(SENT_FILE, list(sent))
    else:
        with open(SENT_FILE, 'w') as f:
            json.dump(list(sent), f)
    # Añadir al pipeline (atomic)
    if ATOMIC:
        pipeline = safe_read_json(PIPELINE_FILE, [])
    else:
        pipeline = []
        if os.path.exists(PIPELINE_FILE):
            try:
                with open(PIPELINE_FILE) as f:
                    pipeline = json.load(f)
            except (json.JSONDecodeError, IOError):
                pipeline = []
    pipeline.append({**lead, 'sent_at': datetime.now().isoformat(), 'status': 'sent'})
    if ATOMIC:
        atomic_write_json(PIPELINE_FILE, pipeline)
    else:
        with open(PIPELINE_FILE, 'w') as f:
            json.dump(pipeline, f, indent=2, ensure_ascii=False)


# ── Main autonomous loop ───────────────────────────────────────────────────
async def run_autopilot_cycle(prospector_instance, notify_fn=None):
    """Un ciclo completo de prospección autónoma."""
    state = load_state()

    # Reset diario
    today = str(datetime.now().date())
    if state.get('daily_reset') != today:
        state['daily_sent'] = 0
        state['daily_reset'] = today
        save_state(state)

    if state['daily_sent'] >= DAILY_DM_LIMIT:
        msg = f"⏸ Límite diario alcanzado ({DAILY_DM_LIMIT} DMs). Reanudo mañana."
        logger.info(msg)
        if notify_fn:
            await notify_fn(msg)
        return

    sent_ids = load_sent()
    remaining = DAILY_DM_LIMIT - state['daily_sent']

    # Seleccionar zona y tipo rotativos
    zone = ZONES_PRIORITY[state['zone_index'] % len(ZONES_PRIORITY)]
    btype = BUSINESS_TARGETS[state['type_index'] % len(BUSINESS_TARGETS)]
    city, lat, lng = zone

    if notify_fn:
        await notify_fn(f"🔍 Buscando {btype}s en {city}...")

    # Buscar leads con Google Maps
    leads = find_leads_without_web(city, lat, lng, btype, limit=remaining + 5)
    leads = [l for l in leads if l.get('instagram', '') and
             l['instagram'] not in sent_ids][:remaining]

    if not leads:
        # Avanzar zona/tipo si no hay leads
        state['zone_index'] += 1
        save_state(state)
        if notify_fn:
            await notify_fn(f"ℹ️ Sin nuevos leads en {city} para {btype}. Probando otra zona.")
        return

    sent_count = 0
    for i, lead in enumerate(leads):
        ig = lead['instagram']
        if not ig or ig in sent_ids:
            continue

        # Generar mensaje
        mensaje = generate_sales_dm(lead)

        # Delay anti-ban
        if i > 0:
            delay = random.randint(DELAY_MIN, DELAY_MAX)
            await asyncio.sleep(delay)

        # Intentar obtener IG ID real y enviar
        try:
            # Primero intentar via instagrapi si está logueado
            if prospector_instance and prospector_instance.cl:
                username = ig.lstrip('@')
                try:
                    uid = prospector_instance.cl.user_id_from_username(username)
                    prospector_instance.cl.direct_send(mensaje, [int(uid)])
                    mark_sent(ig, lead)
                    sent_count += 1
                    state['total_sent'] += 1
                    state['daily_sent'] += 1
                    logger.info(f"✅ DM enviado a {ig}: {lead['name']}")
                except Exception as e:
                    if 'spam' in str(e).lower() or 'block' in str(e).lower():
                        telegram_notify("🚨 Instagram detectó spam. Pausa automática 2h.")
                        await asyncio.sleep(7200)
                        break
                    logger.warning(f"❌ {ig}: {e}")
        except Exception as e:
            logger.error(f'Error enviando a {ig}: {e}')

    # Rotar zona y tipo
    state['zone_index'] = (state['zone_index'] + 1) % len(ZONES_PRIORITY)
    state['type_index'] = (state['type_index'] + 1) % len(BUSINESS_TARGETS)
    state['last_run'] = datetime.now().isoformat()
    save_state(state)

    summary = (
        f"✅ Ciclo completado\n"
        f"📨 Enviados: {sent_count}\n"
        f"📊 Hoy: {state['daily_sent']}/{DAILY_DM_LIMIT}\n"
        f"📈 Total histórico: {state['total_sent']}"
    )
    if notify_fn:
        await notify_fn(summary)
    telegram_notify(summary)


async def autopilot_scheduler(prospector_instance):
    """Loop infinito que ejecuta ciclos de prospección cada 2 horas."""
    state = load_state()
    state['running'] = True
    state['started_at'] = datetime.now().isoformat()
    save_state(state)

    telegram_notify("🤖 Autopilot iniciado — Sistema 180 prospectando solo")

    while True:
        state = load_state()
        if not state.get('running'):
            telegram_notify("⏹ Autopilot detenido.")
            break
        try:
            await run_autopilot_cycle(prospector_instance)
        except Exception as e:
            logger.error(f'Error en ciclo: {e}')
            telegram_notify(f"⚠️ Error en ciclo: {str(e)[:100]}")

        # Esperar 2 horas entre ciclos (dentro de horario laboral)
        hour = datetime.now().hour
        if hour < 9 or hour >= 20:
            # Fuera de horario — esperar hasta las 9am
            now = datetime.now()
            next_run = now.replace(hour=9, minute=0, second=0)
            if hour >= 20:
                next_run += timedelta(days=1)
            wait_secs = (next_run - now).total_seconds()
            telegram_notify(f"😴 Fuera de horario. Reanudo a las 9:00 ({int(wait_secs/3600)}h)")
            await asyncio.sleep(wait_secs)
        else:
            await asyncio.sleep(7200)  # 2 horas entre ciclos


def get_pipeline_stats() -> dict:
    if ATOMIC:
        pipeline = safe_read_json(PIPELINE_FILE, [])
    elif os.path.exists(PIPELINE_FILE):
        try:
            with open(PIPELINE_FILE) as f:
                pipeline = json.load(f)
        except (json.JSONDecodeError, IOError):
            pipeline = []
    else:
        pipeline = []
    return {
        'total': len(pipeline),
        'sent': sum(1 for p in pipeline if p.get('status') == 'sent'),
        'responded': sum(1 for p in pipeline if p.get('status') == 'responded'),
        'closed': sum(1 for p in pipeline if p.get('status') == 'closed'),
    }
