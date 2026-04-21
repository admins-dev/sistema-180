"""
Sistema 180 — API Service
Backend API para el dashboard de Sistema 180 (Vercel frontend).
Endpoints para agentes, Meta Ads, CRM y métricas.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import secrets
import logging
import time
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

# ─── Logging ───
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger("api-service")

app = Flask(__name__)

# ─── CORS ───
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://sistema-180.vercel.app",
    "https://dist-eta-mocha.vercel.app",
]
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS, "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "X-API-Key"]}})

# ─── API Key Authentication ───
API_SECRET = os.getenv("FLASK_API_SECRET", secrets.token_hex(32))


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if not key or not secrets.compare_digest(key, API_SECRET):
            logger.warning(f"Unauthorized access to {request.path}")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════
# AGENT DEFINITIONS — 57 Agents
# ══════════════════════════════════════════════════

AGENT_DEFINITIONS = [
    # ── Revenue & Sales ──
    {"id": "closer-principal", "name": "Closer Principal", "role": "Cierra ventas high-ticket", "department": "revenue", "status": "active"},
    {"id": "prospector-b2b", "name": "Prospector B2B", "role": "Identificación de leads empresariales", "department": "revenue", "status": "active"},
    {"id": "lead-qualifier", "name": "Lead Qualifier", "role": "Cualifica leads por scoring", "department": "revenue", "status": "active"},
    {"id": "follow-up-engine", "name": "Follow-Up Engine", "role": "Secuencias de seguimiento automatizado", "department": "revenue", "status": "active"},
    {"id": "objection-handler", "name": "Objection Handler", "role": "Maneja objeciones de ventas", "department": "revenue", "status": "active"},
    {"id": "pricing-optimizer", "name": "Pricing Optimizer", "role": "Optimiza precios según mercado", "department": "revenue", "status": "active"},
    {"id": "upsell-agent", "name": "Upsell Agent", "role": "Detecta oportunidades de upsell", "department": "revenue", "status": "active"},
    {"id": "contract-generator", "name": "Contract Generator", "role": "Genera contratos y propuestas", "department": "revenue", "status": "active"},
    {"id": "payment-collector", "name": "Payment Collector", "role": "Gestión de cobros y facturación", "department": "revenue", "status": "active"},
    {"id": "churn-predictor", "name": "Churn Predictor", "role": "Predice riesgo de baja de clientes", "department": "revenue", "status": "active"},

    # ── Marketing & Ads ──
    {"id": "meta-ads-manager", "name": "Meta Ads Manager", "role": "Gestión campañas Meta (FB/IG)", "department": "marketing", "status": "active"},
    {"id": "google-ads-manager", "name": "Google Ads Manager", "role": "Gestión campañas Google Ads", "department": "marketing", "status": "active"},
    {"id": "copywriter-ai", "name": "Copywriter AI", "role": "Genera copy persuasivo", "department": "marketing", "status": "active"},
    {"id": "creative-director", "name": "Creative Director", "role": "Dirección creativa de anuncios", "department": "marketing", "status": "active"},
    {"id": "audience-builder", "name": "Audience Builder", "role": "Construye audiencias y lookalikes", "department": "marketing", "status": "active"},
    {"id": "ab-tester", "name": "A/B Tester", "role": "Testing de variantes de anuncios", "department": "marketing", "status": "active"},
    {"id": "budget-allocator", "name": "Budget Allocator", "role": "Distribuye presupuesto entre campañas", "department": "marketing", "status": "active"},
    {"id": "retargeting-engine", "name": "Retargeting Engine", "role": "Secuencias de retargeting avanzado", "department": "marketing", "status": "active"},
    {"id": "seo-optimizer", "name": "SEO Optimizer", "role": "Optimización SEO on-page/off-page", "department": "marketing", "status": "active"},
    {"id": "content-calendar", "name": "Content Calendar", "role": "Planifica calendario editorial", "department": "marketing", "status": "active"},
    {"id": "email-marketer", "name": "Email Marketer", "role": "Campañas de email marketing", "department": "marketing", "status": "active"},
    {"id": "social-scheduler", "name": "Social Scheduler", "role": "Programa publicaciones en redes", "department": "marketing", "status": "active"},

    # ── Operations ──
    {"id": "jarvis-core", "name": "JARVIS Core", "role": "Asistente principal de Sistema 180", "department": "operations", "status": "active"},
    {"id": "task-router", "name": "Task Router", "role": "Enruta tareas a agentes especializados", "department": "operations", "status": "active"},
    {"id": "scheduler", "name": "Scheduler", "role": "Gestión de agenda y calendarios", "department": "operations", "status": "active"},
    {"id": "inbox-manager", "name": "Inbox Manager", "role": "Gestión inteligente de emails", "department": "operations", "status": "active"},
    {"id": "meeting-prep", "name": "Meeting Prep", "role": "Prepara briefings para reuniones", "department": "operations", "status": "active"},
    {"id": "report-generator", "name": "Report Generator", "role": "Genera informes automáticos", "department": "operations", "status": "active"},
    {"id": "workflow-automator", "name": "Workflow Automator", "role": "Automatiza flujos de trabajo n8n", "department": "operations", "status": "active"},
    {"id": "data-sync", "name": "Data Sync", "role": "Sincronización de datos entre plataformas", "department": "operations", "status": "active"},
    {"id": "backup-guardian", "name": "Backup Guardian", "role": "Respaldos automáticos de datos", "department": "operations", "status": "active"},
    {"id": "health-monitor", "name": "Health Monitor", "role": "Monitoriza salud de servicios", "department": "operations", "status": "active"},

    # ── Client Success ──
    {"id": "onboarding-agent", "name": "Onboarding Agent", "role": "Onboarding automatizado de clientes", "department": "client_success", "status": "active"},
    {"id": "support-tier1", "name": "Support Tier 1", "role": "Soporte básico automatizado", "department": "client_success", "status": "active"},
    {"id": "support-tier2", "name": "Support Tier 2", "role": "Soporte avanzado con contexto", "department": "client_success", "status": "active"},
    {"id": "satisfaction-survey", "name": "Satisfaction Survey", "role": "Encuestas de satisfacción NPS", "department": "client_success", "status": "active"},
    {"id": "review-collector", "name": "Review Collector", "role": "Solicita y gestiona reseñas", "department": "client_success", "status": "active"},
    {"id": "referral-engine", "name": "Referral Engine", "role": "Programa de referidos automatizado", "department": "client_success", "status": "active"},
    {"id": "client-reporter", "name": "Client Reporter", "role": "Informes mensuales para clientes", "department": "client_success", "status": "active"},

    # ── Intelligence & Analytics ──
    {"id": "market-analyzer", "name": "Market Analyzer", "role": "Análisis de mercado y competencia", "department": "intelligence", "status": "active"},
    {"id": "trend-detector", "name": "Trend Detector", "role": "Detecta tendencias del sector", "department": "intelligence", "status": "active"},
    {"id": "competitor-spy", "name": "Competitor Spy", "role": "Monitoriza competencia", "department": "intelligence", "status": "active"},
    {"id": "sentiment-analyzer", "name": "Sentiment Analyzer", "role": "Análisis de sentimiento de marca", "department": "intelligence", "status": "active"},
    {"id": "roi-calculator", "name": "ROI Calculator", "role": "Calcula ROI por canal y campaña", "department": "intelligence", "status": "active"},
    {"id": "forecast-engine", "name": "Forecast Engine", "role": "Predicciones de revenue", "department": "intelligence", "status": "active"},
    {"id": "kpi-tracker", "name": "KPI Tracker", "role": "Tracking de KPIs en tiempo real", "department": "intelligence", "status": "active"},
    {"id": "anomaly-detector", "name": "Anomaly Detector", "role": "Detecta anomalías en métricas", "department": "intelligence", "status": "active"},

    # ── Content & Creative ──
    {"id": "video-producer", "name": "Video Producer", "role": "Producción de vídeos con IA", "department": "creative", "status": "active"},
    {"id": "image-generator", "name": "Image Generator", "role": "Genera imágenes para anuncios", "department": "creative", "status": "active"},
    {"id": "script-writer", "name": "Script Writer", "role": "Escribe guiones para vídeos", "department": "creative", "status": "active"},
    {"id": "brand-voice", "name": "Brand Voice", "role": "Mantiene consistencia de marca", "department": "creative", "status": "active"},
    {"id": "landing-builder", "name": "Landing Builder", "role": "Construye landing pages", "department": "creative", "status": "active"},

    # ── Infrastructure ──
    {"id": "deploy-agent", "name": "Deploy Agent", "role": "CI/CD y deploys automatizados", "department": "infrastructure", "status": "active"},
    {"id": "security-scanner", "name": "Security Scanner", "role": "Escaneo de seguridad continuo", "department": "infrastructure", "status": "active"},
    {"id": "cost-optimizer", "name": "Cost Optimizer", "role": "Optimiza costes de infraestructura", "department": "infrastructure", "status": "active"},
    {"id": "log-analyzer", "name": "Log Analyzer", "role": "Análisis de logs y errores", "department": "infrastructure", "status": "active"},
    {"id": "api-gateway", "name": "API Gateway", "role": "Gestión de APIs y rate limiting", "department": "infrastructure", "status": "active"},
]

BOOT_TIME = time.time()


# ══════════════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'sistema-180-api',
        'version': '1.0.0',
        'uptime_seconds': round(time.time() - BOOT_TIME, 1),
    }), 200


# ══════════════════════════════════════════════════
# AGENTS API
# ══════════════════════════════════════════════════

@app.route('/api/agents', methods=['GET'])
@require_api_key
def get_agents():
    """Returns all 57 agents with status."""
    department = request.args.get('department')
    agents = AGENT_DEFINITIONS
    if department:
        agents = [a for a in agents if a['department'] == department]
    return jsonify({
        'total': len(agents),
        'active': len([a for a in agents if a['status'] == 'active']),
        'agents': agents,
    })


@app.route('/api/agents/<agent_id>', methods=['GET'])
@require_api_key
def get_agent(agent_id):
    """Returns a single agent by ID."""
    agent = next((a for a in AGENT_DEFINITIONS if a['id'] == agent_id), None)
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    return jsonify(agent)


@app.route('/api/agents/departments', methods=['GET'])
@require_api_key
def get_departments():
    """Returns agent counts per department."""
    deps = {}
    for a in AGENT_DEFINITIONS:
        d = a['department']
        deps[d] = deps.get(d, 0) + 1
    return jsonify({
        'departments': deps,
        'total_agents': len(AGENT_DEFINITIONS),
    })


# ══════════════════════════════════════════════════
# META ADS API (Proxy to main bot)
# ══════════════════════════════════════════════════

@app.route('/api/meta-ads/status', methods=['GET'])
@require_api_key
def meta_ads_status():
    return jsonify({
        'active': True,
        'metaConnected': True,
        'service': 'meta-ads-bot',
        'totalCampaigns': 0,
    })


@app.route('/api/meta-ads/campaigns', methods=['GET'])
@require_api_key
def meta_ads_campaigns():
    return jsonify([])


# ══════════════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════════════

@app.route('/api/dashboard/stats', methods=['GET'])
@require_api_key
def dashboard_stats():
    """Main dashboard statistics."""
    return jsonify({
        'agents': {
            'total': len(AGENT_DEFINITIONS),
            'active': len([a for a in AGENT_DEFINITIONS if a['status'] == 'active']),
            'departments': len(set(a['department'] for a in AGENT_DEFINITIONS)),
        },
        'revenue': {
            'mrr': 0,
            'arr': 0,
            'pipeline': 0,
            'clients_active': 0,
        },
        'marketing': {
            'campaigns_active': 0,
            'total_spend': 0,
            'total_leads': 0,
            'conversion_rate': 0,
        },
        'system': {
            'status': 'operational',
            'uptime_seconds': round(time.time() - BOOT_TIME, 1),
            'services': ['api-service', 'meta-ads-bot', 'vercel-frontend'],
        },
    })


# ══════════════════════════════════════════════════
# CRM API
# ══════════════════════════════════════════════════

@app.route('/api/crm/leads', methods=['GET'])
@require_api_key
def crm_leads():
    return jsonify({'leads': [], 'total': 0})


@app.route('/api/crm/clients', methods=['GET'])
@require_api_key
def crm_clients():
    return jsonify({'clients': [], 'total': 0})


# ══════════════════════════════════════════════════
# ENTRYPOINT
# ══════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    logger.info(f"🚀 Sistema 180 API Service starting on port {port}")
    logger.info(f"📊 {len(AGENT_DEFINITIONS)} agents loaded")
    logger.info(f"🔑 API Key: {API_SECRET[:16]}...")
    app.run(debug=debug, port=port, host='0.0.0.0')
