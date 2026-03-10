# 🏢 SISTEMA180 — Referencia Maestra de la Empresa

> **Última actualización:** 7 de Marzo de 2026  
> **Repositorio GitHub:** [admins-dev/sistema-180](https://github.com/admins-dev/sistema-180) (privado)  
> **Deploy Vercel:** [dist-eta-mocha.vercel.app](https://dist-eta-mocha.vercel.app/)  
> **Cuenta GitHub:** admins-dev

---

## 🏗️ Las 6 Patas de la Empresa

### 1. 💳 Stripe (Pagos)
- **Checkout** con sesiones de pago
- **Webhooks** para procesar eventos (pagos, suscripciones, reembolsos, disputas)
- **Stripe Connect** para payouts de afiliados
- **Comisiones** con hold de 14 días
- **2 productos** + precios configurados en modo TEST

### 2. 📢 Slack (Comunicación Interna)
- **Bot Token** configurado
- **3 canales** creados para alertas
- Notificaciones automáticas de: ventas afiliados, leaderboard, payouts, reembolsos, KYC

### 3. 🤝 Programa de Afiliación
- **3 niveles:** Bronce (20%), Plata (33%), Gold (40%)
- Onboarding completo documentado
- Cookies de afiliado de 30 días
- Stripe Connect para payouts directos
- Dashboard de afiliados

### 4. 🎬 Fábrica de Contenido IA (Hub Principal)
**La joya de la corona — construida en 13 horas intensivas**

#### Motor de Avatares Multi-IA
| Motor | Tipo | Coste |
|-------|------|-------|
| Pollinations (FLUX) | Borrador rápido | GRATIS |
| Gemini + FLUX | Prompt optimizado | GRATIS (con tu key) |
| Perplexity + Gemini + FLUX | Max realismo | GRATIS (con tus keys) |
| Freepik Mystic | 4K Premium final | ~0.05€/imagen |

#### Guiones Virales — Método Heras
- **Metodología UMV** (Umbral Mínimo de Viralidad): Mainstream hook + Target story
- **4 Pilares SDD** (Motivadores Universales): Salud 🏥, Dinero 💰, Desarrollo Personal 🧠, Parejas ❤️
- **7 Tipos de Gancho:** Dolor, Curiosidad, Controversia, Educativo, Resultados, Relatable, Urgencia
- **12 Formatos de Vídeo:** Talking Head, Voiceover, POV, Tutorial, Storytime, Green Screen, Slideshow, Antes/Después, Reacción, Listicle, Entrevista, Challenge
- **10 Plantillas Probadas 2026** pre-cargadas y listas para usar

#### AI Cascade Engine (El Motor Estrella)
```
Paso 1: Gemini 2.0 Flash → genera estructura de investigación
Paso 2: Perplexity Sonar Pro → busca datos reales en Reddit/foros
Paso 3: Gemini 2.0 Flash → escribe guión final con metodología UMV
```
- **Coste:** ~$0.005/guión → **3.000 guiones por $15**
- **API Key Gemini:** Comprada con $15 de crédito

#### Módulo de Anuncios
- 9 plataformas soportadas: TikTok, Instagram (Reels, Stories, Feed), YouTube (Shorts, standard), Facebook, X
- Presets de formato, duración y resolución por plataforma

### 5. 🔥 Hub de Viralidad (Pendiente)
- Métricas de viralidad en tiempo real
- Calendario de publicación
- Análisis de engagement

### 6. 👤 Hub de Marca Personal (Pendiente)
- Gestión de perfil de Instagram
- Bio, Highlights, estrategia de Stories
- Funnel de contenido (TOFU → MOFU → BOFU)

---

## 🗂️ Estructura de Carpetas

```
C:\Users\Jose\.gemini\antigravity\scratch\
├── SISTEMA180\                    ← 📁 ESTA CARPETA (referencia maestra)
│   ├── README.md                  ← Este archivo
│   ├── APIS.md                    ← Todas las APIs y keys
│   ├── ARQUITECTURA.md            ← Arquitectura técnica completa
│   └── METODOLOGIA_HERAS.md       ← Documentación del Método Heras
│
├── sistema-180\                   ← 📁 CÓDIGO FUENTE (conectado a GitHub)
│   ├── index.html                 ← Frontend SPA
│   ├── src/
│   │   ├── main.js                ← Router + bootstrap
│   │   ├── pages/                 ← 6 páginas UI
│   │   ├── services/              ← AI Cascade, Freepik API, Storage
│   │   ├── components/            ← Sidebar
│   │   └── styles/                ← Dark premium CSS
│   ├── backend/                   ← Node.js + Stripe + Slack
│   ├── docs/                      ← Documentación
│   └── .env                       ← Variables de entorno
│
└── ugc-avatar-hub\                ← 📁 VERSIÓN ORIGINAL VERCEL (archivo)
    └── dist/                      ← Build desplegado en Vercel
```

---

## 🔑 APIs Configuradas

| Servicio | Estado | Key Prefix |
|----------|--------|------------|
| Freepik Mystic (Premium+) | ✅ Conectada | `FPSX...` |
| Google Gemini 2.0 Flash | ✅ $15 crédito | `AIza...` |
| Perplexity Sonar Pro | ✅ Conectada | `pplx-...` |
| Stripe (TEST mode) | ✅ Webhook activo | `sk_test_...` |
| Slack Bot | ✅ 3 canales | Token configurado |
| Neon Postgres | ✅ 7 tablas | Configurado en .env |

---

## 📦 Stack Técnico

| Capa | Tecnología |
|------|------------|
| Frontend | HTML + Vanilla JS + CSS (dark premium) |
| Dev Server | Vite 7.3 |
| Deploy | Vercel |
| Backend | Node.js + Express |
| DB | Neon Postgres (7 tablas) |
| Pagos | Stripe (Checkout + Connect + Webhooks) |
| Comunicación | Slack Bot API |
| IA Guiones | Gemini 2.0 Flash + Perplexity Sonar Pro |
| IA Avatares | Freepik Mystic + Pollinations FLUX |
| Repo | GitHub (admins-dev/sistema-180, privado) |

---

## 📊 Tests y QA
- **27/27 tests PASSED** (backend)
- **8 escenarios de integración** verificados
- **Stripe webhook** verificado con 4 eventos
- **Frontend** verificado en navegador (todas las rutas funcionales)
