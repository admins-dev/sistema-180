"""
integrations.py — Sistema 180
Notion CRM + Slack control center.
Scalability: connection pooling, rate limiting, caching.
"""
import os, logging, html, requests, re, threading, time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

NOTION_TOKEN          = os.getenv("NOTION_TOKEN", "")
NOTION_DB_ID          = os.getenv("NOTION_CLIENTS_DB_ID", "")
NOTION_FACTURAS_DB    = os.getenv("NOTION_FACTURAS_DB_ID", "")
NOTION_GASTOS_DB      = os.getenv("NOTION_GASTOS_DB_ID", "")
NOTION_CONTRATOS_DB   = os.getenv("NOTION_CONTRATOS_DB_ID", "")
NOTION_CAJA_DB        = os.getenv("NOTION_CAJA_DB_ID", "")
NOTION_KPIS_DB        = os.getenv("NOTION_KPIS_DB_ID", "")
NOTION_AFILIADOS_DB   = os.getenv("NOTION_AFILIADOS_DB_ID", "")
NOTION_AGENTES_DB     = os.getenv("NOTION_AGENTES_DB_ID", "")
NOTION_PROVEEDORES_DB = os.getenv("NOTION_PROVEEDORES_DB_ID", "")
SLACK_TOKEN           = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL         = os.getenv("SLACK_CHANNEL_ID", "")
ELEVENLABS_API_KEY    = os.getenv("ELEVENLABS_API_KEY", "")

# Canal IDs por departamento — loaded from config file
import json as _json
from pathlib import Path as _Path

_slack_config = _Path(__file__).parent / "slack_channels.json"
if _slack_config.exists():
    SLACK_CHANNELS = _json.loads(_slack_config.read_text(encoding="utf-8"))
    logger.info(f"Slack channels loaded from {_slack_config} ({len(SLACK_CHANNELS)} channels)")
else:
    SLACK_CHANNELS = {}
    logger.warning("slack_channels.json not found — Slack channel routing disabled")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# ══════════════════════════════════════════════
# SCALABILITY: Connection Pool + Rate Limiter + Cache
# ══════════════════════════════════════════════

# HTTP Session pooling — reuses TCP connections (10x faster than raw requests)
_notion_session = requests.Session()
_notion_session.headers.update(NOTION_HEADERS)

_slack_session = requests.Session()
_slack_session.headers.update({"Authorization": f"Bearer {SLACK_TOKEN}"})

# Notion rate limiter — max 3 concurrent requests (Notion limit)
_notion_semaphore = threading.Semaphore(3)

# Import resilience layer
try:
    from resilience import cb_notion, cb_slack, metrics
except ImportError:
    cb_notion = cb_slack = None
    metrics = None

def _notion_post(url: str, json_data: dict = None, timeout: int = 10) -> requests.Response:
    """Rate-limited, pooled, circuit-broken Notion API call."""
    if cb_notion and not cb_notion.can_execute():
        raise requests.exceptions.ConnectionError("Notion circuit breaker OPEN")
    _notion_semaphore.acquire()
    t0 = time.time()
    try:
        r = _notion_session.post(url, json=json_data, timeout=timeout)
        if cb_notion:
            cb_notion.record_success()
        if metrics:
            metrics.record_api_call("notion", (time.time() - t0) * 1000, r.ok)
        return r
    except Exception as e:
        if cb_notion:
            cb_notion.record_failure()
        if metrics:
            metrics.record_api_call("notion", 0, False)
        raise
    finally:
        _notion_semaphore.release()

def _notion_patch(url: str, json_data: dict = None, timeout: int = 10) -> requests.Response:
    """Rate-limited, pooled, circuit-broken Notion API PATCH."""
    if cb_notion and not cb_notion.can_execute():
        raise requests.exceptions.ConnectionError("Notion circuit breaker OPEN")
    _notion_semaphore.acquire()
    t0 = time.time()
    try:
        r = _notion_session.patch(url, json=json_data, timeout=timeout)
        if cb_notion:
            cb_notion.record_success()
        if metrics:
            metrics.record_api_call("notion", (time.time() - t0) * 1000, r.ok)
        return r
    except Exception as e:
        if cb_notion:
            cb_notion.record_failure()
        if metrics:
            metrics.record_api_call("notion", 0, False)
        raise
    finally:
        _notion_semaphore.release()

# In-memory cache with TTL (avoids repeated API calls)
_cache: dict[str, tuple[float, any]] = {}
_cache_lock = threading.Lock()
CACHE_TTL = 300  # 5 minutes

def _cache_get(key: str):
    with _cache_lock:
        if key in _cache:
            ts, val = _cache[key]
            if time.time() - ts < CACHE_TTL:
                return val
            del _cache[key]
    return None

def _cache_set(key: str, val):
    with _cache_lock:
        _cache[key] = (time.time(), val)

def _cache_invalidate(prefix: str = ""):
    with _cache_lock:
        if prefix:
            keys = [k for k in _cache if k.startswith(prefix)]
            for k in keys:
                del _cache[k]
        else:
            _cache.clear()


# ══════════════════════════════════════════════
# NOTION — CRM de clientes
# ══════════════════════════════════════════════

def notion_create_client(name: str, service: str, price: float,
                          phone: str = "", email: str = "",
                          niche: str = "", notes: str = "") -> dict:
    """Crea una entrada en la base de datos de clientes de Notion."""
    # Sanitizar inputs
    name = html.escape(name[:100])
    service = html.escape(service[:100])
    niche = html.escape(niche[:200])
    notes = html.escape(notes[:500])
    phone = re.sub(r"[^0-9+\- ]", "", phone)[:20] if phone else ""
    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Nombre": {"title": [{"text": {"content": name}}]},
            "Servicio": {"select": {"name": service}},
            "Precio (€/mes)": {"number": price},
            "Teléfono": {"phone_number": phone},
            "Email": {"email": email if email else None},
            "Nicho": {"rich_text": [{"text": {"content": niche}}]},
            "Estado": {"select": {"name": "Activo"}},
            "Fecha Alta": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
            "Notas": {"rich_text": [{"text": {"content": notes}}]},
        }
    }
    # Limpiar campos vacíos
    if not email:
        del payload["properties"]["Email"]

    try:
        r = _notion_post("https://api.notion.com/v1/pages", payload)
        if r.ok:
            page_id = r.json().get("id", "")
            logger.info(f"Cliente '{name}' creado en Notion: {page_id}")
            _cache_invalidate("clients_")  # invalidate cache
            return {"ok": True, "page_id": page_id, "url": r.json().get("url", "")}
        logger.error(f"Notion error: {r.status_code} {r.text}")
        return {"ok": False, "error": r.text}
    except requests.exceptions.RequestException as e:
        logger.error(f"Notion connection error: {e}")
        return {"ok": False, "error": str(e)}


def notion_get_clients(status: str = "Activo") -> list[dict]:
    """Devuelve clientes filtrados por estado. Cached 5 min."""
    cache_key = f"clients_{status}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    payload = {
        "filter": {"property": "Estado", "select": {"equals": status}},
        "sorts": [{"property": "Fecha Alta", "direction": "descending"}]
    }
    try:
        r = _notion_post(f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query", payload)
        if not r.ok:
            logger.error(f"Notion query error: {r.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Notion connection error: {e}")
        return []
    clients = []
    for page in r.json().get("results", []):
        p = page["properties"]
        clients.append({
            "id":      page["id"],
            "nombre":  p.get("Nombre",{}).get("title",[{}])[0].get("plain_text",""),
            "servicio":p.get("Servicio",{}).get("select",{}).get("name",""),
            "precio":  p.get("Precio (€/mes)",{}).get("number",0),
            "estado":  p.get("Estado",{}).get("select",{}).get("name",""),
            "alta":    p.get("Fecha Alta",{}).get("date",{}).get("start",""),
        })
    _cache_set(cache_key, clients)
    return clients


def notion_update_client_status(page_id: str, status: str) -> bool:
    """Actualiza el estado de un cliente (Activo/Trial/Pausado/Baja)."""
    try:
        r = _notion_patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            {"properties": {"Estado": {"select": {"name": status}}}}
        )
        _cache_invalidate("clients_")  # invalidate cache
        return r.ok
    except requests.exceptions.RequestException as e:
        logger.error(f"Notion update error: {e}")
        return False


# ══════════════════════════════════════════════
# SLACK — Centro de control
# ══════════════════════════════════════════════

def slack_send(message: str, channel: str = None) -> bool:
    """Envía mensaje a Slack (connection-pooled)."""
    ch = channel or SLACK_CHANNEL
    try:
        r = _slack_session.post(
            "https://slack.com/api/chat.postMessage",
            json={"channel": ch, "text": message, "mrkdwn": True},
            timeout=10
        )
        return r.ok and r.json().get("ok", False)
    except requests.exceptions.RequestException as e:
        logger.error(f"Slack error: {e}")
        return False


def slack_notify_new_client(name: str, service: str, price: float, phone: str = "") -> bool:
    """Notifica en Slack cuando llega un cliente nuevo."""
    msg = (
        f"🟢 *Nuevo cliente activado*\n"
        f"👤 *Nombre:* {name}\n"
        f"📦 *Servicio:* {service}\n"
        f"💰 *Precio:* {price}€/mes\n"
        f"📱 *Teléfono:* {phone or 'pendiente'}\n"
        f"🕐 *Alta:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        f"_Onboarding automático iniciado_"
    )
    return slack_send(msg, channel=SLACK_CHANNELS["clientes_onboarding"])


def slack_notify_invoice(client_name: str, amount: float, invoice_url: str = "") -> bool:
    msg = (
        f"🧾 *Factura generada*\n"
        f"👤 {client_name} — *{amount}€*\n"
        f"{f'🔗 {invoice_url}' if invoice_url else ''}"
    )
    return slack_send(msg, channel=SLACK_CHANNELS["clientes_facturas"])


def slack_get_channels() -> list[dict]:
    """Lista canales del workspace."""
    r = _slack_session.get("https://slack.com/api/conversations.list",
                     headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
                     params={"limit": 50}, timeout=10)
    if not r.ok or not r.json().get("ok"):
        return []
    return [{"id": c["id"], "name": c["name"]} for c in r.json().get("channels", [])]


# ══════════════════════════════════════════════
# FLUJO COMPLETO — onboarding automático
# ══════════════════════════════════════════════

# ══════════════════════════════════════════════
# NOTION — 8 bases de datos ERP
# ══════════════════════════════════════════════

def notion_create_factura(cliente: str, concepto: str, importe: float, metodo: str = "Stripe") -> dict:
    """Crea factura en Notion."""
    from datetime import date, timedelta
    num = f"S180-{date.today().strftime('%Y%m')}-{str(hash(cliente+concepto))[-4:]}"
    payload = {
        "parent": {"database_id": NOTION_FACTURAS_DB},
        "properties": {
            "Número": {"title": [{"text": {"content": num}}]},
            "Cliente": {"rich_text": [{"text": {"content": cliente}}]},
            "Concepto": {"rich_text": [{"text": {"content": concepto}}]},
            "Importe (€)": {"number": importe},
            "IVA %": {"number": 0.21},
            "Estado": {"select": {"name": "Pendiente"}},
            "Método Pago": {"select": {"name": metodo}},
            "Fecha Emisión": {"date": {"start": date.today().isoformat()}},
            "Fecha Vencimiento": {"date": {"start": (date.today() + timedelta(days=30)).isoformat()}},
        }
    }
    r = _notion_post("https://api.notion.com/v1/pages", payload)
    return {"ok": r.ok, "id": r.json().get("id", ""), "url": r.json().get("url", "")} if r.ok else {"ok": False, "error": r.text}


def notion_create_gasto(proveedor: str, concepto: str, importe: float, categoria: str = "Operativo") -> dict:
    """Crea gasto en Notion."""
    from datetime import date
    payload = {
        "parent": {"database_id": NOTION_GASTOS_DB},
        "properties": {
            "Proveedor": {"rich_text": [{"text": {"content": proveedor}}]},
            "Concepto": {"rich_text": [{"text": {"content": concepto}}]},
            "Importe (€)": {"number": importe},
            "Categoría": {"select": {"name": categoria}},
            "Estado": {"select": {"name": "Pagado"}},
            "Fecha": {"date": {"start": date.today().isoformat()}},
        }
    }
    r = _notion_post("https://api.notion.com/v1/pages", payload)
    return {"ok": r.ok, "id": r.json().get("id", "")} if r.ok else {"ok": False, "error": r.text}


def notion_create_contrato(cliente: str, servicio: str, valor: float, duracion_meses: int = 12) -> dict:
    """Crea contrato en Notion. Estructura flexible para diferentes layouts de DB."""
    from datetime import date, timedelta

    # Intenta estructura con propiedades comunes
    payload = {
        "parent": {"database_id": NOTION_CONTRATOS_DB},
        "properties": {
            "Nombre": {"title": [{"text": {"content": f"{cliente} — {servicio[:50]}"}}]},
            "Cliente": {"rich_text": [{"text": {"content": cliente}}]},
            "Descripción": {"rich_text": [{"text": {"content": servicio}}]},
            "Monto": {"number": valor},
            "Duración": {"number": duracion_meses},
            "Fecha Inicio": {"date": {"start": date.today().isoformat()}},
            "Fecha Vencimiento": {"date": {"start": (date.today() + timedelta(days=duracion_meses*30)).isoformat()}},
            "Estado": {"select": {"name": "Activo"}},
        }
    }

    r = _notion_post("https://api.notion.com/v1/pages", payload)
    if r.ok:
        return {"ok": True, "id": r.json().get("id", "")}

    # Si falla, intenta con estructura más simple (solo propiedades básicas)
    logger.warning(f"Primera estructura falló. Intentando estructura alternativa: {r.text}")
    payload_alt = {
        "parent": {"database_id": NOTION_CONTRATOS_DB},
        "properties": {
            "Nombre": {"title": [{"text": {"content": f"{cliente} — {servicio[:50]}"}}]},
        }
    }
    r2 = _notion_post("https://api.notion.com/v1/pages", payload_alt)
    return {"ok": r2.ok, "id": r2.json().get("id", "")} if r2.ok else {"ok": False, "error": f"{r.text} | {r2.text}"}


def notion_get_caja_resumen() -> dict:
    """Obtiene resumen de caja de hoy."""
    payload = {"page_size": 100}
    r = _notion_post(f"https://api.notion.com/v1/databases/{NOTION_CAJA_DB}/query",
                      headers=NOTION_HEADERS, json=payload, timeout=10)
    if not r.ok:
        return {"ingresos": 0, "gastos": 0, "saldo": 0}

    ingresos, gastos = 0, 0
    for page in r.json().get("results", []):
        p = page["properties"]
        tipo = p.get("Tipo", {}).get("select", {}).get("name", "")
        monto = p.get("Monto (€)", {}).get("number", 0)
        if tipo == "Ingreso":
            ingresos += monto
        elif tipo == "Gasto":
            gastos += monto
    return {"ingresos": ingresos, "gastos": gastos, "saldo": ingresos - gastos}


def notion_get_kpis() -> dict:
    """Obtiene KPIs del mes."""
    payload = {"page_size": 20}
    r = _notion_post(f"https://api.notion.com/v1/databases/{NOTION_KPIS_DB}/query",
                      headers=NOTION_HEADERS, json=payload, timeout=10)
    if not r.ok:
        return {}
    kpis = {}
    for page in r.json().get("results", []):
        p = page["properties"]
        nombre = p.get("Nombre", {}).get("title", [{}])[0].get("plain_text", "")
        valor = p.get("Valor", {}).get("number", 0)
        kpis[nombre] = valor
    return kpis


def notion_get_afiliados() -> list[dict]:
    """Lista afiliados activos."""
    payload = {"filter": {"property": "Estado", "select": {"equals": "Activo"}}}
    r = _notion_post(f"https://api.notion.com/v1/databases/{NOTION_AFILIADOS_DB}/query",
                      headers=NOTION_HEADERS, json=payload, timeout=10)
    if not r.ok:
        return []
    afiliados = []
    for page in r.json().get("results", []):
        p = page["properties"]
        afiliados.append({
            "nombre": p.get("Nombre", {}).get("title", [{}])[0].get("plain_text", ""),
            "comision": p.get("Comisión %", {}).get("number", 0),
            "estado": p.get("Estado", {}).get("select", {}).get("name", ""),
        })
    return afiliados


def notion_get_agentes() -> list[dict]:
    """Lista agentes IA registrados."""
    payload = {"page_size": 50}
    r = _notion_post(f"https://api.notion.com/v1/databases/{NOTION_AGENTES_DB}/query",
                      headers=NOTION_HEADERS, json=payload, timeout=10)
    if not r.ok:
        return []
    agentes = []
    for page in r.json().get("results", []):
        p = page["properties"]
        agentes.append({
            "nombre": p.get("Nombre", {}).get("rich_text", [{}])[0].get("plain_text", ""),
            "departamento": p.get("Departamento", {}).get("select", {}).get("name", ""),
            "canal_slack": p.get("Canal Slack", {}).get("rich_text", [{}])[0].get("plain_text", ""),
            "estado": p.get("Estado", {}).get("select", {}).get("name", ""),
        })
    return agentes


def notion_add_agent(nombre: str, rol: str, departamento: str, estado: str = "En desarrollo") -> dict | None:
    """Crea agente en Notion. Devuelve page_id si éxito, None si falla."""
    try:
        payload = {
            "parent": {"database_id": NOTION_AGENTES_DB},
            "properties": {
                "Agente": {"title": [{"text": {"content": nombre}}]},
                "Función": {"rich_text": [{"text": {"content": rol}}]},
                "Departamento": {"select": {"name": departamento}},
                "Estado": {"select": {"name": estado}},
            }
        }
        r = _notion_post("https://api.notion.com/v1/pages", payload)
        if r.ok:
            logger.info(f"✅ Agente {nombre} añadido a Notion: {r.json().get('id')}")
            return r.json().get("id")
        else:
            logger.error(f"❌ Error añadiendo {nombre} a Notion: {r.status_code} | {r.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None


def notion_get_proveedores() -> list[dict]:
    """Lista proveedores."""
    payload = {"filter": {"property": "Activo", "checkbox": {"equals": True}}}
    r = _notion_post(f"https://api.notion.com/v1/databases/{NOTION_PROVEEDORES_DB}/query",
                      headers=NOTION_HEADERS, json=payload, timeout=10)
    if not r.ok:
        return []
    proveedores = []
    for page in r.json().get("results", []):
        p = page["properties"]
        proveedores.append({
            "nombre": p.get("Nombre", {}).get("title", [{}])[0].get("plain_text", ""),
            "telefono": p.get("Teléfono", {}).get("phone_number", ""),
            "email": p.get("Email", {}).get("email", ""),
            "categoria": p.get("Categoría", {}).get("select", {}).get("name", ""),
        })
    return proveedores


# ══════════════════════════════════════════════
# SPEECH-TO-TEXT — Groq Whisper API
# ══════════════════════════════════════════════

def speech_to_text(audio_file_path: str) -> str | None:
    """
    Convierte audio a texto usando Groq Whisper API.

    Args:
        audio_file_path: Ruta al archivo de audio (ogg, mp3, wav, m4a, etc)

    Returns:
        Texto transcrito, o None si falla
    """
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY no configurada. STT deshabilitado.")
        return None

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        # Detectar tipo de archivo por extensión
        ext = audio_file_path.split(".")[-1].lower()
        mime_types = {
            "ogg": "audio/ogg",
            "opus": "audio/opus",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4",
            "webm": "audio/webm",
        }
        mime_type = mime_types.get(ext, "audio/ogg")

        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file_path.split("/")[-1], audio_file, mime_type),
                model="whisper-large-v3-turbo",
                language="es",
                temperature=0.0,
            )

        text = transcription.text.strip()
        if not text:
            logger.warning("Audio transcribed but empty")
            return None

        logger.info(f"STT exitoso: {len(text)} caracteres - '{text[:50]}'")
        return text

    except FileNotFoundError:
        logger.error(f"Audio file not found: {audio_file_path}")
        return None
    except Exception as e:
        logger.error(f"STT error: {str(e)}")
        return None


# ══════════════════════════════════════════════
# TEXT-TO-SPEECH — ElevenLabs
# ══════════════════════════════════════════════

def text_to_speech(texto: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes | None:
    """
    Convierte texto a bytes de audio MP3 usando ElevenLabs API.

    Args:
        texto: Texto a sintetizar (max 500 chars)
        voice_id: ID de voz de ElevenLabs (default: Rachel)

    Returns:
        bytes de audio MP3, o None si falla (con degradación graceful)
    """
    if not ELEVENLABS_API_KEY:
        logger.warning("ELEVENLABS_API_KEY no configurada. TTS deshabilitado.")
        return None

    if not texto or len(texto.strip()) == 0:
        logger.warning("Texto vacío para TTS")
        return None

    # Limitar texto a 500 caracteres
    texto = texto[:500]

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": texto,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            logger.info(f"TTS generado exitosamente ({len(texto)} chars)")
            return response.content
        else:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logger.error("ElevenLabs API timeout (>10s)")
        return None
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return None


# ══════════════════════════════════════════════
# FLUJO COMPLETO — onboarding automático
# ══════════════════════════════════════════════

def onboard_new_client(name: str, service: str, price: float,
                        phone: str = "", email: str = "",
                        niche: str = "", notes: str = "") -> dict:
    """
    Flujo completo de alta de cliente:
    1. Crea en Notion
    2. Notifica en Slack
    3. Devuelve resultado
    """
    results = {"notion": False, "slack": False, "notion_url": ""}

    # 1. Notion
    notion_result = notion_create_client(name, service, price, phone, email, niche, notes)
    results["notion"] = notion_result["ok"]
    results["notion_url"] = notion_result.get("url", "")

    # 2. Slack
    results["slack"] = slack_notify_new_client(name, service, price, phone)

    logger.info(f"Onboarding {name}: Notion={results['notion']} Slack={results['slack']}")
    return results
