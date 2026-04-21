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

# === CUENTAS INSTAGRAM + PROXIES ===
ACCOUNTS = [
    {
        "username": "lauramtz.95",
        "password": "Lauraa2026",
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
