# Sistema 180 — Meta Ads Bot Setup Guide

## 📋 Checklist de Configuración

### ✅ Completado

- [x] `.env` con credenciales Meta Business + Telegram Bot Token
- [x] `bot.py` — Telegram Bot con NLP (intent detection via Claude Haiku)
- [x] `server.py` — Flask API con endpoints `/api/meta-ads/*`
- [x] `meta_client.py` — Cliente Meta Graph API v19.0
- [x] `nlp.py` — Procesamiento natural de lenguaje (Haiku)
- [x] `sync.py` — Sincronización de campañas Meta ↔ memoria local
- [x] Integración dashboard.js con sección Meta Ads Bot
- [x] Servicios compartidos (`api-client.js`, `cache.js`)
- [x] Componente `meta-ads-section.js` en dashboard

---

## 🚀 Instalación y Inicio Rápido

### Paso 1: Instalar Dependencias

```bash
cd /home/jose/proyectos/sistema-180/meta-ads-bot
./install.sh
```

Esto:
- Detecta tu gestor de paquetes (apt, brew, etc.)
- Crea virtualenv
- Instala: `python-telegram-bot`, `flask`, `requests`, `python-dotenv`, `flask-cors`

### Paso 2: Iniciar Servicios

```bash
source venv/bin/activate  # Si no está activo
./start.sh
```

Esto inicia en paralelo:
- 🤖 **Telegram Bot** (`bot.py`) — Escucha mensajes en `@Sistema180ADS_bot`
- 🌐 **Flask Server** (`server.py`) — API en `http://localhost:5000`

---

## 🔗 API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/meta-ads/status` | GET | Estado del bot y últimas campañas |
| `/api/meta-ads/campaigns` | GET | Lista completa de campañas con métricas |
| `/api/meta-ads/launch` | POST | Crear nueva campaña |
| `/api/meta-ads/pause` | POST | Pausar campaña activa |
| `/api/meta-ads/metrics` | GET | Métricas detalladas de campaña |

### Ejemplo: Obtener estado del bot

```bash
curl http://localhost:5000/api/meta-ads/status
```

**Respuesta:**
```json
{
  "active": true,
  "lastSync": "2026-04-12T15:30:00Z",
  "totalCampaigns": 5
}
```

---

## 💬 Comandos Telegram

### Natural Language (Recomendado)

El bot procesa intención automáticamente vía Claude Haiku:

```
"Dame los datos de las campañas de ADS"
→ Intent: GET_CAMPAIGNS → Retorna métricas completas

"Quiero pausar la campaña Málaga Abril"
→ Intent: PAUSE_CAMPAIGN → Pausa por nombre

"Crea una campaña de 50€ para Barberías"
→ Intent: CREATE_CAMPAIGN → Abre formulario interactivo
```

### Comandos Directos

```
/status               — Estado actual del bot
/nuevacampaña 15 Test — Crea campaña con presupuesto 15€
/pausar <id>         — Pausa campaña por ID
```

---

## 📊 Integración Dashboard

El dashboard mostrará sección **Meta Ads Bot** con:

1. **Bot Status Badge** — Indica si bot está activo
2. **Sync Button** — Sincroniza campañas en tiempo real
3. **Campaigns Table** — Lista campañas (nombre, objetivo, presupuesto, estado)
4. **Create Campaign Form** — Formulario rápido para crear campañas
5. **Links** — Botones a Designer y settings

### Flujo de Datos

```
Telegram → bot.py
  ↓
Claude NLP (intent detection)
  ↓
Meta Graph API (meta_client.py)
  ↓
sync.py (actualiza memoria)
  ↓
server.py (API endpoints)
  ↓
Dashboard cache.js (localStorage)
  ↓
UI renderiza meta-ads-section.js
```

---

## 🔐 Credenciales Requeridas en `.env`

```env
TELEGRAM_BOT_TOKEN=8095222820:AAHAWjXQ7RUdUMn_d7KO4o5bMwtImrBfJKc
META_ACCESS_TOKEN=EAAT1Gp...  # Access token Meta Business
META_AD_ACCOUNT_ID=665665724415645
ANTHROPIC_API_KEY=sk-ant-...  # Para Claude Haiku NLP
LOG_LEVEL=INFO
```

**IMPORTANTE:** Nunca commitear `.env` a Git. Use `.env.example` como template.

---

## 🧪 Testing Manual

### 1. Verificar Flask Server

```bash
curl -X GET http://localhost:5000/api/meta-ads/status
# Debe retornar: {"active": true, ...}
```

### 2. Verificar Telegram Bot

Abre Telegram → busca `@Sistema180ADS_bot` → envía: `"Dame el estado"`
→ Bot debe responder con estado actual

### 3. Verificar Dashboard

1. Abre dashboard: `http://localhost:3000/`
2. Busca sección **Meta Ads Bot** (panel derecho)
3. Haz click en **Sync**
4. Verifica que tabla de campañas se actualiza

### 4. Monitorear Logs

```bash
# Terminal 1 — Ver logs del bot
tail -f bot.py

# Terminal 2 — Ver logs del servidor
tail -f server.py
```

---

## 🔄 Flujo de Creación de Campaña Completo

### Opción A: Desde Dashboard UI

1. Dashboard → Meta Ads Bot section
2. Click **"➕ Nueva Campaña"** → abre formulario
3. Completa: nombre, presupuesto, objetivo, audiencia, copy
4. Click **"Crear campaña"**
5. ✅ Campaña creada en Meta + notificación a Telegram

### Opción B: Desde Telegram (Natural Language)

```
Usuario: "Crea una campaña de 25 euros para barberías en Málaga"

Bot procesa:
1. Intent: CREATE_CAMPAIGN
2. Parámetros: budget=25, name="Barberías Málaga"
3. Opens interactive form si faltan datos
4. POST /api/meta-ads/launch
5. Retorna: "✅ Campaña 'Barberías Málaga' creada"
```

### Opción C: API Directa

```bash
curl -X POST http://localhost:5000/api/meta-ads/launch \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "budget": 20,
    "objective": "TRAFFIC",
    "audience": "competitors",
    "copy": "Escribe ANÁLISIS"
  }'
```

---

## ⚠️ Troubleshooting

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'telegram'` | Ejecutar `./install.sh` |
| `ConnectionRefusedError: localhost:5000` | Flask no está corriendo; ejecutar `start.sh` |
| `Bot no responde en Telegram` | Verificar TELEGRAM_BOT_TOKEN en `.env` |
| `Error 401: Invalid access token` | META_ACCESS_TOKEN expirado; renovar en Meta Business |
| Dashboard no carga sección Meta Ads | Verificar browser console (F12) por errores |

---

## 📈 Roadmap Futuro

- [ ] Base de datos persistente (Postgres) en lugar de memoria
- [ ] Webhooks de Meta para notificaciones en tiempo real
- [ ] Dashboard de métricas avanzadas (ROI, ROAS)
- [ ] Automatización de reportes diarios a Telegram
- [ ] A/B testing integrado

---

## 📞 Contacto & Support

**Responsable:** José María Moreno García  
**Repo:** `/home/jose/proyectos/sistema-180/`  
**Slack alertas:** Configuradas en n8n

---

*Last updated: 2026-04-12*
