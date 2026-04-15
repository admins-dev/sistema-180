"""
ig_multi_account.py — Sistema 180
Multi-cuenta Instagram con rotación automática.
Pipeline: Google Maps → encontrar IG del negocio → Claude DM → enviar rotando cuentas.
Anti-ban: límites por cuenta, delays aleatorios, sesiones persistentes.
"""
import os, json, re, time, random, logging, requests
from datetime import date, datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
ACCOUNTS_FILE = Path("ig_accounts.json")
MAPS_KEY      = os.getenv("GOOGLE_MAPS_KEY", "")
GROQ_KEY      = os.getenv("GROQ_API_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_KEY    = os.getenv("GEMINI_API_KEY", "")

# Límites anti-ban por semana (se configura por cuenta)
DEFAULT_DAILY_LIMIT = 25   # semana 1
MAX_DAILY_LIMIT     = 150  # modo crucero


# ══════════════════════════════════════════════════════════════════════════════
# AccountStore — persiste cuentas en JSON
# ══════════════════════════════════════════════════════════════════════════════

class AccountStore:
    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        if ACCOUNTS_FILE.exists():
            try:
                return json.loads(ACCOUNTS_FILE.read_text())
            except Exception:
                pass
        return {"accounts": []}

    def _save(self):
        ACCOUNTS_FILE.write_text(json.dumps(self._data, indent=2, ensure_ascii=False))

    def add_account(self, username: str, password: str, daily_limit: int = DEFAULT_DAILY_LIMIT) -> bool:
        """Añade cuenta. Retorna False si ya existe."""
        if any(a["username"] == username for a in self._data["accounts"]):
            return False
        self._data["accounts"].append({
            "username":    username,
            "password":    password,
            "session_file": f"ig_session_{username}.json",
            "daily_limit": daily_limit,
            "sent_today":  0,
            "sent_total":  0,
            "sent_ids":    [],
            "last_reset":  str(date.today()),
            "active":      True,
            "status":      "pending_login",  # pending_login | ok | challenge | error | banned
            "last_error":  None,
            "added_at":    datetime.utcnow().isoformat(),
        })
        self._save()
        return True

    def remove_account(self, username: str) -> bool:
        before = len(self._data["accounts"])
        self._data["accounts"] = [a for a in self._data["accounts"] if a["username"] != username]
        if len(self._data["accounts"]) < before:
            self._save()
            return True
        return False

    def get_all(self) -> list[dict]:
        return self._data["accounts"]

    def get(self, username: str) -> dict | None:
        return next((a for a in self._data["accounts"] if a["username"] == username), None)

    def update(self, username: str, **kwargs):
        for acc in self._data["accounts"]:
            if acc["username"] == username:
                acc.update(kwargs)
                self._save()
                return

    def reset_daily_if_needed(self):
        """Resetea contadores diarios a las 00:00."""
        today = str(date.today())
        for acc in self._data["accounts"]:
            if acc.get("last_reset") != today:
                acc["sent_today"] = 0
                acc["last_reset"] = today
        self._save()

    def best_account(self) -> dict | None:
        """Devuelve la cuenta activa con menos DMs enviados hoy."""
        self.reset_daily_if_needed()
        candidates = [
            a for a in self._data["accounts"]
            if a["active"]
            and a["status"] in ("ok", "pending_login")
            and a["sent_today"] < a["daily_limit"]
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda a: a["sent_today"])

    def mark_sent(self, username: str, target_id: str):
        for acc in self._data["accounts"]:
            if acc["username"] == username:
                acc["sent_today"] += 1
                acc["sent_total"] += 1
                if target_id not in acc["sent_ids"]:
                    acc["sent_ids"].append(target_id)
        self._save()


# Singleton
_store = AccountStore()


def get_store() -> AccountStore:
    return _store


# ══════════════════════════════════════════════════════════════════════════════
# IGSession — wrapper instagrapi por cuenta
# ══════════════════════════════════════════════════════════════════════════════

class IGSession:
    """Gestiona el cliente instagrapi de una sola cuenta."""

    def __init__(self, account: dict):
        self.acc      = account
        self.username = account["username"]
        self.password = account["password"]
        self.session_file = account["session_file"]
        self.cl = None
        self._challenge_pending = False

    def _make_client(self):
        from instagrapi import Client
        cl = Client()
        cl.delay_range = [3, 8]
        cl.set_device({
            "app_version":    "269.0.0.18.75",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi":            "480dpi",
            "resolution":     "1080x1920",
            "manufacturer":   "Samsung",
            "device":         "SM-G973F",
            "model":          "galaxy_s10",
            "cpu":            "exynos9820",
            "version_code":   "314665256",
        })
        return cl

    def login(self) -> dict:
        from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired
        self.cl = self._make_client()
        sf = Path(self.session_file)

        # Restaurar sesión guardada
        if sf.exists():
            try:
                self.cl.load_settings(str(sf))
                self.cl.login(self.username, self.password)
                self.cl.get_timeline_feed()
                _store.update(self.username, status="ok", last_error=None)
                logger.info(f"[{self.username}] Sesión restaurada")
                return {"ok": True, "status": "logged_in"}
            except LoginRequired:
                logger.info(f"[{self.username}] Sesión expirada, relogueando")
            except Exception as e:
                logger.warning(f"[{self.username}] Error restaurando sesión: {e}")

        # Login fresco
        try:
            self.cl.login(self.username, self.password)
            self.cl.dump_settings(str(sf))
            _store.update(self.username, status="ok", last_error=None)
            logger.info(f"[{self.username}] Login exitoso")
            return {"ok": True, "status": "logged_in"}

        except ChallengeRequired:
            self._challenge_pending = True
            try:
                self.cl.challenge_resolve(self.cl.last_json)
            except Exception:
                pass
            _store.update(self.username, status="challenge")
            return {"ok": False, "status": "challenge", "msg": f"@{self.username}: Instagram pide verificación"}

        except TwoFactorRequired:
            self._challenge_pending = True
            _store.update(self.username, status="challenge")
            return {"ok": False, "status": "2fa", "msg": f"@{self.username}: Instagram pide código 2FA"}

        except Exception as e:
            _store.update(self.username, status="error", last_error=str(e)[:200])
            return {"ok": False, "status": "error", "msg": str(e)[:200]}

    def submit_code(self, code: str) -> dict:
        if not self.cl:
            return {"ok": False, "msg": "Cuenta no inicializada"}
        try:
            self.cl.challenge_resolve_simple(code)
            self.cl.get_timeline_feed()
            self.cl.dump_settings(self.session_file)
            _store.update(self.username, status="ok")
            self._challenge_pending = False
            return {"ok": True, "msg": f"@{self.username} verificado correctamente"}
        except Exception as e1:
            try:
                self.cl.login(self.username, self.password, verification_code=code)
                self.cl.dump_settings(self.session_file)
                _store.update(self.username, status="ok")
                return {"ok": True, "msg": f"@{self.username} verificado (2FA)"}
            except Exception as e2:
                return {"ok": False, "msg": f"Código incorrecto: {str(e1)[:80]}"}

    def send_dm(self, user_id: str, text: str) -> bool:
        if not self.cl:
            res = self.login()
            if not res["ok"]:
                return False
        try:
            self.cl.direct_send(text, [int(user_id)])
            _store.mark_sent(self.username, user_id)
            logger.info(f"[{self.username}] DM enviado a {user_id}")
            return True
        except Exception as e:
            err = str(e).lower()
            if "spam" in err or "block" in err or "restrict" in err:
                _store.update(self.username, status="banned", last_error=str(e)[:200])
                logger.error(f"[{self.username}] BANNED: {e}")
            else:
                _store.update(self.username, last_error=str(e)[:200])
                logger.error(f"[{self.username}] DM error: {e}")
            return False

    def search_by_keyword(self, query: str, limit: int = 15) -> list[dict]:
        """Busca usuarios de Instagram por palabra clave (nombre negocio)."""
        if not self.cl:
            res = self.login()
            if not res["ok"]:
                return []
        results = []
        try:
            users = self.cl.search_users(query)
            for u in users[:limit]:
                try:
                    info = self.cl.user_info(u.pk)
                    if (info.biography and
                            50 < info.follower_count < 100_000 and
                            not info.is_private):
                        results.append({
                            "id":        str(info.pk),
                            "username":  info.username,
                            "name":      info.full_name,
                            "bio":       info.biography[:200],
                            "followers": info.follower_count,
                        })
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"[{self.username}] search_users error: {e}")
        return results


# Pool de sesiones activas en memoria
_sessions: dict[str, IGSession] = {}

def get_session(username: str) -> IGSession | None:
    acc = _store.get(username)
    if not acc:
        return None
    if username not in _sessions:
        _sessions[username] = IGSession(acc)
    return _sessions[username]

def get_best_session() -> IGSession | None:
    """Devuelve la sesión de la cuenta óptima (rotación automática)."""
    acc = _store.best_account()
    if not acc:
        return None
    sess = get_session(acc["username"])
    if sess and not sess.cl:
        res = sess.login()
        if not res["ok"]:
            _store.update(acc["username"], status=res.get("status", "error"))
            return None
    return sess


# ══════════════════════════════════════════════════════════════════════════════
# Instagram Handle Discovery — Google Maps → IG
# ══════════════════════════════════════════════════════════════════════════════

def extract_ig_from_website(url: str) -> str | None:
    """Scrapea la web del negocio buscando su link de Instagram."""
    if not url:
        return None
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        # Buscar links directos a instagram.com/HANDLE
        patterns = [
            r'instagram\.com/([A-Za-z0-9_\.]{2,30})(?:/|\?|"|\'|\s|$)',
            r'@([A-Za-z0-9_\.]{2,30})',  # fallback: @handle en texto
        ]
        for pat in patterns:
            matches = re.findall(pat, r.text, re.IGNORECASE)
            for m in matches:
                clean = m.rstrip("/").lower()
                # Filtrar palabras genéricas
                if clean not in {"p", "reel", "reels", "stories", "explore", "share",
                                  "accounts", "login", "signup", "oauth", "api"}:
                    return clean
    except Exception as e:
        logger.debug(f"extract_ig_from_website({url}): {e}")
    return None


def find_ig_handle(business_name: str, city: str, website: str = "") -> str | None:
    """
    Estrategia en cascada para encontrar el handle de Instagram de un negocio:
    1. Scrape del website si tiene
    2. Búsqueda en Instagram por nombre + ciudad
    Retorna el handle sin @ o None si no encuentra.
    """
    # 1. Desde website
    if website:
        handle = extract_ig_from_website(website)
        if handle:
            logger.info(f"Handle encontrado en web: @{handle}")
            return handle

    # 2. Búsqueda en IG (necesita sesión activa)
    sess = get_best_session()
    if sess:
        query = f"{business_name} {city}"
        results = sess.search_by_keyword(query, limit=5)
        if results:
            # Primer resultado con name similar
            best = results[0]
            logger.info(f"Handle encontrado por búsqueda: @{best['username']}")
            return best["username"]

    return None


# ══════════════════════════════════════════════════════════════════════════════
# DM Generator — Claude/Groq/Gemini cascade
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_DM = (
    "Eres un experto en ventas para negocios locales en España. "
    "Escribes DMs de Instagram cortos (2-3 líneas), naturales, sin spam, "
    "sin emojis de relleno. Sin 'Hola equipo'. "
    "Termina siempre con una pregunta abierta breve. Solo el texto del DM."
)

FALLBACKS = {
    "peluqueria": "Vi tu peluquería y tengo una pregunta — ¿cuántos clientes pierdes por no contestar fuera de horario? Hay algo que puede ayudarte.",
    "barberia":   "¿Cuántas llamadas para cita no puedes atender? Hay una forma sencilla de no perder ninguna.",
    "estetica":   "Tus fotos están muy bien. ¿Tienes citas entrando solas por Instagram? Se puede automatizar sin complicaciones.",
    "clinica":    "He visto tu clínica. ¿Cuántos pacientes pierdes por no contestar a tiempo? Tengo algo que puede ayudarte.",
    "default":    "Vi tu negocio — ¿cuántos clientes pierdes porque no contestas rápido? Tengo una solución sencilla.",
}

def _detect_type(name: str, bio: str = "") -> str:
    text = (name + bio).lower()
    for t, words in {
        "barberia":  ["barberia", "barber", "barbershop", "barbero"],
        "estetica":  ["estetica", "beauty", "spa", "uñas", "nail", "laser", "belleza"],
        "clinica":   ["clinica", "dental", "fisio", "medico", "salud"],
        "peluqueria": ["peluqueria", "peluquer", "salon", "hair", "stylist"],
    }.items():
        if any(w in text for w in words):
            return t
    return "default"

def generate_dm(business_name: str, ig_username: str = "", bio: str = "",
                city: str = "", tipo: str = "") -> str:
    """Genera DM personalizado con cascade: Groq → Claude → Gemini → fallback."""
    if not tipo:
        tipo = _detect_type(business_name + ig_username, bio)

    prompt = (
        f"Negocio: {business_name}"
        + (f" (@{ig_username})" if ig_username else "")
        + (f" en {city}" if city else "")
        + f"\nTipo: {tipo}"
        + (f"\nBio Instagram: {bio[:120]}" if bio else "")
        + "\nEscribe el DM:"
    )

    # 1. Groq/LLaMA (gratis, ultrarrápido)
    if GROQ_KEY:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": SYSTEM_DM},
                        {"role": "user",   "content": prompt},
                    ],
                    "max_tokens": 120, "temperature": 0.85,
                },
                timeout=10,
            )
            text = r.json()["choices"][0]["message"]["content"].strip()
            if text:
                return text
        except Exception as e:
            logger.warning(f"Groq falló: {e}")

    # 2. Claude Haiku
    if ANTHROPIC_KEY:
        try:
            from anthropic import Anthropic
            msg = Anthropic(api_key=ANTHROPIC_KEY).messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=120,
                system=SYSTEM_DM,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            logger.warning(f"Claude falló: {e}")

    # 3. Gemini Flash
    if GEMINI_KEY:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
                json={"contents": [{"parts": [{"text": SYSTEM_DM + "\n\n" + prompt}]}],
                      "generationConfig": {"maxOutputTokens": 120, "temperature": 0.85}},
                timeout=10,
            )
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            logger.warning(f"Gemini falló: {e}")

    return FALLBACKS.get(tipo, FALLBACKS["default"])


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL: Google Maps → Instagram DM
# ══════════════════════════════════════════════════════════════════════════════

def maps_to_ig_pipeline(
    city: str,
    business_type: str,
    lat: float,
    lng: float,
    radius: int = 5000,
    limit: int = 20,
    notify_fn=None,        # async callback: notify_fn(text) para Telegram
    dry_run: bool = False, # si True: genera DM pero no envía
) -> dict:
    """
    Pipeline completo:
    1. Google Maps → negocios de tipo `business_type` en `city`
    2. Por cada negocio: extrae Instagram (web scrape o búsqueda IG)
    3. Genera DM personalizado con Claude/Groq
    4. Envía DM rotando cuentas Instagram

    Retorna dict con stats: found, ig_found, sent, errors
    """
    from lead_factory import search_places, get_place_details

    stats = {"found": 0, "ig_found": 0, "sent": 0, "errors": 0, "skipped": 0}

    if not MAPS_KEY:
        return {**stats, "error": "GOOGLE_MAPS_KEY no configurada"}

    if notify_fn:
        import asyncio
        def _notify(msg):
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(notify_fn(msg))
            except Exception:
                pass
    else:
        _notify = lambda msg: None

    # 1. Google Maps
    places = search_places(f"{business_type} {city}", lat, lng, radius=radius)
    stats["found"] = len(places)
    _notify(f"📍 {len(places)} negocios encontrados en Maps para '{business_type}' en {city}")

    sent_count = 0
    for place in places[:limit]:
        if sent_count >= limit:
            break

        details = get_place_details(place["place_id"])
        name    = place["name"]
        website = details.get("website", "")

        # 2. Encontrar Instagram
        handle = find_ig_handle(name, city, website)
        if not handle:
            stats["skipped"] += 1
            logger.info(f"Sin IG: {name}")
            continue

        stats["ig_found"] += 1

        # Verificar si ya enviamos a este handle
        store = get_store()
        all_sent = {sid for acc in store.get_all() for sid in acc.get("sent_ids", [])}
        if handle in all_sent:
            stats["skipped"] += 1
            logger.info(f"Ya contactado: @{handle}")
            continue

        # 3. Generar DM
        dm_text = generate_dm(
            business_name=name,
            ig_username=handle,
            city=city,
        )

        _notify(
            f"🎯 *{name}*\n"
            f"@{handle} | {details.get('phone', 'sin tel')}\n"
            f"```\n{dm_text[:200]}\n```"
        )

        if dry_run:
            stats["sent"] += 1
            sent_count += 1
            continue

        # 4. Enviar con cuenta óptima
        sess = get_best_session()
        if not sess:
            _notify("⚠️ Todas las cuentas han alcanzado el límite diario.")
            break

        # Obtener user_id de IG (necesitamos el ID numérico)
        try:
            target_id = str(sess.cl.user_id_from_username(handle))
        except Exception as e:
            logger.error(f"user_id_from_username({handle}): {e}")
            stats["errors"] += 1
            continue

        ok = sess.send_dm(target_id, dm_text)
        if ok:
            stats["sent"] += 1
            sent_count += 1
            _notify(f"✅ DM enviado a @{handle} desde @{sess.username}")
        else:
            stats["errors"] += 1

        # Delay anti-ban entre envíos
        delay = random.uniform(30, 70)
        logger.info(f"Esperando {delay:.0f}s antes del siguiente DM...")
        time.sleep(delay)

    return stats


# ══════════════════════════════════════════════════════════════════════════════
# Stats
# ══════════════════════════════════════════════════════════════════════════════

def get_accounts_summary() -> str:
    """Resumen de todas las cuentas para Telegram."""
    _store.reset_daily_if_needed()
    accs = _store.get_all()
    if not accs:
        return "No hay cuentas registradas. Usa /ig_add_account usuario contraseña"

    STATUS_EMOJI = {
        "ok":            "✅",
        "pending_login": "🔄",
        "challenge":     "⚠️",
        "error":         "❌",
        "banned":        "🚫",
    }

    lines = [f"📱 *Instagram Accounts ({len(accs)} cuentas)*\n"]
    total_today = 0
    total_total = 0
    for a in accs:
        emoji  = STATUS_EMOJI.get(a["status"], "❓")
        today  = a["sent_today"]
        limit  = a["daily_limit"]
        total  = a["sent_total"]
        total_today += today
        total_total += total
        lines.append(
            f"{emoji} *@{a['username']}*\n"
            f"   Hoy: {today}/{limit} DMs | Total: {total}\n"
            f"   Estado: {a['status']}"
            + (f" — {a['last_error'][:60]}" if a.get("last_error") else "")
        )

    lines.append(f"\n📊 *Total hoy: {total_today} DMs enviados | {total_total} total*")
    return "\n".join(lines)
