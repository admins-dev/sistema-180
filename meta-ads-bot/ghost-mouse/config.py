"""
Ghost Mouse — Configuracion central.
Todas las credenciales se leen de archivos .env (nunca hardcodeadas).
"""

import os
import json
from dotenv import load_dotenv

# Cargar .env del root del proyecto y del meta-ads-bot/
_root_env = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
_bot_env = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(_root_env)
load_dotenv(_bot_env)
load_dotenv()  # fallback al .env del working directory

# === APIs ===
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY", "")
SMSPOOL_KEY = os.getenv("SMSPOOL_KEY", "")
PERPLEXITY_KEY = os.getenv("PERPLEXITY_KEY") or os.getenv("PERPLEXITY_API_KEY", "")
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

# Claude / Anthropic
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY") or os.getenv("ANTHROPIC_API_KEY", "")

# Groq (LLaMA + Whisper + TTS gratis)
GROQ_KEY = os.getenv("GROQ_KEY") or os.getenv("GROQ_API_KEY", "")

# GoHighLevel
GHL_API_KEY = os.getenv("GHL_API_KEY", "")
GHL_BASE_URL = os.getenv("GHL_BASE_URL", "https://services.leadconnectorhq.com")

# Twilio WhatsApp API
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Meta Ads API
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")


# === CUENTAS INSTAGRAM + PROXIES ===
# Se cargan desde accounts.json (gitignored) para no exponer credenciales en el repo.
_accounts_path = os.path.join(os.path.dirname(__file__), "accounts.json")
if os.path.exists(_accounts_path):
    with open(_accounts_path, "r", encoding="utf-8") as f:
        ACCOUNTS = json.load(f)
else:
    ACCOUNTS = []

# === LIMITES DE SEGURIDAD ===
MAX_DMS_PER_ACCOUNT_PER_DAY = 20
PAUSE_BETWEEN_DMS_MIN = 30   # segundos
PAUSE_BETWEEN_DMS_MAX = 90   # segundos
MAX_HOURS_ACTIVE_PER_DAY = 3
