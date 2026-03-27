-- SISTEMA180 - Marketplace Schema v1.0
-- Ejecutar: psql $DATABASE_URL -f 002_marketplace.sql

-- ==========================================================
-- MARKETPLACE_PROPERTIES (propiedades/negocios listados)
-- ==========================================================
CREATE TABLE IF NOT EXISTS marketplace_properties (
  id                  SERIAL PRIMARY KEY,
  owner_name          VARCHAR(255) NOT NULL,
  owner_email         VARCHAR(255) UNIQUE NOT NULL,
  owner_phone         VARCHAR(50),
  property_name       VARCHAR(255) NOT NULL,
  property_type       VARCHAR(50) DEFAULT 'rental',     -- rental / business
  description         TEXT,
  location            VARCHAR(255),
  price_per_night_cents INTEGER,                        -- para alquileres
  monthly_fee_cents   INTEGER,                          -- para negocios (suscripción)
  commission_pct      DECIMAL(5,4) DEFAULT 0.1300,      -- 13% por defecto
  stripe_account_id   VARCHAR(255),                     -- Stripe Connect Express
  connect_status      VARCHAR(32) DEFAULT 'pending',    -- pending / onboarding / active / restricted
  connect_onboarded_at TIMESTAMP,
  web_url             VARCHAR(500),
  status              VARCHAR(32) DEFAULT 'pending',    -- pending / active / suspended
  metadata            JSONB,
  created_at          TIMESTAMP DEFAULT now(),
  updated_at          TIMESTAMP DEFAULT now()
);

-- ==========================================================
-- MARKETPLACE_BOOKINGS (reservas y transacciones)
-- ==========================================================
CREATE TABLE IF NOT EXISTS marketplace_bookings (
  id                        SERIAL PRIMARY KEY,
  property_id               INTEGER REFERENCES marketplace_properties(id) NOT NULL,
  customer_email            VARCHAR(255),
  customer_name             VARCHAR(255),
  check_in                  DATE,
  check_out                 DATE,
  nights                    INTEGER,
  amount_cents              INTEGER NOT NULL,          -- total cobrado al cliente
  platform_fee_cents        INTEGER NOT NULL,          -- comisión S180 (13%)
  owner_amount_cents        INTEGER NOT NULL,          -- lo que recibe el propietario (87%)
  currency                  VARCHAR(10) DEFAULT 'eur',
  stripe_payment_intent_id  VARCHAR(255),
  stripe_transfer_id        VARCHAR(255),              -- transfer al propietario
  status                    VARCHAR(32) DEFAULT 'pending',  -- pending/paid/cancelled/refunded
  notes                     TEXT,
  metadata                  JSONB,
  created_at                TIMESTAMP DEFAULT now(),
  updated_at                TIMESTAMP DEFAULT now()
);

-- ==========================================================
-- INDEXES
-- ==========================================================
CREATE INDEX IF NOT EXISTS idx_properties_owner_email ON marketplace_properties(owner_email);
CREATE INDEX IF NOT EXISTS idx_properties_status ON marketplace_properties(status);
CREATE INDEX IF NOT EXISTS idx_bookings_property ON marketplace_bookings(property_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON marketplace_bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_payment_intent ON marketplace_bookings(stripe_payment_intent_id);

-- System config defaults for marketplace
INSERT INTO system_config (key, value) VALUES
  ('marketplace_commission_pct', '0.13'),
  ('marketplace_enabled', 'true')
ON CONFLICT (key) DO NOTHING;
