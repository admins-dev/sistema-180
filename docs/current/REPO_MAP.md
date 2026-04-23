# SISTEMA 180 — MAPA DEL REPOSITORIO

> **Última actualización:** 23 Abril 2026  
> **Este documento explica qué hace cada carpeta importante del repositorio.**

---

## Estructura General

```
sistema-180/
├── src/                    [CURRENT]  Frontend Vite SPA — Dashboard HQ
├── backend/                [CURRENT]  Backend Node.js — Pagos, afiliación, Stripe
├── meta-ads-bot/           [CURRENT]  Bot JARVIS + Motor de prospección
├── video-editor/           [LIVE]     VideoForge Pro — Editor de vídeo IA
├── scripts/comfyui/        [LEGACY]   Scripts experimentales de ComfyUI
├── landings/               [LIVE]     Landing pages del negocio
├── docs/                   [MIXED]    Documentación organizada por estado
│   ├── current/            Docs activos y vigentes
│   ├── legacy/             Docs de fases anteriores
│   └── backlog/            Docs de visión futura
├── legacy/                 [LEGACY]   Archivos de fases anteriores
└── [config files]          Configs de deploy (Vercel, Railway, Vite)
```

---

## Detalle por carpeta

### `src/` — Frontend Dashboard HQ [CURRENT]
| Subcarpeta | Contenido | Estado |
|------------|-----------|--------|
| `pages/` | 15 módulos JS (dashboard, agents, despacho, editor, scripts, ads, videos, crm, clients, finances, affiliates, marketplace, settings, legal) | Activo |
| `services/` | 9 servicios (ai-cascade, ai-service, claudeflow, freepik-api, pixel-service, sanitize, script-engine, storage, supabase) | Activo |
| `components/` | sidebar.js | Activo |
| `styles/` | index.css (dark premium glassmorphism) | Activo |
| `main.js` | Router SPA principal | Activo |

**Deploy:** Vercel → `dist-eta-mocha.vercel.app`

---

### `backend/` — Backend Node.js [CURRENT]
| Subcarpeta | Contenido | Estado |
|------------|-----------|--------|
| `src/routes/` | admin, avatars, checkout, webhook, marketplace | Activo |
| `src/services/` | stripeService, slackService | Activo |
| `src/migrations/` | 001_init.sql, 002_marketplace.sql | Activo |
| `src/cron/` | jobs.js (leaderboard, settlement) | Activo |
| `tests/` | Integration tests (27/27 passed) | Activo |

**Deploy:** Railway (staging)

---

### `meta-ads-bot/` — Bot JARVIS + Prospección [CURRENT]
El módulo más grande del repositorio (~140 archivos Python).

| Componente | Archivos clave | Función |
|------------|---------------|---------|
| **JARVIS Bot** | bot.py (87KB), brain.py, jarvis_*.py | Bot Telegram principal con voz, NLP, Meta Ads |
| **Ghost Mouse** | ghost-mouse/*.py (~73 archivos) | Motor de prospección masiva |
| **API Service** | api-service/app.py | Flask API auxiliar para Railway |

#### Dentro de `ghost-mouse/`:
| Grupo | Archivos | Función |
|-------|----------|---------|
| **Scrapers** | gmaps_ghost_scraper.py, gmaps_mega_scanner.py, mass_scraper.py, lead_finder.py | Scraping de Google Maps |
| **LinkedIn** | linkedin_ghost.py, linkedin_engine.py, linkedin_optimizer.py | Automatización LinkedIn |
| **Instagram** | ig_automator.py, dm_sender.py, create_ig_account.py, setter_profiles.py, phantom_agency.py | IG DMs + cuentas setter |
| **Email** | cold_email_engine.py, email_marketing.py, email_scraper_massive.py, email_enricher.py, email_crm.py | Cold email + enriquecimiento |
| **Campañas** | ai_smart_campaign.py, railway_campaign.py, launch_campaign.py, fire_day1.py, war_plan_9days.py | Campañas automatizadas |
| **CRM** | crm.py, sales_pipeline.py, followup_scheduler.py | Pipeline de ventas |
| **Cerebro IA** | brain.py, llm_brain.py, config.py, catalogo_precios.py | Calificación IA multi-modelo |
| **Browser** | browser_manager.py, ghost_mouse.py, human_cursor.py | Gestión de navegadores anti-detección |
| **Agentes** | agents/*.py (framework + 4 agentes especializados) | Mini-framework de agentes |
| **ComfyUI** | comfy_orchestrator.py | Conexión con ComfyUI local |
| **Contenido** | content_generator.py, pablo_script_agent.py | Generación de contenido |
| **Dashboard** | dashboard/ (HTML + JS + CSS) | Dashboard local auxiliar |
| **Tests** | test_*.py (7 archivos) | Tests ad-hoc de scrapers |

**NOTA:** Los archivos de datos runtime (profiles/, screenshots/, generated_photos/, dossiers/, *.db, leads.json) están en `.gitignore` — son artefactos locales, no código.

---

### `video-editor/` — VideoForge Pro [LIVE]
| Componente | Archivos | Función |
|------------|----------|---------|
| Server | server.py, main.py | API Flask :5000 + CLI |
| Frontend | web/index.html | UI del editor (37 KB) |
| Pipeline v10 | editor/*.py (15 módulos) | 12 presets profesionales |
| Pipeline v15 | editor/v15/*.py (7+ archivos) | 14 agentes IA autónomos |

---

### `scripts/comfyui/` — Scripts experimentales [LEGACY]
Scripts `.mjs` de Node.js para ComfyUI API — faceswap, generación de perfiles, búsqueda de modelos. De fase experimental temprana.

---

### `landings/` — Landing pages [LIVE]
- `landing.html` — Landing principal Sistema 180
- `landing-it.html` — Versión italiana
- `informe-ahorro.html` — Informe de ahorro por automatización IA

---

### `docs/` — Documentación
| Subcarpeta | Contenido |
|------------|-----------|
| `current/` | ARQUITECTURA.md, APIS.md, README_SISTEMA180.md, DEPLOY_VERCEL.md |
| `legacy/` | Estrategia marzo, influencers 4M, cliente Estefanía, metodología Heras, mapa completo v1 |
| `backlog/` | BACKLOG_MAP.md (visión futura, 9 patas, expansiones) |
| `emails/` | Templates HTML de emails (affiliate, KYC, payout) |
| `runbook_production.md` | Procedimiento staging → producción |

---

### `legacy/` — Archivos de fases anteriores
- `miro/` — Export de tablero Miro (CSV, HTML, PS1)
- `Informe_Ahorro_Automatizacion_IA.pdf` — Material de venta v1

---

### Archivos raíz (config/deploy)

| Archivo | Función | Tocar con cuidado |
|---------|---------|-------------------|
| `index.html` | Entry point Vite | ⚠️ |
| `vite.config.js` | Config Vite | ⚠️ |
| `package.json` | Dependencies + scripts npm | ⚠️ |
| `vercel.json` | Deploy Vercel | ⚠️ |
| `railway.json` | Deploy Railway | ⚠️ |
| `Procfile` | Config Railway | ⚠️ |
| `.env` | Variables de entorno (NO en git) | 🔒 |
| `CLAUDE.md` | Contexto para agentes IA | ✅ |
| `CURRENT_STATE.md` | Source of truth del negocio | ✅ |
| `PLAN_MAESTRO.md` | Visión general del ecosistema | ✅ |
| `README.md` | Puerta de entrada al repo | ✅ |
| `DECISION_LOG.md` | Log de decisiones | ✅ |
