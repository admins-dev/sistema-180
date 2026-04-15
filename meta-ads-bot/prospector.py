"""
prospector.py — Sistema 180
Auto-prospector de negocios locales vía Instagram DM
Sin Redis. Controlado desde Telegram.
"""
import os, time, random, logging, json, asyncio
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GRAPH = 'https://graph.facebook.com/v19.0'
TOKEN = os.getenv('META_ACCESS_TOKEN', '')
IG_ID = os.getenv('IG_USER_ID', os.getenv('META_IG_USER_ID', '17841409217534579'))
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# Anti-spam: delay entre mensajes
DELAY_MIN = 20   # segundos
DELAY_MAX = 50

SYSTEM_PROMPT = (
    "Eres experto en ventas para negocios locales en España. "
    "Escribes DMs de Instagram directos, naturales, sin spam. "
    "Máximo 2-3 líneas, sin emojis de relleno, sin 'Hola equipo de X'. "
    "Termina siempre con una pregunta abierta."
)

# ── Buscar IG ID por username (Business Discovery) ─────────────────────────
def get_ig_id_by_username(username: str) -> str | None:
    """Busca el Instagram IGSID de un usuario por su handle."""
    username = username.lstrip('@')
    try:
        r = requests.get(
            f'{GRAPH}/{IG_ID}',
            params={
                'fields': f'business_discovery.fields(id,username,name,followers_count)',
                'username': username,
                'access_token': TOKEN,
            },
            timeout=10,
        )
        data = r.json()
        if 'business_discovery' in data:
            bd = data['business_discovery']
            return bd.get('id')
        logger.warning(f'No business_discovery para @{username}: {data.get("error",{}).get("message","")}')
    except Exception as e:
        logger.error(f'Error buscando @{username}: {e}')
    return None


# ── Generar mensaje personalizado ──────────────────────────────────────────
def generate_message(negocio: dict) -> str:
    """Genera DM personalizado con Claude. Fallback a plantilla si no hay API key."""
    if not ANTHROPIC_KEY:
        return (
            f"Vi {negocio.get('name','tu negocio')} en Maps. "
            f"¿Cuántos clientes pierdes por no contestar a tiempo? "
            "Tenemos algo que puede ayudarte."
        )
    try:
        client = Anthropic(api_key=ANTHROPIC_KEY)
        prompt = (
            f"Negocio: {negocio.get('name', 'Negocio local')}\n"
            f"Tipo: {negocio.get('type', 'negocio local')}\n"
            f"Ciudad: {negocio.get('city', 'España')}\n"
            f"Problema observado: {negocio.get('pain', 'no responden rápido a clientes')}\n\n"
            "Escribe el DM. SOLO el mensaje, nada más."
        )
        msg = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=120,
            system=SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        logger.error(f'Claude error: {e}')
        return (
            f"Vi tu negocio en {negocio.get('city','tu ciudad')}. "
            "¿Cuántos clientes pierdes cuando no contestas a tiempo? "
            "Tenemos algo que puede ayudarte."
        )


# ── Enviar DM vía Meta Graph API ──────────────────────────────────────────
def send_dm(recipient_id: str, text: str) -> dict:
    """Envía DM por Instagram Graph API."""
    try:
        r = requests.post(
            f'{GRAPH}/{IG_ID}/messages',
            json={
                'recipient': {'id': recipient_id},
                'message': {'text': text},
            },
            params={'access_token': TOKEN},
            timeout=15,
        )
        data = r.json()
        if 'message_id' in data or 'id' in data:
            return {'success': True, 'id': data.get('message_id', data.get('id', ''))}
        return {'success': False, 'error': data.get('error', {}).get('message', str(data))}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ── Runner principal ────────────────────────────────────────────────────────
async def run_campaign(prospects: list[dict], notify_fn=None, daily_limit=30) -> dict:
    """
    Ejecuta una campaña de DMs.
    prospects: lista de dicts con keys: name, instagram, type, city, pain
    notify_fn: async callable(str) para enviar updates a Telegram
    daily_limit: máx mensajes por ejecución
    """
    results = {'sent': 0, 'failed': 0, 'skipped': 0, 'errors': []}
    total = min(len(prospects), daily_limit)

    if notify_fn:
        await notify_fn(f"🚀 Iniciando campaña: {total} prospectos")

    for i, negocio in enumerate(prospects[:total]):
        handle = negocio.get('instagram', '').strip()
        if not handle:
            results['skipped'] += 1
            continue

        # 1. Resolver username → IGSID
        ig_id = get_ig_id_by_username(handle)
        if not ig_id:
            results['skipped'] += 1
            logger.info(f'[{i+1}/{total}] @{handle} — no se pudo resolver ID')
            continue

        # 2. Generar mensaje
        mensaje = generate_message(negocio)

        # 3. Delay anti-spam (excepto el primero)
        if i > 0:
            delay = random.randint(DELAY_MIN, DELAY_MAX)
            logger.info(f'Esperando {delay}s antes de enviar...')
            await asyncio.sleep(delay)

        # 4. Enviar
        result = send_dm(ig_id, mensaje)

        if result['success']:
            results['sent'] += 1
            logger.info(f'[{i+1}/{total}] ✅ @{handle} — enviado')
            if notify_fn and results['sent'] % 5 == 0:
                await notify_fn(f"📨 {results['sent']} DMs enviados...")
        else:
            results['failed'] += 1
            results['errors'].append(f"@{handle}: {result['error']}")
            logger.warning(f'[{i+1}/{total}] ❌ @{handle} — {result["error"]}')

    if notify_fn:
        await notify_fn(
            f"✅ Campaña completada\n"
            f"📨 Enviados: {results['sent']}\n"
            f"❌ Fallidos: {results['failed']}\n"
            f"⏭ Omitidos: {results['skipped']}"
        )

    return results


# ── Lista de prospectos por defecto ────────────────────────────────────────
def load_prospects(path='prospects.json') -> list[dict]:
    """Carga prospectos desde JSON o devuelve lista de ejemplo."""
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []
