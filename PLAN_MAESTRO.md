# SISTEMA 180 — PLAN MAESTRO
> Fundadores: José María Moreno García + Ares Villalba Sánchez | Marbella, España

---

## MISIÓN
**"Que a nadie le falte un plato en la mesa."**

---

## LAS 9 PATAS DEL NEGOCIO

| # | Pata | Precio | Estado |
|---|------|--------|--------|
| 1 | Webs negocios locales | 297€ → 497€ → 1.500€ | Activo |
| 2 | Recepcionista IA (chatbot WhatsApp 24/7) | 300-500€/mes | Activo |
| 3 | Afiliación (15/25/33%) | % por venta | Activo |
| 4 | Marketplace negocios + alquileres | 10-15% comisión | En construcción |
| 5 | Avatares IA (ComfyUI) | Por proyecto | Activo |
| 6 | Marca personal Ares | Contenido viral | Activo |
| 7 | Bots trading MT5 | Separado | Activo |
| 8 | Marcas de ropa | TBD | Para después |
| 9 | Ecommerce con influencers IA | TBD | Para después |

**Objetivo inmediato:** 300 clientes × 300€/mes = 90.000€/mes = 1.080.000€/año

---

## EL EDIFICIO — ARQUITECTURA

```
PENTHOUSE    → José María + Ares (fundadores) — vista total
PLANTA 4     → Orquestadores IA (CEO, COO, CMO)
PLANTA 3     → Jefes de departamento (5 agentes)
PLANTA 2     → Trabajadores IA (37 agentes)
PLANTA 1     → Automatizaciones (n8n + Slack + Stripe)
SUBSUELO     → Base de datos (Neon Postgres)
```

---

## DASHBOARD HQ

- Solo fundadores (clientes NO tienen dashboard)
- Construido a medida — NO Lovable
- Deploy: Vercel | Dominio: Namecheap
- Módulos: KPIs, Agentes, Clientes, Finanzas, Afiliados, Marketplace, Contenido, Editor, CRM, Newsletter
- Editor de vídeo integrado (construido desde cero — VideoForge Pro DESCARTADO)

---

## LOS 43 AGENTES

### Orquestadores (3): CEO, COO, CMO
### Jefes de área (5): Sales, Content, Client Success, Finance, Marketplace
### Edición (10): Orchestrator + Cut + Audio + Color + Subtitle + Zoom + Thumbnail + Format + Quality + Publisher
### Copy (6): Orchestrator + Script + Ads + Caption + Email + WhatsApp
### Ventas (5): Orchestrator + Lead Scout + SDR + CRM + Closer Support
### Clientes (5): Orchestrator + Onboarding + Support + Billing + Report
### Afiliados (4): Orchestrator + Commission + Payment + Fraud
### Marketplace (4): Orchestrator + Booking + Split + Review
### Legal (1): Genera GDPR/LSSI automáticamente por cada web

---

## SISTEMA DE AFILIACIÓN

- **Starter:** 15% | **Pro:** 25% | **Elite:** 33%
- Códigos únicos por afiliado
- Split automático vía Stripe Connect
- Hold 14 días | KYC >2.000€/mes | Circuit breaker 3 chargebacks

---

## MARKETPLACE

- Como Amazon: sección Negocios + sección Alquileres + VSL acceso
- Competencia directa a Airbnb/Booking (propietario se lleva 85-90%)
- Stripe Connect: pago entra a José → split automático al propietario
- **URGENTE:** cliente activo con web alquileres incompleta → terminar antes de mayo

---

## WEB COMERCIAL

```
sistema180.com
├── / (Home + VSL)
├── /negocios
├── /alquileres
├── /afiliados
└── /login (Dashboard HQ fundadores)
```

- Colores: azul profundo + blanco + amarillo dorado + negro
- CRM + Newsletter integrados
- Contratos digitales: HelloSign (eIDAS compliant)

---

## N8N — 14 FLUJOS PRINCIPALES

1. Nuevo cliente (onboarding completo)
2. Facturación mensual automática
3. Reembolso con aprobación manual
4. Afiliado nueva venta + comisión
5. Chargeback/fraude + circuit breaker
6. Nuevo lead Meta Ads → CRM
7. Marketplace reserva + split
8. Contrato firmado → activar cobro
9. Resumen diario → Slack
10. Newsletter secuencia automática
11. Meta Ads audiencias automáticas
12. Optimización campañas diaria
13. Contenido orgánico → ad automático
14. Estrategia ads completa (3 fases)

---

## 22 APIS EN N8N

Meta (4) | TikTok (2) | YouTube (2) | Instagram | LinkedIn | Metricool | Stripe (2) | HelloSign | WhatsApp Business | Gmail | Slack | Google Calendar | Gemini Flash | ElevenLabs | fal.ai | ComfyUI local | Neon Postgres | Google Analytics

---

## FÁBRICA DE CONTENIDO

- **Motor de tendencias:** escanea virales diariamente → replica estructura
- **3 líneas:** cara real / avatar IA / imágenes y ads
- **Por cliente:** 4-7 vídeos/semana automáticos → Metricool publica
- **Stack:** ComfyUI + Gemini Flash + fal.ai + ElevenLabs (110K créditos)
- **Freepik API: DESCARTADA**

---

## EDITOR DE VÍDEO (desde cero)

- Integrado en dashboard HQ
- Cortes automáticos silencios (FFmpeg + Whisper)
- Subtítulos animados | Música + FX | Color grading | Zoom dinámico
- Auto-publicación vía Metricool

---

## CONTRATOS DIGITALES

- Plataforma: **HelloSign** (internacional, API, eIDAS)
- Plantillas: web básica, recepcionista IA, marketplace, afiliado, closer
- Agente Legal genera GDPR/LSSI por cada web → José + abogado revisan
- **Signaturit descartado** (empresa española, José se va de España en ~1 año)

---

## BIBLIA COMFYUI (curso personal)

- Para José y Ares únicamente — NO infoproducto
- 18 bloques | 500-1000+ páginas | lenguaje de cocina
- Desde cero hasta hacer películas completas
- RTX 4080 Super | 53 extensiones instaladas
- **Se construye después de terminar el edificio**

---

## STACK TÉCNICO COMPLETO

| Herramienta | Uso |
|-------------|-----|
| ComfyUI (RTX 4080 Super) | Avatares, imágenes, vídeo local |
| n8n plan avanzado | 14 flujos + 22 APIs |
| Stripe + Connect Express | Pagos + splits afiliados/marketplace |
| Neon Postgres | Base de datos principal |
| Slack | Sistema nervioso interno |
| Metricool | Auto-publicación redes |
| fal.ai | Vídeo cloud (Kling, Wan, Veo3) |
| ElevenLabs | Voz clonada (110K créditos) |
| Gemini Flash | Agentes IA (coste ~0) |
| HelloSign | Contratos digitales |
| Vercel | Deploy dashboard + web |
| Namecheap | Dominios propios |
| Meta Ads | Captación pagada |

---

*Última actualización: 27 marzo 2026*
