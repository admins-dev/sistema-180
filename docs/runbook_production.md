# Runbook — Staging → Producción

## Pre-requisitos Staging

### Infraestructura
- [ ] PostgreSQL accesible (DigitalOcean / RDS / local)
- [ ] Backend desplegado (Heroku / Railway / VPS)
- [ ] Stripe TEST configurado (products + webhook)
- [ ] Slack App instalada con canales creados
- [ ] DNS apuntando a staging

### Variables de Entorno (staging)
```
PORT=3000
DATABASE_URL=postgres://...
STRIPE_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONT_URL=https://staging.sistema180.com
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
NODE_ENV=staging
```

## Deploy a Staging

```bash
# 1. Push código
git push origin main

# 2. Ejecutar migraciones
psql $DATABASE_URL -f src/migrations/001_init.sql

# 3. Instalar dependencias
npm ci --production

# 4. Arrancar
npm start

# 5. Verificar health
curl https://staging-api.sistema180.com/admin/health
# → {"ok":true}
```

## Checklist Pre-Producción

### 1. Tests de integración (OBLIGATORIO)
```bash
cd tests/integration
./run_integration_tests.sh
# → Revisar REPORT.md — todo debe ser ✅
```

### 2. Stripe
- [ ] Products `web_gancho` y `recepcionista_ia` creados (TEST)
- [ ] Webhook endpoint registrado con events correctos
- [ ] Checkout test con tarjeta `4242 4242 4242 4242` → OK
- [ ] Refund test → comisión anulada
- [ ] Connect Express funcional (onboarding link generado)

### 3. Slack
- [ ] Bot publica en `#afiliacion-alerts`
- [ ] Leaderboard publicado en `#afiliados-ranking`
- [ ] Payouts notificados en `#ops-payouts`

### 4. Base de Datos
- [ ] Schema migrado sin errores
- [ ] Indexes creados
- [ ] Backup automático configurado

### 5. Seguridad
- [ ] HTTPS activo
- [ ] CORS configurado (solo dominios propios)
- [ ] Rate limiting en endpoints públicos
- [ ] Webhook firma Stripe verificada
- [ ] `.env` NO committeado en git

## Promoción a Producción

```bash
# 1. Pausar payouts PRIMERO
curl -X POST -H "Authorization: Bearer $ADMIN_KEY" \
  -d '{"enabled":false}' \
  https://api.sistema180.com/admin/config/payouts

# 2. Cambiar keys en producción
STRIPE_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...

# 3. Crear webhook en Stripe LIVE (mismo endpoint, mismos events)

# 4. Deploy
git tag v1.0.0
git push origin v1.0.0

# 5. Smoke test
curl https://api.sistema180.com/admin/health

# 6. Test checkout con tarjeta real (1€/test product)

# 7. Si OK → activar payouts
curl -X POST -H "Authorization: Bearer $ADMIN_KEY" \
  -d '{"enabled":true}' \
  https://api.sistema180.com/admin/config/payouts
```

## Monitoreo Post-Deploy (48h)

- [ ] Revisar `webhooks_log` para errores
- [ ] Verificar que commissions se reservan correctamente
- [ ] Comprobar settlement cron (cada hora)
- [ ] Leaderboard Slack publicado (08:00 CET)
- [ ] No hay errores 5xx en logs

## Rollback de Emergencia

```bash
# 1. Pausar payouts inmediatamente
curl -X POST -d '{"enabled":false}' .../admin/config/payouts

# 2. Revertir a versión anterior
git revert HEAD
git push origin main

# 3. Restaurar DB snapshot si hay corrupción
pg_restore -d sistema180 backup_YYYYMMDD.dump

# 4. Notificar equipo en Slack
# 5. Post-mortem en 24h
```

## Contactos de Escalación
| Rol | Quién | Canal |
|-----|-------|-------|
| Tech Lead | Antigravity | Chat directo |
| Stripe Issues | Stripe Support | Dashboard |
| Slack Issues | Slack Admin | Workspace settings |
| DB Issues | DBA / Hosting | Panel hosting |
