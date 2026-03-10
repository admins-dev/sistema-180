# 🗺️ MAPA COMPLETO — SISTEMA 180

> **Última actualización:** 10 de Marzo de 2026
> **GitHub:** [admins-dev/sistema-180](https://github.com/admins-dev/sistema-180) (privado)
> **Deploy:** [dist-eta-mocha.vercel.app](https://dist-eta-mocha.vercel.app/)
> **Cuenta GitHub:** admins-dev

---

## 📋 Resumen Ejecutivo

**SISTEMA 180** es una plataforma B2B de automatización para negocios locales que integra:
- 🤖 **Bot IA** para atención al cliente 24/7 (WhatsApp/Teléfono)
- 🌐 **Webs profesionales** generadas con Lovable
- 📍 **SEO Local** (Google Maps optimizado)
- 🎬 **Fábrica de Contenido IA** (avatares, guiones virales, vídeos)
- 💳 **Pagos y Afiliación** (Stripe + 3 niveles de comisión)
- 🎬 **Oficina de Editores** (VideoForge Pro — editor de vídeo IA con 12+ presets)

**Precio de penetración:** 297€ pago único → Objetivo Marzo: 30-35 ventas (~9.000€)

---

## 🏗️ Arquitectura

```
SISTEMA180
├── FRONTEND (Vite SPA) ──────── 6 páginas + 6 servicios + sidebar
│   └── APIs: Gemini 2.0 Flash · Perplexity Sonar · Freepik Mystic · Pollinations FLUX
│
├── BACKEND (Node.js + Express) ── Stripe · Slack · Neon Postgres (7 tablas)
│   └── 4 rutas: admin · avatars · checkout · webhook
│
├── OFICINA DE EDITORES (Python + Flask) ── VideoForge Pro
│   ├── Pipeline v10: 16 módulos · 12 presets profesionales
│   └── Pipeline v15: 14 agentes IA autónomos (100% local, sin API)
│
└── DEPLOY: Vercel (frontend) · localtunnel (backend staging)
```

---

## 💻 Frontend — Código Fuente

📁 `sistema-180/src/`

### Páginas (`src/pages/`)

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| [dashboard.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/pages/dashboard.js) | Panel principal con métricas | 4.5 KB |
| [avatars.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/pages/avatars.js) | Generador de avatares multi-IA (4 motores) | 17.6 KB |
| [scripts.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/pages/scripts.js) | Generador de guiones virales (Método Heras) | 24.6 KB |
| [ads.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/pages/ads.js) | Módulo de anuncios (9 plataformas) | 7.5 KB |
| [videos.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/pages/videos.js) | Hub de vídeos UGC | 6 KB |
| [settings.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/pages/settings.js) | Configuración de 3 API keys | 6 KB |

### Servicios (`src/services/`)

| Archivo | Función | Tamaño |
|---------|---------|--------|
| [ai-cascade.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/services/ai-cascade.js) | Motor AI Cascade (Gemini → Perplexity → Gemini) | 5.7 KB |
| [script-engine.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/services/script-engine.js) | Motor de guiones virales completo | 22.5 KB |
| [script-ai.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/services/script-ai.js) | Integración IA para guiones | 7.5 KB |
| [freepik-api.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/services/freepik-api.js) | API de Freepik Mystic (avatares 4K) | 3.5 KB |
| [voice-cloning.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/services/voice-cloning.js) | Clonación de voz (ElevenLabs) | 5.8 KB |
| [storage.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/services/storage.js) | LocalStorage persistente | 2.2 KB |

### Otros

| Archivo | Descripción |
|---------|-------------|
| [sidebar.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/components/sidebar.js) | Navegación lateral |
| [main.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/main.js) | Router + bootstrap |
| [index.css](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/src/styles/index.css) | CSS dark premium (15 KB) |
| [vite.config.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/vite.config.js) | Config de Vite 7.3 |

---

## ⚙️ Backend — Node.js + Express

📁 `sistema-180/backend/`

### Rutas (`src/routes/`)

| Archivo | Descripción |
|---------|-------------|
| [admin.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/backend/src/routes/admin.js) | Panel admin, estadísticas, gestión afiliados (6.3 KB) |
| [avatars.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/backend/src/routes/avatars.js) | API de avatares (2.4 KB) |
| [checkout.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/backend/src/routes/checkout.js) | Stripe Checkout sessions (674 B) |
| [webhook.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/backend/src/routes/webhook.js) | Stripe Webhooks (940 B) |

### Servicios (`src/services/`)

| Archivo | Descripción |
|---------|-------------|
| [stripeService.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/backend/src/services/stripeService.js) | Checkout, Connect, comisiones, hold 14 días (9.7 KB) |
| [slackService.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/backend/src/services/slackService.js) | Alertas, leaderboard, payouts (5.2 KB) |

### Base de Datos

| Archivo | Descripción |
|---------|-------------|
| [db.js](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/backend/src/db.js) | Conexión Neon Postgres |
| [001_init.sql](file:///C:/Users/Jose/.gemini/antigravity/scratch/sistema-180/backend/src/migrations/001_init.sql) | 7 tablas: usuarios, afiliados, comisiones, pagos, suscripciones, config, logs |

### QA: **27/27 tests PASSED** · 8 escenarios de integración · Stripe webhook verificado

---

## 🎬 Oficina de Editores — VideoForge Pro

📁 `SISTEMA180/video-editor/`

### Server + Entry Point

| Archivo | Descripción |
|---------|-------------|
| [server.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/server.py) | API Flask (:5000) — upload, process, status, download |
| [main.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/main.py) | CLI entry point |
| [index.html (web)](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/web/index.html) | Frontend web del editor (37 KB) |
| [requirements.txt](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/requirements.txt) | Dependencias Python |

### Pipeline v10 — 16 Módulos (`editor/`)

| Módulo | Descripción | Tamaño |
|--------|-------------|--------|
| [pipeline.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/pipeline.py) | 🎯 **Orquestador maestro** — 12 presets profesionales | 27.8 KB |
| [silence_cutter.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/silence_cutter.py) | Cortador de silencios inteligente | 10.6 KB |
| [subtitles.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/subtitles.py) | Subtítulos animados (Whisper + word-level) | 12 KB |
| [smart_zoom.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/smart_zoom.py) | Zooms inteligentes con detección de énfasis | 7.6 KB |
| [smart_reframe.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/smart_reframe.py) | Reencuadre automático (horizontal → vertical) | 9.2 KB |
| [audio_engine.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/audio_engine.py) | Procesamiento de audio pro | 8.3 KB |
| [beat_engine.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/beat_engine.py) | Sincronización con beat de música | 8.4 KB |
| [broll_engine.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/broll_engine.py) | Inserción automática de B-Roll | 14.5 KB |
| [retention_engine.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/retention_engine.py) | Motor de retención (anti-scroll) | 12.4 KB |
| [vfx_engine.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/vfx_engine.py) | VFX: glitch, grain, glow, particles, RGB split | 14.3 KB |
| [compositing.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/compositing.py) | Composición final multicapa | 10 KB |
| [sound_design.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/sound_design.py) | Diseño de sonido (SFX, whoosh, impact) | 12.7 KB |
| [transitions.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/transitions.py) | Transiciones profesionales | 8.8 KB |
| [overlays.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/overlays.py) | Overlays (textos, logos, marcos) | 8.9 KB |
| [gpu_engine.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/gpu_engine.py) | Aceleración GPU (NVENC/CUDA) | 8.3 KB |

### 12 Presets Profesionales

| Categoría | Preset | Efectos |
|-----------|--------|---------|
| **God Mode** | 🔥 Viral Max | 12+ efectos, beat sync, retención brutal |
| **God Mode** | 🎬 Cinematic Pro | Color grade cine, grain, letterbox, SFX épico |
| **God Mode** | ⚡ Aggressive v10 | Cortes 0.05s, glitch, bass drops, RGB split |
| **Creator** | 💰 Hormozi | Estilo Alex Hormozi: zooms, subs grandes |
| **Creator** | 🧲 MrBeast | Colorido, rápido, SFX pesados, máxima energía |
| **Creator** | 🎵 Music Video | Beat-sync total, VFX reactivos al ritmo |
| **Platform** | 📱 Reel Pro | Instagram vertical, subtítulos, retención |
| **Platform** | 🎵 TikTok Pro | Vertical, beat-sync, retención, SFX |
| **Platform** | 📢 Ad Killer | Anuncio con retención máxima, B-Roll, CTA |
| **Platform** | 🎙️ Podcast Pro | Horizontal, cortes limpios, subs discretos |
| **Platform** | 🎬 YouTube Pro | Horizontal, efectos pro, SFX |
| **Quick** | ⏩ Speed Cut | Solo corte de silencios + GPU |

### Pipeline v15 — 14 Agentes IA (`editor/v15/`)

**Sistema de agentes 100% LOCAL (sin API externa).** Cada agente opera sobre un EDL (Edit Decision List).

| Agente | Clase | Función |
|--------|-------|---------|
| 🎤 Transcript | `TranscriptAgent` | Transcribe con faster-whisper (local) |
| 👁️ Visual Analyst | `VisualAnalystAgent` | Segmenta escenas por silencio y ritmo |
| ✂️ Cut Script | `CutScriptAgentLocal` | Decide qué cortes sobreviven |
| 🪝 Hook Editor | `HookEditorAgent` | Identifica hooks y momentos virales |
| 📝 Subtitle | `SubtitleAgent` | Genera subtítulos animados |
| 🎆 VFX Editor | `VFXEditorAgent` | Asigna VFX a momentos virales |
| 🔊 SFX Designer | `SFXDesignerAgent` | Asigna SFX complementarios a VFX |
| 🎬 B-Roll Director | `BRollDirectorAgent` | Inserta B-Roll en gaps largos |
| 🎵 Music Supervisor | `MusicSupervisorAgent` | Configura música y ducking |
| 📐 Crop Reframing | `CropReframingAgent` | Crop según aspect ratio del preset |
| 🎨 Style Designer | `StyleDesignerAgent` | Asigna LUT y estilo visual |
| ✅ Style Consistency | `StyleConsistencyAgent` | Verifica coherencia de estilos |
| 🔍 QC | `QCAgent` | Control de calidad final |
| 📋 Compliance | `ComplianceAgent` | Verifica que todos los assets existen |
| 🖥️ Render Planner | `RenderPlannerAgent` | Genera plan de render optimizado |

Otros archivos v15:

| Archivo | Descripción |
|---------|-------------|
| [orchestrator.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/v15/orchestrator.py) | Orquestador de la cadena de agentes |
| [models.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/v15/models.py) | Modelos de datos (EDL, Segment, etc.) — 16.8 KB |
| [bridge.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/v15/bridge.py) | Puente EDL → FFmpeg commands |
| [pipeline_runner.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/v15/pipeline_runner.py) | Runner principal del pipeline v15 |
| [ffmpeg_builder.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/v15/ffmpeg_builder.py) | Constructor de comandos FFmpeg |
| [media_analyzer.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/v15/media_analyzer.py) | Analizador de medios |
| [validators.py](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/video-editor/editor/v15/validators.py) | Validadores de datos |

---

## 🔑 APIs Configuradas

| Servicio | Estado | Uso | Key en |
|----------|--------|-----|--------|
| Freepik Mystic (Premium+) | ✅ | Avatares 4K | LocalStorage |
| Google Gemini 2.0 Flash | ✅ $15 crédito | Guiones + prompts | LocalStorage |
| Perplexity Sonar Pro | ✅ | Investigación Reddit/foros | LocalStorage |
| Pollinations FLUX | ✅ GRATIS | Avatares borrador | Sin key |
| Stripe (TEST mode) | ✅ | Pagos + Connect + Webhooks | backend/.env |
| Slack Bot | ✅ 3 canales | Alertas internas | backend/.env |
| Neon Postgres | ✅ 7 tablas | Base de datos | backend/.env |

---

## 🧠 Motor IA — AI Cascade Engine

```
Usuario introduce tema + nicho + gancho + pilar SDD
        │
        ▼
  PASO 1: Gemini 2.0 Flash → 3 preguntas de investigación
        │
        ▼
  PASO 2: Perplexity Sonar → Busca en Reddit, foros, datos 2026
        │
        ▼
  PASO 3: Gemini 2.0 Flash → Guión final UMV (Hook→Story→Moraleja→CTA)
        │
        ▼
     JSON listo para producir vídeo
```

**Coste:** ~$0.005/guión → **3.000 guiones por $15**

---

## 📈 Estrategia de Negocio

| Documento | Contenido |
|-----------|-----------|
| [ESTRATEGIA_VENTAS_MARZO.md](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/ESTRATEGIA_VENTAS_MARZO.md) | Modelo B2B, prospección CRM, proyección 30-35 ventas/marzo |
| [ESTRATEGIA_INFLUENCERS_4M.md](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/ESTRATEGIA_INFLUENCERS_4M.md) | Piloto influencer 4M seguidores, clonación multilingüe |
| [CLIENTE_ESTEFANIA_ROMERO.md](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/CLIENTE_ESTEFANIA_ROMERO.md) | Propuesta completa para peluquería (SEO + Web + Bot IA) |
| [METODOLOGIA_HERAS.md](file:///C:/Users/Jose/.gemini/antigravity/scratch/SISTEMA180/METODOLOGIA_HERAS.md) | Método UMV + SDD: 7 ganchos, 12 formatos, 10 plantillas |

---

## 📂 Árbol Completo de Ficheros

```
SISTEMA180/                           ← Documentación maestra
├── README.md
├── MAPA_COMPLETO_SISTEMA180.md       ← ESTE ARCHIVO
├── ARQUITECTURA.md
├── APIS.md
├── METODOLOGIA_HERAS.md
├── ESTRATEGIA_VENTAS_MARZO.md
├── ESTRATEGIA_INFLUENCERS_4M.md
├── CLIENTE_ESTEFANIA_ROMERO.md
├── clon_influencer_perfecto.png
└── video-editor/                     ← OFICINA DE EDITORES
    ├── server.py                     ← API Flask :5000
    ├── main.py                       ← CLI
    ├── requirements.txt
    ├── web/index.html                ← Frontend editor (37 KB)
    ├── assets/{fonts,sounds}
    ├── editor/                       ← Pipeline v10 (16 módulos)
    │   ├── pipeline.py               ← Orquestador + 12 presets
    │   ├── silence_cutter.py
    │   ├── subtitles.py
    │   ├── smart_zoom.py
    │   ├── smart_reframe.py
    │   ├── audio_engine.py
    │   ├── beat_engine.py
    │   ├── broll_engine.py
    │   ├── retention_engine.py
    │   ├── vfx_engine.py
    │   ├── compositing.py
    │   ├── sound_design.py
    │   ├── transitions.py
    │   ├── overlays.py
    │   ├── gpu_engine.py
    │   └── v15/                      ← Pipeline v15 (14 agentes IA)
    │       ├── all_agents.py         ← 14 agentes (833 líneas)
    │       ├── orchestrator.py
    │       ├── models.py
    │       ├── bridge.py
    │       ├── pipeline_runner.py
    │       ├── ffmpeg_builder.py
    │       ├── media_analyzer.py
    │       └── validators.py
    ├── uploads/
    └── output/

sistema-180/                          ← Código fuente (GitHub)
├── index.html
├── vite.config.js
├── package.json
├── src/
│   ├── main.js
│   ├── pages/{dashboard,avatars,scripts,ads,videos,settings}.js
│   ├── services/{ai-cascade,script-engine,script-ai,freepik-api,voice-cloning,storage}.js
│   ├── components/sidebar.js
│   └── styles/index.css
├── backend/
│   ├── src/
│   │   ├── index.js
│   │   ├── db.js
│   │   ├── routes/{admin,avatars,checkout,webhook}.js
│   │   ├── services/{stripeService,slackService}.js
│   │   └── migrations/001_init.sql
│   ├── tests/
│   └── ci/
├── docs/
│   ├── affiliate_onboarding.md
│   ├── runbook_production.md
│   ├── emails/
│   └── playbooks/
├── generated-clones/
├── miro/
└── public/
```
