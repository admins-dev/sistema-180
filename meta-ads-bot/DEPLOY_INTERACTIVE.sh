#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA 180 — Railway Deployment (Interactive)
# Guía interactiva para obtener credenciales y desplegar a Railway
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                  🚀 SISTEMA 180 — RAILWAY DEPLOYMENT                       ║"
echo "║                   Security-Hardened Meta Ads Bot                           ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# ─── Check Prerequisites ───
echo -e "${YELLOW}📋 Verificando requisitos...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git no instalado${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm no instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Git y npm disponibles${NC}"

# ─── Install Railway CLI if needed ───
if ! command -v railway &> /dev/null; then
    echo ""
    echo -e "${YELLOW}📦 Instalando Railway CLI...${NC}"
    npm install -g @railway/cli
    echo -e "${GREEN}✅ Railway CLI instalado${NC}"
else
    echo -e "${GREEN}✅ Railway CLI ya disponible${NC}"
fi

# ─── Navigate to meta-ads-bot ───
cd "$(dirname "$0")"
echo ""
echo -e "${YELLOW}📁 Directorio de trabajo: $(pwd)${NC}"

# ─── Check requirements.txt ───
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ requirements.txt encontrado${NC}"

# ─── Interactive Credential Collection ───
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🔐 RECOLECCIÓN DE CREDENCIALES                          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Meta Access Token
echo -e "${BLUE}1. META ACCESS TOKEN${NC}"
echo "   Cómo obtenerlo:"
echo "   → https://developers.facebook.com/apps"
echo "   → Tu app → Settings → Basic"
echo "   → Scroll abajo → Generate New Token"
echo "   → Permisos: ads_read + ads_management"
echo ""
read -sp "   Pega tu Meta Access Token: " META_ACCESS_TOKEN
echo ""
if [ -z "$META_ACCESS_TOKEN" ]; then
    echo -e "${RED}❌ Token vacío, abortando${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Token guardado${NC}"

# Telegram Bot Token
echo ""
echo -e "${BLUE}2. TELEGRAM BOT TOKEN${NC}"
echo "   Cómo obtenerlo:"
echo "   → Telegram: Busca @BotFather"
echo "   → Envía: /newbot"
echo "   → Nombre: Sistema 180 Ads Bot"
echo "   → Username: algo único (ej: sistema180adsbot)"
echo "   → Copia el token (formato: 123456:ABC-DEF...)"
echo ""
read -sp "   Pega tu Telegram Bot Token: " TELEGRAM_BOT_TOKEN
echo ""
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ Token vacío, abortando${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Token guardado${NC}"

# Telegram User ID
echo ""
echo -e "${BLUE}3. TU ID DE TELEGRAM${NC}"
echo "   Cómo obtenerlo:"
echo "   → Telegram: Busca @userinfobot"
echo "   → Envía: /start"
echo "   → Copia tu ID (ej: 665665724415645)"
echo ""
read -p "   Pega tu ID de Telegram: " TELEGRAM_USER_ID
if [ -z "$TELEGRAM_USER_ID" ]; then
    echo -e "${RED}❌ ID vacío, abortando${NC}"
    exit 1
fi
echo -e "${GREEN}✅ ID guardado${NC}"

# Meta Ad Account ID
echo ""
echo -e "${BLUE}4. META AD ACCOUNT ID${NC}"
echo "   Cómo obtenerlo:"
echo "   → https://ads.facebook.com"
echo "   → Settings → Ad Account"
echo "   → Copia el ID (formato: 665665724415645 o act_XXXXXXXXX)"
echo ""
read -p "   Pega tu Meta Ad Account ID: " META_AD_ACCOUNT_ID
if [ -z "$META_AD_ACCOUNT_ID" ]; then
    echo -e "${RED}❌ ID vacío, abortando${NC}"
    exit 1
fi
# Normalize to act_ format if needed
if [[ ! $META_AD_ACCOUNT_ID =~ ^act_ ]]; then
    META_AD_ACCOUNT_ID="act_$META_AD_ACCOUNT_ID"
fi
echo -e "${GREEN}✅ ID guardado: $META_AD_ACCOUNT_ID${NC}"

# ─── Railway Authentication ───
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🔑 AUTENTICACIÓN RAILWAY                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Si no tienes cuenta Railway:"
echo "  1. Ve a https://railway.app"
echo "  2. Haz click en 'Sign Up'"
echo "  3. Completa el registro"
echo ""
read -p "Presiona Enter cuando estés listo para login en Railway..."

railway login

# ─── Railway Project Setup ───
echo ""
echo -e "${YELLOW}📊 Configurando proyecto Railway...${NC}"

# Create or link project
RAILWAY_PROJECT="sistema-180-meta-ads"
railway init --name "$RAILWAY_PROJECT" || true

echo -e "${GREEN}✅ Proyecto Railway configurado${NC}"

# ─── Set Environment Variables ───
echo ""
echo -e "${YELLOW}🔑 Configurando variables de entorno en Railway...${NC}"

railway variables set META_ACCESS_TOKEN="$META_ACCESS_TOKEN" || echo -e "${YELLOW}⚠️  META_ACCESS_TOKEN${NC}"
railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" || echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN${NC}"
railway variables set TELEGRAM_ALLOWED_USER_IDS="$TELEGRAM_USER_ID" || echo -e "${YELLOW}⚠️  TELEGRAM_ALLOWED_USER_IDS${NC}"
railway variables set META_AD_ACCOUNT_ID="$META_AD_ACCOUNT_ID" || echo -e "${YELLOW}⚠️  META_AD_ACCOUNT_ID${NC}"
railway variables set FLASK_ENV="production" || echo -e "${YELLOW}⚠️  FLASK_ENV${NC}"
railway variables set FLASK_DEBUG="false" || echo -e "${YELLOW}⚠️  FLASK_DEBUG${NC}"
railway variables set META_PIXEL_ID="0" || echo -e "${YELLOW}⚠️  META_PIXEL_ID${NC}"

echo -e "${GREEN}✅ Variables de entorno configuradas${NC}"

# ─── Deploy ───
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🚀 DESPLEGANDO A RAILWAY                                ║"
echo "║                    Esto puede tomar 2-5 minutos...                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

railway up

# ─── Get Project URL ───
echo ""
echo -e "${YELLOW}🔍 Obteniendo URL del proyecto...${NC}"
RAILWAY_URL=$(railway domain 2>/dev/null || echo "unknown")

# ─── Verification ───
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEPLOYMENT COMPLETADO                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📱 URL del Backend: ${BLUE}$RAILWAY_URL${NC}"
echo ""
echo -e "${YELLOW}🔗 Próximos pasos:${NC}"
echo ""
echo "1️⃣  Verifica Health Check (en 30 segundos):"
echo "   ${BLUE}curl $RAILWAY_URL/health${NC}"
echo ""
echo "2️⃣  Prueba tu Telegram Bot:"
echo "   • Abre Telegram"
echo "   • Busca tu bot (@...AdsBot)"
echo "   • Envía: /start"
echo "   • Debe responder con bienvenida"
echo ""
echo "3️⃣  Dashboard:"
echo "   • Vercel: ${BLUE}https://sistema-180.vercel.app${NC}"
echo "   • Railway: ${BLUE}https://railway.app${NC}"
echo ""
echo "4️⃣  Control de Agentes:"
echo "   • Ve al dashboard → Sidebar → 🎮 Control Panel"
echo "   • Botón: 🚀 Spawn Todos (57)"
echo ""
echo -e "${YELLOW}📊 Monitoreo de Logs:${NC}"
echo "   • Railway Dashboard → Logs"
echo "   • Busca: ERROR, WARNING"
echo ""
echo -e "${YELLOW}🔐 Recordatorio de Seguridad:${NC}"
echo "   • X-API-Key requerida para todas las llamadas API"
echo "   • Solo tu ID de Telegram puede usar comandos"
echo "   • Tokens guardados en Railway (no en git)"
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║  ¡Sistema 180 Meta Ads Bot está VIVO y PROTEGIDO en producción! 🚀          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
