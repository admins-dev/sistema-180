# SISTEMA180 — Backend

Sistema de gestión de afiliación, cobros y operaciones para la agencia digital SISTEMA180.

## Stack

- **Node.js** + Express
- **PostgreSQL** (schema en `src/migrations/`)
- **Stripe** (Checkout, Webhooks, Connect payouts)
- **Slack** (alertas, leaderboard, payouts)
- **Cron** (settlement horario, leaderboard diario 08:00 CET)

## Quick Start

```bash
# 1. Instalar dependencias
npm install

# 2. Configurar entorno
cp .env.example .env
# Editar .env con tus keys reales (Stripe TEST, Slack, Postgres)

# 3. Crear base de datos y ejecutar migraciones
createdb sistema180
psql -d sistema180 -f src/migrations/001_init.sql

# 4. Arrancar servidor
npm run dev
```

## Endpoints

### Público
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/create-checkout-session` | Crea sesión Stripe con affiliate tracking |
| POST | `/webhook` | Recibe webhooks de Stripe (firma verificada) |

### Admin
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/admin/health` | Health check |
| GET | `/admin/affiliates` | Lista todos los afiliados |
| POST | `/admin/affiliates` | Crear afiliado |
| GET | `/admin/affiliates/:id` | Detalle + comisiones |
| POST | `/admin/affiliates/:id/connect` | Generar link Stripe Connect |
| POST | `/admin/affiliates/:id/payout` | Ejecutar payout |
| GET | `/admin/orders` | Lista pedidos |
| POST | `/admin/config/payouts` | Toggle pagos on/off |

## Affiliate Cookie Flow

```
User visits: tudominio.com/?af=AF-XXXXXX
  → Cookie 'affiliate_code' set (30 days)
  → Checkout sends metadata.affiliate_code to Stripe
  → Webhook creates order + reserves commission (14d hold)
  → Cron settles after 14 days → balance available
  → Admin triggers payout via Stripe Connect
```

## Commission Levels

| Nivel | Rate | Ejemplo (web 300€) |
|-------|------|---------------------|
| Bronce | 20% | 60€ |
| Plata | 33% | ~100€ |
| Gold | 40% | 120€ |

## Protecciones

- **Hold 14 días** antes de liberar comisión
- **KYC obligatorio** si afiliado > 2.000€ acumulado
- **Circuit breaker**: >3 chargebacks → suspended
- **Payouts toggle**: admin puede pausar todos los pagos
- **Daily payout cap**: 5.000€ configurable

## Tests de Integración

```bash
cd tests/integration
cp env.sample .env   # rellenar con valores staging
chmod +x helpers.sh run_integration_tests.sh
./run_integration_tests.sh
# → Genera results_YYYYMMDD_HHMMSS/ con JSON + REPORT.md
```

## Estructura

```
backend/
├── .env.example
├── package.json
├── README.md
├── src/
│   ├── index.js              # Server + cookie tracking
│   ├── db.js                 # Postgres pool + helpers
│   ├── migrations/
│   │   └── 001_init.sql      # Schema (7 tablas)
│   ├── services/
│   │   ├── stripeService.js   # Checkout, webhooks, Connect
│   │   └── slackService.js    # Alerts, leaderboard
│   ├── routes/
│   │   ├── checkout.js        # POST /create-checkout-session
│   │   ├── webhook.js         # POST /webhook (raw body)
│   │   └── admin.js           # Admin CRUD + payouts
│   └── cron/
│       └── jobs.js            # Leaderboard + settlement
└── tests/
    └── integration/
        ├── env.sample
        ├── helpers.sh
        ├── run_integration_tests.sh
        └── payloads/          # 4 event templates
```

## Licencia

Privado — SISTEMA180 © 2026
