# SISTEMA 180

> **Agencia digital automatizada para negocios locales en España**  
> **Fundadores:** José María Moreno García + Ares Villalba Sánchez | Marbella

---

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [CURRENT_STATE.md](./CURRENT_STATE.md) | **Source of truth** — qué es verdad hoy, líneas activas, pricing, stack |
| [PLAN_MAESTRO.md](./PLAN_MAESTRO.md) | Visión general del ecosistema (9 patas) |
| [docs/current/REPO_MAP.md](./docs/current/REPO_MAP.md) | Mapa del repositorio — qué hace cada carpeta |
| [docs/backlog/BACKLOG_MAP.md](./docs/backlog/BACKLOG_MAP.md) | Visión futura, expansiones, módulos pendientes |
| [docs/legacy/LEGACY_MAP.md](./docs/legacy/LEGACY_MAP.md) | Histórico: pricing anterior, herramientas descartadas |
| [DECISION_LOG.md](./DECISION_LOG.md) | Log de decisiones de reorganización |
| [CLAUDE.md](./CLAUDE.md) | Contexto permanente para agentes IA |

---

## Estructura del repo

```
sistema-180/
├── src/                    Frontend Dashboard HQ (Vite SPA)
├── backend/                Backend (Node.js, Stripe, Slack, Postgres)
├── meta-ads-bot/           Bot JARVIS + Motor de prospección (Ghost Mouse)
├── video-editor/           Editor de vídeo IA (VideoForge Pro)
├── scripts/comfyui/        Scripts experimentales ComfyUI
├── landings/               Landing pages
├── docs/                   Documentación organizada
│   ├── current/            Docs actuales y vigentes
│   ├── legacy/             Docs de fases anteriores
│   └── backlog/            Visión futura
└── legacy/                 Archivos de fases anteriores
```

---

## Quick start

```bash
# Frontend (Dashboard HQ)
npm install
npm run dev

# Meta Ads Bot (JARVIS)
cd meta-ads-bot
pip install -r requirements.txt
python bot.py

# Ghost Mouse (Prospección)
cd meta-ads-bot/ghost-mouse
pip install -r requirements.txt
python orchestrator_server.py
```

---

## Deploy

- **Frontend:** Vercel → `dist-eta-mocha.vercel.app`
- **Backend:** Railway (staging)
- **API Service:** Railway
- **Repo:** GitHub privado — `admins-dev/sistema-180`
