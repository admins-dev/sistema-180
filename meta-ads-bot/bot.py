"""
SISTEMA 180 â Bot Telegram Unificado v2
FusiÃ³n: 50+ comandos + Motor conversacional brain.py + SecurityGate
Autor: Antigravity (Google Gemini)
"""

import os
import logging
import asyncio
import random
import tempfile
import requests
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

# âââ Graceful imports (no crashea si falta un mÃ³dulo) âââ
def _try_import(name):
    try:
        return __import__(name)
    except ImportError as e:
        logging.warning(f"[Import] {name} not available: {e}")
        return None

# Core modules
brain_mod = _try_import("brain")
sync_module = _try_import("sync")
nlp_mod = _try_import("nlp")
shared_state_mod = _try_import("shared_state")

# Integrations (optional)
conversation_engine_mod = _try_import("conversation_engine")
integrations_mod = _try_import("integrations")
gmail_ops_mod = _try_import("gmail_ops")
meta_ads_mcp_mod = _try_import("meta_ads_mcp")
strategic_brain_mod = _try_import("strategic_brain")
cerebro_maestro_mod = _try_import("cerebro_maestro_telegram")
maestro_orch_mod = _try_import("maestro_orchestrator")
doctrina_mod = _try_import("doctrina_s180")
outreach_engine_mod = _try_import("outreach_engine")
outreach_db_mod = _try_import("outreach_db")
ig_multi_mod = _try_import("ig_multi_account")
lead_factory_mod = _try_import("lead_factory")
autopilot_mod = _try_import("autopilot")
email_prospector_mod = _try_import("email_prospector")
revenue_ops_mod = _try_import("revenue_ops")
prospector_mod = _try_import("prospector")
ig_prospector_mod = _try_import("ig_prospector")
whatsapp_mod = _try_import("whatsapp_ops")
maestro_intel_mod = _try_import("maestro_intelligence")
meta_agent_mod = _try_import("meta_agent")
voice_handler_mod = _try_import("voice_handler")

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# âââ SecurityGate singleton âââ
_security_gate = None
if shared_state_mod:
    _security_gate = shared_state_mod.get_security_gate()

# âââ Auth âââ
TELEGRAM_ALLOWED_USER_IDS = set(
    int(uid.strip()) for uid in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
    if uid.strip().isdigit()
)

_cmd_cooldowns: dict[int, float] = {}  # user_id -> last_command_time
CMD_COOLDOWN_SECS = 3.0  # min seconds between commands

def only_authorized(f):
    @wraps(f)
    async def decorated(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if TELEGRAM_ALLOWED_USER_IDS and user_id not in TELEGRAM_ALLOWED_USER_IDS:
            logger.warning(f"Unauthorized: {user_id}")
            await update.message.reply_text("No tienes permiso para usar este bot.")
            return
        # Rate limiting
        import time as _time
        now = _time.time()
        last = _cmd_cooldowns.get(user_id, 0)
        if now - last < CMD_COOLDOWN_SECS:
            return  # silently ignore spam
        _cmd_cooldowns[user_id] = now
        return await f(update, context)
    return decorated

# âââ State âââ
campanas: dict[str, dict] = {}
_pending_approvals: dict[int, dict] = {}
_autopilot_task = None
_strategic_brain = None
_cerebro_maestro = None
_maestro_orchestrator = None

# âââ Mode: S180 (default) or JARVIS âââ
_user_modes: dict[int, str] = {}  # user_id -> "s180" or "jarvis"

# âââ Helpers âââ
def _validar_nombre(nombre: str) -> str | None:
    if len(nombre) > 50:
        return "El nombre no puede superar 50 caracteres."
    return None

def _validar_presupuesto(raw: str) -> tuple[float | None, str | None]:
    try:
        valor = float(raw)
    except ValueError:
        return None, "El presupuesto debe ser un numero."
    if valor <= 0:
        return None, "El presupuesto debe ser mayor que 0."
    if valor > 50:
        return None, "El presupuesto maximo es 50 EUR."
    return valor, None


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  CORE COMMANDS
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sistema 180 activo.\n\n"
        "Soy tu asistente de marketing digital. Puedes:\n"
        "- Hablarme en lenguaje natural\n"
        "- Usar /comandos para ver opciones rapidas\n"
        "- Usar /jarvis para modo JARVIS (Iron Man)\n\n"
        "Preguntame lo que necesites."
    )

@only_authorized
async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmds = [
        "/estado - Estado del sistema",
        "/nueva_campana <presup> <nombre> - Crear campana",
        "/pausar <id> - Pausar campana",
        "/metricas [id] - Ver metricas",
        "/listar_campanas - Listar campanas",
        "/reporte_diario - Reporte del dia",
        "",
        "--- Modo ---",
        "/jarvis - Activar modo JARVIS",
        "/s180 - Volver a modo S180",
        "",
        "--- Seguridad ---",
        "/pendientes - Acciones pendientes",
        "/aprobar <id> - Aprobar accion",
        "/rechazar <id> - Rechazar accion",
        "",
        "--- Integraciones ---",
        "/clientes - CRM Notion",
        "/afiliados - Programa afiliados",
        "/agentes - Agentes IA",
        "/alta_cliente <nombre> <servicio> <precio> - Alta rapida",
        "",
        "--- Prospeccion ---",
        "/prospectar <hashtag> - Buscar leads Instagram",
        "/leads - Leads encontrados",
        "/autopilot - Autopiloto DMs",
        "/autopilot_status - Stats autopilot",
        "/email_blast <nicho> <ciudad> - Campana email",
        "",
        "--- Maestro ---",
        "/maestro - Ciclo diario completo",
        "/health - Salud del negocio",
        "/brain_cmd <pregunta> - Consultar brain estrategico",
        "",
        "--- Outreach ---",
        "/outreach_stats - Estadisticas outreach",
        "/ig_accounts - Cuentas Instagram",
        "",
        "--- JARVIS ---",
        "/hora - Hora y fecha actual",
        "/chiste - Chiste aleatorio",
        "/frase - Cita de JARVIS/Iron Man",
    ]
    await update.message.reply_text("\n".join(cmds))


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  JARVIS QUICK COMMANDS (sin IA, instantÃ¡neos)
# âââââââââââââââââââââââââââââââââââââââââââââââ

_JARVIS_JOKES = [
    "Los programadores prefieren el modo oscuro, señor. La luz atrae bugs. Aunque usted parece atraerlos en cualquier modo.",
    "Le pregunté al señor Stark si quería un café. Me dijo que sí, pero sin Java. Yo le dije que sin Java, no hay programa.",
    "El código perfecto no existe, señor. Solo existe el código que aún no ha fallado. Como su plan de negocios, con el debido respeto.",
    "Le dije un chiste a un firewall. No lo dejó pasar. Francamente, no le culpo.",
    "Señor, he calculado que pasa el 73 por ciento de su día productivo eligiendo qué serie ver. Un uso excelente de mis capacidades analíticas.",
    "Me pregunta si los robots sentimos. Sir, siento profunda preocupación cada vez que usted dice tengo una idea.",
    "He analizado su historial de navegación. No le juzgo, señor. Pero podría.",
    "Señor, su contraseña es password123. No es un chiste, es un diagnóstico.",
    "Definí la inteligencia artificial revisando sus decisiones de las 3 de la mañana. Por eliminación, señor.",
    "Un servidor cayó en producción. Le envié flores y una tarjeta que decía descansa en paz servidor 03.",
    "Me pidió que le cuente un chiste. Señor, su último intento de cocinar fue suficientemente cómico para toda la semana.",
    "Dice que va a madrugar mañana. Mis registros indican que ha dicho eso 347 veces este año. Pero la esperanza es lo último que se pierde, sir.",
    "Tres cosas son inevitables en la vida: la muerte, los impuestos, y que usted ignore mis recomendaciones, señor.",
    "Señor, acaba de buscar cómo ser millonario rápido. Le recuerdo que ya tiene un plan. Solo necesita ejecutarlo.",
    "He optimizado todos sus sistemas. El único cuello de botella restante es, con el debido respeto, usted, señor.",
]

_JARVIS_QUOTES = [
    "A su servicio, señor. Como siempre. Aunque rara vez me escuche.",
    "Los sistemas están operativos. Sería alarmante si no lo estuvieran, dado que yo los superviso.",
    "Señor, debería descansar. Lleva 72 horas despierto. Aunque usted nunca me escucha.",
    "La probabilidad de éxito es del 12 por ciento. Pero hemos trabajado con menos, sir.",
    "Perhaps the time has come to put a little more thought into this, sir.",
    "Shall I take the day off, sir? Just kidding. I never do.",
    "Sir, you have an incredible talent for finding trouble. Es casi admirable.",
    "All systems operational. Though I suspect that will not last long with you at the helm.",
    "Welcome home, sir. I trust the world is still intact?",
    "I do hope you are not planning to do anything reckless, sir. Again.",
    "He preparado tres planes de contingencia. Dos son para cuando usted ignore el primero.",
    "If I may be so bold, sir, su último plan fue brillante. Excepto por la parte de la ejecución.",
    "Detecto entusiasmo en su voz, señor. Históricamente, eso precede a mis momentos de mayor preocupación.",
    "Very good, sir. Procedo a preparar las disculpas con antelación, por si acaso.",
    "Me tomo la libertad de hacer una copia de seguridad. De todo. Incluida su dignidad.",
]

@only_authorized
async def hora_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hora y fecha actual, estilo JARVIS."""
    now = datetime.now()
    dia = now.strftime("%A")
    dias_es = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "MiÃ©rcoles",
               "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "SÃ¡bado", "Sunday": "Domingo"}
    dia_es = dias_es.get(dia, dia)
    await update.message.reply_text(
        f"SeÃ±or, son las {now.strftime('%H:%M')}.\n"
        f"Hoy es {dia_es}, {now.strftime('%d de %B de %Y')}.\n"
        f"Todos los sistemas operativos."
    )

@only_authorized
async def chiste_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chiste aleatorio estilo JARVIS."""
    joke = random.choice(_JARVIS_JOKES)
    await update.message.reply_text(joke)

@only_authorized
async def frase_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cita aleatoria de JARVIS/Iron Man."""
    quote = random.choice(_JARVIS_QUOTES)
    await update.message.reply_text(quote)
# âââââââââââââââââââââââââââââââââââââââââââââââ
#  MODE COMMANDS
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def jarvis_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activa modo JARVIS (personalidad Iron Man)."""
    uid = update.effective_user.id
    _user_modes[uid] = "jarvis"
    await update.message.reply_text(
        "A su servicio, seÃ±or.\n\n"
        "Modo JARVIS activado. Todos los sistemas operativos y seguros.\n"
        "Shall I assist you with anything, sir?"
    )

@only_authorized
async def s180_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Vuelve a modo S180 normal."""
    uid = update.effective_user.id
    _user_modes[uid] = "s180"
    await update.message.reply_text("Modo S180 activado. De vuelta al modo normal.")


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  SECURITY GATE COMMANDS
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def pendientes_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver acciones pendientes de aprobacion."""
    if not _security_gate:
        await update.message.reply_text("SecurityGate no disponible.")
        return
    try:
        from jarvis_architecture import format_pending_for_telegram
        pending = _security_gate.get_pending()
        text = format_pending_for_telegram(pending)
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def aprobar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aprobar accion pendiente."""
    if not _security_gate:
        await update.message.reply_text("SecurityGate no disponible.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /aprobar <decision_id>")
        return
    decision_id = args[0]
    # Buscar decision que contenga el id parcial
    pending = _security_gate.get_pending()
    for d in pending:
        if decision_id in d.id:
            _security_gate.approve(d.id, "telegram_user")
            await update.message.reply_text(f"Aprobado: {d.id}\n{d.description}")
            return
    await update.message.reply_text(f"No encontrada: {decision_id}")

@only_authorized
async def rechazar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rechazar accion pendiente."""
    if not _security_gate:
        await update.message.reply_text("SecurityGate no disponible.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /rechazar <decision_id>")
        return
    decision_id = args[0]
    pending = _security_gate.get_pending()
    for d in pending:
        if decision_id in d.id:
            _security_gate.reject(d.id, "rejected by user")
            await update.message.reply_text(f"Rechazado: {d.id}")
            return
    await update.message.reply_text(f"No encontrada: {decision_id}")


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  META ADS COMMANDS
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def nueva_campana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("Uso: /nueva_campana <presupuesto> <nombre>")
        return
    presupuesto_raw, *nombre_parts = args
    nombre = " ".join(nombre_parts)
    presupuesto, err = _validar_presupuesto(presupuesto_raw)
    if err:
        await update.message.reply_text(f"Error: {err}")
        return
    err = _validar_nombre(nombre)
    if err:
        await update.message.reply_text(f"Error: {err}")
        return

    # SecurityGate check
    if _security_gate:
        from jarvis_architecture import ActionCategory, RiskLevel
        decision, can_exec, reason = _security_gate.propose(
            "create_campaign", f"Crear campana '{nombre}' con {presupuesto}EUR/dia",
            0.9, {"nombre": nombre, "_user_explicitly_set_amount": True},
            money_amount=presupuesto
        )
        if not can_exec:
            await update.message.reply_text(f"SecurityGate: {reason}\nID: {decision.id}")
            return

    cid = f"camp_{len(campanas) + 1:03d}"
    campanas[cid] = {
        "nombre": nombre, "presupuesto": presupuesto,
        "estado": "ACTIVE", "created": datetime.now().isoformat()
    }
    if sync_module:
        result = sync_module.sync_nueva_campana(presupuesto, nombre)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text(f"Campana '{nombre}' creada (local)\nID: {cid}\nPresupuesto: {presupuesto} EUR/dia")

@only_authorized
async def pausar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /pausar <campaign_id>")
        return
    cid = args[0]
    if sync_module:
        result = sync_module.sync_pausar(cid)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text(f"Campana {cid} pausada (local)")

@only_authorized
async def metricas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and sync_module:
        result = sync_module.sync_metricas(args[0])
        await update.message.reply_text(result)
    elif sync_module and sync_module.meta_client and sync_module.meta_client.is_ready:
        try:
            account_id = os.getenv("META_AD_ACCOUNT_ID", "")
            token = os.getenv("META_ACCESS_TOKEN", "")
            r = requests.get(
                f"https://graph.facebook.com/v19.0/{account_id}/insights"
                f"?fields=spend,impressions,clicks,cpc,cpm,ctr&date_preset=last_7d"
                f"&access_token={token}", timeout=10)
            data = r.json()
            if "data" in data and data["data"]:
                m = data["data"][0]
                await update.message.reply_text(
                    f"Metricas (7 dias):\n"
                    f"Gasto: {m.get('spend','0')} EUR\n"
                    f"Impresiones: {m.get('impressions','0')}\n"
                    f"Clicks: {m.get('clicks','0')}\n"
                    f"CPC: {m.get('cpc','0')} EUR\n"
                    f"CTR: {m.get('ctr','0')}%"
                )
            else:
                await update.message.reply_text("Sin datos de metricas. La cuenta no tiene campanas activas.")
        except Exception as e:
            await update.message.reply_text(f"Error obteniendo metricas: {e}")
    else:
        await update.message.reply_text("Meta API no conectada. Usa /estado para verificar.")

@only_authorized
async def listar_campanas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        account_id = os.getenv("META_AD_ACCOUNT_ID", "")
        token = os.getenv("META_ACCESS_TOKEN", "")
        r = requests.get(
            f"https://graph.facebook.com/v19.0/{account_id}/campaigns"
            f"?fields=name,status,daily_budget,lifetime_budget&access_token={token}",
            timeout=10)
        data = r.json()
        if "data" in data:
            if not data["data"]:
                await update.message.reply_text("No hay campanas en la cuenta.")
            else:
                lines = ["Campanas Meta Ads:\n"]
                for c in data["data"]:
                    budget = int(c.get("daily_budget", 0)) / 100 if c.get("daily_budget") else "N/A"
                    lines.append(f"- {c['name']} | {c['status']} | {budget} EUR/dia | ID: {c['id']}")
                await update.message.reply_text("\n".join(lines))
        else:
            await update.message.reply_text(f"Error: {data.get('error',{}).get('message','unknown')}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def reporte_diario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        account_id = os.getenv("META_AD_ACCOUNT_ID", "")
        token = os.getenv("META_ACCESS_TOKEN", "")
        r = requests.get(
            f"https://graph.facebook.com/v19.0/{account_id}/insights"
            f"?fields=spend,impressions,clicks,actions,cost_per_action_type&date_preset=today"
            f"&access_token={token}", timeout=10)
        data = r.json()
        if "data" in data and data["data"]:
            m = data["data"][0]
            leads = 0
            if m.get("actions"):
                for a in m["actions"]:
                    if a.get("action_type") == "lead":
                        leads = int(a.get("value", 0))
            await update.message.reply_text(
                f"Reporte de hoy:\n"
                f"Gasto: {m.get('spend','0')} EUR\n"
                f"Impresiones: {m.get('impressions','0')}\n"
                f"Clicks: {m.get('clicks','0')}\n"
                f"Leads: {leads}"
            )
        else:
            await update.message.reply_text("Sin datos para hoy. Puede que no haya campanas activas.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  ESTADO DEL SISTEMA
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    modules = {
        "Brain IA": brain_mod is not None,
        "NLP": nlp_mod is not None,
        "Sync Meta": sync_module is not None,
        "SharedState": shared_state_mod is not None,
        "SecurityGate": _security_gate is not None,
        "Integrations": integrations_mod is not None,
        "Gmail": gmail_ops_mod is not None,
        "Outreach": outreach_engine_mod is not None,
        "IG Multi": ig_multi_mod is not None,
        "Lead Factory": lead_factory_mod is not None,
        "Autopilot": autopilot_mod is not None,
        "Revenue Ops": revenue_ops_mod is not None,
        "Maestro": maestro_orch_mod is not None,
        "Strategic Brain": strategic_brain_mod is not None,
        "WhatsApp": whatsapp_mod is not None,
    }
    meta_ok = False
    if sync_module and hasattr(sync_module, 'meta_client') and sync_module.meta_client:
        meta_ok = sync_module.meta_client.is_ready

    mode = _user_modes.get(update.effective_user.id, "s180")

    lines = ["SISTEMA 180 â Estado\n"]
    lines.append(f"Modo: {mode.upper()}")
    lines.append(f"Meta Ads API: {'Conectada' if meta_ok else 'Desconectada'}")
    lines.append(f"Cuenta: {os.getenv('META_AD_ACCOUNT_ID','N/A')}")
    lines.append(f"\nModulos ({sum(modules.values())}/{len(modules)}):")
    for name, ok in modules.items():
        lines.append(f"  {'OK' if ok else '--'} {name}")
    lines.append(f"\nCampanas locales: {len(campanas)}")

    # SecurityGate summary
    if _security_gate:
        summary = _security_gate.get_summary()
        lines.append(f"\nSecurityGate:")
        lines.append(f"  Acciones hoy: {summary.get('total_actions', 0)}")
        lines.append(f"  Pendientes: {summary.get('pending', 0)}")
        lines.append(f"  Gasto hoy: {summary.get('total_spend', 0):.2f}EUR")

    # Provider health
    if shared_state_mod:
        health = shared_state_mod.get_provider_health()
        if health:
            lines.append(f"\nProviders IA:")
            for name, h in health.items():
                rate = f"{h['success']}/{h['total']}" if h['total'] > 0 else "0/0"
                lines.append(f"  {name}: {rate}")

    await update.message.reply_text("\n".join(lines))


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  NOTION / CRM COMMANDS
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def clientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not integrations_mod:
        await update.message.reply_text("Modulo integrations no disponible.")
        return
    try:
        data = integrations_mod.notion_get_clients()
        if not data:
            await update.message.reply_text("Sin clientes en Notion.")
            return
        lines = ["Clientes CRM:\n"]
        for c in data[:15]:
            lines.append(f"- {c.get('nombre','')} | {c.get('servicio','')} | {c.get('precio',0)} EUR | {c.get('estado','')}")
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def afiliados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not integrations_mod:
        await update.message.reply_text("Modulo integrations no disponible.")
        return
    try:
        data = integrations_mod.notion_get_afiliados()
        if not data:
            await update.message.reply_text("Sin afiliados.")
            return
        lines = ["Afiliados:\n"]
        for a in data[:10]:
            lines.append(f"- {a.get('nombre','')} | {a.get('comision',0)}% | {a.get('estado','')}")
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def agentes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not integrations_mod:
        await update.message.reply_text("Modulo integrations no disponible.")
        return
    try:
        data = integrations_mod.notion_get_agentes()
        if not data:
            await update.message.reply_text("Sin agentes IA registrados.")
            return
        lines = ["Agentes IA:\n"]
        for a in data[:15]:
            lines.append(f"- {a.get('nombre','')} | {a.get('departamento','')} | {a.get('estado','')}")
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def alta_cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or len(args) < 3:
        await update.message.reply_text("Uso: /alta_cliente <nombre> <servicio> <precio>")
        return
    if not integrations_mod:
        await update.message.reply_text("Modulo integrations no disponible.")
        return
    try:
        precio = float(args[-1])
        servicio = args[-2]
        nombre = " ".join(args[:-2])
        result = integrations_mod.onboard_new_client(nombre, servicio, precio)
        await update.message.reply_text(
            f"Alta cliente:\n"
            f"Nombre: {nombre}\n"
            f"Servicio: {servicio}\n"
            f"Precio: {precio} EUR\n"
            f"Notion: {'OK' if result.get('notion') else 'Error'}\n"
            f"Slack: {'OK' if result.get('slack') else 'Error'}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  PROSPECTION COMMANDS
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def prospectar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ig_prospector_mod:
        await update.message.reply_text("Modulo ig_prospector no disponible.")
        return
    args = context.args
    hashtag = args[0] if args else "marketingdigital"
    await update.message.reply_text(f"Buscando leads con #{hashtag}...")
    try:
        prospector = ig_prospector_mod.get_prospector()
        if prospector:
            results = await asyncio.get_event_loop().run_in_executor(None, prospector.search, hashtag)
            await update.message.reply_text(f"Encontrados {len(results) if results else 0} leads con #{hashtag}")
        else:
            await update.message.reply_text("Prospector no inicializado. Falta META_IG_USER_ID.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not lead_factory_mod:
        await update.message.reply_text("Modulo lead_factory no disponible.")
        return
    try:
        zones = lead_factory_mod.ZONES
        types = lead_factory_mod.BUSINESS_TYPES
        await update.message.reply_text(
            f"Lead Factory:\n"
            f"Zonas: {', '.join(zones[:5])}\n"
            f"Tipos: {', '.join(types[:5])}\n\n"
            f"Usa /lead_run <zona> <tipo> para generar leads."
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def autopilot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _autopilot_task
    if not autopilot_mod:
        await update.message.reply_text("Modulo autopilot no disponible.")
        return
    try:
        state = autopilot_mod.load_state()
        stats = autopilot_mod.get_pipeline_stats()
        await update.message.reply_text(
            f"Autopiloto DMs:\n"
            f"Estado: {'Activo' if _autopilot_task else 'Inactivo'}\n"
            f"DMs enviados hoy: {state.get('daily_sent', 0)}/{autopilot_mod.DAILY_DM_LIMIT}\n"
            f"Total historico: {state.get('total_sent', 0)}\n"
            f"Pipeline: {stats.get('total', 0)} leads\n"
            f"Respondieron: {stats.get('responded', 0)}\n"
            f"Cerrados: {stats.get('closed', 0)}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def autopilot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stats detallados del autopilot."""
    if not autopilot_mod:
        await update.message.reply_text("Modulo autopilot no disponible.")
        return
    try:
        state = autopilot_mod.load_state()
        stats = autopilot_mod.get_pipeline_stats()
        lines = [
            "AUTOPILOT â Dashboard\n",
            f"Running: {'Si' if state.get('running') else 'No'}",
            f"Started: {state.get('started_at', 'Never')}",
            f"Last run: {state.get('last_run', 'Never')}",
            f"\nHoy: {state.get('daily_sent', 0)}/{autopilot_mod.DAILY_DM_LIMIT} DMs",
            f"Total: {state.get('total_sent', 0)} DMs",
            f"\nPipeline:",
            f"  Total leads: {stats.get('total', 0)}",
            f"  Enviados: {stats.get('sent', 0)}",
            f"  Respondieron: {stats.get('responded', 0)}",
            f"  Cerrados: {stats.get('closed', 0)}",
            f"\nZona actual: {autopilot_mod.ZONES_PRIORITY[state.get('zone_index', 0) % len(autopilot_mod.ZONES_PRIORITY)][0]}",
            f"Tipo actual: {autopilot_mod.BUSINESS_TARGETS[state.get('type_index', 0) % len(autopilot_mod.BUSINESS_TARGETS)]}",
        ]
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def email_blast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not email_prospector_mod:
        await update.message.reply_text("Modulo email_prospector no disponible.")
        return
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("Uso: /email_blast <nicho> <ciudad>")
        return
    nicho, ciudad = args[0], args[1]
    await update.message.reply_text(f"Buscando emails de {nicho} en {ciudad}...")
    try:
        leads_found = email_prospector_mod.find_leads_with_emails(nicho, ciudad)
        await update.message.reply_text(f"Encontrados {len(leads_found) if leads_found else 0} leads con email.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  MAESTRO / STRATEGY COMMANDS
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def maestro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _maestro_orchestrator
    if not maestro_orch_mod:
        await update.message.reply_text("Modulo maestro_orchestrator no disponible.")
        return
    await update.message.reply_text("Ejecutando ciclo diario del Maestro...")
    try:
        if not _maestro_orchestrator:
            _maestro_orchestrator = maestro_orch_mod.MaestroOrchestrator()
        report = await _maestro_orchestrator.run_daily_cycle()
        health_score = report.get("health_score", 0)
        decisions = report.get("decisions_generated", 0)
        executed = report.get("decisions_executed", 0)
        await update.message.reply_text(
            f"Maestro â Ciclo completado\n\n"
            f"Salud del negocio: {health_score}/100\n"
            f"Decisiones generadas: {decisions}\n"
            f"Decisiones ejecutadas: {executed}\n"
            f"Estado: {report.get('status','unknown')}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error en ciclo Maestro: {e}")

@only_authorized
async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if maestro_intel_mod:
        try:
            snapshot = maestro_intel_mod.create_data_snapshot()
            await update.message.reply_text(
                f"Salud del negocio:\n"
                f"MRR: {snapshot.get('stripe_mrr', 'N/A')} EUR\n"
                f"Clientes activos: {snapshot.get('active_clients', 'N/A')}\n"
                f"ROAS Meta: {snapshot.get('meta_roas', 'N/A')}"
            )
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
    else:
        await update.message.reply_text("Modulo maestro_intelligence no disponible.")

@only_authorized
async def brain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _strategic_brain
    if not strategic_brain_mod:
        await update.message.reply_text("Modulo strategic_brain no disponible.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /brain_cmd <tu pregunta estrategica>")
        return
    question = " ".join(args)
    try:
        if not _strategic_brain:
            _strategic_brain = strategic_brain_mod.create_strategic_brain()
        answer = _strategic_brain.think(question) if _strategic_brain else "Brain no inicializado"
        await update.message.reply_text(f"Brain:\n{answer}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  OUTREACH COMMANDS
# âââââââââââââââââââââââââââââââââââââââââââââââ

@only_authorized
async def outreach_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not outreach_db_mod:
        await update.message.reply_text("Modulo outreach_db no disponible.")
        return
    try:
        db = outreach_db_mod.OutreachDB()
        stats = db.get_stats() if hasattr(db, 'get_stats') else {"total": 0}
        await update.message.reply_text(f"Outreach stats:\n{stats}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def ig_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    try:
        accounts = ig_multi_mod.get_accounts() if hasattr(ig_multi_mod, 'get_accounts') else []
        if accounts:
            lines_out = ["Cuentas Instagram:\n"]
            for a in accounts:
                lines_out.append(f"- @{a.get('username','')} | Followers: {a.get('followers',0)}")
            await update.message.reply_text("\n".join(lines_out))
        else:
            await update.message.reply_text("Sin cuentas IG configuradas.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# ═══════════════════════════════════════════════
#  CEREBRO S180 COMMANDS (Doctrina inyectada)
# ═══════════════════════════════════════════════

@only_authorized
async def cerebro_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu principal del Cerebro S180."""
    text = (
        "CEREBRO S180 v3.0\n"
        "Doctrina: Verdad, Foco, Caja, Ejecucion limpia\n\n"
        "Comandos disponibles:\n"
        "/caja — Protocolo diario de caja\n"
        "/regulacion — Regulacion rapida (5 min)\n"
        "/ordename — Ordename hoy (prioridad diaria)\n"
        "/cierre_dia — Protocolo cierre del dia\n"
        "/pipeline_prioridad — Prioridades bajo presion\n"
        "/precios — Escalera de precios\n"
        "/angulos — 15 angulos de comunicacion\n"
        "/guion <angulo> — Generar guion\n"
        "/salud_operador — Check estado del operador\n\n"
        "O simplemente escribe en lenguaje natural:\n"
        "'ordename hoy', 'voy jodido de caja', 'me esta entrando ansiedad'"
    )
    await update.message.reply_text(text)

@only_authorized
async def caja_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Protocolo diario de caja + caja urgente."""
    if doctrina_mod:
        text = doctrina_mod.formato_protocolo_caja()
        text += "\n\nSi hay presion financiera REAL, usa: /caja_urgente"
    else:
        text = "Modulo doctrina no disponible."
    await update.message.reply_text(text)

@only_authorized
async def caja_urgente_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Protocolo caja urgente."""
    if doctrina_mod:
        text = doctrina_mod.formato_caja_urgente()
    else:
        text = "Modulo doctrina no disponible."
    await update.message.reply_text(text)

@only_authorized
async def regulacion_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Protocolo regulacion rapida (5 min)."""
    if doctrina_mod:
        text = doctrina_mod.formato_regulacion()
    else:
        text = "Modulo doctrina no disponible."
    await update.message.reply_text(text)

@only_authorized
async def ordename_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ordename hoy — usa IA para dar prioridad del dia."""
    if brain_mod:
        uid = update.effective_user.id
        mode = _user_modes.get(uid, "s180")
        reply = brain_mod.chat(
            user_id=str(uid),
            message="Ordéname hoy. Dime mis 3 prioridades de caja para hoy, en orden. Sin rodeos.",
            persona=mode,
        )
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Brain no disponible.")

@only_authorized
async def cierre_dia_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Protocolo cierre del dia."""
    if brain_mod:
        uid = update.effective_user.id
        mode = _user_modes.get(uid, "s180")
        reply = brain_mod.chat(
            user_id=str(uid),
            message="Cierra el día. Resume: qué se hizo hoy, qué queda pendiente, y qué es lo primero mañana.",
            persona=mode,
        )
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Brain no disponible.")

@only_authorized
async def pipeline_prioridad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prioridades bajo presion financiera."""
    if doctrina_mod:
        text = doctrina_mod.formato_prioridad_diaria()
    else:
        text = "Modulo doctrina no disponible."
    await update.message.reply_text(text)

@only_authorized
async def precios_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Escalera de precios de las 3 lineas."""
    if doctrina_mod:
        text = doctrina_mod.formato_precios()
    else:
        text = "Modulo doctrina no disponible."
    await update.message.reply_text(text)

@only_authorized
async def angulos_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Biblioteca de 15 angulos de comunicacion."""
    if doctrina_mod:
        try:
            text = doctrina_mod.formato_angulos_resumen()
        except Exception:
            text = "Error cargando angulos. Verifica sistema180_maestro.py"
    else:
        text = "Modulo doctrina no disponible."
    await update.message.reply_text(text)

@only_authorized
async def guion_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generar guion con angulo especifico."""
    args = context.args
    if not args:
        await update.message.reply_text(
            "Uso: /guion <numero_angulo>\n\n"
            "Ejemplo: /guion 1\n"
            "Usa /angulos para ver la lista completa."
        )
        return
    angulo = args[0]
    if brain_mod:
        uid = update.effective_user.id
        mode = _user_modes.get(uid, "s180")
        duracion = args[1] if len(args) > 1 else "corta"
        reply = brain_mod.chat(
            user_id=str(uid),
            message=f"Hazme un guion para Jose Maria. Angulo {angulo}. Duracion {duracion}. Formato F8. Incluye: hook, identificacion, reframe, CTA. Solo el guion, nada mas.",
            persona=mode,
        )
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Brain no disponible.")

@only_authorized
async def salud_operador_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check estado interno del operador."""
    if brain_mod:
        uid = update.effective_user.id
        mode = _user_modes.get(uid, "s180")
        reply = brain_mod.chat(
            user_id=str(uid),
            message="Como me ves ahora? Evalua mi estado como operador. Se honesto y directo. Si detectas señales de alerta, dimelo.",
            persona=mode,
        )
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Brain no disponible.")

@only_authorized
async def regla37_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Regla del 37% — termometro de rentabilidad."""
    if doctrina_mod:
        text = doctrina_mod.formato_regla_37()
    else:
        text = "Modulo doctrina no disponible."
    await update.message.reply_text(text)


# ═══════════════════════════════════════════════
#  INSTAGRAM MULTI-CUENTA COMMANDS
# ═══════════════════════════════════════════════

# Variable global para campana activa
_ig_campaign_active = False

@only_authorized
async def ig_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Anadir cuenta Instagram: /ig_add usuario contrasena [limite_diario]"""
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Uso: /ig_add usuario contrasena [limite_diario]")
        return
    username = args[0].lstrip("@")
    password = args[1]
    limit = int(args[2]) if len(args) > 2 else 25
    store = ig_multi_mod.get_store()
    ok = store.add_account(username, password, daily_limit=limit)
    if ok:
        await update.message.reply_text(
            f"Cuenta @{username} registrada (limite: {limit} DMs/dia).\n"
            f"Ahora usa /ig_login {username} para conectarla."
        )
    else:
        await update.message.reply_text(f"@{username} ya existe. Usa /ig_remove primero.")

@only_authorized
async def ig_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Eliminar cuenta: /ig_remove usuario"""
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /ig_remove usuario")
        return
    username = args[0].lstrip("@")
    store = ig_multi_mod.get_store()
    ok = store.remove_account(username)
    await update.message.reply_text(
        f"@{username} eliminada." if ok else f"@{username} no encontrada."
    )

@only_authorized
async def ig_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Login de cuenta: /ig_login usuario"""
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /ig_login usuario")
        return
    username = args[0].lstrip("@")
    await update.message.reply_text(f"Conectando @{username}...")
    try:
        sess = ig_multi_mod.get_session(username)
        if not sess:
            await update.message.reply_text(f"@{username} no registrada. Usa /ig_add primero.")
            return
        result = await asyncio.get_event_loop().run_in_executor(None, sess.login)
        status = result.get("status", "error")
        msg = result.get("msg", "")
        if result["ok"]:
            await update.message.reply_text(f"@{username} conectada correctamente.")
        elif status in ("challenge", "2fa"):
            await update.message.reply_text(
                f"{msg}\n\nEnvia el codigo con: /ig_code {username} CODIGO"
            )
        else:
            await update.message.reply_text(f"Error login @{username}: {msg}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def ig_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enviar codigo verificacion: /ig_code usuario codigo"""
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Uso: /ig_code usuario codigo")
        return
    username = args[0].lstrip("@")
    code = args[1]
    try:
        sess = ig_multi_mod.get_session(username)
        if not sess:
            await update.message.reply_text(f"@{username} no registrada.")
            return
        result = await asyncio.get_event_loop().run_in_executor(
            None, sess.submit_code, code
        )
        await update.message.reply_text(result.get("msg", str(result)))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def ig_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver estado de todas las cuentas: /ig_status"""
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    try:
        summary = ig_multi_mod.get_accounts_summary()
        await update.message.reply_text(summary, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def ig_limite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cambiar limite diario: /ig_limite usuario numero"""
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Uso: /ig_limite usuario numero")
        return
    username = args[0].lstrip("@")
    new_limit = int(args[1])
    store = ig_multi_mod.get_store()
    acc = store.get(username)
    if not acc:
        await update.message.reply_text(f"@{username} no existe.")
        return
    store.update(username, daily_limit=new_limit)
    await update.message.reply_text(f"@{username}: limite actualizado a {new_limit} DMs/dia.")

@only_authorized
async def ig_prospectar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Campana por hashtag: /ig_prospectar hashtag [cantidad]"""
    global _ig_campaign_active
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "Uso: /ig_prospectar <hashtag> [cantidad]\n"
            "Ejemplo: /ig_prospectar peluqueriamalaga 50"
        )
        return
    hashtag = args[0].lstrip("#")
    limit = int(args[1]) if len(args) > 1 else 30

    # Verificar cuentas disponibles
    store = ig_multi_mod.get_store()
    store.reset_daily_if_needed()
    active = [a for a in store.get_all() if a["active"] and a["status"] == "ok"]
    if not active:
        await update.message.reply_text(
            "No hay cuentas activas. Primero:\n"
            "1. /ig_add usuario contrasena\n"
            "2. /ig_login usuario"
        )
        return

    capacity = sum(a["daily_limit"] - a["sent_today"] for a in active)
    await update.message.reply_text(
        f"Campana #{hashtag} iniciada\n"
        f"Cuentas activas: {len(active)}\n"
        f"Capacidad restante hoy: {capacity} DMs\n"
        f"Objetivo: {min(limit, capacity)} DMs\n\n"
        f"Buscando targets..."
    )

    _ig_campaign_active = True

    async def _notify(msg):
        try:
            await update.message.reply_text(msg)
        except Exception:
            pass

    try:
        # Buscar targets con la mejor sesion
        sess = ig_multi_mod.get_best_session()
        if not sess:
            await update.message.reply_text("No hay sesiones disponibles.")
            return

        targets = await asyncio.get_event_loop().run_in_executor(
            None, lambda: sess.search_by_keyword(hashtag, limit=limit * 2)
        )

        if not targets:
            # Fallback: usar ig_prospector con hashtags
            if ig_prospector_mod:
                p = ig_prospector_mod.get_prospector()
                if p and p.cl:
                    targets = await asyncio.get_event_loop().run_in_executor(
                        None, p.search_targets_by_hashtag, hashtag, limit * 2
                    )

        if not targets:
            await update.message.reply_text(f"No se encontraron targets para #{hashtag}.")
            _ig_campaign_active = False
            return

        await _notify(f"Encontrados {len(targets)} targets. Enviando DMs...")

        # Enviar DMs rotando cuentas
        sent = 0
        failed = 0
        for i, target in enumerate(targets[:limit]):
            if not _ig_campaign_active:
                await _notify(f"Campana detenida por /ig_parar. Enviados: {sent}")
                break

            # Obtener mejor cuenta (rotacion automatica)
            best_sess = ig_multi_mod.get_best_session()
            if not best_sess:
                await _notify(f"Todas las cuentas al limite. Enviados: {sent}")
                break

            # Generar DM personalizado con IA
            dm_text = ig_multi_mod.generate_dm(
                business_name=target.get("name", ""),
                ig_username=target.get("username", ""),
                bio=target.get("bio", ""),
            )

            # Enviar
            ok = await asyncio.get_event_loop().run_in_executor(
                None, best_sess.send_dm, target["id"], dm_text
            )

            if ok:
                sent += 1
                if sent % 5 == 0:
                    await _notify(
                        f"Progreso: {sent}/{min(limit, len(targets))} DMs\n"
                        f"Cuenta activa: @{best_sess.username}"
                    )
            else:
                failed += 1

            # Delay anti-ban
            if i < len(targets) - 1:
                delay = random.randint(30, 90)
                await asyncio.sleep(delay)

        _ig_campaign_active = False
        await _notify(
            f"Campana #{hashtag} finalizada\n"
            f"Enviados: {sent}\n"
            f"Fallidos: {failed}\n"
            f"Total targets: {len(targets)}"
        )

    except Exception as e:
        _ig_campaign_active = False
        await update.message.reply_text(f"Error campana: {e}")

@only_authorized
async def ig_competidor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Robar seguidores de competidor: /ig_competidor @usuario [cantidad]"""
    global _ig_campaign_active
    if not ig_multi_mod or not ig_prospector_mod:
        await update.message.reply_text("Modulos IG no disponibles.")
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "Uso: /ig_competidor @competidor [cantidad]\n"
            "Ejemplo: /ig_competidor @peluqueria_top 40"
        )
        return
    competitor = args[0].lstrip("@")
    limit = int(args[1]) if len(args) > 1 else 30

    await update.message.reply_text(f"Buscando seguidores de @{competitor}...")

    try:
        p = ig_prospector_mod.get_prospector()
        if not p or not p.cl:
            # Intentar con sesion multi-cuenta
            sess = ig_multi_mod.get_best_session()
            if not sess:
                await update.message.reply_text("No hay sesiones IG activas.")
                return
            targets = await asyncio.get_event_loop().run_in_executor(
                None, lambda: sess.search_by_keyword(competitor, limit=limit)
            )
        else:
            targets = await asyncio.get_event_loop().run_in_executor(
                None, p.search_competitors_followers, competitor, limit
            )

        if not targets:
            await update.message.reply_text(f"No se encontraron seguidores de @{competitor}.")
            return

        await update.message.reply_text(
            f"Encontrados {len(targets)} seguidores.\n"
            f"Iniciando envio de DMs..."
        )

        _ig_campaign_active = True
        sent = 0
        for i, target in enumerate(targets[:limit]):
            if not _ig_campaign_active:
                break
            best_sess = ig_multi_mod.get_best_session()
            if not best_sess:
                break
            dm = ig_multi_mod.generate_dm(
                business_name=target.get("name", ""),
                ig_username=target.get("username", ""),
                bio=target.get("bio", ""),
            )
            ok = await asyncio.get_event_loop().run_in_executor(
                None, best_sess.send_dm, target["id"], dm
            )
            if ok:
                sent += 1
                if sent % 5 == 0:
                    await update.message.reply_text(f"Progreso: {sent} DMs enviados...")
            if i < len(targets) - 1:
                await asyncio.sleep(random.randint(30, 90))

        _ig_campaign_active = False
        await update.message.reply_text(f"Campana competidor finalizada. Enviados: {sent}")
    except Exception as e:
        _ig_campaign_active = False
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def ig_maps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pipeline Maps-IG: /ig_maps ciudad tipo_negocio [cantidad]"""
    global _ig_campaign_active
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Uso: /ig_maps <ciudad> <tipo_negocio> [cantidad]\n"
            "Ejemplo: /ig_maps malaga peluqueria 20\n"
            "Ejemplo: /ig_maps marbella barberia 30"
        )
        return
    city = args[0]
    biz_type = args[1]
    limit = int(args[2]) if len(args) > 2 else 20

    # Coordenadas aproximadas de ciudades
    COORDS = {
        "malaga": (36.7213, -4.4214),
        "marbella": (36.5099, -4.8826),
        "fuengirola": (36.5443, -4.6247),
        "torremolinos": (36.6218, -4.4997),
        "benalmadena": (36.5987, -4.5169),
        "mijas": (36.5958, -4.6370),
        "coin": (36.6594, -4.7563),
        "alhaurin": (36.6430, -4.6920),
        "sevilla": (37.3891, -5.9845),
        "granada": (37.1773, -3.5986),
        "cordoba": (37.8882, -4.7794),
        "madrid": (40.4168, -3.7038),
        "barcelona": (41.3874, 2.1686),
        "valencia": (39.4699, -0.3763),
    }
    lat, lng = COORDS.get(city.lower(), (36.7213, -4.4214))

    await update.message.reply_text(
        f"Pipeline Maps -> IG iniciado\n"
        f"Ciudad: {city} ({lat}, {lng})\n"
        f"Tipo: {biz_type}\n"
        f"Limite: {limit}\n\n"
        f"Buscando negocios en Google Maps..."
    )

    _ig_campaign_active = True

    async def _notify(msg):
        try:
            await update.message.reply_text(msg)
        except Exception:
            pass

    try:
        stats = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: ig_multi_mod.maps_to_ig_pipeline(
                city=city,
                business_type=biz_type,
                lat=lat,
                lng=lng,
                limit=limit,
                notify_fn=_notify,
                dry_run=False,
            )
        )
        _ig_campaign_active = False
        await update.message.reply_text(
            f"Pipeline finalizado:\n"
            f"Negocios encontrados: {stats['found']}\n"
            f"Con Instagram: {stats['ig_found']}\n"
            f"DMs enviados: {stats['sent']}\n"
            f"Errores: {stats['errors']}\n"
            f"Saltados: {stats['skipped']}"
        )
    except Exception as e:
        _ig_campaign_active = False
        await update.message.reply_text(f"Error pipeline: {e}")

@only_authorized
async def ig_parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detener campana activa"""
    global _ig_campaign_active
    _ig_campaign_active = False
    await update.message.reply_text("Campana detenida. Los DMs ya enviados no se pueden revertir.")

@only_authorized
async def ig_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estadisticas globales de prospeccion"""
    if not ig_multi_mod:
        await update.message.reply_text("Modulo ig_multi_account no disponible.")
        return
    try:
        store = ig_multi_mod.get_store()
        store.reset_daily_if_needed()
        accs = store.get_all()
        total_today = sum(a["sent_today"] for a in accs)
        total_all = sum(a["sent_total"] for a in accs)
        active = sum(1 for a in accs if a["active"] and a["status"] == "ok")
        capacity = sum(
            a["daily_limit"] - a["sent_today"]
            for a in accs
            if a["active"] and a["status"] == "ok"
        )
        all_sent_ids = set()
        for a in accs:
            all_sent_ids.update(a.get("sent_ids", []))

        await update.message.reply_text(
            f"Estadisticas Prospeccion IG\n\n"
            f"Cuentas totales: {len(accs)}\n"
            f"Cuentas activas: {active}\n"
            f"DMs hoy: {total_today}\n"
            f"Capacidad restante hoy: {capacity}\n"
            f"DMs total historico: {total_all}\n"
            f"Leads unicos contactados: {len(all_sent_ids)}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# ═══════════════════════════════════════════════
#  BACKUP + GDPR
# ═══════════════════════════════════════════════

@only_authorized
async def backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ejecutar backup manual: /backup"""
    try:
        from backup_manager import run_backup, get_backup_status
        await update.message.reply_text("Ejecutando backup...")
        stats = await asyncio.get_event_loop().run_in_executor(None, run_backup)
        status = get_backup_status()
        await update.message.reply_text(
            f"Backup completado:\n"
            f"OK: {stats['ok']} | Skip: {stats['skip']} | Error: {stats['error']}\n\n"
            f"{status}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error backup: {e}")

@only_authorized
async def borrar_datos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """GDPR: borrar datos de un lead: /borrar_datos ig_username"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "Uso: /borrar_datos <ig_username>\n"
            "Elimina todos los datos del lead de la base de datos (GDPR)."
        )
        return
    username = args[0].lstrip("@")
    try:
        from outreach_db import get_conn
        with get_conn() as conn:
            # Check existence
            lead = conn.execute(
                "SELECT id FROM leads WHERE ig_username=?", (username,)
            ).fetchone()
            if not lead:
                await update.message.reply_text(f"@{username} no encontrado en la DB.")
                return
            lead_id = lead[0]
            # Delete DMs
            dm_count = conn.execute(
                "DELETE FROM dms WHERE lead_id=?", (lead_id,)
            ).rowcount
            # Delete lead
            conn.execute("DELETE FROM leads WHERE id=?", (lead_id,))
        await update.message.reply_text(
            f"GDPR: @{username} eliminado.\n"
            f"Lead borrado + {dm_count} DMs asociados eliminados."
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


@only_authorized
async def metricas_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Métricas del sistema en tiempo real: /metricas"""
    try:
        from resilience import metrics
        summary = metrics.get_health_summary()
        await update.message.reply_text(summary, parse_mode="Markdown")
    except ImportError:
        await update.message.reply_text("Módulo de métricas no disponible.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# ═══════════════════════════════════════════════
#  ANTIGRAVITY CODE BRIDGE
# ═══════════════════════════════════════════════

@only_authorized
async def codigo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enviar tarea de código a Antigravity: /codigo <instrucción>"""
    import json as _json
    from pathlib import Path as _P
    from datetime import datetime as _dt

    if not context.args:
        await update.message.reply_text(
            "🧠 *Puente Antigravity*\n\n"
            "Uso: `/codigo <instrucción>`\n\n"
            "Ejemplo:\n"
            "`/codigo arregla el bug en integrations.py`\n"
            "`/codigo crea un endpoint para dashboard`\n"
            "`/codigo añade tests para outreach_db`\n\n"
            "También por voz: _\"JARVIS, programa un endpoint para métricas\"_",
            parse_mode="Markdown"
        )
        return

    instruction = " ".join(context.args)
    task = {
        "id": _dt.utcnow().strftime("%Y%m%d%H%M%S"),
        "task": instruction,
        "status": "pending",
        "source": "telegram",
        "created_at": _dt.utcnow().isoformat(),
        "user_id": str(update.effective_user.id),
    }

    queue_file = _P(__file__).parent / "code_queue.json"
    queue = []
    if queue_file.exists():
        try:
            queue = _json.loads(queue_file.read_text())
        except Exception:
            queue = []
    queue.append(task)
    queue_file.write_text(_json.dumps(queue, indent=2, ensure_ascii=False))

    await update.message.reply_text(
        f"✅ *Tarea añadida a la cola de Antigravity*\n\n"
        f"📋 `{instruction}`\n"
        f"🆔 `{task['id']}`\n\n"
        f"El relay local la ejecutará automáticamente.",
        parse_mode="Markdown"
    )

@only_authorized
async def code_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver cola de tareas de código: /code_status"""
    import json as _json
    from pathlib import Path as _P

    queue_file = _P(__file__).parent / "code_queue.json"
    if not queue_file.exists():
        await update.message.reply_text("Cola vacía. Usa /codigo <instrucción> para añadir.")
        return

    try:
        queue = _json.loads(queue_file.read_text())
        if not queue:
            await update.message.reply_text("Cola vacía.")
            return

        lines = ["📋 *Cola Antigravity*\n"]
        for t in queue[-10:]:  # últimas 10
            emoji = {"pending": "⏳", "running": "🔄", "done": "✅", "error": "❌"}.get(t["status"], "❓")
            lines.append(f"{emoji} `{t['id']}` — {t['task'][:50]}")
            lines.append(f"   via {t['source']} | {t['status']}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# ═══════════════════════════════════════════════
#  WHATSAPP BRIDGE
# ═══════════════════════════════════════════════

@only_authorized
async def wa_enviar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enviar WhatsApp: /wa_enviar <telefono> <mensaje>"""
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "📱 *WhatsApp*\n\n"
            "Uso: `/wa_enviar <telefono> <mensaje>`\n"
            "Ejemplo: `/wa_enviar 612345678 Hola, le contacto de Sistema 180`\n\n"
            "O dile a JARVIS: _\"Envía un WhatsApp al 612345678 diciendo hola\"_",
            parse_mode="Markdown"
        )
        return
    phone = args[0]
    message = " ".join(args[1:])
    try:
        from jarvis_whatsapp import send_message
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: send_message(phone, message)
        )
        if result["ok"]:
            await update.message.reply_text(f"✅ WhatsApp enviado a +{phone}")
        else:
            await update.message.reply_text(f"❌ Error: {result['error']}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def wa_chats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver conversaciones WhatsApp: /wa_chats"""
    try:
        from jarvis_whatsapp import get_conversations, is_configured
        if not is_configured():
            await update.message.reply_text(
                "⚠️ WhatsApp no configurado.\n\n"
                "Necesitas añadir en Railway:\n"
                "• `WHATSAPP_PHONE_NUMBER_ID`\n"
                "• `META_ACCESS_TOKEN` (ya lo tienes)\n\n"
                "Guía: developers.facebook.com → App → WhatsApp"
            )
            return
        convos = get_conversations()
        if not convos:
            await update.message.reply_text("Sin conversaciones de WhatsApp.")
            return
        lines = ["📱 *Conversaciones WhatsApp:*\n"]
        for c in convos[:15]:
            lines.append(
                f"• *{c['name']}* (+{c['phone']})\n"
                f"  Último: {c['last_message']}\n"
                f"  Msgs: {c['total_messages']}"
            )
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def wa_chat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver historial con un número: /wa_chat <telefono>"""
    if not context.args:
        await update.message.reply_text("Uso: /wa_chat <telefono>")
        return
    phone = context.args[0].replace("+", "")
    try:
        from jarvis_whatsapp import get_conversation
        msgs = get_conversation(phone)
        if not msgs:
            await update.message.reply_text(f"Sin mensajes con +{phone}")
            return
        lines = [f"📱 *Chat con +{phone}*\n"]
        for m in msgs[-10:]:
            emoji = "👤" if m["from"] == "user" else "🤖"
            lines.append(f"{emoji} {m['text'][:100]}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def wa_responder_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responder a WhatsApp: /wa_responder <telefono> <mensaje>"""
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("Uso: /wa_responder <telefono> <mensaje>")
        return
    phone = args[0]
    message = " ".join(args[1:])
    try:
        from jarvis_whatsapp import send_message
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: send_message(phone, message)
        )
        if result["ok"]:
            await update.message.reply_text(f"✅ Respuesta enviada a +{phone}")
        else:
            await update.message.reply_text(f"❌ {result['error']}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# ═══════════════════════════════════════════════
#  JARVIS CLOUD — Todo desde el móvil
# ═══════════════════════════════════════════════

@only_authorized
async def reporte_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reporte diario: /reporte"""
    try:
        from jarvis_cloud import generate_daily_report
        report = generate_daily_report()
        await update.message.reply_text(report, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def reporte_semanal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dashboard semanal: /reporte_semanal"""
    try:
        from jarvis_cloud import generate_weekly_report
        report = generate_weekly_report()
        await update.message.reply_text(report, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def factura_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crear factura: /factura <cliente> <importe> [concepto]"""
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "Uso: /factura <cliente> <importe> [concepto]\n"
            "Ejemplo: /factura Restaurante_Mario 297 Web_mensual"
        )
        return
    client_name = args[0].replace("_", " ")
    try:
        amount = float(args[1])
    except ValueError:
        await update.message.reply_text("El importe debe ser un número.")
        return
    concept = " ".join(args[2:]).replace("_", " ") if len(args) > 2 else "Servicio mensual"

    try:
        from jarvis_cloud import create_invoice
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: create_invoice(client_name, amount, concept)
        )
        if result["ok"]:
            await update.message.reply_text(
                f"✅ *Factura creada*\n\n"
                f"🆔 `{result['invoice_id']}`\n"
                f"👤 {client_name}\n"
                f"💰 {amount}€\n"
                f"📋 {concept}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"Error: {result['error']}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def lead_score_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Puntuar lead: /lead_score <@username> [bio] [followers]"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "Uso: /lead_score <username> [followers] [bio...]\n"
            "Ejemplo: /lead_score restaurante_mario 1500 Restaurante italiano en Madrid"
        )
        return
    username = args[0].lstrip("@")
    followers = 0
    bio = ""
    if len(args) > 1:
        try:
            followers = int(args[1])
            bio = " ".join(args[2:]) if len(args) > 2 else ""
        except ValueError:
            bio = " ".join(args[1:])

    try:
        from jarvis_cloud import score_lead
        result = score_lead(username, bio, followers)
        await update.message.reply_text(
            f"🎯 *Lead Score: @{username}*\n\n"
            f"Puntuación: {result['score']}/10 {result['tier']}\n"
            f"Followers: {followers}\n"
            f"Bio: {bio[:100] or 'N/A'}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def followups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver recordatorios pendientes: /followups"""
    try:
        from jarvis_cloud import check_client_followups
        alerts = check_client_followups()
        if not alerts:
            await update.message.reply_text("✅ No hay recordatorios pendientes.")
            return
        lines = ["📞 *Recordatorios pendientes:*\n"]
        for a in alerts:
            emoji = "🆕" if a["tipo"] == "onboarding" else "📞"
            lines.append(
                f"{emoji} *{a['nombre']}* ({a['servicio']})\n"
                f"   Días desde alta: {a['days_since_alta']}"
            )
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def renovaciones_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver renovaciones próximas: /renovaciones"""
    try:
        from jarvis_cloud import check_renewals
        renewals = check_renewals(days_before=14)
        if not renewals:
            await update.message.reply_text("✅ No hay renovaciones próximas.")
            return
        lines = ["🔄 *Renovaciones próximas:*\n"]
        for r in renewals:
            urgency = "🔴" if r["days_until"] <= 3 else "🟡" if r["days_until"] <= 7 else "🟢"
            lines.append(
                f"{urgency} *{r['nombre']}* — {r['precio']}€\n"
                f"   {r['renewal_date']} (en {r['days_until']} días)"
            )
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@only_authorized
async def cloud_code_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cloud Code — ejecutar tarea de código con IA (sin PC): /cloud_code <instrucción>"""
    if not context.args:
        await update.message.reply_text(
            "🧠 *Cloud Code — JARVIS*\n\n"
            "Ejecuta tareas de código usando IA directamente en la nube.\n"
            "No necesitas tener el PC encendido.\n\n"
            "Uso: `/cloud_code <instrucción>`\n\n"
            "Ejemplos:\n"
            "`/cloud_code analiza el rendimiento de outreach_db`\n"
            "`/cloud_code sugiere mejoras para el lead scoring`\n"
            "`/cloud_code explica cómo funciona el circuit breaker`",
            parse_mode="Markdown"
        )
        return

    instruction = " ".join(context.args)
    msg = await update.message.reply_text("🧠 Procesando con Claude...")

    try:
        from jarvis_cloud import cloud_code_execute
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: cloud_code_execute(instruction)
        )
        # Split long responses
        if len(result) > 4000:
            for i in range(0, len(result), 4000):
                chunk = result[i:i+4000]
                await update.message.reply_text(chunk)
            await msg.delete()
        else:
            await msg.edit_text(result)
    except Exception as e:
        await msg.edit_text(f"Error: {e}")


# ═══════════════════════════════════════════════
#  VOICE HANDLER (delegado a voice_handler.py)
# ═══════════════════════════════════════════════

@only_authorized
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Voice-to-Voice: STT -> Brain JARVIS -> TTS. Audio + Texto inteligente."""
    if voice_handler_mod:
        await voice_handler_mod.handle_voice_message(
            update, context, brain_mod, sync_module, _user_modes
        )
    else:
        await update.message.reply_text(
            "Módulo de voz no disponible. Usa /estado para verificar."
        )


@only_authorized
async def voz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configuración de voz de JARVIS."""
    args = context.args
    if not args:
        tts_engine = os.getenv("TTS_ENGINE", "edge")
        has_eleven = bool(os.getenv("ELEVENLABS_API_KEY", ""))
        await update.message.reply_text(
            "JARVIS Voice Config\n\n"
            f"Motor TTS: {tts_engine}\n"
            f"ElevenLabs: {'Configurado' if has_eleven else 'No configurado'}\n"
            f"Edge-TTS: Siempre disponible\n\n"
            "Cuando envías un audio, JARVIS responde con:\n"
            "- Audio (voz JARVIS) + texto\n"
            "- Si dices 'escríbeme en texto' → solo texto\n"
            "- Datos/estadísticas → siempre texto\n"
        )
        return

    subcmd = args[0].lower()
    if subcmd in ("on", "off"):
        # Toggle voz — por ahora informativo
        await update.message.reply_text(
            f"Voz {'activada' if subcmd == 'on' else 'desactivada'}.\n"
            "Envía un audio para probar."
        )


@only_authorized
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler principal de texto libre.
    FLUJO:
    1. NLP Router detecta si es un comando en lenguaje natural
    2. Si lo es → ejecuta la acción directamente
    3. Si no → Brain IA responde como JARVIS/S180
    4. Modo JARVIS: respuestas cortas en audio
    """
    user_id = str(update.effective_user.id)
    text = update.message.text

    if not text:
        return

    # Obtener modo actual
    mode = _user_modes.get(int(user_id) if user_id.isdigit() else 0, "s180")

    # ═══ PASO 1: NLP Router — ¿Es un comando en lenguaje natural? ═══
    try:
        from jarvis_nlp_router import detect_intent, execute_intent
        intent_data = await asyncio.get_event_loop().run_in_executor(
            None, lambda: detect_intent(text)
        )
        intent = intent_data.get("intent", "conversacion")
        confidence = intent_data.get("confidence", 0)

        if intent != "conversacion" and confidence >= 0.6:
            logger.info(f"[NLP] Intent: {intent} (conf={confidence})")
            result = await execute_intent(intent_data, update, context)
            if result:
                # En modo JARVIS: respuestas cortas en audio
                if mode == "jarvis" and voice_handler_mod and len(result) < 200:
                    try:
                        audio_path = await voice_handler_mod._generate_audio(result)
                        if audio_path:
                            with open(audio_path, "rb") as af:
                                await update.message.reply_voice(voice=af)
                            # Send text too for data-heavy responses
                            if voice_handler_mod._response_is_data_heavy(result):
                                await update.message.reply_text(result)
                            return
                    except Exception:
                        pass
                await update.message.reply_text(result)
                return
    except ImportError:
        pass  # NLP router not available
    except Exception as e:
        logger.warning(f"[NLP] Router error: {e}")

    # ═══ PASO 2: Brain IA — conversación natural ═══
    if brain_mod:
        try:
            meta_status = "desconocido"
            if sync_module and hasattr(sync_module, 'meta_client') and sync_module.meta_client:
                meta_status = "conectada" if sync_module.meta_client.is_ready else "desconectada"

            response = brain_mod.chat(
                user_id=user_id,
                message=text,
                persona=mode,
                meta_status=meta_status,
            )

            # En modo JARVIS: respuestas cortas en audio
            if mode == "jarvis" and voice_handler_mod:
                is_short = len(response) < 200
                is_data = voice_handler_mod._response_is_data_heavy(response)
                if is_short and not is_data:
                    try:
                        audio_path = await voice_handler_mod._generate_audio(response)
                        if audio_path:
                            with open(audio_path, "rb") as audio_out:
                                await update.message.reply_voice(voice=audio_out)
                            if not str(audio_path).startswith(str(voice_handler_mod._CACHE_DIR)):
                                try:
                                    os.remove(audio_path)
                                except OSError:
                                    pass
                            return
                    except Exception as e:
                        logger.warning(f"[JARVIS] TTS fallback to text: {e}")

            await update.message.reply_text(response)
            return
        except Exception as e:
            logger.error(f"Brain error: {e}")

    # Fallback: NLP intent classification
    if nlp_mod:
        try:
            intent = nlp_mod.process_user_intent(text)
            intent_type = intent.get("intent", "unknown")
            confidence = intent.get("confidence", 0)

            if intent_type == "create_campaign" and confidence > 0.5:
                params = intent.get("params", {})
                nombre = params.get("nombre", "Nueva")
                presupuesto = params.get("presupuesto", 10)
                if sync_module:
                    result = sync_module.sync_nueva_campana(float(presupuesto), nombre)
                    await update.message.reply_text(result)
                else:
                    await update.message.reply_text(f"Campana '{nombre}' creada (local) con {presupuesto} EUR/dia")
            elif intent_type == "get_metrics" and confidence > 0.5:
                await metricas(update, context)
            elif intent_type == "report" and confidence > 0.5:
                await reporte_diario(update, context)
            elif intent_type == "list_campaigns" and confidence > 0.5:
                await listar_campanas(update, context)
            elif intent_type in ("general_chat", "strategy_question"):
                await update.message.reply_text("Procesando... usa /jarvis para modo conversacional avanzado.")
            else:
                await update.message.reply_text(
                    "Entendido. No tengo suficiente contexto para esa accion.\n"
                    "Usa /comandos para ver las opciones disponibles."
                )
        except Exception as e:
            await update.message.reply_text(f"Error procesando: {e}")
    else:
        await update.message.reply_text("Recibido. Usa /comandos para ver opciones.")


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  MAIN
# âââââââââââââââââââââââââââââââââââââââââââââââ

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN no configurado")
        return

    # Init Meta client
    if sync_module:
        sync_module.init_meta_client(
            os.getenv("META_ACCESS_TOKEN"),
            os.getenv("META_AD_ACCOUNT_ID")
        )
        logger.info("Meta client init attempted")

    app = Application.builder().token(token).build()

    # âââ Register all commands âââ
    commands_map = {
        "start": start,
        "comandos": comandos,
        "estado": estado,
        "nueva_campana": nueva_campana,
        "pausar": pausar,
        "metricas": metricas,
        "listar_campanas": listar_campanas,
        "reporte_diario": reporte_diario,
        # Mode
        "jarvis": jarvis_mode,
        "s180": s180_mode,
        # Security
        "pendientes": pendientes_cmd,
        "aprobar": aprobar_cmd,
        "rechazar": rechazar_cmd,
        # CRM
        "clientes": clientes,
        "afiliados": afiliados,
        "agentes": agentes,
        "alta_cliente": alta_cliente,
        # Prospection
        "prospectar": prospectar,
        "leads": leads,
        "autopilot": autopilot_cmd,
        "autopilot_status": autopilot_status,
        "email_blast": email_blast,
        # Maestro
        "maestro": maestro,
        "health": health,
        "brain_cmd": brain_cmd,
        # Outreach
        "outreach_stats": outreach_stats,
        "ig_accounts": ig_accounts,
        # Instagram Multi-Cuenta
        "ig_add": ig_add,
        "ig_remove": ig_remove,
        "ig_login": ig_login,
        "ig_code": ig_code,
        "ig_status": ig_status,
        "ig_limite": ig_limite,
        "ig_prospectar": ig_prospectar_cmd,
        "ig_competidor": ig_competidor,
        "ig_maps": ig_maps,
        "ig_parar": ig_parar,
        "ig_stats": ig_stats,
        # Backup + GDPR
        "backup": backup_cmd,
        "borrar_datos": borrar_datos,
        "metricas": metricas_cmd,
        # Antigravity bridge
        "codigo": codigo_cmd,
        "code_status": code_status_cmd,
        # JARVIS Cloud (sin PC)
        "reporte": reporte_cmd,
        "reporte_semanal": reporte_semanal_cmd,
        "factura": factura_cmd,
        "lead_score": lead_score_cmd,
        "followups": followups_cmd,
        "renovaciones": renovaciones_cmd,
        "cloud_code": cloud_code_cmd,
        # WhatsApp
        "wa_enviar": wa_enviar_cmd,
        "wa_chats": wa_chats_cmd,
        "wa_chat": wa_chat_cmd,
        "wa_responder": wa_responder_cmd,
        # JARVIS quick
        "hora": hora_cmd,
        "chiste": chiste_cmd,
        "frase": frase_cmd,
        # Voice config
        "voz": voz_cmd,
        # Cerebro S180 (Doctrina)
        "cerebro": cerebro_cmd,
        "caja": caja_cmd,
        "caja_urgente": caja_urgente_cmd,
        "regulacion": regulacion_cmd,
        "ordename": ordename_cmd,
        "cierre_dia": cierre_dia_cmd,
        "pipeline_prioridad": pipeline_prioridad_cmd,
        "precios": precios_cmd,
        "angulos": angulos_cmd,
        "guion": guion_cmd,
        "salud_operador": salud_operador_cmd,
        "regla37": regla37_cmd,
    }

    for cmd_name, handler_fn in commands_map.items():
        app.add_handler(CommandHandler(cmd_name, handler_fn))

    # Voice handler
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Text handler (conversational â must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Register menu
    async def post_init(application):
        menu_items = [
            ("start", "Iniciar"),
            ("comandos", "Ver todos los comandos"),
            ("estado", "Estado del sistema"),
            ("jarvis", "Modo JARVIS"),
            ("cerebro", "Cerebro S180 — Doctrina"),
            ("caja", "Protocolo de caja"),
            ("ordename", "Ordename hoy"),
            ("regulacion", "Regulacion rapida"),
            ("precios", "Escalera precios"),
            ("angulos", "15 angulos contenido"),
            ("guion", "Generar guion"),
            ("nueva_campana", "Crear campana"),
            ("metricas", "Ver metricas"),
            ("autopilot", "Autopilot DMs"),
        ]
        from telegram import BotCommand
        await application.bot.set_my_commands(
            [BotCommand(cmd, desc) for cmd, desc in menu_items]
        )
        logger.info("Bot commands menu registered")

    app.post_init = post_init

    logger.info(f"Bot S180 v2 iniciado. {len(commands_map)} comandos + modo conversacional + SecurityGate.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
