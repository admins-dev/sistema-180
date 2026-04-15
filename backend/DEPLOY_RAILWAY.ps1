# ══════════════════════════════════════════════════════════════════════════════
# SISTEMA 180 — RAILWAY DEPLOYMENT (Windows PowerShell)
# ══════════════════════════════════════════════════════════════════════════════
# Ejecución: .\DEPLOY_RAILWAY.ps1
# No requiere login — usa API Token directamente
# ══════════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"

# ─── RAILWAY API TOKEN ───
$env:RAILWAY_TOKEN = "9f2416c2-6e5a-4056-9226-6bd20a4c4446"

# ─── HELPERS ───
function Log-Title($msg) {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $msg" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Log-Success($msg) { Write-Host "  ✅ $msg" -ForegroundColor Green }
function Log-Error($msg)   { Write-Host "  ❌ $msg" -ForegroundColor Red }
function Log-Warning($msg) { Write-Host "  ⚠️  $msg" -ForegroundColor Yellow }
function Log-Info($msg)    { Write-Host "  ℹ️  $msg" -ForegroundColor Blue }
function Log-Step($msg)    { Write-Host "  ▶ $msg" -ForegroundColor Cyan }

# ══════════════════════════════════════════════════════════════════════════════
Log-Title "🚀 SISTEMA 180 — RAILWAY DEPLOYMENT ENGINE"
# ══════════════════════════════════════════════════════════════════════════════

# ─── FASE 1: PREREQUISITOS ───
Log-Info "FASE 1/5: Validando requisitos previos..."

# Check Git
try { git --version | Out-Null; Log-Success "Git disponible" }
catch { Log-Error "Git no instalado"; exit 1 }

# Check npm
try { npm --version | Out-Null; Log-Success "npm disponible" }
catch { Log-Error "npm no instalado"; exit 1 }

# ─── FASE 2: RAILWAY CLI ───
Log-Info "FASE 2/5: Preparando Railway CLI..."

$railwayCli = Get-Command railway -ErrorAction SilentlyContinue
if (-not $railwayCli) {
    Log-Step "Instalando Railway CLI globalmente..."
    npm install -g @railway/cli
    Log-Success "Railway CLI instalado"
} else {
    Log-Success "Railway CLI ya disponible"
}

# ─── FASE 3: VALIDAR DIRECTORIO ───
Log-Info "FASE 3/5: Validando directorio y archivos..."

$backendDir = Split-Path -Parent $PSCommandPath
Set-Location $backendDir
Log-Success "Directorio: $backendDir"

if (-not (Test-Path "package.json")) {
    Log-Error "package.json no encontrado en $backendDir"
    exit 1
}
Log-Success "package.json encontrado"

if (-not (Test-Path "src/index.js")) {
    Log-Error "src/index.js no encontrado"
    exit 1
}
Log-Success "src/index.js presente"

# ─── FASE 4: VERIFICAR AUTENTICACIÓN ───
Log-Title "🔐 AUTENTICACIÓN RAILWAY (API TOKEN)"

Log-Step "Verificando token..."
try {
    $whoami = railway whoami 2>&1
    Log-Success "Autenticado como: $whoami"
} catch {
    Log-Error "Token inválido o expirado. Genera uno nuevo en https://railway.com/account/tokens"
    exit 1
}

# ─── FASE 5: DEPLOY ───
Log-Title "⚡ DEPLOYING A RAILWAY"

Log-Info "FASE 5/5: Iniciando deploy..."

# Crear Procfile si no existe (Railway lo necesita para saber cómo arrancar)
if (-not (Test-Path "Procfile")) {
    Log-Step "Creando Procfile..."
    "web: npm start" | Set-Content -Path "Procfile" -Encoding UTF8
    Log-Success "Procfile creado"
}

# Crear nixpacks.toml para configurar el build
if (-not (Test-Path "nixpacks.toml")) {
    Log-Step "Creando nixpacks.toml..."
    @"
[phases.setup]
nixPkgs = ["nodejs_20"]

[phases.install]
cmds = ["npm ci || npm install"]

[start]
cmd = "npm start"
"@ | Set-Content -Path "nixpacks.toml" -Encoding UTF8
    Log-Success "nixpacks.toml creado"
}

# Inicializar proyecto en Railway
Log-Step "Inicializando proyecto en Railway..."
try {
    railway init --name "sistema-180-backend" 2>&1 | Out-Null
    Log-Success "Proyecto creado/vinculado"
} catch {
    Log-Warning "Proyecto ya existe o error al crear — continuando..."
}

# Configurar variables de entorno desde .env.example como referencia
Log-Step "Configurando variables de entorno en Railway..."

# Variables de producción necesarias
$envVars = @{
    "NODE_ENV"         = "production"
    "PORT"             = "3000"
    "FRONT_URL"        = "https://dist-eta-mocha.vercel.app"
}

foreach ($key in $envVars.Keys) {
    try {
        railway variables set "$key=$($envVars[$key])" 2>&1 | Out-Null
        Log-Success "  $key configurada"
    } catch {
        Log-Warning "  $key ya existe o error"
    }
}

Log-Warning "IMPORTANTE: Necesitas configurar manualmente las variables sensibles:"
Write-Host "   railway variables set DATABASE_URL=postgres://..."  -ForegroundColor Magenta
Write-Host "   railway variables set STRIPE_SECRET_KEY=sk_test_..." -ForegroundColor Magenta
Write-Host "   railway variables set STRIPE_WEBHOOK_SECRET=whsec_..." -ForegroundColor Magenta
Write-Host "   railway variables set SLACK_BOT_TOKEN=xoxb-..." -ForegroundColor Magenta
Write-Host ""

# Deploy
Log-Step "Desplegando código a Railway..."
Log-Warning "Esto puede tomar 2-5 minutos..."
Write-Host ""

railway up --detach

Log-Success "Deploy iniciado"

# Obtener dominio
Log-Step "Generando dominio público..."
try {
    $domain = railway domain 2>&1
    Log-Success "Dominio: $domain"
} catch {
    Log-Warning "No se pudo generar dominio automáticamente"
    Log-Info "Genera uno manualmente en Railway Dashboard → Settings → Domains"
}

# ═══════════════════════════════════════════════════════════════════════════
Log-Title "📋 PRÓXIMOS PASOS"
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "  1️⃣  CONFIGURA VARIABLES SENSIBLES:" -ForegroundColor Cyan
Write-Host "     Ve a Railway Dashboard → tu proyecto → Variables" -ForegroundColor White
Write-Host "     Añade: DATABASE_URL, STRIPE_SECRET_KEY, SLACK_BOT_TOKEN, etc." -ForegroundColor White
Write-Host ""
Write-Host "  2️⃣  VERIFICA HEALTH CHECK:" -ForegroundColor Cyan
Write-Host "     curl https://tu-dominio.railway.app/health" -ForegroundColor Magenta
Write-Host ""
Write-Host "  3️⃣  ACTUALIZA VERCEL FRONTEND:" -ForegroundColor Cyan
Write-Host "     Cambia la URL del backend en el frontend para apuntar a Railway" -ForegroundColor White
Write-Host ""
Write-Host "  4️⃣  CONFIGURA STRIPE WEBHOOK:" -ForegroundColor Cyan
Write-Host "     En Stripe Dashboard → Webhooks → Añade endpoint:" -ForegroundColor White
Write-Host "     https://tu-dominio.railway.app/webhook" -ForegroundColor Magenta
Write-Host ""

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║    🎉 DEPLOY INICIADO — REVISA RAILWAY DASHBOARD           ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
