import logging
from meta_client import MetaAdsClient

logger = logging.getLogger(__name__)

# Instancia global del cliente Meta
meta_client = None


def init_meta_client(access_token: str = None, ad_account_id: str = None) -> None:
    """Inicializa el cliente Meta API (graceful — no crashea si faltan env vars)"""
    global meta_client
    try:
        meta_client = MetaAdsClient(access_token, ad_account_id)
        if meta_client.is_ready:
            logger.info("[Sync] Meta client initialized and ready")
        else:
            logger.warning("[Sync] Meta client created but disabled (missing env vars)")
    except Exception as e:
        logger.error(f"[Sync] Error initializing Meta client: {e}")
        meta_client = None


def sync_nueva_campaña(presupuesto_eur: float, nombre: str) -> str:
    """Crea campaña en Meta API. Presupuesto en EUR."""
    if not meta_client or not meta_client.is_ready:
        return "⚠️ Meta API no conectada — campaña guardada solo en local"
    try:
        presupuesto_cents = int(presupuesto_eur * 100)
        result = meta_client.create_campaign(nombre, presupuesto_cents)
        if result["campaign_id"]:
            logger.info(f"Campaign {nombre} created: {result['campaign_id']}")
            return f"✅ Campaña '{nombre}' creada en Meta\nID: {result['campaign_id']}\nPresupuesto: €{presupuesto_eur:.2f}/día"
        return "❌ Error creando campaña en Meta API"
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


def sync_pausar(campaign_id: str) -> str:
    """Pausa una campaña"""
    if not meta_client or not meta_client.is_ready:
        return "⚠️ Meta API no conectada"
    try:
        result = meta_client.pause_campaign(campaign_id)
        if result["status"] == "PAUSED":
            logger.info(f"Campaign {campaign_id} paused")
            return f"⏸️ Campaña {campaign_id} pausada"
        return "❌ Error pausando campaña"
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


def sync_metricas(campaign_id: str) -> str:
    """Obtiene métricas formateadas para Telegram"""
    if not meta_client or not meta_client.is_ready:
        return "⚠️ Meta API no conectada"
    try:
        m = meta_client.get_metrics(campaign_id)
        cpa = m.get("cpa", 0)
        return (
            f"📊 Campaña: {campaign_id}\n"
            f"Gasto: €{m.get('spend', 0):.2f}\n"
            f"Leads: {m.get('leads', 0)}\n"
            f"CPA: €{cpa:.2f}\n"
            f"CPC: €{m.get('cpc', 0):.2f}"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


def sync_reporte() -> str:
    """Compila reporte diario basado en campañas en memoria (desde bot.py)"""
    return "📈 Para reporte diario, llama a /reporte_diario en Telegram"
