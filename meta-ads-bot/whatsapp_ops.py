"""
whatsapp_ops.py — Sistema 180
WhatsApp automático via Twilio.
Onboarding, facturas, guiones y notificaciones a clientes.
"""
import os, logging, requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TWILIO_SID   = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM  = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # sandbox por defecto

BASE_URL = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"


def send_whatsapp(to_phone: str, message: str) -> dict:
    """Envía mensaje de WhatsApp. to_phone formato: +34612345678"""
    if not to_phone.startswith("+"):
        to_phone = "+" + to_phone
    r = requests.post(
        BASE_URL,
        auth=(TWILIO_SID, TWILIO_TOKEN),
        data={
            "From": TWILIO_FROM,
            "To":   f"whatsapp:{to_phone}",
            "Body": message,
        }
    )
    if r.ok:
        sid = r.json().get("sid", "")
        logger.info(f"WhatsApp enviado a {to_phone}: {sid}")
        return {"ok": True, "sid": sid}
    logger.error(f"Twilio error {r.status_code}: {r.text}")
    return {"ok": False, "error": r.text}


def whatsapp_bienvenida(name: str, phone: str, service: str) -> dict:
    """Mensaje de bienvenida automático para cliente nuevo."""
    msg = (
        f"¡Hola {name}! 👋\n\n"
        f"Bienvenido/a a *Sistema 180*. Soy José María y voy a estar contigo en todo el proceso.\n\n"
        f"📦 *Tu servicio:* {service}\n\n"
        f"En las próximas horas recibirás:\n"
        f"✅ Tu plan personalizado de 30 días\n"
        f"✅ Acceso a tu dashboard\n"
        f"✅ Primera reunión de arranque\n\n"
        f"Cualquier duda, escríbeme aquí directamente.\n\n"
        f"¡Vamos a por ello! 🚀"
    )
    return send_whatsapp(phone, msg)


def whatsapp_factura(name: str, phone: str, amount: float, concept: str) -> dict:
    """Notificación de factura al cliente."""
    msg = (
        f"Hola {name} 👋\n\n"
        f"🧾 *Nueva factura generada*\n"
        f"💰 Importe: *{amount}€*\n"
        f"📋 Concepto: {concept}\n\n"
        f"Recibirás el PDF por email en breve.\n"
        f"Gracias por confiar en Sistema 180 ✨"
    )
    return send_whatsapp(phone, msg)


def whatsapp_guion_listo(name: str, phone: str, topic: str) -> dict:
    """Avisa al cliente que su guión está listo."""
    msg = (
        f"Hola {name}! 🎬\n\n"
        f"Tu guión sobre *\"{topic}\"* está listo.\n\n"
        f"Accede a tu dashboard para verlo, editarlo y descargarlo.\n\n"
        f"Recuerda: grábalo en los próximos 2 días para mantener el ritmo de publicación 📅"
    )
    return send_whatsapp(phone, msg)


def whatsapp_plan_contenido(name: str, phone: str) -> dict:
    """Envía el plan de contenido mensual al cliente."""
    msg = (
        f"Hola {name}! 📅\n\n"
        f"Tu *plan de contenido del mes* está listo en el dashboard.\n\n"
        f"📌 Incluye:\n"
        f"• 4 guiones semanales\n"
        f"• Hooks optimizados por plataforma\n"
        f"• Calendario de publicación\n"
        f"• Estrategia de hashtags\n\n"
        f"¿Tienes alguna preferencia de tema para esta semana? 💬"
    )
    return send_whatsapp(phone, msg)
