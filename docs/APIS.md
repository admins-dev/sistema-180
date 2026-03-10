# 🔑 APIs y Servicios de SISTEMA180

## 1. Freepik API (Premium+ Mystic)
- **Uso:** Generación de avatares 4K ultrarrealistas
- **Endpoint:** `https://api.freepik.com/v1/ai/mystic`
- **Flujo:** POST → task_id → poll hasta COMPLETED
- **Coste:** ~0.05€/imagen
- **Key guardada en:** LocalStorage del navegador (pestaña Configuración)

## 2. Google Gemini 2.0 Flash
- **Uso:** Estructura de guiones + optimización de prompts + escritura final
- **Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- **Crédito comprado:** $15 → ~3.000 llamadas
- **Retry automático:** 3 intentos con backoff de 15s en caso de 429 (rate limit)
- **Key guardada en:** LocalStorage del navegador

## 3. Perplexity Sonar Pro
- **Uso:** Investigación profunda en Reddit, foros y métricas reales 2026
- **Endpoint:** `https://api.perplexity.ai/chat/completions`
- **Modelo:** `sonar-pro`
- **Key guardada en:** LocalStorage del navegador

## 4. Stripe
- **Modo:** TEST
- **Productos:** 2 configurados
- **Webhook ID:** `we_1T82sYCetqXM41XwyT4xgl80` (4 eventos)
- **Keys en:** `backend/.env`

## 5. Slack Bot
- **Canales:** 3 creados (ventas, payouts, alertas)
- **Token en:** `backend/.env`

## 6. Neon Postgres
- **Tablas:** 7 (usuarios, afiliados, comisiones, pagos, suscripciones, config, logs)
- **Connection string en:** `backend/.env`

---

## ⚠️ Seguridad
- Las API keys del frontend (Gemini, Perplexity, Freepik) se guardan en **LocalStorage** del navegador
- Las API keys del backend (Stripe, Slack, Neon) están en el archivo `.env` (no se sube a GitHub gracias al `.gitignore`)
- El repositorio de GitHub es **PRIVADO**
