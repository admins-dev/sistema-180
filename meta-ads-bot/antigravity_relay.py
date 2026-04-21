#!/usr/bin/env python3
"""
antigravity_relay.py — Sistema 180
Puente Telegram ↔ Antigravity Cloud Code.

Corre LOCAL en tu PC. Hace polling al bot de Railway,
recoge tareas pendientes de code_queue.json, y las ejecuta
abriendo Antigravity con el prompt.

USO:
    python antigravity_relay.py

REQUISITOS:
    - TELEGRAM_BOT_TOKEN en .env
    - Railway bot corriendo (code_queue.json accesible)
    - Antigravity instalado localmente
"""
import os, json, time, logging, subprocess, requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [Relay] %(message)s")
logger = logging.getLogger("relay")

# ── Config ──
RAILWAY_URL = os.getenv(
    "RAILWAY_HEALTH_URL",
    "https://sistema-180-meta-ads-production.up.railway.app"
)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0].strip()
POLL_INTERVAL = 10  # seconds
QUEUE_FILE = Path(__file__).parent / "code_queue.json"
WORKSPACE = r"c:\Users\Jose\.antigravity\extensions\fabrica-avatares"

# ── Antigravity CLI path ──
ANTIGRAVITY_CMD = "antigravity"  # Assumes it's in PATH


def send_telegram(msg: str):
    """Send message to Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram token/chat_id not configured")
        return
    try:
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
        logger.error(f"Telegram send error: {e}")


def get_pending_tasks() -> list[dict]:
    """Read pending tasks from queue."""
    if not QUEUE_FILE.exists():
        return []
    try:
        queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        return [t for t in queue if t.get("status") == "pending"]
    except Exception:
        return []


def update_task_status(task_id: str, status: str, result: str = ""):
    """Update task status in queue."""
    if not QUEUE_FILE.exists():
        return
    try:
        queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        for t in queue:
            if t["id"] == task_id:
                t["status"] = status
                t["result"] = result[:500]
                t["completed_at"] = datetime.utcnow().isoformat()
                break
        QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.error(f"Update status error: {e}")


def execute_task(task: dict):
    """Execute a coding task via Antigravity."""
    task_id = task["id"]
    instruction = task["task"]
    source = task.get("source", "unknown")

    logger.info(f"Executing task {task_id}: {instruction[:60]}...")
    update_task_status(task_id, "running")
    send_telegram(f"🔄 *Ejecutando tarea {task_id}*\n`{instruction[:80]}`")

    # Create a prompt file for Antigravity
    prompt_file = Path(__file__).parent / f"_task_{task_id}.md"
    prompt_content = f"""# Tarea desde Telegram ({source})
ID: {task_id}
Fecha: {task.get('created_at', '')}

## Instrucción
{instruction}

## Contexto
- Workspace: {WORKSPACE}
- Proyecto: Sistema 180 meta-ads-bot
- Ejecutar la tarea completa, verificar que compila, y hacer deploy si es necesario.
"""
    prompt_file.write_text(prompt_content, encoding="utf-8")

    try:
        # Option 1: Try to run antigravity CLI
        result = subprocess.run(
            [ANTIGRAVITY_CMD, "run", "--prompt", instruction, "--workspace", WORKSPACE],
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max
            cwd=WORKSPACE,
        )
        output = result.stdout[-500:] if result.stdout else ""
        if result.returncode == 0:
            update_task_status(task_id, "done", output)
            send_telegram(
                f"✅ *Tarea {task_id} completada*\n"
                f"`{instruction[:60]}`\n\n"
                f"```\n{output[:300]}\n```"
            )
        else:
            error = result.stderr[-300:] if result.stderr else "Unknown error"
            update_task_status(task_id, "error", error)
            send_telegram(f"❌ *Tarea {task_id} falló*\n`{error[:200]}`")

    except FileNotFoundError:
        # Antigravity CLI not found — save for manual execution
        update_task_status(task_id, "pending_manual",
                          "Antigravity CLI no disponible. Tarea guardada para ejecución manual.")
        send_telegram(
            f"📝 *Tarea {task_id} guardada*\n"
            f"`{instruction[:80]}`\n\n"
            f"Antigravity CLI no encontrado. "
            f"Abre Antigravity manualmente y ejecuta la tarea desde el archivo:\n"
            f"`{prompt_file}`"
        )
    except subprocess.TimeoutExpired:
        update_task_status(task_id, "timeout", "Timeout after 5 minutes")
        send_telegram(f"⏰ *Tarea {task_id} timeout* (5 min)")
    except Exception as e:
        update_task_status(task_id, "error", str(e))
        send_telegram(f"❌ *Tarea {task_id} error:* `{str(e)[:200]}`")
    finally:
        # Cleanup prompt file
        try:
            prompt_file.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    logger.info("=" * 50)
    logger.info("  ANTIGRAVITY RELAY — Telegram ↔ Code Bridge")
    logger.info(f"  Workspace: {WORKSPACE}")
    logger.info(f"  Queue: {QUEUE_FILE}")
    logger.info(f"  Poll interval: {POLL_INTERVAL}s")
    logger.info("=" * 50)

    send_telegram("🟢 *Antigravity Relay activado*\nPuedes enviar tareas con `/codigo <instrucción>`")

    while True:
        try:
            tasks = get_pending_tasks()
            if tasks:
                logger.info(f"Found {len(tasks)} pending tasks")
                for task in tasks:
                    execute_task(task)
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Relay stopped.")
            send_telegram("🔴 *Antigravity Relay detenido*")
            break
        except Exception as e:
            logger.error(f"Relay error: {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
