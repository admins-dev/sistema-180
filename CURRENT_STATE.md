# SISTEMA 180 — ESTADO ACTUAL

> **Última actualización:** 24 Abril 2026  
> **Responsable:** José María Moreno García + Ares Villalba Sánchez  
> **Este documento es la VERDAD ACTUAL del negocio. Si algo contradice a otros docs, este manda.**

---

## MISIÓN

**"Que a nadie le falte un plato en la mesa."**

---

## LÍNEAS ACTIVAS (Prioridad operativa)

### Línea A — IA para PYMEs
**El motor de ingresos principal.**
- **Producto:** Web profesional + Bot IA WhatsApp 24/7 + SEO Local (Google Maps)
- **Precio actual:** 497€ pago único (web) + 300€/mes (recepcionista IA)
- **Target:** Negocios con citas (peluquerías, barberías, estética, clínicas, dentistas) en Málaga y semiciudades españolas
- **Herramientas de captación:** Ghost Mouse (scrapers GMaps/LinkedIn/IG), JARVIS (bot Telegram), cold email engine
- **Estado:** Operativo y escalando

### Línea B — Partnerships con infoproductores
- **Modelo:** Colaboraciones con creadores que tengan audiencia, ofrecer servicios de IA/automatización como producto white-label
- **Estado:** En desarrollo de partnerships

### Línea C — Webs
- **Producto:** Webs profesionales para negocios locales
- **Modelo:** Producción rápida (30-180 min), entrega 48-72h
- **Stack:** Vite SPA + Backend Node.js en Vercel
- **Estado:** Activo, produciendo

---

## ECOSISTEMA COMPLETO — Las 9 Patas

> Las 9 patas representan la VISIÓN COMPLETA del ecosistema. Las 3 líneas activas de arriba son el foco operativo actual. Las demás patas se mantienen como parte de la visión estratégica.

| # | Pata | Estado | Precio |
|---|------|--------|--------|
| 1 | **Webs negocios locales** | 🟢 ACTIVA (Línea C) | 497€ pago único |
| 2 | **Recepcionista IA (chatbot WhatsApp 24/7)** | 🟢 ACTIVA (Línea A) | 300€/mes |
| 3 | **Programa de Afiliación** | 🟡 LIVE (backend listo) | Bronce 20% / Plata 33% / Gold 40% |
| 4 | **Marketplace dual (negocios + alquileres)** | 🔵 BACKLOG (en construcción) | 10-13% comisión |
| 5 | **Avatares IA (ComfyUI)** | 🟡 LIVE (capacidad interna) | Por proyecto |
| 6 | **Marca personal Ares** | 🟡 LIVE (contenido activo) | — |
| 7 | **Bots Trading MT5** | 🟡 LIVE (repo separado) | — |
| 8 | **Marcas de ropa** | 🔵 BACKLOG | TBD |
| 9 | **Ecommerce con influencers IA** | 🔵 BACKLOG | TBD |

---

## STACK TÉCNICO VÁLIDO HOY

| Herramienta | Uso | Estado |
|-------------|-----|--------|
| ComfyUI (RTX 4080 Super) | Avatares, imágenes, vídeo local | ✅ Activo |
| Claude/Gemini/Groq | Cerebro IA multi-modelo | ✅ Activo |
| n8n plan avanzado | 14 flujos + 22 APIs | ✅ Activo |
| Stripe + Connect Express | Pagos + splits afiliados/marketplace | ✅ Configurado (test) |
| Neon Postgres | Base de datos principal (7 tablas) | ✅ Activo |
| Slack (3 canales) | Sistema nervioso interno | ✅ Activo |
| fal.ai | Vídeo cloud (Kling, Wan, Veo3) | ✅ Activo |
| ElevenLabs | Voz clonada | ✅ Activo |
| Gemini Flash | Agentes IA (coste ~0) | ✅ Activo |
| CEREBRO S180 v3.0 | Doctrina inyectada en bots (10 docs, protocolos, módulos) | ✅ Activo |
| Vercel | Deploy dashboard + web | ✅ Activo |
| Playwright | Automatización de navegador (scrapers) | ✅ Activo |
| GoHighLevel | CRM central (en integración) | 🔄 En progreso |

**Herramientas descartadas:** Lovable (para dashboard), Freepik API, VideoForge Pro (nombre descartado, editor propio mantiene), Signaturit

---

## MÓDULOS ESTRATÉGICOS HOY

### 1. Dashboard HQ (Frontend)
- **Ruta:** `src/`
- **Deploy:** Vercel
- **Módulos:** KPIs, Agentes (57), Clientes, Finanzas, Afiliados, Marketplace, Contenido, Editor, CRM, Legal
- Solo fundadores (clientes NO tienen dashboard)

### 2. Motor de Prospección (Ghost Mouse)
- **Ruta:** `meta-ads-bot/ghost-mouse/`
- **Capacidades:** Google Maps scraping, LinkedIn automation, Instagram DMs, cold email (Monge Malo), AI scoring con Gemini
- **Objetivo:** alimentar pipeline de ventas de forma autónoma

### 3. JARVIS (Bot Telegram)
- **Ruta:** `meta-ads-bot/bot.py` + `brain.py` + `jarvis_*.py`
- **Capacidades:** Voice-to-voice, NLP routing, Meta Ads management, calendar, WhatsApp bridge

### 4. Backend de pagos y afiliación
- **Ruta:** `backend/`
- **Stack:** Node.js + Express + Stripe + Slack + Neon Postgres
- **Tests:** 27/27 passed

---

## EQUIPO

| Persona | Rol |
|---------|-----|
| **Ares Villalba Sánchez** | Parte creativa, estrategia, marca personal, cara del negocio |
| **José María Moreno García** | Parte operativa, automatizaciones, técnica, desarrollo |

---

## OBJETIVO INMEDIATO

**50 clientes en 40 días → escalar a 300 clientes × 300€/mes = 90.000€/mes**

## CEREBRO S180 v3.0 — ESTADO

| Componente | Archivo | Estado |
|------------|---------|--------|
| Doctrina central | `meta-ads-bot/doctrina_s180.py` | ✅ Inyectada |
| Brain Jarvis | `meta-ads-bot/brain.py` | ✅ Reescrito con Doc 09 |
| Bot Telegram | `meta-ads-bot/bot.py` | ✅ 12 comandos Cerebro añadidos |
| Routing módulos | Auto-detect por keywords | ✅ Activo |
| Operador guard | Doc 02 integrado en brain | ✅ Activo |
| Ghost Mouse brain | `ghost-mouse/brain.py` | ✅ Alineado |
