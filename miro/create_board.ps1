# SISTEMA180 — Miro Board Schema Creator via REST API
$token = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_4lv8lG-CALzt_vuzXbYU0b-HxmE"
$boardId = "uXjVG1rJBTk="
$base = "https://api.miro.com/v2/boards/$boardId"
$h = @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" }

function Create-Shape($x, $y, $w, $h2, $text, $color, $shape="round_rectangle") {
    $body = @{
        data = @{ shape = $shape; content = $text }
        style = @{ fillColor = $color; fontFamily = "open_sans"; fontSize = "14"; textAlign = "center"; fontColor = "#ffffff"; borderColor = "transparent"; borderWidth = "0" }
        position = @{ x = $x; y = $y }
        geometry = @{ width = $w; height = $h2 }
    } | ConvertTo-Json -Depth 4
    try { Invoke-RestMethod -Uri "$base/shapes" -Headers $h -Method POST -Body $body | Out-Null; Write-Host "OK shape: $text" } catch { Write-Host "ERR shape: $_" }
}

function Create-Text($x, $y, $text, $size="24", $color="#ffffff") {
    $body = @{
        data = @{ content = $text }
        style = @{ fillOpacity = "0"; fontFamily = "open_sans"; fontSize = $size; textAlign = "center"; color = $color }
        position = @{ x = $x; y = $y }
    } | ConvertTo-Json -Depth 4
    try { Invoke-RestMethod -Uri "$base/texts" -Headers $h -Method POST -Body $body | Out-Null; Write-Host "OK text: $($text.Substring(0,[Math]::Min(30,$text.Length)))" } catch { Write-Host "ERR text: $_" }
}

function Create-Frame($x, $y, $w, $h2, $title) {
    $body = @{
        data = @{ format = "custom"; title = $title; type = "freeform" }
        style = @{ fillColor = "#1a1a2e" }
        position = @{ x = $x; y = $y }
        geometry = @{ width = $w; height = $h2 }
    } | ConvertTo-Json -Depth 4
    try { $r = Invoke-RestMethod -Uri "$base/frames" -Headers $h -Method POST -Body $body; Write-Host "OK frame: $title"; return $r.id } catch { Write-Host "ERR frame: $_"; return $null }
}

function Create-StickyNote($x, $y, $text, $color="yellow") {
    $body = @{
        data = @{ content = $text; shape = "square" }
        style = @{ fillColor = $color; textAlign = "left"; textAlignVertical = "top" }
        position = @{ x = $x; y = $y }
    } | ConvertTo-Json -Depth 4
    try { $r = Invoke-RestMethod -Uri "$base/sticky_notes" -Headers $h -Method POST -Body $body; Write-Host "OK sticky: $($text.Substring(0,[Math]::Min(30,$text.Length)))"; return $r.id } catch { Write-Host "ERR sticky: $_"; return $null }
}

function Create-Connector($startId, $endId) {
    $body = @{
        startItem = @{ id = $startId }
        endItem = @{ id = $endId }
        style = @{ strokeColor = "#4C8CFF"; strokeWidth = "2" }
    } | ConvertTo-Json -Depth 4
    try { Invoke-RestMethod -Uri "$base/connectors" -Headers $h -Method POST -Body $body | Out-Null; Write-Host "OK connector" } catch { Write-Host "ERR connector: $_" }
}

Write-Host "=== SISTEMA180 MIRO BOARD BUILDER ==="
Write-Host ""

# ────────────────────────────────────────────
# SECTION 1: MAIN TITLE (top center)
# ────────────────────────────────────────────
Write-Host "--- TITULO PRINCIPAL ---"
Create-Frame 0 -800 2400 200 "SISTEMA180 - PLAN ESTRATEGICO DE ESCALADO"
Create-Shape 0 -800 2200 150 "<b>SISTEMA180 - PLAN ESTRATEGICO DE ESCALADO</b><br><i>Agencia digital automatizada para negocios locales con IA y programa de afiliacion</i>" "#1a1a2e" "rectangle"

# ────────────────────────────────────────────
# SECTION 2: POR QUE (left top)
# ────────────────────────────────────────────
Write-Host "--- POR QUE ---"
Create-Frame -1600 -400 700 500 "POR QUE HACEMOS ESTO"
Create-Shape -1750 -450 280 90 "<b>LIBERTAD</b><br>No depender de un jefe<br>Elegir donde vivir" "#FF6B6B" "round_rectangle"
Create-Shape -1450 -450 280 90 "<b>IMPACTO</b><br>Ayudar negocios locales<br>Democratizar la IA" "#FF6B6B" "round_rectangle"
Create-Shape -1750 -300 280 90 "<b>ESCALABILIDAD</b><br>MRR recurrente<br>Sistema 24/7" "#FF6B6B" "round_rectangle"
Create-Shape -1450 -300 280 90 "<b>LEGACY</b><br>Empresa vendible<br>Marca reconocida" "#FF6B6B" "round_rectangle"

# ────────────────────────────────────────────
# SECTION 3: DISTRIBUCION DE INGRESOS (center)
# ────────────────────────────────────────────
Write-Host "--- DISTRIBUCION DINERO ---"
Create-Frame 0 -400 900 500 "DISTRIBUCION DE INGRESOS"
Create-Shape -200 -500 250 120 "<b>50% EMPRESA</b><br>Gastos operativos<br>Ads, Infra, Legal<br>Impuestos" "#4C8CFF" "round_rectangle"
Create-Shape 0 -500 180 120 "<b>40% FUNDADORES</b><br>20% Jose<br>20% Socio<br>Mensual neto" "#00D4AA" "round_rectangle"
Create-Shape 200 -500 180 120 "<b>10% REINVERSION</b><br>Fondo libre<br>Formacion, eventos<br>Proyectos" "#FFD700" "round_rectangle"

# ────────────────────────────────────────────
# SECTION 4: FASES DE ESCALADO (right top)
# ────────────────────────────────────────────
Write-Host "--- FASES ESCALADO ---"
Create-Frame 1200 -400 1800 500 "FASES DE ESCALADO"
$f1 = Create-StickyNote 550 -500 "<b>FASE 1 - TRACCION</b>`nMes 1-2`n5.000 EUR/mes`n15-20 clientes web (300 EUR)`n5 suscripciones IA`n10 afiliados activos`n50 llamadas/semana" "light_green"
$f2 = Create-StickyNote 850 -500 "<b>FASE 2 - VELOCIDAD</b>`nMes 3-4`n15.000 EUR/mes`n40 clientes web`n20 suscripciones (2K MRR)`n30 afiliados, 1 Gold`nAds 500 EUR/mes" "yellow"
$f3 = Create-StickyNote 1150 -500 "<b>FASE 3 - ESCALA</b>`nMes 5-8`n50.000 EUR/mes`n100+ clientes`n50 suscripciones (5K MRR)`n100 afiliados, 10 Gold`nEquipo 3-4 personas" "orange"
$f4 = Create-StickyNote 1450 -500 "<b>FASE 4 - DOMINIO</b>`nMes 9-12`n100.000 EUR/mes`n300+ clientes`n150 suscripciones`n500 afiliados`nExpansion ciudades" "red"

# Connect phases
if ($f1 -and $f2) { Create-Connector $f1 $f2 }
if ($f2 -and $f3) { Create-Connector $f2 $f3 }
if ($f3 -and $f4) { Create-Connector $f3 $f4 }

# ────────────────────────────────────────────
# SECTION 5: 6 PILARES (center row)
# ────────────────────────────────────────────
Write-Host "--- 6 PILARES ---"
Create-Frame 0 300 2400 600 "LOS 6 PILARES DEL ECOSISTEMA"

Create-Shape -900 200 350 200 "<b>1. AFILIACION 180</b><br>Estado: LISTO<br>Owner: Jose + Ares<br><br>Bronce 20% | Plata 33% | Gold 40%<br><br>Tareas:<br>- Reclutar 10 afiliados<br>- Material marketing<br>- Dashboard afiliado<br>- Ranking Slack semanal" "#00D4AA" "round_rectangle"

Create-Shape -500 200 350 200 "<b>2. MARKETPLACE</b><br>Estado: PLANIFICADO<br>Owner: Jose<br><br>Comision 10%/transaccion<br><br>Tareas:<br>- 1a categoria: estetica<br>- 5 proveedores iniciales<br>- Panel proveedor<br>- Pasarela pago" "#4C8CFF" "round_rectangle"

Create-Shape -100 200 350 200 "<b>3. AVATARES IA</b><br>Estado: DEMOS<br>Owner: Jose<br><br>500-2.000 EUR/avatar<br><br>Tareas:<br>- Pipeline generacion<br>- 3 demos B2B reales<br>- Landing page<br>- Framework legal GDPR" "#A78BFA" "round_rectangle"

Create-Shape 300 200 350 200 "<b>4. MARCA PERSONAL</b><br>Estado: PENDIENTE<br>Owner: Ares<br><br>High-ticket 2-5K EUR<br><br>Tareas:<br>- Definir oferta y formato<br>- 5 plazas premium<br>- Plan de contenidos<br>- Funnel captacion" "#FFD700" "round_rectangle"

Create-Shape 700 200 350 200 "<b>5. MARCAS DE ROPA</b><br>Estado: CONCEPTO<br>Owner: Jose + Ares<br><br>E-commerce + avatares IA<br><br>Tareas:<br>- Definir marca y estilo<br>- Mini-coleccion 10 piezas<br>- Setup e-commerce<br>- Shooting con avatares" "#71717a" "round_rectangle"

Create-Shape 1100 200 350 200 "<b>6. BOTS TRADING</b><br>Estado: LIVE v6 VPS<br>Owner: Jose<br><br>Alfonso v6 + Elena v6<br><br>Tareas:<br>- Evolucionar a v7 con IA<br>- Dashboard rendimiento<br>- Sistema licencias<br>- Backtesting auto" "#4C8CFF" "round_rectangle"

# ────────────────────────────────────────────
# SECTION 6: CUSTOMER JOURNEY (bottom)
# ────────────────────────────────────────────
Write-Host "--- CUSTOMER JOURNEY ---"
Create-Frame 0 800 2200 350 "CUSTOMER JOURNEY"

$j1 = Create-Shape -800 750 280 100 "<b>CAPTACION</b><br>TikTok, Instagram<br>Afiliados, Ads" "#4C8CFF" "round_rectangle"
$j2 = Create-Shape -450 750 280 100 "<b>WEB GANCHO</b><br>300 EUR pago unico<br>Entrega 48-72h" "#00D4AA" "round_rectangle"
$j3 = Create-Shape -100 750 280 100 "<b>RECEPCIONISTA IA</b><br>100 EUR/mes<br>Atencion 24/7" "#A78BFA" "round_rectangle"
$j4 = Create-Shape 250 750 280 100 "<b>UPSELL</b><br>Marketplace<br>Avatares, Marca" "#FFD700" "round_rectangle"
$j5 = Create-Shape 600 750 280 100 "<b>RETENCION</b><br>Soporte<br>Updates, Comunidad" "#FF6B6B" "round_rectangle"
$j6 = Create-Shape 950 750 280 100 "<b>FEEDBACK</b><br>NPS, Data<br>Optimizacion" "#FFA500" "round_rectangle"

# Connect journey steps
if ($j1 -and $j2) { Create-Connector $j1 $j2 }
if ($j2 -and $j3) { Create-Connector $j2 $j3 }
if ($j3 -and $j4) { Create-Connector $j3 $j4 }
if ($j4 -and $j5) { Create-Connector $j4 $j5 }
if ($j5 -and $j6) { Create-Connector $j5 $j6 }

# ────────────────────────────────────────────
# SECTION 7: INFRAESTRUCTURA (bottom right)
# ────────────────────────────────────────────
Write-Host "--- INFRAESTRUCTURA ---"
Create-Frame 1500 800 600 350 "INFRAESTRUCTURA TECH"
Create-Shape 1350 750 200 50 "<b>Stripe TEST</b> OK" "#00D4AA" "round_rectangle"
Create-Shape 1550 750 200 50 "<b>Slack Bot</b> OK" "#00D4AA" "round_rectangle"
Create-Shape 1350 820 200 50 "<b>Postgres</b> OK" "#00D4AA" "round_rectangle"
Create-Shape 1550 820 200 50 "<b>Backend :3000</b> OK" "#00D4AA" "round_rectangle"
Create-Shape 1450 890 200 50 "<b>Antigravity IA</b> OK" "#4C8CFF" "round_rectangle"

Write-Host ""
Write-Host "=== BOARD COMPLETO ==="
Write-Host "Todas las secciones creadas con exito."
