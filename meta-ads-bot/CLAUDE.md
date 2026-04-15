# CLAUDE.md — Sistema 180 Meta Ads Bot + JARVIS

## ESTADO: OPERATIVO CON LIMITACIONES (2026-04-15 10:10 CET)

Bot conversacional S180 funcionando en modo polling. NLP + Brain (Groq) activos.
JARVIS Voice Server v3 funcional en localhost:5180.

---

## MISIÓN PARA CLAUDE CODE (2026-04-15)

**OBJETIVO**: Mejorar TODO el sistema JARVIS manteniendo la seguridad existente intacta.

### ⚠️ ARCHIVOS DE SEGURIDAD — NO MODIFICAR ⚠️

Estos archivos contienen el modelo de seguridad híbrido 3.5 (Zero-Trust). 
**NO cambiar la lógica de seguridad, solo mejorar/ampliar si es necesario:**

1. **`system_protection.py`** (375 líneas) — Protecciones del sistema:
   - PyAutoGUI BLOQUEADO
   - Comandos shell BLOQUEADOS (rm, del, sudo, etc.)
   - Solo rutas seguras (`~/.jarvis/` y directorio del bot)
   - Extensiones protegidas (.exe, .dll, .sys, .bat, .key, etc.)
   - URLs solo apis conocidas (Telegram, Facebook, Groq, Anthropic, etc.)
   - Límite financiero: 50€/acción, 100€/día
   - Solo localhost:127.0.0.1
   - Se importa ANTES que todo lo demás

2. **`jarvis_architecture.py`** (545 líneas) — SecurityGate + DecisionEngine:
   - RiskLevel: SAFE → LOW → MEDIUM → HIGH → CRITICAL
   - ActionCategory: READ, CREATE, MODIFY, DELETE, MONEY, OUTREACH, EXTERNAL
   - SecurityGate: Zero-trust, evaluación por confianza
   - DINERO: NUNCA auto-aprobar (max_auto_approve_amount=0.0)
   - Kill switch global
   - Audit trail con hash SHA-256
   - Rate limits: 20 acciones/hora, 50 outreach/día, 1 campaña/día
   - Aprobación expira en 1 hora
   - Singleton ExecutionController

### 🎯 ARCHIVOS A MEJORAR

3. **`jarvis_server.py`** (470 líneas) — Backend Flask localhost:5180:
   - Motor: Gemini 3.1 Pro (primario) → Groq (fallback)
   - TTS: Edge TTS Neural (en-GB-RyanNeural)
   - Búsqueda: Perplexity Sonar
   - Imágenes: Nano Banana 2 (Gemini image)
   - Endpoints: `/api/chat`, `/api/tts`, `/api/imagine`, `/api/status`, `/api/killswitch`, `/api/clear`
   - Contexto en vivo: Meta Ads API, SecurityGate

4. **`templates/jarvis.html`** (453 líneas) — Frontend JARVIS UI:
   - Three.js plasma brain sphere (partículas reactivas al audio)
   - Paneles: Sistema, Seguridad, Recursos, Data Stream, Neural Log
   - Chat interactivo con voz (Web Speech API)
   - TTS con fallback a SpeechSynthesis
   - Layout: Grid 3 columnas (paneles + centro 3D + paneles)

5. **`bot.py`** (30,568 bytes) — Telegram bot conversacional
6. **`brain.py`** (8,171 bytes) — Motor IA con memoria
7. **`nlp.py`** (7,138 bytes) — Clasificador de intents
8. **`server.py`** (6,260 bytes) — Flask REST API para dashboard Vercel

---

## AUDITORÍA EN VIVO (2026-04-15)

### RESULTADOS DE CONECTIVIDAD

| Servicio | Estado | Detalle |
|----------|--------|---------|
| Telegram API | OK | @Sistema180ADS_bot (ID: 8095222820) |
| Groq API | OK | llama-3.3-70b-versatile respondiendo |
| Anthropic API | OK | claude-haiku-4-5 respondiendo |
| Gemini API | FAIL | API key LEAKED — Google la bloqueó (HTTP 403) |
| Meta Ads API | FAIL | Access token EXPIRADO (caducó 12-Abr-2026) |

### PROBLEMA CRÍTICO #1: GEMINI_API_KEY BLOQUEADA
- **Error:** `Your API key was reported as leaked. Please use another API key.`
- **Causa:** La key `AIzaSyCzaQP2Tad...` fue detectada en un repo público o log
- **Impacto:** Gemini no funciona como fallback de NLP ni del brain
- **Acción:** Regenerar key en https://console.cloud.google.com/apis/credentials
- **Workaround:** El bot usa Groq como primario, que funciona. Gemini solo entra si Groq falla.

### PROBLEMA CRÍTICO #2: META ACCESS TOKEN EXPIRADO
- **Error:** `Session has expired on Sunday, 12-Apr-26 06:00:00 PDT`
- **Impacto:** TODAS las operaciones de Meta Ads fallan (crear/pausar campañas, métricas reales)
- **Acción:** Regenerar token en https://developers.facebook.com/tools/explorer/
- **Nota:** Los tokens de corta duración duran ~1h. Usar un token de larga duración o System User.

---

## DIAGNÓSTICO PREVIO (2026-04-14) — YA CORREGIDO

### PROBLEMA #1: `python-telegram-bot` NO INSTALADO (CORREGIDO)
- `pip install python-telegram-bot>=20.0` → v22.7

### PROBLEMA #2: `TELEGRAM_ALLOWED_USER_IDS` INCORRECTO (CORREGIDO)
- Tenía `665665724415645` (Meta Account ID) → Corregido a `5510404767`

### PROBLEMA #3: COMANDOS CON CARACTERES UNICODE (CORREGIDO)
- `nueva_campaña` y `métricas` → `nueva_campana` y `metricas`
- python-telegram-bot v22+ solo acepta `[a-z0-9_]`

### PROBLEMA #4: DEPENDENCIAS FALTANTES (CORREGIDO)
- `flask-limiter` y `groq` instalados

---

## REGLA CRÍTICA: Nombres de Comandos Telegram

NUNCA usar caracteres no-ASCII en CommandHandler:
```python
# INCORRECTO — crashea python-telegram-bot v22+
CommandHandler("nueva_campaña", handler)   # ñ no válido

# CORRECTO — solo [a-z0-9_]
CommandHandler("nueva_campana", handler)
```

---

## Arquitectura Actual

```
JARVIS Voice UI (localhost:5180)
├── jarvis.html          → Frontend Three.js + Chat + Voice
├── jarvis_server.py     → Flask backend Gemini/Groq/Perplexity/TTS
├── jarvis_architecture.py → SecurityGate + DecisionEngine (NO TOCAR LÓGICA)
└── system_protection.py → Protecciones del sistema (NO TOCAR LÓGICA)

Bot Telegram(@Sistema180ADS_bot)
├── bot.py               → Telegram bot conversacional (polling, v22.7)
├── brain.py             → Motor IA: Groq (primario) → Gemini (fallback) + memoria
├── nlp.py               → Clasificador de intents: Anthropic → Groq → Gemini → Keywords
├── sync.py              → Bridge Meta Ads API (crear/pausar/métricas)
├── meta_client.py       → Cliente Meta Graph API v19.0
├── server.py            → Flask REST API (dashboard Vercel)
└── start_all.py         → Startup unificado (Railway)
```

## Variables de Entorno (.env)

```
TELEGRAM_BOT_TOKEN=<valid>
TELEGRAM_ALLOWED_USER_IDS=5510404767
META_ACCESS_TOKEN=<EXPIRADO — regenerar>
META_AD_ACCOUNT_ID=act_665665724415645
ANTHROPIC_API_KEY=<valid>
GROQ_API_KEY=<valid>
GEMINI_API_KEY=<LEAKED — regenerar>
PERPLEXITY_API_KEY=<set>
GOOGLE_MAPS_KEY=<set>
```

## Comandos Telegram (solo [a-z0-9_])

- `/start` — Bienvenida conversacional
- `/estado` — Estado del sistema
- `/nueva_campana` — Crear campaña
- `/pausar` — Pausar campaña
- `/metricas` — Ver métricas
- `/reporte_diario` — Reporte del día

El bot entiende lenguaje natural — no requiere comandos.
