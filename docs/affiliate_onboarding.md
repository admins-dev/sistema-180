# Affiliate Onboarding — Playbook

## Flujo de Alta

### Paso 1: Registro
1. El candidato rellena formulario con:
   - Nombre completo
   - Email
   - Teléfono
   - NIF/CIF (para facturación)
   - IBAN (opcional — se puede añadir después via Stripe Connect)

2. Admin crea afiliado via API:
   ```
   POST /admin/affiliates
   { "name": "...", "email": "...", "phone": "...", "level": "plata" }
   ```
   → Sistema genera código `AF-XXXXXX`

### Paso 2: Stripe Connect (para cobros)
1. Admin genera link de onboarding:
   ```
   POST /admin/affiliates/:id/connect
   → { "onboarding_url": "https://connect.stripe.com/..." }
   ```
2. Enviar link al afiliado por email/WhatsApp
3. Afiliado completa onboarding en Stripe (datos bancarios, identidad)
4. Stripe notifica via webhook cuando la cuenta está lista

### Paso 3: Activación
1. Se envía al afiliado:
   - Su código único `AF-XXXXXX`
   - Link personalizado: `https://tudominio.com/?af=AF-XXXXXX`
   - Material de marketing (plantillas, banners, copy)
   - Invitación a Slack `#afiliados-onboarding`

### Paso 4: KYC (si aplica)
- Si el afiliado supera **2.000€ acumulados**, el sistema marca `status = kyc_required`
- Se envía email solicitando documentación adicional
- Pagos se pausan hasta verificar

## Niveles

| Nivel | Comisión | Requisitos |
|-------|----------|------------|
| Bronce | 20% | Alta inicial |
| Plata | 33% | Default / referido directo |
| Gold | 40% | >10 ventas/mes o acuerdo especial |

## Protecciones
- **Hold 14 días**: la comisión se reserva y no se libera hasta pasados 14 días sin refund/dispute
- **Circuit breaker**: >3 chargebacks en 30 días → afiliado suspendido automáticamente
- **KYC**: obligatorio al superar umbral (configurable en `system_config`)

## Comunicación
- **Slack**: el afiliado recibe invitación a `#afiliados-onboarding` y puede ver su ranking en `#afiliados-ranking`
- **Email**: notificaciones de venta, payout, y KYC
- **WhatsApp** (opcional): para soporte directo

## FAQ Afiliado
**¿Cuándo cobro?** → 14 días después de la venta, si no hay refund
**¿Cómo veo mis ventas?** → Dashboard (futuro) o pregunta al admin
**¿Puedo subir de nivel?** → Sí, según volumen de ventas mensuales
