# CLAUDE.md — SISTEMA 180
## Contexto permanente — se carga automáticamente en cada sesión

> IMPORTANTE: Lee este archivo COMPLETO al inicio de cada conversación. Nunca pierdas este contexto.

---

## QUIÉNES SOMOS

**SISTEMA 180** — Agencia digital automatizada para negocios locales en España.

| Persona | Rol |
|---------|-----|
| **Ares Villalba Sánchez** | Parte creativa, estrategia, marca personal, cara del negocio |
| **José María Moreno García** | Parte operativa, automatizaciones, técnica, desarrollo |

- **Sede:** Marbella, España
- **Target principal:** Negocios con citas (peluquerías, barberías, estética, clínicas) en Málaga y semiciudades españolas
- **Objetivo inmediato:** 50 clientes en 40 días

---

## LAS 7 PATAS DEL NEGOCIO

### 1. Webs para negocios locales (entrada principal)
- **Precio:** 297€ pago único → subir a 497€ en Abril → 1.500€ High-Ticket desde Mayo
- **Producto:** Web profesional (Lovable, 30-180 min) + Google Maps optimizado + Bot IA WhatsApp 24/7
- **Pitch:** "Una IA atiende a tus clientes por WhatsApp, cierra citas automáticamente y te posicionamos en Google Maps"

### 2. Recepcionista IA / Chatbots
- **Precio:** 300€/mes por cliente (MRR recurrente)
- **Tecnología:** Make/Vapi/OpenAI — el cliente paga los costes de API directamente

### 3. Afiliación 180
- **Niveles:** Bronce 20% · Plata 33% · Gold 40%
- **Protecciones:** Hold 14 días · KYC >2.000€/mes · Circuit breaker >3 chargebacks → suspended
- **Infraestructura:** Stripe Connect Express + Slack alertas

### 4. Marketplace dual
- Directorio negocios locales + alquileres vacacionales
- Comisión ~10-13% mensual por transacción

### 5. Avatares IA
- Clones digitales de clientes para contenido (ComfyUI, gratis para S180)
- Protocolo onboarding: fotos todas las caras + cuerpo entero + voz 30s (silencio, sin eco)
- Hardware Ares: `C:\ComfyUI\` · foto `C:\ComfyUI\input\foto_ares.jpg` · voz: `voz_ares_referencia.wav`

### 6. Marca personal de Ares
- Contenido viral diario (3-5 vídeos/día con VideoForge Pro)
- Método Heras: GANCHO → HISTORIA → MORALEJA → CTA
- 4 Pilares SDD: Salud · Dinero · Desarrollo Personal · Parejas

### 7. Bots Trading + Dashboard
- EAs MT5 (Alfonso, Ana, Elena, JoseMaria) — sistemas de trading automatizados
- Dashboard de journaling y licenciamiento

---

## STACK TÉCNICO ACTIVO

| Herramienta | Uso | Coste |
|-------------|-----|-------|
| ComfyUI (RTX 4080 Super) | Avatares + vídeos IA | 0€ |
| Claude Code | Desarrollo + agente IA | incluido |
| n8n plan avanzado | Automatizaciones | mensual |
| Lovable Pro | Webs rápidas para clientes | mensual |
| Stripe + Connect | Pagos + afiliación | % por venta |
| Neon Postgres | Base de datos (7 tablas) | gratis tier |
| Slack (3 canales) | Alertas operativas | gratis |
| fal.ai | Vídeo en cloud | por uso |
| ElevenLabs | Clonación de voz | mensual |
| Meta Ads | Captación pagada | variable |
| **Ahorro total:** | Reemplaza HeyGen+Midjourney+Runway+ChatGPT+etc | **~6.000€/año** |

---

## CRM INTERNO — MACHINE DE PROSPECCIÓN (Agent Orchestrator v9)

No es el producto que se vende — es la maquinaria interna de captación:

1. **Lead Factory Engine** — Busca negocios en Google Maps (webs rotas, malas reseñas)
2. **SDR Agent** — Mensajes WhatsApp hiper-personalizados en frío
3. **WhatsApp Bridge** (Chrome Extension) — Envía emulando comportamiento humano (sin Meta API)
4. **Closer Agent** — Negocia, agenda reunión, pasa el relevo a José

**Protocolo calentamiento anti-ban:**
- Semana 1: 20-30 WhatsApps/día
- Semana 2: 50-80/día
- Semana 3: 100-150/día
- Modo crucero: 150-200/día

---

## META ADS — ESTRATEGIA

- **Audiencia 1:** Seguidores de competidores (marketing/IA/automatización España)
- **Audiencia 2:** Lookalike 1% España (requiere Pixel instalado en web)
- **Audiencia 3:** Engagement propio (crece sola)
- **Presupuesto inicio:** 0€ orgánico → con 600€ revenue meter 10€/día × 7 días test → escalar
- **Copy hooks:** "¿Sabes cuántos clientes pierdes por no contestar a tiempo?" · "El 67% de clientes se van si no contestas en 5 min"
- **CTA:** "Escribe ANÁLISIS y te hago auditoría gratis"

---

## ARQUITECTURA FRONTEND (Vite SPA)

```
/src
  main.js              ← Router principal
  pages/
    dashboard.js       ← Panel maestro KPIs + pipeline + producción
    avatars.js         ← Generador avatares (FLUX + Gemini + Freepik 4K)
    scripts.js         ← Guiones virales (Método Heras + AI Cascade)
    ads.js             ← Diseñador anuncios 9 plataformas
    videos.js          ← Hub vídeos UGC
    editor.js          ← VideoForge Pro (integra pipeline Python)
    settings.js        ← Config APIs
    legal.js           ← GDPR: cookies, privacidad, aviso legal ← PENDIENTE
  services/
    ai-cascade.js      ← Gemini → Perplexity → Gemini (guiones)
    freepik-api.js     ← Avatares 4K
    voice-cloning.js   ← ElevenLabs
    storage.js         ← LocalStorage
  components/
    sidebar.js         ← Navegación (añadir sección Legal) ← PENDIENTE
  styles/
    index.css          ← Dark premium glassmorphism
```

**Deploy:** Vercel (frontend) · localtunnel (backend staging)
**Repo:** `admins-dev/sistema-180` (GitHub privado)

---

## VIDEOFORGE PRO — EDITOR IA

```
video-editor/
  editor/
    pipeline.py        ← Orquestador + 12 presets profesionales
    v15/all_agents.py  ← 14 agentes IA (100% local, sin API)
  server.py            ← API Flask :5000
  web/index.html       ← Frontend editor (37 KB)
```

**12 Presets:** Viral Max · Cinematic Pro · Aggressive v10 · Hormozi · MrBeast · Music Video · Reel Pro · TikTok Pro · Ad Killer · Podcast Pro · YouTube Pro · Speed Cut

---

## CURSO COMFYUI PROFESIONAL (PENDIENTE)

El usuario quiere crear un curso profesional de ComfyUI para:
- Crear películas / contenido cinematográfico con IA
- Desarrollar todo el potencial creativo como creador
- Posiblemente venderlo como infoproducto

**Formato a crear:** PDF profesional + workflows exportables
**Audiencia:** Creadores de contenido que quieren producción nivel profesional

---

## TAREAS PENDIENTES (por orden de prioridad)

- [ ] **legal.js** — Página GDPR completa (cookies, privacidad, aviso legal para sistema-180.com)
- [ ] **sidebar.js** — Añadir sección "Legal & GDPR"
- [ ] **main.js** — Registrar ruta `/legal`
- [ ] **Curso ComfyUI profesional** — PDF + workflows (cine, creatividad máxima)
- [ ] **Flujos n8n completos** — Automatizaciones operativas
- [ ] **Sistema facturación automática** — Facturas para clientes
- [ ] **Auto-publicación redes** — Buffer / API directa
- [ ] **Agente copies virales** — Guionista autónomo

---

## REGLAS PARA CLAUDE

1. **No pedir permiso** para continuar — ejecutar directamente. Solo parar ante decisiones irreversibles (borrar datos, push producción, cambio arquitectura mayor).
2. **Respuestas compactas** — sin relleno, sin resúmenes al final.
3. **Todo en** `/home/jose/proyectos/sistema-180/` — nunca en mt5-trading-eas.
4. **Diseño:** dark premium glassmorphism, variables CSS del sistema (`--accent`, `--green`, `--bg-card`, etc.)
5. **Antes de editar un archivo:** siempre leerlo primero.
6. **José María usa VS Code** con Claude Code integrado en WSL2 (Ubuntu en Windows).
