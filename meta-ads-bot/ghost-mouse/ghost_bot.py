"""
ghost_bot.py — Orquestador Principal del Ratón Fantasma
Coordina: navegadores + LLM + DMs + dashboard en tiempo real.
"""
import asyncio
import json
import random
import logging
import time
from datetime import datetime, date
from pathlib import Path
from config import (
    ACCOUNTS, DAILY_LIMIT_PER_ACCOUNT, BETWEEN_DMS_MIN, BETWEEN_DMS_MAX,
    READ_PAUSE_MIN, READ_PAUSE_MAX, SENT_FILE, STATS_FILE,
    TARGET_HASHTAGS, MAX_CONCURRENT_BROWSERS,
)
from browser_manager import BrowserPool, GhostBrowser
from ig_automator import ig_login, scrape_profile, send_dm, search_hashtag_targets
from llm_brain import generate_dm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Estado persistente: usuarios ya contactados + estadísticas
# ══════════════════════════════════════════════════════════════════════════════

class GhostState:
    """Gestiona el estado persistente del bot."""

    def __init__(self):
        self.sent_users: set[str] = set()
        self.stats: dict = {
            "total_sent": 0,
            "sent_today": 0,
            "today_date": str(date.today()),
            "responses": 0,
            "calls_booked": 0,
            "by_account": {},
            "history": [],
        }
        self._load()

    def _load(self):
        if SENT_FILE.exists():
            try:
                self.sent_users = set(json.loads(SENT_FILE.read_text()))
            except Exception:
                pass
        if STATS_FILE.exists():
            try:
                saved = json.loads(STATS_FILE.read_text())
                self.stats.update(saved)
            except Exception:
                pass
        # Reset diario
        if self.stats.get("today_date") != str(date.today()):
            self.stats["sent_today"] = 0
            self.stats["today_date"] = str(date.today())
            self.stats["by_account"] = {}

    def save(self):
        SENT_FILE.write_text(json.dumps(list(self.sent_users), ensure_ascii=False))
        STATS_FILE.write_text(json.dumps(self.stats, indent=2, ensure_ascii=False))

    def mark_sent(self, username: str, account: str):
        self.sent_users.add(username)
        self.stats["total_sent"] += 1
        self.stats["sent_today"] += 1
        acc_stats = self.stats["by_account"].setdefault(account, {"sent": 0})
        acc_stats["sent"] += 1
        self.save()

    def already_sent(self, username: str) -> bool:
        return username in self.sent_users

    def account_limit_reached(self, account: str) -> bool:
        acc = self.stats["by_account"].get(account, {})
        return acc.get("sent", 0) >= DAILY_LIMIT_PER_ACCOUNT


# ══════════════════════════════════════════════════════════════════════════════
# Callback para el Dashboard en tiempo real (WebSocket)
# ══════════════════════════════════════════════════════════════════════════════

# Cola global de eventos para el dashboard
_event_queue: asyncio.Queue | None = None


def set_event_queue(queue: asyncio.Queue):
    global _event_queue
    _event_queue = queue


async def _emit(event_type: str, data: dict):
    """Envía un evento al dashboard vía WebSocket."""
    if _event_queue:
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data,
        }
        await _event_queue.put(json.dumps(event))


# ══════════════════════════════════════════════════════════════════════════════
# Pipeline Principal
# ══════════════════════════════════════════════════════════════════════════════

async def prospect_with_account(
    pool: BrowserPool,
    account: dict,
    targets: list[str],
    state: GhostState,
) -> dict:
    """
    Ejecuta la prospección con UNA cuenta:
    1. Abre navegador visible
    2. Login en Instagram
    3. Por cada target: scrapea perfil → genera DM con LLM → envía con ratón fantasma
    """
    username = account["username"]
    results = {"sent": 0, "failed": 0, "skipped": 0}

    await _emit("account_start", {"account": username, "targets": len(targets)})

    try:
        ghost = await pool.get_browser(username)
        success = await ig_login(ghost)

        if not success:
            await _emit("login_failed", {"account": username})
            logger.error(f"[@{username}] Login fallido — saltando cuenta")
            return results

        await _emit("login_ok", {"account": username})

        for target in targets:
            # Verificar límites
            if state.account_limit_reached(username):
                await _emit("limit_reached", {"account": username})
                logger.info(f"[@{username}] Límite diario alcanzado")
                break

            if state.already_sent(target):
                results["skipped"] += 1
                continue

            try:
                # 1. Scrapear perfil del target
                await _emit("scraping", {
                    "account": username,
                    "target": target,
                    "action": f"Analizando perfil @{target}...",
                })

                profile = await scrape_profile(ghost, target)
                if not profile:
                    results["failed"] += 1
                    continue

                # Pausa de "lectura" humana
                await asyncio.sleep(random.uniform(READ_PAUSE_MIN, READ_PAUSE_MAX))

                # 2. Generar DM con LLM
                await _emit("generating_dm", {
                    "account": username,
                    "target": target,
                    "bio": profile.get("bio", "")[:80],
                    "followers": profile.get("followers", 0),
                })

                dm_text = await generate_dm(
                    business_name=profile.get("name", target),
                    username=target,
                    bio=profile.get("bio", ""),
                    followers=profile.get("followers", 0),
                )

                # 3. Enviar DM con ratón fantasma
                await _emit("sending_dm", {
                    "account": username,
                    "target": target,
                    "message_preview": dm_text[:60] + "...",
                })

                ok = await send_dm(ghost, target, dm_text)

                if ok:
                    state.mark_sent(target, username)
                    results["sent"] += 1

                    await _emit("dm_sent", {
                        "account": username,
                        "target": target,
                        "message": dm_text[:100],
                        "total_today": state.stats["sent_today"],
                        "total_all": state.stats["total_sent"],
                    })

                    logger.info(
                        f"[@{username}] ✅ DM #{state.stats['sent_today']} → @{target}"
                    )
                else:
                    results["failed"] += 1
                    await _emit("dm_failed", {"account": username, "target": target})

                # 4. Delay anti-ban entre DMs
                delay = random.uniform(BETWEEN_DMS_MIN, BETWEEN_DMS_MAX)
                await _emit("waiting", {
                    "account": username,
                    "seconds": round(delay),
                    "action": f"Esperando {delay:.0f}s antes del siguiente...",
                })
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"[@{username}] Error con @{target}: {e}")
                results["failed"] += 1

                # Si parece ban, parar esta cuenta
                err = str(e).lower()
                if any(w in err for w in ["spam", "block", "restrict", "challenge"]):
                    await _emit("account_banned", {"account": username, "error": str(e)[:100]})
                    logger.error(f"[@{username}] 🚨 POSIBLE BAN — parando cuenta")
                    break

    except Exception as e:
        logger.error(f"[@{username}] Error crítico: {e}")

    await _emit("account_done", {"account": username, **results})
    return results


async def run_campaign(
    hashtags: list[str] | None = None,
    target_usernames: list[str] | None = None,
    dry_run: bool = False,
):
    """
    Ejecuta una campaña completa de prospección:
    1. Busca targets por hashtags (o usa lista directa)
    2. Reparte targets entre cuentas
    3. Lanza navegadores en paralelo (con semáforo)
    4. Envía DMs con ratón fantasma
    """
    if not ACCOUNTS:
        logger.error("❌ No hay cuentas configuradas en config.py")
        await _emit("error", {"message": "No hay cuentas en config.py"})
        return

    state = GhostState()
    pool = BrowserPool(ACCOUNTS)
    targets_to_process: list[str] = list(target_usernames or [])

    hashtags = hashtags or TARGET_HASHTAGS

    await _emit("campaign_start", {
        "accounts": len(ACCOUNTS),
        "hashtags": hashtags,
        "existing_targets": len(targets_to_process),
    })

    # ── Fase 1: Buscar targets si no tenemos una lista directa ────────
    if not targets_to_process and hashtags:
        logger.info("🔍 Fase 1: Buscando targets por hashtags...")
        # Usar la primera cuenta para buscar
        first_acc = ACCOUNTS[0]
        ghost = await pool.get_browser(first_acc["username"])
        await ig_login(ghost)

        for tag in hashtags[:5]:
            await _emit("searching_hashtag", {"hashtag": tag})
            found = await search_hashtag_targets(ghost, tag, limit=15)
            for u in found:
                if not state.already_sent(u) and u not in targets_to_process:
                    targets_to_process.append(u)
            await asyncio.sleep(random.uniform(3, 6))

        logger.info(f"📋 {len(targets_to_process)} targets encontrados")

    if not targets_to_process:
        logger.warning("⚠️ No se encontraron targets")
        await _emit("no_targets", {})
        await pool.close_all()
        return

    # ── Fase 2: Repartir targets entre cuentas ────────────────────────
    active_accounts = [a for a in ACCOUNTS if not state.account_limit_reached(a["username"])]
    if not active_accounts:
        logger.warning("⚠️ Todas las cuentas han alcanzado su límite diario")
        await _emit("all_limits_reached", {})
        await pool.close_all()
        return

    # Distribuir targets equitativamente
    chunks: dict[str, list[str]] = {a["username"]: [] for a in active_accounts}
    for i, target in enumerate(targets_to_process):
        acc_name = active_accounts[i % len(active_accounts)]["username"]
        chunks[acc_name].append(target)

    await _emit("targets_distributed", {
        "total_targets": len(targets_to_process),
        "accounts": len(active_accounts),
    })

    # ── Fase 3: Ejecutar en paralelo (limitado por semáforo) ──────────
    logger.info(f"🚀 Fase 2: Lanzando {len(active_accounts)} cuentas en paralelo...")

    sem = asyncio.Semaphore(MAX_CONCURRENT_BROWSERS)
    total_results = {"sent": 0, "failed": 0, "skipped": 0}

    async def _run_account(acc):
        async with sem:
            r = await prospect_with_account(pool, acc, chunks[acc["username"]], state)
            total_results["sent"] += r["sent"]
            total_results["failed"] += r["failed"]
            total_results["skipped"] += r["skipped"]

    tasks = [_run_account(acc) for acc in active_accounts if chunks.get(acc["username"])]
    await asyncio.gather(*tasks)

    # ── Fase 4: Cierre ────────────────────────────────────────────────
    await pool.close_all()
    state.save()

    await _emit("campaign_done", {
        **total_results,
        "total_today": state.stats["sent_today"],
        "total_ever": state.stats["total_sent"],
    })

    logger.info(
        f"🏁 Campaña terminada | "
        f"Enviados: {total_results['sent']} | "
        f"Fallidos: {total_results['failed']} | "
        f"Hoy total: {state.stats['sent_today']}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Ejecución directa: python ghost_bot.py
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════╗
    ║   🖱️  SISTEMA 180 — RATÓN FANTASMA v1.0     ║
    ║   Ghost Mouse Instagram Prospector           ║
    ╚══════════════════════════════════════════════╝
    """)
    asyncio.run(run_campaign())
