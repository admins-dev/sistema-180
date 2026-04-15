"""
SHARED STATE — Sistema 180
Estado centralizado para JARVIS + Bot Telegram.
Comparten: SecurityGate, memoria, estado del sistema.

Importar ANTES que cualquier otro módulo excepto system_protection.
"""

import os
import json
import sqlite3
import logging
import threading
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# ── Directorio seguro ──
JARVIS_DATA_DIR = os.path.join(os.path.expanduser("~"), ".jarvis", "data")
os.makedirs(JARVIS_DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(JARVIS_DATA_DIR, "conversations.db")

# ── Thread-safe lock ──
_db_lock = threading.Lock()


# ═══════════════════════════════════════════════
#  SQLITE PERSISTENT MEMORY
# ═══════════════════════════════════════════════

def _init_db():
    """Crea tablas si no existen."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                persona TEXT DEFAULT 's180'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conv_user
            ON conversations(user_id, persona)
        """)
        conn.commit()
    logger.info(f"[SharedState] DB ready at {DB_PATH}")

_init_db()


@contextmanager
def _get_db():
    """Thread-safe database connection."""
    with _db_lock:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# ── Memory operations ──

def save_message(user_id: str, role: str, content: str, persona: str = "s180"):
    """Guarda un mensaje en la memoria persistente."""
    with _get_db() as conn:
        conn.execute(
            "INSERT INTO conversations (user_id, role, content, persona) VALUES (?, ?, ?, ?)",
            (str(user_id), role, content, persona)
        )


def get_memory(user_id: str, persona: str = "s180", max_messages: int = 20) -> list[dict]:
    """Obtiene historial de conversación de un usuario."""
    with _get_db() as conn:
        rows = conn.execute(
            "SELECT role, content FROM conversations "
            "WHERE user_id = ? AND persona = ? "
            "ORDER BY id DESC LIMIT ?",
            (str(user_id), persona, max_messages)
        ).fetchall()
    # Devolver en orden cronológico
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def clear_memory(user_id: str, persona: str = None):
    """Limpia memoria de un usuario (o toda si persona=None)."""
    with _get_db() as conn:
        if persona:
            conn.execute(
                "DELETE FROM conversations WHERE user_id = ? AND persona = ?",
                (str(user_id), persona)
            )
        else:
            conn.execute(
                "DELETE FROM conversations WHERE user_id = ?",
                (str(user_id),)
            )


def get_all_users() -> list[str]:
    """Lista usuarios con conversación."""
    with _get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT user_id FROM conversations"
        ).fetchall()
    return [r["user_id"] for r in rows]


# ── System state operations ──

def set_state(key: str, value: str):
    """Guarda un valor de estado del sistema."""
    with _get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO system_state (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, datetime.now().isoformat())
        )


def get_state(key: str, default: str = None) -> str:
    """Obtiene un valor de estado del sistema."""
    with _get_db() as conn:
        row = conn.execute(
            "SELECT value FROM system_state WHERE key = ?", (key,)
        ).fetchone()
    return row["value"] if row else default


# ═══════════════════════════════════════════════
#  SINGLETON SECURITY GATE
# ═══════════════════════════════════════════════

_security_gate = None
_execution_controller = None

def get_security_gate():
    """Obtiene la instancia singleton del SecurityGate."""
    global _execution_controller
    if _execution_controller is None:
        try:
            from jarvis_architecture import get_jarvis, SecurityPolicy
            policy = SecurityPolicy(allow_outside_hours=True)
            _execution_controller = get_jarvis(policy)
            logger.info("[SharedState] SecurityGate singleton initialized")
        except ImportError:
            logger.warning("[SharedState] jarvis_architecture not available")
            _execution_controller = None
    return _execution_controller


# ═══════════════════════════════════════════════
#  AI PROVIDER HEALTH TRACKING
# ═══════════════════════════════════════════════

_provider_health: dict[str, dict] = {}

def record_provider_call(provider: str, success: bool, latency_ms: float = 0):
    """Registra resultado de llamada a provider IA."""
    if provider not in _provider_health:
        _provider_health[provider] = {
            "total": 0, "success": 0, "fail": 0,
            "avg_latency_ms": 0, "last_error": None,
            "last_success": None
        }
    h = _provider_health[provider]
    h["total"] += 1
    if success:
        h["success"] += 1
        h["last_success"] = datetime.now().isoformat()
        # Running average
        h["avg_latency_ms"] = (h["avg_latency_ms"] * (h["success"] - 1) + latency_ms) / h["success"]
    else:
        h["fail"] += 1
        h["last_error"] = datetime.now().isoformat()


def get_provider_health() -> dict:
    """Estado de salud de todos los providers."""
    return dict(_provider_health)


def get_best_provider() -> str:
    """Devuelve el provider con mejor success rate y latencia."""
    if not _provider_health:
        return "groq"  # Default
    
    scored = []
    for name, h in _provider_health.items():
        if h["total"] == 0:
            continue
        success_rate = h["success"] / h["total"]
        # Score: 70% success rate + 30% latency (lower is better)
        latency_score = max(0, 1 - h["avg_latency_ms"] / 10000)
        score = success_rate * 0.7 + latency_score * 0.3
        scored.append((name, score))
    
    if not scored:
        return "groq"
    
    return max(scored, key=lambda x: x[1])[0]


# ═══════════════════════════════════════════════
#  ATOMIC FILE OPERATIONS
# ═══════════════════════════════════════════════

def atomic_write_json(filepath: str, data):
    """Escritura atómica de JSON — evita corrupción en crash."""
    import tempfile
    dirpath = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(dirpath, exist_ok=True)
    
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Atomic rename (en Windows puede fallar si destino existe)
        if os.path.exists(filepath):
            os.replace(tmp_path, filepath)
        else:
            os.rename(tmp_path, filepath)
    except Exception:
        # Cleanup temp file on error
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def safe_read_json(filepath: str, default=None):
    """Lectura segura de JSON con fallback."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"[SharedState] Error reading {filepath}: {e}")
    return default if default is not None else {}


logger.info("[SharedState] Module loaded — DB, SecurityGate, ProviderHealth ready")
