# CLAUDE.md — SISTEMA 180
## Contexto permanente — se carga automáticamente en cada sesión

> IMPORTANTE: Lee este archivo COMPLETO al inicio de cada conversación.

---

## QUIÉNES SOMOS

**SISTEMA 180** — Agencia digital automatizada para negocios locales en España.

| Persona | Rol |
|---------|-----|
| **Ares Villalba Sánchez** | Parte creativa, estrategia, marca personal, cara del negocio |
| **José María Moreno García** | Parte operativa, automatizaciones, técnica, desarrollo |

- **Sede:** Marbella, España
- **Target principal:** Negocios con citas (peluquerías, barberías, estética, clínicas) en Málaga y semiciudades españolas

---

## SOURCE OF TRUTH

**Para entender el estado actual del negocio, lee estos documentos en este orden:**

1. **[CURRENT_STATE.md](./CURRENT_STATE.md)** — Verdad actual: líneas activas, pricing, stack, módulos
2. **[docs/current/REPO_MAP.md](./docs/current/REPO_MAP.md)** — Qué hace cada carpeta del repo
3. **[docs/backlog/BACKLOG_MAP.md](./docs/backlog/BACKLOG_MAP.md)** — Visión futura, 9 patas completas
4. **[PLAN_MAESTRO.md](./PLAN_MAESTRO.md)** — Visión general del ecosistema (documento de referencia)
5. **[DECISION_LOG.md](./DECISION_LOG.md)** — Log de decisiones de reorganización

> Si algo contradice entre documentos, **CURRENT_STATE.md manda.**

---

## LÍNEAS ACTIVAS (Prioridad operativa)

| Línea | Qué es | Foco |
|-------|--------|------|
| **A — IA para PYMEs** | Bot IA + captación masiva + automatización | Motor de ingresos |
| **B — Partnerships** | Colaboraciones con infoproductores | Growth |
| **C — Webs** | Webs profesionales para negocios locales | Cash rápido |

**Las 9 patas del ecosistema siguen vivas** — ver BACKLOG_MAP.md para la visión completa.

---

## ARQUITECTURA DEL REPO

```
sistema-180/
├── src/                    [CURRENT]  Frontend Dashboard HQ (Vite SPA)
├── backend/                [CURRENT]  Backend (Node.js, Stripe, Slack, Postgres)
├── meta-ads-bot/           [CURRENT]  JARVIS Bot + Ghost Mouse (prospección)
├── video-editor/           [LIVE]     Editor de vídeo IA
├── scripts/comfyui/        [LEGACY]   Scripts experimentales ComfyUI
├── landings/               [LIVE]     Landing pages
├── docs/                   Documentación (current/ legacy/ backlog/)
├── legacy/                 Archivos de fases anteriores
└── [configs]               Deploy (Vercel, Railway, Vite)
```

---

## STACK TÉCNICO

| Herramienta | Uso |
|-------------|-----|
| ComfyUI (RTX 4080 Super) | Avatares, imágenes, vídeo local |
| Claude / Gemini / Groq | Cerebro IA multi-modelo |
| Playwright | Scrapers anti-detección |
| n8n | Automatizaciones |
| Stripe + Connect | Pagos + afiliación |
| Neon Postgres | Base de datos (7 tablas) |
| Slack | Alertas operativas |
| Vercel | Deploy frontend |
| GoHighLevel | CRM central (en integración) |

---

## REGLAS PARA CLAUDE / AGENTES IA

1. **No pedir permiso** para continuar — ejecutar directamente. Solo parar ante decisiones irreversibles (borrar datos, push producción, cambio arquitectura mayor).
2. **Respuestas compactas** — sin relleno, sin resúmenes al final.
3. **Todo el código en** `sistema-180/` — nunca en mt5-trading-eas.
4. **Diseño:** dark premium glassmorphism, variables CSS del sistema (`--accent`, `--green`, `--bg-card`, etc.)
5. **Antes de editar un archivo:** siempre leerlo primero.
6. **No borrar visión** — las 9 patas del ecosistema se preservan siempre.
7. **CURRENT_STATE.md es la fuente de verdad** — si hay contradicciones, ese documento manda.

---

## TAREAS PENDIENTES (por orden de prioridad)

- [ ] **legal.js** — Página GDPR completa (cookies, privacidad, aviso legal para sistema-180.com)
- [ ] **sidebar.js** — Añadir sección "Legal & GDPR"
- [ ] **main.js** — Registrar ruta `/legal`
- [ ] **Regenerar API keys expuestas** — Todas las keys del archivo PROMPT_CLAUDE_CODE.md están en el historial de git
- [ ] **Flujos n8n completos** — Automatizaciones operativas
- [ ] **Sistema facturación automática** — Facturas para clientes
- [ ] **Integración GoHighLevel completa** — CRM central
