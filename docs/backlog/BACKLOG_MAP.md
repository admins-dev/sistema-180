# SISTEMA 180 — MAPA DE BACKLOG Y VISIÓN FUTURA

> **Propósito:** Este documento preserva la visión completa del ecosistema — las 9 patas, expansiones futuras, módulos pendientes e ideas estratégicas. Nada de esto se borra. Todo espera su turno.

---

## VISIÓN: LAS 9 PATAS DEL ECOSISTEMA

> El ecosistema completo tiene 9 patas. Operativamente se priorizan 3 líneas (ver CURRENT_STATE.md), pero la visión completa se mantiene aquí.

### Patas ACTIVAS (ver CURRENT_STATE.md para detalle operativo)

| # | Pata | Estado |
|---|------|--------|
| 1 | Webs negocios locales | 🟢 ACTIVA |
| 2 | Recepcionista IA (chatbot WhatsApp 24/7) | 🟢 ACTIVA |
| 3 | Programa de Afiliación | 🟡 LIVE (backend listo, Stripe Connect configurado) |
| 5 | Avatares IA (ComfyUI) | 🟡 LIVE (capacidad interna activa) |
| 6 | Marca personal Ares | 🟡 LIVE (contenido viral diario) |
| 7 | Bots Trading MT5 | 🟡 LIVE (repo separado: mt5-trading-eas) |

### Patas en BACKLOG (visión futura, sin prioridad operativa actual)

#### Pata 4 — Marketplace Dual
- **Qué es:** Plataforma tipo Amazon de negocios locales + alquileres vacacionales
- **Modelo:** Comisión 10-13% por transacción
- **Competencia directa:** Airbnb/Booking (propietario se lleva 85-90%)
- **Estado técnico:** Ruta `backend/src/routes/marketplace.js` existe, migración SQL creada
- **Dependencias:** Stripe Connect (ya configurado), KYC proveedores
- **Prioridad:** Media — hay un cliente activo con web de alquileres pendiente

#### Pata 8 — Marcas de Ropa
- **Qué es:** E-commerce + branding usando avatares IA
- **Modelo:** TBD
- **Estado técnico:** Sin código
- **Prioridad:** Baja — "para después"

#### Pata 9 — Ecommerce con Influencers IA
- **Qué es:** Tiendas online operadas por avatares/influencers IA
- **Modelo:** TBD
- **Estado técnico:** Sin código
- **Prioridad:** Baja — "para después"

---

## MÓDULOS FUTUROS PENDIENTES

### Hub de Viralidad
- Métricas de viralidad en tiempo real
- Calendario de publicación automática
- Análisis de engagement por plataforma
- **Estado:** Planificado, sin código

### Hub de Marca Personal
- Gestión de perfil de Instagram
- Bio, Highlights, estrategia de Stories
- Funnel de contenido (TOFU → MOFU → BOFU)
- **Estado:** Planificado, sin código

### Biblia ComfyUI (Curso personal)
- 18 bloques, 500-1000+ páginas
- Lenguaje accesible ("de cocina")
- Desde cero hasta películas completas
- Para José y Ares únicamente — NO infoproducto (puede cambiar)
- **Se construye después de terminar el edificio principal**

### Cold Caller con Voz IA
- Groq PlayAI TTS para generar audio ultra-realista (gratis)
- Claude genera guion personalizado por negocio
- Whisper STT transcribe respuestas
- GHL/Twilio para llamadas VoIP
- **Estado:** Arquitectura diseñada en PROMPT_CLAUDE_CODE.md, no implementada

### Auto-Responder GHL
- Monitor de inbox cada 30 segundos
- Claude clasifica intención (INTERESADO/PREGUNTA/OBJECION/NO_INTERESADO/OPT_OUT)
- Respuestas automáticas adaptadas
- Booking automático cuando detecta interés
- **Estado:** Arquitectura diseñada, no implementada

---

## EXPANSIONES GEOGRÁFICAS

| Fase | Mercado | Estado |
|------|---------|--------|
| 1 | Málaga y Costa del Sol | 🟢 Activo |
| 2 | Semiciudades españolas | 🔵 Planificado |
| 3 | España completa | 🔵 Planificado |
| 4 | Internacional (José planea salir de España en ~1 año) | 🔵 Visión |

---

## IDEAS ESTRATÉGICAS FUTURAS

- **Implementación Sistema Completo:** Instalar toda la infraestructura IA dentro del negocio del cliente — high ticket mensual, precio por definir
- **Sistema de licenciamiento de bots trading** — dashboard de journaling + licencias
- **Infoproducto Biblia ComfyUI** — posible monetización del curso
- **Multi-setter scaling:** Escalar de 5 a 50+ cuentas setter con proxies residenciales
- **Automatización WhatsApp Business API** — migrar de emulación de navegador a API oficial cuando el volumen lo justifique

---

## ARQUITECTURA FUTURA: EL EDIFICIO

```
PENTHOUSE    → José María + Ares (fundadores) — vista total
PLANTA 4     → Orquestadores IA (CEO, COO, CMO)
PLANTA 3     → Jefes de departamento (5 agentes)
PLANTA 2     → Trabajadores IA (37 agentes)
PLANTA 1     → Automatizaciones (n8n + Slack + Stripe)
SUBSUELO     → Base de datos (Neon Postgres)
```

**Objetivo final:** 300 clientes × 300€/mes = 90.000€/mes = 1.080.000€/año
