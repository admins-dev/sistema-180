-- SISTEMA180 - Database Schema v1.0
-- Ejecutar: psql $DATABASE_URL -f 001_init.sql

-- ==========================================================
-- AFFILIATES (programa de afiliación)
-- ==========================================================
CREATE TABLE IF NOT EXISTS affiliates (
  id            SERIAL PRIMARY KEY,
  code          VARCHAR(32) UNIQUE NOT NULL,          -- AF-XXXXXX
  name          VARCHAR(255),
  email         VARCHAR(255) UNIQUE,
  phone         VARCHAR(50),
  country       VARCHAR(10) DEFAULT 'ES',
  tax_id        VARCHAR(50),                          -- NIF/CIF
  iban          VARCHAR(50),
  stripe_account_id VARCHAR(255),                     -- Stripe Connect
  level         VARCHAR(32) DEFAULT 'plata',          -- bronce/plata/gold
  balance_cents INTEGER DEFAULT 0,                    -- disponible para pagar
  reserved_cents INTEGER DEFAULT 0,                   -- reservado (hold 14d)
  total_earned_cents INTEGER DEFAULT 0,               -- total histórico
  total_sales   INTEGER DEFAULT 0,
  status        VARCHAR(32) DEFAULT 'active',         -- active/suspended/kyc_required
  kyc_verified  BOOLEAN DEFAULT false,
  notes         TEXT,
  created_at    TIMESTAMP DEFAULT now(),
  updated_at    TIMESTAMP DEFAULT now()
);

-- ==========================================================
-- ORDERS (pedidos: webs y suscripciones)
-- ==========================================================
CREATE TABLE IF NOT EXISTS orders (
  id            SERIAL PRIMARY KEY,
  stripe_payment_intent_id VARCHAR(255),
  stripe_checkout_session_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255),
  affiliate_id  INTEGER REFERENCES affiliates(id),
  customer_email VARCHAR(255),
  customer_name  VARCHAR(255),
  amount_cents  INTEGER NOT NULL,
  currency      VARCHAR(10) DEFAULT 'eur',
  product_type  VARCHAR(50) NOT NULL,                 -- web / subscription
  status        VARCHAR(32) DEFAULT 'pending',        -- pending/paid/refunded/chargeback
  metadata      JSONB,
  created_at    TIMESTAMP DEFAULT now()
);

-- ==========================================================
-- AFFILIATE_COMMISSIONS (ledger de comisiones)
-- ==========================================================
CREATE TABLE IF NOT EXISTS affiliate_commissions (
  id            SERIAL PRIMARY KEY,
  affiliate_id  INTEGER REFERENCES affiliates(id) NOT NULL,
  order_id      INTEGER REFERENCES orders(id) NOT NULL,
  commission_cents INTEGER NOT NULL,
  commission_pct DECIMAL(5,4),                        -- 0.2000 = 20%
  status        VARCHAR(32) DEFAULT 'reserved',       -- reserved/settled/paid/void
  reserved_until TIMESTAMP,                           -- hold period
  settled_at    TIMESTAMP,
  created_at    TIMESTAMP DEFAULT now()
);

-- ==========================================================
-- AFFILIATE_PAYOUTS (pagos a afiliados)
-- ==========================================================
CREATE TABLE IF NOT EXISTS affiliate_payouts (
  id            SERIAL PRIMARY KEY,
  affiliate_id  INTEGER REFERENCES affiliates(id) NOT NULL,
  amount_cents  INTEGER NOT NULL,
  method        VARCHAR(50) DEFAULT 'stripe_connect', -- stripe_connect/manual/bank_transfer
  stripe_transfer_id VARCHAR(255),
  reference     VARCHAR(255),
  status        VARCHAR(32) DEFAULT 'processing',     -- processing/completed/failed
  notes         TEXT,
  created_at    TIMESTAMP DEFAULT now()
);

-- ==========================================================
-- PROVIDERS (proveedores marketplace)
-- ==========================================================
CREATE TABLE IF NOT EXISTS providers (
  id            SERIAL PRIMARY KEY,
  name          VARCHAR(255) NOT NULL,
  email         VARCHAR(255),
  phone         VARCHAR(50),
  category      VARCHAR(100),                         -- estetica/clinica/profesional
  location      VARCHAR(255),
  stripe_account_id VARCHAR(255),
  commission_pct DECIMAL(5,4) DEFAULT 0.1000,         -- 10%
  status        VARCHAR(32) DEFAULT 'pending',        -- pending/active/suspended
  kyc_verified  BOOLEAN DEFAULT false,
  metadata      JSONB,
  created_at    TIMESTAMP DEFAULT now()
);

-- ==========================================================
-- WEBHOOKS_LOG (auditoría)
-- ==========================================================
CREATE TABLE IF NOT EXISTS webhooks_log (
  id            SERIAL PRIMARY KEY,
  provider      VARCHAR(50) NOT NULL,                 -- stripe/slack/other
  event_type    VARCHAR(255),
  event_id      VARCHAR(255),
  payload       JSONB,
  processed     BOOLEAN DEFAULT false,
  error         TEXT,
  created_at    TIMESTAMP DEFAULT now()
);

-- ==========================================================
-- SYSTEM_CONFIG (configuración dinámica)
-- ==========================================================
CREATE TABLE IF NOT EXISTS system_config (
  key           VARCHAR(100) PRIMARY KEY,
  value         TEXT,
  updated_at    TIMESTAMP DEFAULT now()
);

-- Defaults
INSERT INTO system_config (key, value) VALUES
  ('payouts_enabled', 'true'),
  ('commission_hold_days', '14'),
  ('kyc_threshold_cents', '200000'),
  ('daily_payout_cap_cents', '500000')
ON CONFLICT (key) DO NOTHING;

-- ==========================================================
-- INDEXES
-- ==========================================================
CREATE INDEX IF NOT EXISTS idx_orders_affiliate ON orders(affiliate_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_commissions_affiliate ON affiliate_commissions(affiliate_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON affiliate_commissions(status);
CREATE INDEX IF NOT EXISTS idx_webhooks_event ON webhooks_log(event_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_webhooks_event_id ON webhooks_log(event_id);
