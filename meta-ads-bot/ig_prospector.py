"""
ig_prospector.py — Sistema 180
Prospector de Instagram usando instagrapi (emula app móvil)
Funciona con CUALQUIER cuenta, no solo Business.
Anti-ban: delays aleatorios, límites diarios, sesión persistente.
"""
import os, json, random, asyncio, logging, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Config anti-ban ────────────────────────────────────────────────────────
DELAY_MIN = 25        # segundos entre DMs
DELAY_MAX = 65
DAILY_LIMIT = 30      # máx DMs por día (semana 1: 20-30)
SESSION_FILE = 'ig_session.json'

# ── Búsqueda por hashtags (negocios locales en España) ────────────────────
TARGET_HASHTAGS = [
    # Alhaurín y alrededores
    'peluqueriaalhaurin', 'barberiaalhaurin', 'alhaurinelgrande', 'alhaurin',
    'peluqueriacoin', 'barberiamijas', 'peluqueriafuengirola',
    # Málaga provincia
    'peluqueriamalaga', 'barberiamalaga', 'esteticamalaga',
    'centrodeesteticamalaga', 'salondebellezmálaga',
    'peluqueriatorremolinos', 'barberiabenalmadena',
    # Genéricos España
    'peluqueriasespaña', 'barberiasespaña', 'negociolocal',
]

# ── Mensajes fallback personalizados por tipo ─────────────────────────────
FALLBACK_DM = {
    'peluqueria': (
        "Vi tu peluquería y me surgió una duda — ¿cuántos clientes pierdes "
        "por no contestar fuera de horario? Tengo algo que puede ayudarte."
    ),
    'barberia': (
        "¿Cuántas veces te llaman para cita y no puedes contestar? "
        "Hay una forma de no perder ninguna consulta."
    ),
    'estetica': (
        "Tus fotos están muy bien. ¿Tienes citas entrando solas por Instagram? "
        "Se puede automatizar sin complicaciones."
    ),
    'default': (
        "Vi tu negocio — ¿a cuántos clientes pierdes porque no contestas a tiempo? "
        "Tengo una solución sencilla para negocios como el tuyo."
    ),
}


def detect_type(username: str, bio: str = '') -> str:
    text = (username + bio).lower()
    if any(w in text for w in ['barberia', 'barber', 'barbershop', 'barbero']):
        return 'barberia'
    if any(w in text for w in ['estetica', 'beauty', 'spa', 'uñas', 'nail', 'laser']):
        return 'estetica'
    if any(w in text for w in ['peluqueria', 'peluquer', 'salon', 'hair', 'stylist']):
        return 'peluqueria'
    return 'default'


def build_message(username: str, bio: str = '', name: str = '') -> str:
    """
    Genera DM personalizado.
    Prioridad: Meta LLaMA (Groq) → Claude Haiku → Gemini → Fallback
    """
    tipo = detect_type(username, bio)
    prompt_system = (
        "Eres un vendedor consultivo para negocios locales en España. "
        "Escribes DMs de Instagram: 2-3 líneas máximo, naturales, sin spam, "
        "sin emojis de relleno, sin 'Hola equipo'. "
        "Termina con una pregunta abierta breve."
    )
    prompt_user = (
        f"Negocio: @{username} ({tipo})\n"
        f"Bio: {bio[:100] if bio else 'sin bio'}\n"
        "Escribe el DM. Solo el texto, nada más."
    )

    # 1. Meta LLaMA 3 vía Groq (gratis, rápido)
    groq_key = os.getenv('GROQ_API_KEY', '')
    if groq_key:
        try:
            r = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'},
                json={
                    'model': 'llama-3.1-8b-instant',
                    'messages': [
                        {'role': 'system', 'content': prompt_system},
                        {'role': 'user', 'content': prompt_user},
                    ],
                    'max_tokens': 120,
                    'temperature': 0.8,
                },
                timeout=10,
            )
            text = r.json()['choices'][0]['message']['content'].strip()
            logger.info('DM generado con Meta LLaMA (Groq)')
            return text
        except Exception as e:
            logger.warning(f'Groq/LLaMA falló: {e}')

    # 2. Claude Haiku (backup)
    if os.getenv('ANTHROPIC_API_KEY', ''):
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            msg = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=120,
                system=prompt_system,
                messages=[{'role': 'user', 'content': prompt_user}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            logger.warning(f'Claude falló: {e}')

    # 3. Gemini (backup)
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    if gemini_key:
        try:
            r = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}',
                json={'contents': [{'parts': [{'text': prompt_system + '\n\n' + prompt_user}]}],
                      'generationConfig': {'maxOutputTokens': 120, 'temperature': 0.8}},
                timeout=10,
            )
            return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            logger.warning(f'Gemini falló: {e}')

    # 4. Fallback hardcoded
    return FALLBACK_DM.get(tipo, FALLBACK_DM['default'])


class IGProspector:
    def __init__(self):
        self.cl = None
        self._sent_today = 0
        self._sent_file = 'ig_sent.json'
        self._sent_ids = self._load_sent()
        self._challenge_username = None  # pendiente verificación
        self._challenge_password = None

    def _load_sent(self) -> set:
        if os.path.exists(self._sent_file):
            try:
                with open(self._sent_file) as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    def _save_sent(self, user_id: str):
        self._sent_ids.add(user_id)
        with open(self._sent_file, 'w') as f:
            json.dump(list(self._sent_ids), f)

    def login(self, username: str, password: str) -> dict:
        """Login con sesión persistente. Retorna dict con status y mensaje."""
        from instagrapi import Client
        from instagrapi.exceptions import (
            LoginRequired, ChallengeRequired, TwoFactorRequired
        )

        self.cl = Client()
        self.cl.delay_range = [2, 5]
        # Simular dispositivo Android para evitar detección
        self.cl.set_device({
            "app_version": "269.0.0.18.75",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "OnePlus",
            "device": "ONEPLUS A3003",
            "model": "OnePlus3",
            "cpu": "qcom",
            "version_code": "314665256",
        })

        # Intentar restaurar sesión
        if os.path.exists(SESSION_FILE):
            try:
                self.cl.load_settings(SESSION_FILE)
                self.cl.login(username, password)
                self.cl.get_timeline_feed()
                logger.info('Sesión restaurada desde archivo')
                return {'ok': True, 'status': 'logged_in'}
            except LoginRequired:
                logger.info('Sesión expirada, relogueando...')
            except Exception as e:
                logger.info(f'Error restaurando sesión: {e}')

        # Login fresco
        try:
            self.cl.login(username, password)
            self.cl.dump_settings(SESSION_FILE)
            logger.info('Login exitoso, sesión guardada')
            return {'ok': True, 'status': 'logged_in'}

        except ChallengeRequired:
            # Instagram pide código de verificación (SMS o email)
            self._challenge_username = username
            self._challenge_password = password
            try:
                challenge_url = self.cl.last_json.get('challenge', {}).get('url', '')
                self.cl.challenge_resolve(self.cl.last_json)
            except Exception as e2:
                logger.warning(f'challenge_resolve error: {e2}')
            logger.warning('Challenge requerida — esperando código del usuario')
            return {'ok': False, 'status': 'challenge', 'msg': 'Instagram pide verificación'}

        except TwoFactorRequired:
            self._challenge_username = username
            self._challenge_password = password
            logger.warning('2FA requerida')
            return {'ok': False, 'status': '2fa', 'msg': 'Instagram pide código 2FA'}

        except Exception as e:
            logger.error(f'Login fallido: {e}')
            return {'ok': False, 'status': 'error', 'msg': str(e)}

    def submit_code(self, code: str) -> dict:
        """Envía el código de verificación recibido por SMS/email/2FA."""
        if not self.cl:
            return {'ok': False, 'msg': 'Primero usa /ig_login usuario contraseña'}
        try:
            # Intentar como challenge code
            self.cl.challenge_resolve_simple(code)
            # Verificar con timeline
            self.cl.get_timeline_feed()
            self.cl.dump_settings(SESSION_FILE)
            self._challenge_username = None
            logger.info('Challenge resuelta correctamente')
            return {'ok': True, 'msg': 'Verificado. Instagram conectado.'}
        except Exception as e1:
            # Intentar como 2FA TOTP
            try:
                username = self._challenge_username or ''
                password = self._challenge_password or ''
                self.cl.login(username, password, verification_code=code)
                self.cl.dump_settings(SESSION_FILE)
                self._challenge_username = None
                return {'ok': True, 'msg': 'Verificado (2FA). Instagram conectado.'}
            except Exception as e2:
                logger.error(f'submit_code error: {e1} | {e2}')
                return {'ok': False, 'msg': f'Código incorrecto o expirado. Error: {str(e1)[:80]}'}

    def search_targets_by_hashtag(self, hashtag: str, limit: int = 20) -> list[dict]:
        """Busca negocios por hashtag y extrae sus perfiles."""
        targets = []
        try:
            hashtag_clean = hashtag.lstrip('#')
            medias = self.cl.hashtag_medias_recent(hashtag_clean, amount=limit)
            seen = set()
            for media in medias:
                uid = str(media.user.pk)
                if uid in seen or uid in self._sent_ids:
                    continue
                seen.add(uid)
                try:
                    user = self.cl.user_info(uid)
                    # Filtrar: solo negocios (tienen bio, seguidores entre 100-50k)
                    if (user.biography and
                            100 < user.follower_count < 50000 and
                            not user.is_private):
                        targets.append({
                            'id': uid,
                            'username': user.username,
                            'name': user.full_name,
                            'bio': user.biography[:200],
                            'followers': user.follower_count,
                        })
                        if len(targets) >= limit:
                            break
                except Exception:
                    pass
            logger.info(f'#{hashtag_clean}: {len(targets)} targets encontrados')
        except Exception as e:
            logger.error(f'Error buscando #{hashtag}: {e}')
        return targets

    def search_competitors_followers(self, competitor_username: str, limit: int = 30) -> list[dict]:
        """Obtiene seguidores de un competidor como targets."""
        targets = []
        try:
            user_id = self.cl.user_id_from_username(competitor_username)
            followers = self.cl.user_followers(user_id, amount=limit)
            for uid, user in followers.items():
                uid_str = str(uid)
                if uid_str in self._sent_ids:
                    continue
                if not user.is_private and user.follower_count < 50000:
                    targets.append({
                        'id': uid_str,
                        'username': user.username,
                        'name': user.full_name,
                        'bio': '',
                        'followers': user.follower_count,
                    })
        except Exception as e:
            logger.error(f'Error con seguidores de @{competitor_username}: {e}')
        return targets

    async def run_campaign(self, targets: list[dict], notify_fn=None, limit: int = DAILY_LIMIT) -> dict:
        """Envía DMs a la lista de targets con delays anti-ban."""
        results = {'sent': 0, 'skipped': 0, 'failed': 0, 'errors': []}
        to_send = [t for t in targets if t['id'] not in self._sent_ids][:limit]

        if notify_fn:
            await notify_fn(f"🚀 Prospección iniciada: {len(to_send)} objetivos")

        for i, target in enumerate(to_send):
            uid = target['id']
            username = target['username']
            mensaje = build_message(username, target.get('bio', ''), target.get('name', ''))

            try:
                if i > 0:
                    delay = random.randint(DELAY_MIN, DELAY_MAX)
                    logger.info(f'Esperando {delay}s...')
                    await asyncio.sleep(delay)

                self.cl.direct_send(mensaje, [int(uid)])
                self._save_sent(uid)
                results['sent'] += 1
                logger.info(f'[{i+1}/{len(to_send)}] ✅ DM enviado a @{username}')

                if notify_fn and results['sent'] % 5 == 0:
                    await notify_fn(f"📨 {results['sent']} DMs enviados...")

            except Exception as e:
                err = str(e)
                results['failed'] += 1
                results['errors'].append(f'@{username}: {err[:80]}')
                logger.warning(f'❌ @{username}: {err[:80]}')

                # Si hay rate limit, parar
                if 'spam' in err.lower() or 'block' in err.lower() or 'challenge' in err.lower():
                    logger.error('🚨 Instagram bloqueó el envío. Parando campaña.')
                    if notify_fn:
                        await notify_fn('⚠️ Instagram detectó actividad. Pausa automática de 1 hora.')
                    break

        if notify_fn:
            await notify_fn(
                f"✅ Campaña finalizada\n"
                f"📨 Enviados: {results['sent']}\n"
                f"❌ Fallidos: {results['failed']}\n"
                f"⏭ Ya contactados: {results['skipped']}"
            )
        return results


# Instancia global
_prospector: IGProspector | None = None

def get_prospector() -> IGProspector:
    global _prospector
    if _prospector is None:
        _prospector = IGProspector()
    return _prospector
