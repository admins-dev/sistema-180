"""
Ghost Mouse — Configuracion central.
"""

# === APIs ===
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_KEY = "AIzaSyBwFk04waqRtE61DiScWBDmTxoO6dkW2d8"
GEMINI_KEY = os.getenv("GEMINI_KEY", "AIzaSyAJt3YzfhP-r6jxMkoPZyCjtbF1Sy2wiWk")
SMSPOOL_KEY = "jCQH7hDydYjVxO8449OKru8HOsR22eJ1"
PERPLEXITY_KEY = "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"
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
if not NOTION_TOKEN:
    NOTION_TOKEN = "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"

# Twilio WhatsApp API
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") # Twilio Sandbox default

# Meta Ads API
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "EAAT1GpkJzPMBRa8EnHZBFQTROvI4rVMXNgDTlPeptJm7R72KNPMh75AdoEc7wR2ZBiZArZAVyIZBSeQwWsGUUYoFglujzLrpZAxyKw1ZARCGp2hT0MuKEaWwZBvDw01DTqzGxGEXOAMJU3bK0CC2MPfr44IqlwCS8rJrfhO03FfxgL5ZAzcXDz6rsctv4YcOr0ZCXFUQ3dwfPZCvhPoPCAawgXoEESdKaYnZC9qDaPhBxeUsYIFXrSir7iPRSHl2YZB839WnYNczYyHYlvV3eP3hwJxCiXY40BupoS8mzX8DFpiYIZA9ZAFpZAOmMRShnMN8vZBLpxI5kf52KtuoQmXL3xhp0XyVEG5EZD")


# === CUENTAS INSTAGRAM + PROXIES ===
ACCOUNTS = [
    {
        "username": "lauramtz.95",
        "password": "Lauura2026",
        "fullname": "Laura Martinez",
        "proxy": {
            "server": "http://46.34.42.14:12323",
            "username": "14a407c433ed4",
            "password": "60852e0bba",
        },
    },
    {
        "username": "carlosruiz.88",
        "password": "Carlos2026",
        "fullname": "Carlos Ruiz",
        "proxy": {
            "server": "http://213.220.30.200:12323",
            "username": "14a407c433ed4",
            "password": "60852e0bba",
        },
    },
    {
        "username": "anabelenn.90",
        "password": "Ana2026",
        "fullname": "Ana Torres",
        "proxy": {
            "server": "http://213.220.27.116:12323",
            "username": "14a407c433ed4",
            "password": "60852e0bba",
        },
    },
    {
        "username": "pablofdezz86",
        "password": "Pablo2026",
        "fullname": "Pablo Fernandez",
        "proxy": {
            "server": "http://213.220.22.110:12323",
            "username": "14a407c433ed4",
            "password": "60852e0bba",
        },
    },
    {
        "username": "martadiaz.24",
        "password": "Marta2026",
        "fullname": "Marta Diaz",
        "proxy": {
            "server": "http://213.220.23.188:12323",
            "username": "14a407c433ed4",
            "password": "60852e0bba",
        },
    },
]

# === LIMITES DE SEGURIDAD ===
MAX_DMS_PER_ACCOUNT_PER_DAY = 20
PAUSE_BETWEEN_DMS_MIN = 30   # segundos
PAUSE_BETWEEN_DMS_MAX = 90   # segundos
MAX_HOURS_ACTIVE_PER_DAY = 3
