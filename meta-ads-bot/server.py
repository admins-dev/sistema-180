from flask import Flask, jsonify, request
from flask_cors import CORS
from meta_client import MetaAdsClient
from sync import sync_nueva_campaña, sync_pausar, sync_metricas, init_meta_client
import os
import secrets
import logging
import re
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

# ─── Logging ───
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ─── CORS Restringido (CRÍTICO) ───
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://sistema-180.vercel.app", "https://dist-eta-mocha.vercel.app"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "X-API-Key"]
    }
})

# ─── API Key Authentication (CRÍTICO) ───
API_SECRET = os.getenv("FLASK_API_SECRET", secrets.token_hex(32))

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if not key or not secrets.compare_digest(key, API_SECRET):
            logger.warning(f"Acceso no autorizado a {request.path}")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ─── Campaign ID Validation (ALTO) ───
def validate_campaign_id(cid: str) -> bool:
    """Valida que campaign_id sea numérico (Meta format)"""
    return bool(re.match(r'^\d{10,20}$', str(cid)))

# ─── Rate Limiting (ALTO) ───
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["100 per hour"])
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False
    logger.warning("flask-limiter no instalado, rate limiting deshabilitado")

# Inicializar cliente Meta (graceful — no crashea)
meta_client = None
try:
    init_meta_client()
    from sync import meta_client
    logger.info(f"[Server] Meta client ready: {meta_client.is_ready if meta_client else False}")
except Exception as e:
    logger.warning(f"[Server] Meta client init failed (non-fatal): {e}")

# ─── Almacenamiento en memoria ───
campaigns_cache = {}


@app.route('/api/meta-ads/status', methods=['GET'])
@require_api_key
def get_status():
    """Estado del bot y última sincronización"""
    return jsonify({
        'active': True,
        'metaConnected': meta_client.is_ready if meta_client else False,
        'lastSync': campaigns_cache.get('_lastSync'),
        'totalCampaigns': len([c for c in campaigns_cache if not c.startswith('_')])
    })


@app.route('/api/meta-ads/campaigns', methods=['GET'])
@require_api_key
def get_campaigns():
    """Lista campañas con métricas"""
    try:
        campaigns = []
        for cid, data in campaigns_cache.items():
            if not cid.startswith('_'):
                metrics = sync_metricas(cid)
                campaigns.append({
                    'id': cid,
                    'name': data.get('name'),
                    'budget': data.get('budget'),
                    'status': data.get('status'),
                    'metrics': metrics
                })
        return jsonify(campaigns)
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}", exc_info=True)
        return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/api/meta-ads/launch', methods=['POST'])
@require_api_key
def launch_campaign():
    """Crea campaña nueva"""
    try:
        data = request.json
        nombre = data.get('name', '').strip()
        presupuesto = data.get('budget')

        if not nombre or not presupuesto:
            return jsonify({'error': 'Falta nombre o presupuesto'}), 400

        if not isinstance(presupuesto, (int, float)) or presupuesto < 1 or presupuesto > 100000:
            return jsonify({'error': 'Presupuesto debe estar entre 1€ y 100.000€'}), 400

        result = sync_nueva_campaña(presupuesto, nombre)
        return jsonify({"message": result})
    except Exception as e:
        logger.error(f"Error launching campaign: {e}", exc_info=True)
        return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/api/meta-ads/pause/<campaign_id>', methods=['POST'])
@require_api_key
def pause_campaign(campaign_id):
    """Pausa campaña"""
    try:
        if not validate_campaign_id(campaign_id):
            return jsonify({'error': 'campaign_id inválido'}), 400

        result = sync_pausar(campaign_id)
        return jsonify({"message": result})
    except Exception as e:
        logger.error(f"Error pausing campaign {campaign_id}: {e}", exc_info=True)
        return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/api/meta-ads/metrics/<campaign_id>', methods=['GET'])
@require_api_key
def get_metrics(campaign_id):
    """Métricas de campaña"""
    try:
        if not validate_campaign_id(campaign_id):
            return jsonify({'error': 'campaign_id inválido'}), 400

        metrics = sync_metricas(campaign_id)
        return jsonify({"message": metrics})
    except Exception as e:
        logger.error(f"Error getting metrics for {campaign_id}: {e}", exc_info=True)
        return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint (no requiere auth)"""
    return jsonify({
        'status': 'ok',
        'service': 'meta-ads-bot',
        'metaConnected': meta_client.is_ready if meta_client else False,
        'nlpProviders': {
            'anthropic': bool(os.getenv("ANTHROPIC_API_KEY")),
            'groq': bool(os.getenv("GROQ_API_KEY")),
            'gemini': bool(os.getenv("GEMINI_API_KEY")),
        }
    }), 200


if __name__ == '__main__':
    flask_debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    flask_port = int(os.getenv("FLASK_PORT", os.getenv("PORT", 5000)))

    logger.info(f"🚀 Iniciando Flask server en puerto {flask_port}")
    logger.info(f"Debug mode: {flask_debug}")
    logger.info(f"API Key para acceso: {API_SECRET[:16]}...")

    app.run(debug=flask_debug, port=flask_port, host='0.0.0.0')
