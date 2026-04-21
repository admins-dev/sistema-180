"""
jarvis_whatsapp.py — Sistema 180
WhatsApp Business Cloud API integration.
Envía/recibe mensajes de WhatsApp y los gestiona desde Telegram.

SETUP NECESARIO:
1. Ir a https://developers.facebook.com
2. Crear app tipo "Business" → añadir producto "WhatsApp"
3. Obtener WHATSAPP_PHONE_NUMBER_ID y WHATSAPP_BUSINESS_ACCOUNT_ID
4. Configurar webhook URL: https://tu-railway.up.railway.app/whatsapp/webhook
5. Añadir variables a Railway:
   - WHATSAPP_PHONE_NUMBER_ID
   - WHATSAPP_VERIFY_TOKEN (el que tú elijas)
   - META_ACCESS_TOKEN (ya lo tienes)
"""
import os, json, logging, requests, time, threading
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Config: Meta WhatsApp API ──
META_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
WA_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WA_BUSINESS_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
WA_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "sistema180_verify")

# ── Config: Twilio WhatsApp (alternativa sin verificación) ──
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WA_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")  # whatsapp:+14155238886 (sandbox)

# ── Config: Telegram forwarding ──
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0].strip())

# NO reenviar mensajes WA a Telegram por defecto (evitar notificaciones dobles)
WA_FORWARD_TO_TELEGRAM = os.getenv("WA_FORWARD_TO_TELEGRAM", "false").lower() == "true"

# Auto-responder para atención al cliente (desactivado por defecto)
WA_AUTORESPONDER = os.getenv("WA_AUTORESPONDER", "false").lower() == "true"
WA_AUTORESPONDER_MSG = os.getenv(
    "WA_AUTORESPONDER_MESSAGE",
    "¡Hola! Gracias por contactarnos. En breve le atenderemos. "
    "Si es urgente, llámenos al teléfono de la empresa."
)

# Auto-detect provider
WA_PROVIDER = "twilio" if TWILIO_SID else ("meta" if (META_TOKEN and WA_PHONE_ID) else "none")
WA_API_URL = f"https://graph.facebook.com/v19.0/{WA_PHONE_ID}/messages"

# Conversation store
CONVERSATIONS_FILE = Path(__file__).parent / "wa_conversations.json"


def _load_conversations() -> dict:
    if CONVERSATIONS_FILE.exists():
        try:
            return json.loads(CONVERSATIONS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_conversations(data: dict):
    CONVERSATIONS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ══════════════════════════════════════════════════════════════════════════════
# ENVIAR MENSAJES
# ══════════════════════════════════════════════════════════════════════════════

def send_message(phone: str, text: str) -> dict:
    """Envía un mensaje de WhatsApp (auto-detecta Twilio o Meta API).
    phone: número con código país (ej: 34612345678)
    """
    # Limpiar número
    phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    if not phone.startswith("34"):
        phone = "34" + phone  # Default España

    if WA_PROVIDER == "twilio":
        return _send_twilio(phone, text)
    elif WA_PROVIDER == "meta":
        return _send_meta(phone, text)
    else:
        return {"ok": False, "error": "WhatsApp no configurado. Configura TWILIO_ACCOUNT_SID o WHATSAPP_PHONE_NUMBER_ID"}


def _send_twilio(phone: str, text: str) -> dict:
    """Envía WhatsApp via Twilio REST API."""
    try:
        from_number = TWILIO_WA_NUMBER or "whatsapp:+14155238886"  # sandbox default
        to_number = f"whatsapp:+{phone}"

        r = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
            auth=(TWILIO_SID, TWILIO_TOKEN),
            data={
                "From": from_number,
                "To": to_number,
                "Body": text,
            },
            timeout=15,
        )

        if r.ok:
            msg_sid = r.json().get("sid", "")
            logger.info(f"[WA/Twilio] Sent to {phone}: {text[:50]}")
            _save_message(phone, text, "bot", msg_sid)
            return {"ok": True, "msg_id": msg_sid}
        else:
            error = r.json().get("message", r.text[:200])
            logger.error(f"[WA/Twilio] Error: {error}")
            return {"ok": False, "error": error}
    except Exception as e:
        logger.error(f"[WA/Twilio] Error: {e}")
        return {"ok": False, "error": str(e)}


def _send_meta(phone: str, text: str) -> dict:
    """Envía WhatsApp via Meta Cloud API."""
    try:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {"body": text}
        }
        r = requests.post(
            WA_API_URL,
            headers={
                "Authorization": f"Bearer {META_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        if r.ok:
            msg_id = r.json().get("messages", [{}])[0].get("id", "")
            logger.info(f"[WA/Meta] Sent to {phone}: {text[:50]}")
            _save_message(phone, text, "bot", msg_id)
            return {"ok": True, "msg_id": msg_id}
        else:
            error = r.json().get("error", {}).get("message", r.text[:200])
            return {"ok": False, "error": error}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _save_message(phone: str, text: str, sender: str, msg_id: str = ""):
    """Guarda mensaje en historial."""
    convos = _load_conversations()
    if phone not in convos:
        convos[phone] = {"messages": [], "name": "", "status": "active"}
    convos[phone]["messages"].append({
        "from": sender,
        "text": text,
        "ts": datetime.utcnow().isoformat(),
        "msg_id": msg_id,
    })
    _save_conversations(convos)


def send_template(phone: str, template_name: str = "hello_world",
                   language: str = "es") -> dict:
    """Envía un template aprobado de WhatsApp (necesario para iniciar conversación)."""
    if not META_TOKEN or not WA_PHONE_ID:
        return {"ok": False, "error": "WhatsApp no configurado"}

    phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    if not phone.startswith("34"):
        phone = "34" + phone

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language}
        }
    }

    try:
        r = requests.post(
            WA_API_URL,
            headers={
                "Authorization": f"Bearer {META_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        if r.ok:
            return {"ok": True}
        return {"ok": False, "error": r.text[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# RECIBIR MENSAJES (Webhook)
# ══════════════════════════════════════════════════════════════════════════════

def handle_webhook_verify(args: dict) -> tuple[str, int]:
    """Verifica el webhook de WhatsApp (GET request)."""
    mode = args.get("hub.mode", "")
    token = args.get("hub.verify_token", "")
    challenge = args.get("hub.challenge", "")

    if mode == "subscribe" and token == WA_VERIFY_TOKEN:
        logger.info("[WA] Webhook verified")
        return challenge, 200
    return "Forbidden", 403


def handle_incoming_message(data: dict):
    """Procesa mensaje entrante de WhatsApp y lo reenvía a Telegram."""
    try:
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        for msg in messages:
            phone = msg.get("from", "")
            msg_type = msg.get("type", "")

            if msg_type == "text":
                text = msg.get("text", {}).get("body", "")
            elif msg_type == "image":
                text = "[📷 Imagen recibida]"
            elif msg_type == "audio":
                text = "[🎤 Audio recibido]"
            elif msg_type == "document":
                text = "[📎 Documento recibido]"
            else:
                text = f"[{msg_type}]"

            # Get contact name
            contacts = value.get("contacts", [])
            name = contacts[0].get("profile", {}).get("name", phone) if contacts else phone

            logger.info(f"[WA] Incoming from {name} ({phone}): {text[:50]}")

            # Save to conversations
            convos = _load_conversations()
            if phone not in convos:
                convos[phone] = {"messages": [], "name": name, "status": "active"}
            convos[phone]["name"] = name
            convos[phone]["messages"].append({
                "from": "user",
                "text": text,
                "ts": datetime.utcnow().isoformat(),
            })
            # Keep only last 50 messages per conversation
            if len(convos[phone]["messages"]) > 50:
                convos[phone]["messages"] = convos[phone]["messages"][-50:]
            _save_conversations(convos)

            # Forward to Telegram (only if enabled)
            _forward_to_telegram(name, phone, text)

            # Auto-responder for customer service (only first message from new contacts)
            if WA_AUTORESPONDER:
                msg_count = len(convos[phone]["messages"])
                if msg_count == 1:  # First message ever from this person
                    send_message(phone, WA_AUTORESPONDER_MSG)
                    logger.info(f"[WA] Auto-response sent to {phone}")

    except Exception as e:
        logger.error(f"[WA] Webhook processing error: {e}")


def _forward_to_telegram(name: str, phone: str, text: str):
    """Reenvía mensaje de WhatsApp a Telegram (solo si activado)."""
    if not WA_FORWARD_TO_TELEGRAM:
        return  # No forwarding — el usuario no quiere notificaciones dobles
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        msg = (
            f"📱 *WhatsApp*\n"
            f"👤 {name}\n"
            f"📞 +{phone}\n"
            f"💬 {text}"
        )
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": msg,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
    except Exception as e:
        logger.error(f"[WA] Telegram forward error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# GESTIÓN DE CONVERSACIONES
# ══════════════════════════════════════════════════════════════════════════════

def get_conversations() -> list[dict]:
    """Lista conversaciones activas."""
    convos = _load_conversations()
    result = []
    for phone, data in convos.items():
        last_msg = data["messages"][-1] if data.get("messages") else {}
        result.append({
            "phone": phone,
            "name": data.get("name", phone),
            "status": data.get("status", "active"),
            "last_message": last_msg.get("text", "")[:50],
            "last_time": last_msg.get("ts", ""),
            "total_messages": len(data.get("messages", [])),
        })
    result.sort(key=lambda x: x.get("last_time", ""), reverse=True)
    return result


def get_conversation(phone: str) -> list[dict]:
    """Obtiene historial de conversación con un número."""
    convos = _load_conversations()
    phone = phone.replace("+", "").replace(" ", "")
    data = convos.get(phone, {})
    return data.get("messages", [])


def is_configured() -> bool:
    """Verifica si WhatsApp está configurado (Twilio o Meta)."""
    return WA_PROVIDER != "none"
