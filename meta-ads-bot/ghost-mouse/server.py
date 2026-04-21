"""
server.py — WebSocket Server + Dashboard HTTP
Puente entre el Ghost Bot y el Dashboard visual en tiempo real.
"""
import asyncio
import json
import logging
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

import websockets
from config import WS_HOST, WS_PORT, DASHBOARD_PORT, STATS_FILE

logger = logging.getLogger(__name__)

# Clientes WebSocket conectados
_clients: set = set()

# Cola de eventos del bot → dashboard
_event_queue = asyncio.Queue()

DASHBOARD_DIR = Path(__file__).parent / "dashboard"


# ══════════════════════════════════════════════════════════════════════════════
# WebSocket Handler
# ══════════════════════════════════════════════════════════════════════════════

async def ws_handler(websocket):
    """Maneja conexiones WebSocket del dashboard."""
    _clients.add(websocket)
    logger.info(f"[WS] Dashboard conectado ({len(_clients)} activos)")

    # Enviar estado inicial
    if STATS_FILE.exists():
        try:
            stats = json.loads(STATS_FILE.read_text())
            await websocket.send(json.dumps({"type": "init_stats", **stats}))
        except Exception:
            pass

    try:
        async for message in websocket:
            # Recibir comandos del dashboard (ej: start/stop campaña)
            try:
                cmd = json.loads(message)
                logger.info(f"[WS] Comando recibido: {cmd}")
                if cmd.get("action") == "start_campaign":
                    await _event_queue.put(json.dumps({
                        "type": "command",
                        "action": "start_campaign",
                        "hashtags": cmd.get("hashtags", []),
                        "targets": cmd.get("targets", []),
                    }))
            except json.JSONDecodeError:
                pass
    except websockets.ConnectionClosed:
        pass
    finally:
        _clients.discard(websocket)
        logger.info(f"[WS] Dashboard desconectado ({len(_clients)} activos)")


async def broadcast_events():
    """Lee eventos de la cola y los envía a todos los dashboards conectados."""
    while True:
        event = await _event_queue.get()
        if _clients:
            await asyncio.gather(
                *[client.send(event) for client in _clients.copy()],
                return_exceptions=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard HTTP Server (sirve el HTML/CSS/JS)
# ══════════════════════════════════════════════════════════════════════════════

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def log_message(self, format, *args):
        pass  # Silenciar logs HTTP


def start_dashboard_http():
    """Arranca el servidor HTTP del dashboard en un thread separado."""
    server = HTTPServer(("0.0.0.0", DASHBOARD_PORT), DashboardHandler)
    logger.info(f"[HTTP] Dashboard en http://localhost:{DASHBOARD_PORT}")
    server.serve_forever()


# ══════════════════════════════════════════════════════════════════════════════
# Main: arrancar WebSocket + HTTP + Ghost Bot
# ══════════════════════════════════════════════════════════════════════════════

async def main():
    """Punto de entrada: arranca todo el sistema."""
    from ghost_bot import set_event_queue, run_campaign

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   🖱️  SISTEMA 180 — RATÓN FANTASMA + DASHBOARD v1.0        ║
    ║                                                              ║
    ║   Dashboard:  http://localhost:3180                           ║
    ║   WebSocket:  ws://localhost:8765                             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Conectar la cola de eventos al bot
    set_event_queue(_event_queue)

    # Arrancar HTTP del dashboard en thread separado
    http_thread = Thread(target=start_dashboard_http, daemon=True)
    http_thread.start()

    # Arrancar WebSocket server
    ws_server = await websockets.serve(ws_handler, WS_HOST, WS_PORT)
    logger.info(f"[WS] WebSocket server en ws://{WS_HOST}:{WS_PORT}")

    # Arrancar broadcaster de eventos
    broadcast_task = asyncio.create_task(broadcast_events())

    # Escuchar comandos del dashboard para lanzar campañas
    logger.info("[SYSTEM] Sistema listo. Abre el dashboard para iniciar una campaña.")

    while True:
        try:
            # Esperar comandos del dashboard
            event_raw = await asyncio.wait_for(_event_queue.get(), timeout=1.0)
            event = json.loads(event_raw)
            if event.get("type") == "command" and event.get("action") == "start_campaign":
                logger.info("[SYSTEM] 🚀 Campaña lanzada desde el dashboard!")
                asyncio.create_task(
                    run_campaign(
                        hashtags=event.get("hashtags"),
                        target_usernames=event.get("targets"),
                    )
                )
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            logger.error(f"[SYSTEM] Error: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    asyncio.run(main())
