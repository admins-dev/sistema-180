# 🎯 PROMPT MAESTRO — SISTEMA180
## Para Antigravity / Agente IA

---

## CONTEXTO DE LA EMPRESA

**SISTEMA180** es una agencia digital automatizada que ayuda a negocios locales (pueblos y semiciudades de España) a captar clientes usando webs de gancho + automatizaciones con IA.

### Oferta Core
- **Web Gancho**: ~300€ pago único (producción 30-180 min, entrega 48-72h)
- **Recepcionista IA 24/7**: ~100€/mes suscripción (agenda, leads, seguimiento)
- **Servicios Premium**: Marca personal, infoproductos (high-ticket, plazas limitadas)

### 6 Pilares del Ecosistema
1. **Afiliación 180** — Red masiva de prescriptores. Niveles: Bronce 20%, Plata 33%, Gold 40%
2. **Ecosistema/Marketplace** — Plataforma de servicios locales con comisión ~10%
3. **Avatares de IA** — Clones digitales para marcas personales y B2B
4. **Marca Personal** — Posicionamiento de líderes, plazas premium
5. **Marcas de Ropa** — E-commerce + branding con avatares
6. **Bots Trading + Dashboard** — EAs MT5 (Alfonso/Elena v7), journaling, licenciamiento

### Operativa
- **Slack-first**: Panel operativo, ranking afiliados, alertas, payouts
- **Stripe**: Cobros, códigos afiliado en metadata, payouts via Connect
- **Automatización máxima**: Pocos empleados, red grande de afiliados
- **Target**: Negocios con citas (estética, clínicas, profesionales)
- **Objetivo inmediato**: 50 clientes en 40 días

### Equipo
- 2 socios (Jose Ares + socio)
- Red de afiliados como palanca de crecimiento
- Antigravity como operador IA principal

---

## TAREAS A EJECUTAR (PRIORIDAD)

### 1. MIRO — Tablero Ecosistema
- Crear board "SISTEMA180 — Ecosistema y Flujos"
- Importar `miro/sistema180_board.csv` como sticky notes
- Subir `miro/hexagono_sistema180.svg` y `miro/rueda_afiliacion.svg`
- Crear frames por pilar con: Owner, Top 10 tareas, KPIs 30d, Dependencias
- Customer Journey: TikTok→Web→IA→Sub→Upsell→Feedback
- Barra infra: Slack / Stripe / CRM / Antigravity / Dashboard
- Timeline 48h / 7d / 30d
- Exportar PNG/PDF/CSV

### 2. BACKEND — Sistema de Afiliación
El código base está en `backend/`. Completar y desplegar en staging:
- `src/index.js` — Server con cookie tracking (?af=AF-XXXXXX)
- `src/services/stripeService.js` — Checkout, webhooks, comisiones, Connect, payouts
- `src/services/slackService.js` — Alertas, leaderboard, payouts
- `src/routes/checkout.js` — Crear sesiones Stripe con affiliate_code
- `src/routes/webhook.js` — Manejar checkout.session.completed, invoice.paid, refunds, disputes
- `src/routes/admin.js` — CRUD afiliados, payouts, orders, config
- `src/cron/jobs.js` — Leaderboard diario 08:00 CET, settlement cada hora

### 3. STRIPE — Configuración (Test Mode primero)
- Crear productos: web_gancho (300€ one-time), recepcionista_ia (100€/mes recurring)
- Registrar webhook endpoint con eventos: checkout.session.completed, invoice.paid, charge.refunded, charge.dispute.created
- Implementar Stripe Connect Express para afiliados
- Comisión: reserva 14 días, settle automático, void en refund/dispute

### 4. SLACK — App y Canales
- Crear Slack App con scopes: chat:write, channels:read, commands
- Canales: #afiliacion-alerts, #afiliados-ranking, #ops-payouts, #afiliados-onboarding
- Bot messages: venta nueva, leaderboard, payout, refund, KYC
- Ranking semanal automático a las 08:00 CET

### 5. DOCUMENTACIÓN
- `docs/affiliate_onboarding.md` — Flujo completo de alta de afiliado
- `docs/provider_onboarding.md` — Alta de proveedores marketplace
- `docs/gdpr_kyc.md` — GDPR, KYC, consentimientos avatares, línea adulta separada
- `docs/runbook_production.md` — Pasos staging→producción
- `docs/emails/` — Templates: onboarding, payout, KYC request

### 6. QA y TESTS
Ejecutar en staging con Stripe test keys:
1. ✅ Crear afiliado → código AF-XXXXXX generado
2. ✅ Checkout con affiliate_code → order creada → comisión reservada → Slack alert
3. ✅ Refund → comisión anulada → affiliate balance ajustado
4. ✅ Subscription → invoice.paid → comisión en renewal
5. ✅ Settlement → tras 14d comisión pasa de reserved→settled→balance disponible
6. ✅ Payout via Connect → transfer ejecutado → Slack notification
7. ✅ Circuit breaker: >3 disputes → affiliate suspended
8. ✅ Leaderboard cron → ranking en Slack

### 7. CI/CD
- GitHub Actions: install → test → deploy staging
- Manual promotion a producción después de QA

---

## REGLAS DE NEGOCIO

### Comisiones
| Nivel | Rate | Ejemplo (web 300€) |
|-------|------|---------------------|
| Bronce | 20% | 60€ |
| Plata | 33% | 100€ |
| Gold | 40% | 120€ |

### Protecciones
- **Hold 14 días** antes de liberar comisión
- **KYC obligatorio** si afiliado supera 2.000€/mes
- **Circuit breaker**: >3 chargebacks en 30 días → suspended
- **Payouts toggle**: admin puede pausar todos los payouts
- **Daily payout cap**: 5.000€ por defecto

### Marketplace
- Comisión por transacción: ~10%
- KYC proveedores obligatorio
- Políticas: cancelaciones, reembolsos, disputes

---

## ENTREGABLES ESPERADOS
1. Link Miro (Anyone with link — Can view)
2. Repo `sistema180-backend` funcional en staging
3. Stripe test configurado (products, webhooks, Connect)
4. Slack app con canales y bot activo
5. Docs completos (playbooks, legal, runbook)
6. Evidencia QA (logs, screenshots, test results)
7. ZIP final con todo el paquete

---

## NOTAS FINALES
- Trabajar SIEMPRE primero en Stripe Test Mode
- No dejar funciones parciales — todo end-to-end
- Si algo no se puede implementar, documentar exactamente por qué y los pasos para completarlo
- Línea adulta (avatares): separada a nivel de marca/operación/finanzas
- Toda acción financiera debe quedar en webhooks_log
