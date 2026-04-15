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

def only_authorized(f):
    @wraps(f)
    async def decorated(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if TELEGRAM_ALLOWED_USER_IDS and user_id not in TELEGRAM_ALLOWED_USER_IDS:
            logger.warning(f"Unauthorized: {user_id}")
            await update.message.reply_text("No tienes permiso para usar este bot.")
            return
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
    1. Brain IA procesa el mensaje (con la persona activa: S180 o JARVIS)
    2. Si brain detecta una acciÃ³n Meta Ads, la ejecuta via SecurityGate
    3. Responde siempre de forma natural
    """
    user_id = str(update.effective_user.id)
    text = update.message.text

    if not text:
        return

    # Obtener modo actual
    mode = _user_modes.get(int(user_id) if user_id.isdigit() else 0, "s180")

    # Usar brain.py como interfaz principal
    if brain_mod:
        try:
            # Obtener meta status para contexto
            meta_status = "desconocido"
            if sync_module and hasattr(sync_module, 'meta_client') and sync_module.meta_client:
                meta_status = "conectada" if sync_module.meta_client.is_ready else "desconectada"

            response = brain_mod.chat(
                user_id=user_id,
                message=text,
                persona=mode,
                meta_status=meta_status,
            )

            # En modo JARVIS: decide si responder con audio o texto
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
        # JARVIS quick
        "hora": hora_cmd,
        "chiste": chiste_cmd,
        "frase": frase_cmd,
        # Voice config
        "voz": voz_cmd,
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
            ("nueva_campana", "Crear campana"),
            ("metricas", "Ver metricas"),
            ("pendientes", "Acciones pendientes"),
            ("autopilot", "Autopilot DMs"),
            ("reporte_diario", "Reporte diario"),
            ("hora", "Hora actual"),
            ("chiste", "Chiste de JARVIS"),
            ("frase", "Cita Iron Man"),
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
