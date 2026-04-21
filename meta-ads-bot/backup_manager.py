"""
backup_manager.py — Sistema 180
Backup automatico de datos criticos.
Se ejecuta diariamente desde start_all.py.
"""
import os, shutil, logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

# Files to backup
CRITICAL_FILES = [
    "ig_accounts.json",
    "outreach.db",
    "brain_memory.db",
]

MAX_BACKUPS = 7  # keep last 7 days


def run_backup() -> dict:
    """Backup all critical files. Returns stats."""
    stats = {"ok": 0, "skip": 0, "error": 0, "files": []}
    ts = datetime.now().strftime("%Y%m%d_%H%M")

    for fname in CRITICAL_FILES:
        src = Path(fname)
        if not src.exists():
            stats["skip"] += 1
            continue
        try:
            dst = BACKUP_DIR / f"{src.stem}_{ts}{src.suffix}"
            shutil.copy2(str(src), str(dst))
            stats["ok"] += 1
            stats["files"].append(str(dst))
            logger.info(f"[Backup] {src} -> {dst}")
        except Exception as e:
            stats["error"] += 1
            logger.error(f"[Backup] Error copying {src}: {e}")

    # Cleanup old backups
    _cleanup()
    return stats


def _cleanup():
    """Remove backups older than MAX_BACKUPS days."""
    all_backups = sorted(BACKUP_DIR.glob("*"), key=os.path.getmtime, reverse=True)
    # Group by base name
    seen: dict[str, int] = {}
    for f in all_backups:
        # Extract base name (before timestamp)
        base = f.stem.rsplit("_", 2)[0] if "_" in f.stem else f.stem
        seen[base] = seen.get(base, 0) + 1
        if seen[base] > MAX_BACKUPS:
            try:
                f.unlink()
                logger.info(f"[Backup] Cleanup: removed {f}")
            except Exception:
                pass


def get_backup_status() -> str:
    """Returns human-readable backup status."""
    if not BACKUP_DIR.exists():
        return "Sin backups."
    files = list(BACKUP_DIR.glob("*"))
    if not files:
        return "Sin backups."
    latest = max(files, key=os.path.getmtime)
    from datetime import datetime
    mtime = datetime.fromtimestamp(os.path.getmtime(latest))
    return (
        f"Backups: {len(files)} archivos\n"
        f"Ultimo: {latest.name}\n"
        f"Fecha: {mtime.strftime('%d/%m/%Y %H:%M')}"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stats = run_backup()
    print(f"Backup completado: {stats}")
