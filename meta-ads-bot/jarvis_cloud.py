"""
jarvis_cloud.py — Sistema 180
Funcionalidades cloud de JARVIS que no necesitan PC local.
Incluye: reportes automáticos, facturación, lead scoring,
recordatorios, renovaciones, cloud code, y respuestas IG.
"""
import os, json, logging, re, time, threading
from datetime import datetime, timedelta, date
from pathlib import Path

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# 1. REPORTE DIARIO AUTOMÁTICO
# ══════════════════════════════════════════════════════════════════════════════

def generate_daily_report() -> str:
    """Genera reporte diario con métricas del sistema."""
    lines = ["📊 *REPORTE DIARIO — Sistema 180*\n"]
    lines.append(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    # IG Stats
    try:
        from ig_multi_account import AccountStore
        store = AccountStore()
        accs = store.get_all()
        active = sum(1 for a in accs if a.get("active") and a.get("status") == "ok")
        total_today = sum(a.get("sent_today", 0) for a in accs)
        total_all = sum(a.get("sent_total", 0) for a in accs)
        lines.append("📱 *Instagram:*")
        lines.append(f"  • Cuentas activas: {active}/{len(accs)}")
        lines.append(f"  • DMs hoy: {total_today}")
        lines.append(f"  • DMs histórico: {total_all}")
    except Exception:
        lines.append("📱 Instagram: sin datos")

    # Outreach DB stats
    try:
        from outreach_db import get_conn
        with get_conn() as conn:
            total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            today = date.today().isoformat()
            new_today = conn.execute(
                "SELECT COUNT(*) FROM leads WHERE date(created_at)=?", (today,)
            ).fetchone()[0]
            total_dms = conn.execute("SELECT COUNT(*) FROM dms").fetchone()[0]
            replied = conn.execute(
                "SELECT COUNT(*) FROM dms WHERE status='replied'"
            ).fetchone()[0]
        reply_rate = f"{(replied / max(total_dms, 1) * 100):.1f}%"
        lines.append(f"\n📈 *Outreach:*")
        lines.append(f"  • Leads totales: {total_leads}")
        lines.append(f"  • Nuevos hoy: {new_today}")
        lines.append(f"  • DMs enviados: {total_dms}")
        lines.append(f"  • Tasa respuesta: {reply_rate}")
    except Exception:
        lines.append("\n📈 Outreach: sin datos")

    # Notion clients
    try:
        from integrations import notion_get_clients
        clients = notion_get_clients("Activo")
        mrr = sum(c.get("precio", 0) for c in clients)
        lines.append(f"\n💰 *Clientes:*")
        lines.append(f"  • Activos: {len(clients)}")
        lines.append(f"  • MRR: {mrr}€/mes")
    except Exception:
        lines.append("\n💰 Clientes: sin datos")

    # System health
    try:
        from resilience import metrics
        m = metrics.get_metrics()
        total_calls = sum(m["api_calls"].values())
        total_errors = sum(m["api_errors"].values())
        uptime_h = m["uptime_seconds"] // 3600
        lines.append(f"\n🔧 *Sistema:*")
        lines.append(f"  • Uptime: {uptime_h}h")
        lines.append(f"  • API calls: {total_calls}")
        lines.append(f"  • Errores: {total_errors}")
    except Exception:
        pass

    lines.append(f"\n_Generado automáticamente por JARVIS_")
    return "\n".join(lines)


def generate_weekly_report() -> str:
    """Genera dashboard semanal resumido."""
    lines = ["📊 *DASHBOARD SEMANAL — Sistema 180*\n"]
    lines.append(f"📅 Semana del {(datetime.now() - timedelta(days=7)).strftime('%d/%m')} al {datetime.now().strftime('%d/%m/%Y')}\n")

    try:
        from outreach_db import get_conn
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        with get_conn() as conn:
            new_leads = conn.execute(
                "SELECT COUNT(*) FROM leads WHERE created_at >= ?", (week_ago,)
            ).fetchone()[0]
            new_dms = conn.execute(
                "SELECT COUNT(*) FROM dms WHERE sent_at >= ?", (week_ago,)
            ).fetchone()[0]
            new_replies = conn.execute(
                "SELECT COUNT(*) FROM dms WHERE status='replied' AND sent_at >= ?", (week_ago,)
            ).fetchone()[0]
        lines.append(f"🎯 *Prospección esta semana:*")
        lines.append(f"  • Nuevos leads: {new_leads}")
        lines.append(f"  • DMs enviados: {new_dms}")
        lines.append(f"  • Respuestas: {new_replies}")
        conv_rate = f"{(new_replies / max(new_dms, 1) * 100):.1f}%"
        lines.append(f"  • Tasa conversión: {conv_rate}")
    except Exception:
        lines.append("Sin datos de prospección esta semana.")

    try:
        from integrations import notion_get_clients
        clients = notion_get_clients("Activo")
        mrr = sum(c.get("precio", 0) for c in clients)
        lines.append(f"\n💰 *Financiero:*")
        lines.append(f"  • MRR actual: {mrr}€")
        lines.append(f"  • Clientes activos: {len(clients)}")
        lines.append(f"  • Ingreso anual proyectado: {mrr * 12}€")
    except Exception:
        pass

    lines.append(f"\n_Dashboard semanal JARVIS_")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# 2. FACTURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

def create_invoice(client_name: str, amount: float, concept: str = "Servicio mensual") -> dict:
    """Crea factura en Notion y notifica por Slack."""
    try:
        from integrations import _notion_post, NOTION_HEADERS, slack_send, SLACK_CHANNELS
        FACTURAS_DB = os.getenv("NOTION_FACTURAS_DB_ID", "")
        if not FACTURAS_DB:
            return {"ok": False, "error": "NOTION_FACTURAS_DB_ID no configurado"}

        invoice_id = f"F-{datetime.now().strftime('%Y%m%d%H%M')}"
        payload = {
            "parent": {"database_id": FACTURAS_DB},
            "properties": {
                "Factura": {"title": [{"text": {"content": invoice_id}}]},
                "Cliente": {"rich_text": [{"text": {"content": client_name}}]},
                "Importe": {"number": amount},
                "Concepto": {"rich_text": [{"text": {"content": concept}}]},
                "Estado": {"select": {"name": "Pendiente"}},
                "Fecha": {"date": {"start": date.today().isoformat()}},
            }
        }
        r = _notion_post("https://api.notion.com/v1/pages", payload)
        if r.ok:
            # Notify Slack
            ch = SLACK_CHANNELS.get("clientes_facturas", "")
            if ch:
                slack_send(
                    f"💰 *Factura {invoice_id}*\n"
                    f"Cliente: {client_name}\n"
                    f"Importe: {amount}€\n"
                    f"Estado: Pendiente",
                    channel=ch
                )
            return {"ok": True, "invoice_id": invoice_id}
        return {"ok": False, "error": r.text[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# 3. LEAD SCORING (IA)
# ══════════════════════════════════════════════════════════════════════════════

def score_lead(username: str, bio: str = "", followers: int = 0,
               posts: int = 0, is_business: bool = False) -> dict:
    """Puntúa un lead del 1-10 con IA."""
    score = 5  # base

    # Business account bonus
    if is_business:
        score += 2

    # Followers sweet spot (500-50k = local businesses)
    if 500 <= followers <= 50000:
        score += 1
    elif followers > 50000:
        score -= 1  # probably too big

    # Active posting
    if posts > 50:
        score += 1

    # Bio keywords (Spanish business indicators)
    biz_keywords = [
        "restaurante", "peluquería", "clínica", "tienda", "bar",
        "cafetería", "estética", "fisio", "dentist", "abogado",
        "inmobiliaria", "hotel", "taller", "gym", "academia",
        "consultoría", "asesoría", "gestoría", "farmacia",
    ]
    bio_lower = bio.lower()
    if any(kw in bio_lower for kw in biz_keywords):
        score += 2

    # Contact info in bio = high intent
    if re.search(r"(📞|☎|whatsapp|tlf|tel[eé]fono|contacto|reserv)", bio_lower):
        score += 1

    score = max(1, min(10, score))

    tier = "🔥 HOT" if score >= 8 else "🟢 WARM" if score >= 5 else "🔵 COLD"

    return {
        "username": username,
        "score": score,
        "tier": tier,
        "reasons": [],
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4. RECORDATORIOS DE CLIENTES
# ══════════════════════════════════════════════════════════════════════════════

def check_client_followups(days_threshold: int = 7) -> list[dict]:
    """Detecta clientes sin contacto en X días."""
    alerts = []
    try:
        from integrations import notion_get_clients
        clients = notion_get_clients("Activo")
        today = datetime.now()
        for c in clients:
            alta = c.get("alta", "")
            if alta:
                alta_date = datetime.strptime(alta, "%Y-%m-%d")
                days_since = (today - alta_date).days
                # Alert if first week or every 30 days
                if days_since == 7 or days_since % 30 == 0:
                    alerts.append({
                        "nombre": c["nombre"],
                        "servicio": c["servicio"],
                        "days_since_alta": days_since,
                        "tipo": "followup" if days_since > 7 else "onboarding",
                    })
    except Exception as e:
        logger.error(f"Followup check error: {e}")
    return alerts


def check_renewals(days_before: int = 7) -> list[dict]:
    """Detecta renovaciones próximas."""
    alerts = []
    try:
        from integrations import notion_get_clients
        clients = notion_get_clients("Activo")
        today = datetime.now()
        for c in clients:
            alta = c.get("alta", "")
            if alta:
                alta_date = datetime.strptime(alta, "%Y-%m-%d")
                # Monthly renewal
                next_renewal = alta_date
                while next_renewal < today:
                    next_renewal += timedelta(days=30)
                days_until = (next_renewal - today).days
                if 0 <= days_until <= days_before:
                    alerts.append({
                        "nombre": c["nombre"],
                        "servicio": c["servicio"],
                        "precio": c["precio"],
                        "renewal_date": next_renewal.strftime("%d/%m/%Y"),
                        "days_until": days_until,
                    })
    except Exception as e:
        logger.error(f"Renewal check error: {e}")
    return alerts


# ══════════════════════════════════════════════════════════════════════════════
# 5. CLOUD CODE — Ejecutar código con Claude API (sin PC local)
# ══════════════════════════════════════════════════════════════════════════════

def cloud_code_execute(instruction: str) -> str:
    """Ejecuta una tarea de código usando Claude API directamente en la nube.
    Guarda el código para ejecución y pide confirmación."""
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "Error: ANTHROPIC_API_KEY no configurada."

        client = anthropic.Anthropic(api_key=api_key, timeout=60.0)

        # Read relevant project context
        context_files = {}
        bot_dir = Path(__file__).parent
        root_dir = bot_dir.parent  # ~/proyectos/sistema-180
        
        # Mapear estructura del repositorio para que JARVIS entienda dónde está
        import subprocess
        try:
            tree_output = subprocess.run(["ls", "-la", str(root_dir)], capture_output=True, text=True, timeout=5).stdout
            context_files["[ROOT_DIR_ESTRUCTURA]"] = tree_output[:2000]
        except Exception:
            pass
        
        # Archivos de arquitectura globales
        global_files = ["ARCHITECTURE.md", "SISTEMA_MAESTRO_COMPLETO.md"]
        for gf in global_files:
            fp = root_dir / gf
            if fp.exists():
                content = fp.read_text(encoding="utf-8", errors="ignore")
                context_files[f"[ROOT] {gf}"] = "\n".join(content.split("\n")[:300])  # First 300 lines

        # Archivos clave del bot
        key_files = ["bot.py", "integrations.py", "jarvis_cloud.py", "jarvis_nlp_router.py"]
        for f in key_files:
            fp = bot_dir / f
            if fp.exists():
                content = fp.read_text(encoding="utf-8", errors="ignore")
                # Only first 200 lines per file to save tokens
                lines = content.split("\n")[:200]
                context_files[f] = "\n".join(lines)

        context = "\n\n".join(
            f"=== {name} (primeras 200 líneas) ===\n{code}"
            for name, code in context_files.items()
        )

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": (
                    f"Eres JARVIS, programador experto en Python con acceso root al servidor en la nube de Railway. "
                    f"Proyecto: Sistema 180 (bot Telegram + CRM + IG prospecting).\n"
                    f"REPOSITORIO OFICIAL GITHUB: https://github.com/admins-dev/sistema-180.git\n"
                    f"CREDENCIAL SECRETA: claude (para accesos internos/Github si requiere autenticación).\n\n"
                    f"CONTEXTO DEL CÓDIGO ACTUAL:\n{context[:15000]}\n\n"
                    f"TAREA DEL SEÑOR: {instruction}\n\n"
                    f"Responde con una muy breve explicación y luego el código necesario dentro de un ÚNICO bloque ```python ... ``` o script bash ```bash ... ```. "
                    f"El código debe ser un script ejecutable. Si el señor pide actualizar el código en Github, genera un script en os.system() o subprocess ejecutando git add, git commit y git push."
                )
            }]
        )
        
        reply = response.content[0].text
        
        # Extract python code
        match = re.search(r"```python\n(.*?)\n```", reply, re.DOTALL)
        if match:
            code = match.group(1)
            pending_file = Path(__file__).parent / "cloud_pending.py"
            pending_file.write_text(code, encoding="utf-8")
            
            return (f"🧠 *Código generado por JARVIS en Cloud:*\n\n{reply[:3000]}\n\n"
                    f"⚠️ **Código listo en el servidor.** Para ejecutarlo, dígame:\n"
                    f"👉 *'Sí JARVIS, ejecuta el código en la nube'* o envíe `/ejecutar_nube`")
        else:
            return f"Respuesta de nube (sin código ejecutable):\n\n{reply[:4000]}"

    except Exception as e:
        logger.error(f"Cloud code error: {e}")
        return f"Error generando Cloud Code: {e}"


def cloud_code_run() -> str:
    """Ejecuta el código pendiente en la nube de forma segura."""
    pending_file = Path(__file__).parent / "cloud_pending.py"
    if not pending_file.exists():
        return "Sir, no tengo ningún código pendiente en memoria para ejecutar."
        
    try:
        import subprocess
        logger.info("[Cloud] Ejecutando cloud_pending.py")
        result = subprocess.run(
            ["python", str(pending_file)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout
        err = result.stderr
        
        # Eliminar tras ejecución para seguridad
        # pending_file.unlink()
        
        res_msg = f"✅ *EJECUCIÓN COMPLETADA*\n\n"
        if output:
            res_msg += f"**Output:**\n```\n{output[:3500]}\n```\n"
        if err:
            res_msg += f"**Errors:**\n```\n{err[:1000]}\n```\n"
            
        if not output and not err:
            res_msg += "El script se ejecutó sin salida de texto (silencioso)."
            
        return res_msg
        
    except subprocess.TimeoutExpired:
        return "⏳ Error: La ejecución excedió los 120 segundos de tiempo máximo."
    except Exception as e:
        logger.error(f"Cloud exec error: {e}")
        return f"❌ Fallo crítico al ejecutar: {str(e)}"


# ══════════════════════════════════════════════════════════════════════════════
# 6. SCHEDULER — Programador de tareas automáticas
# ══════════════════════════════════════════════════════════════════════════════

class CloudScheduler:
    """Ejecuta tareas programadas sin necesitar PC local."""

    def __init__(self):
        self._telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self._chat_id = (os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
                         .split(",")[0].strip())
        self._last_daily = ""
        self._last_weekly = ""

    def start(self):
        """Arranca scheduler en thread daemon."""
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
        logger.info("[Scheduler] Cloud scheduler started")

    def _loop(self):
        time.sleep(60)  # wait for boot
        while True:
            try:
                now = datetime.now()
                today = now.strftime("%Y-%m-%d")
                week = now.strftime("%Y-W%W")

                # Daily report at 9:00 AM
                if now.hour == 9 and today != self._last_daily:
                    self._last_daily = today
                    report = generate_daily_report()
                    self._send_telegram(report)

                    # Check followups
                    followups = check_client_followups()
                    for f in followups:
                        self._send_telegram(
                            f"📞 *Recordatorio {f['tipo']}*\n"
                            f"Cliente: {f['nombre']}\n"
                            f"Servicio: {f['servicio']}\n"
                            f"Días desde alta: {f['days_since_alta']}"
                        )

                    # Check renewals
                    renewals = check_renewals()
                    for r in renewals:
                        self._send_telegram(
                            f"🔄 *Renovación próxima*\n"
                            f"Cliente: {r['nombre']}\n"
                            f"Servicio: {r['servicio']}\n"
                            f"Precio: {r['precio']}€\n"
                            f"Fecha: {r['renewal_date']} ({r['days_until']} días)"
                        )

                # Weekly report on Mondays at 10:00
                if now.weekday() == 0 and now.hour == 10 and week != self._last_weekly:
                    self._last_weekly = week
                    report = generate_weekly_report()
                    self._send_telegram(report)

            except Exception as e:
                logger.error(f"[Scheduler] Error: {e}")

            time.sleep(300)  # check every 5 min

    def _send_telegram(self, msg: str):
        """Send message to admin via Telegram."""
        if not self._telegram_token or not self._chat_id:
            return
        try:
            import requests
            requests.post(
                f"https://api.telegram.org/bot{self._telegram_token}/sendMessage",
                json={
                    "chat_id": self._chat_id,
                    "text": msg,
                    "parse_mode": "Markdown",
                },
                timeout=10,
            )
        except Exception as e:
            logger.error(f"[Scheduler] Telegram send error: {e}")


# Global scheduler
cloud_scheduler = CloudScheduler()
