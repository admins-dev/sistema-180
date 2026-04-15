#!/usr/bin/env python3
"""
Sistema 180 — Unified Startup Script v2
Arranca bot.py (Telegram) + server.py (Flask) en paralelo.
Diseñado para Railway (un solo proceso entry point).

Features:
- Health check HTTP en PORT para Railway
- Auto-restart de procesos caídos
- Logging estructurado para debug remoto
"""

import os
import sys
import signal
import threading
import logging
import subprocess
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("start_all")

# Directorio base
BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)

# Estado global
_running = True
_bot_status = "starting"
_flask_status = "starting"
_start_time = time.time()


# ═══════════════════════════════════════════════
#  HEALTH CHECK HTTP SERVER (para Railway)
# ═══════════════════════════════════════════════

class HealthHandler(BaseHTTPRequestHandler):
    """Minimal health check for Railway."""

    def do_GET(self):
        if self.path == "/health" or self.path == "/":
            uptime = int(time.time() - _start_time)
            body = (
                f'{{"status":"ok","bot":"{_bot_status}","flask":"{_flask_status}",'
                f'"uptime":{uptime},"version":"2.0"}}'
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silenciar logs de health checks
        pass


def run_health_server():
    """Arranca HTTP health check en PORT (Railway lo requiere)."""
    port = int(os.getenv("PORT", "5000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"[Health] Listening on 0.0.0.0:{port}")
    server.serve_forever()


# ═══════════════════════════════════════════════
#  PROCESS MANAGERS
# ═══════════════════════════════════════════════

def run_with_restart(name: str, script: str, status_setter):
    """Ejecuta un script Python con auto-restart."""
    global _running
    max_restarts = 5
    restart_count = 0
    cooldown = 5  # segundos entre restarts

    while _running and restart_count < max_restarts:
        logger.info(f"[{name}] Starting (attempt {restart_count + 1})...")
        status_setter("running")

        try:
            proc = subprocess.Popen(
                [sys.executable, script],
                cwd=str(BASE_DIR),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            proc.wait()
            exit_code = proc.returncode
        except Exception as e:
            logger.error(f"[{name}] Failed to start: {e}")
            exit_code = 1

        if not _running:
            break

        status_setter("crashed")
        restart_count += 1
        logger.warning(
            f"[{name}] Exited with code {exit_code}. "
            f"Restart {restart_count}/{max_restarts} in {cooldown}s..."
        )
        time.sleep(cooldown)
        cooldown = min(cooldown * 2, 60)  # Exponential backoff

    if restart_count >= max_restarts:
        logger.error(f"[{name}] Max restarts reached. Giving up.")
        status_setter("dead")


def set_bot_status(s):
    global _bot_status
    _bot_status = s


def set_flask_status(s):
    global _flask_status
    _flask_status = s


# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════

def cleanup(signum=None, frame=None):
    """Cierra todo limpiamente."""
    global _running
    _running = False
    logger.info("[start_all] Shutting down...")
    sys.exit(0)


def main():
    logger.info("=" * 60)
    logger.info("  SISTEMA 180 — JARVIS Bot (Cloud v2)")
    logger.info("=" * 60)

    # Verificar env vars críticas
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
    else:
        logger.info("✅ TELEGRAM_BOT_TOKEN configurado")

    groq = os.getenv("GROQ_API_KEY")
    logger.info(f"{'✅' if groq else '⚠️'} GROQ_API_KEY {'OK' if groq else 'missing'}")

    anthropic = os.getenv("ANTHROPIC_API_KEY")
    logger.info(f"{'✅' if anthropic else '⚠️'} ANTHROPIC_API_KEY {'OK' if anthropic else 'missing'}")

    elevenlabs = os.getenv("ELEVENLABS_API_KEY")
    logger.info(f"{'✅' if elevenlabs else 'ℹ️'} ELEVENLABS_API_KEY {'OK' if elevenlabs else 'not set (using edge-tts)'}")

    # Registrar signal handlers
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    # 1. Health check server (Railway necesita esto)
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # 2. Flask server (opcional, para JARVIS web)
    # Flask usa puerto interno 5001 (el health check ya ocupa PORT)
    os.environ["FLASK_PORT"] = "5001"
    os.environ["PORT_FLASK"] = "5001"
    flask_thread = threading.Thread(
        target=run_with_restart,
        args=("Flask", "server.py", set_flask_status),
        daemon=True,
    )
    flask_thread.start()

    # 3. Telegram bot (principal)
    if token:
        bot_thread = threading.Thread(
            target=run_with_restart,
            args=("Bot", "bot.py", set_bot_status),
            daemon=True,
        )
        bot_thread.start()
    else:
        logger.warning("⚠️ Bot de Telegram NO iniciado (falta TELEGRAM_BOT_TOKEN)")
        _bot_status = "disabled"

    # Esperar indefinidamente
    try:
        while _running:
            time.sleep(10)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
