// ============================================================
// SISTEMA180 — Marketplace Routes
// Stripe Connect Express: propietario 87% / S180 13%
// ============================================================
const express = require('express');
const router = express.Router();
const db = require('../db');
const stripeService = require('../services/stripeService');

// ── API Key auth (same as admin) ──────────────────────────────
router.use((req, res, next) => {
    const apiKey = process.env.ADMIN_API_KEY;
    const authHeader = req.headers['authorization'] || '';
    const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
    if (!apiKey || !token || token !== apiKey) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
});

// ── List properties ───────────────────────────────────────────
router.get('/properties', async (req, res) => {
    try {
        const result = await db.query(
            `SELECT id, owner_name, owner_email, owner_phone, property_name, property_type,
                    location, price_per_night_cents, commission_pct, stripe_account_id,
                    connect_status, connect_onboarded_at, web_url, status, created_at
             FROM marketplace_properties
             ORDER BY created_at DESC`
        );
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Create property / register owner ─────────────────────────
router.post('/properties', async (req, res) => {
    try {
        const {
            owner_name, owner_email, owner_phone,
            property_name, property_type, description,
            location, price_per_night_cents, web_url
        } = req.body;

        if (!owner_email || !property_name) {
            return res.status(400).json({ error: 'owner_email and property_name are required' });
        }

        const result = await db.query(
            `INSERT INTO marketplace_properties
             (owner_name, owner_email, owner_phone, property_name, property_type, description,
              location, price_per_night_cents, web_url)
             VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
             RETURNING *`,
            [owner_name, owner_email, owner_phone || null,
             property_name, property_type || 'rental', description || null,
             location || null, price_per_night_cents || null, web_url || null]
        );
        res.json(result.rows[0]);
    } catch (err) {
        if (err.code === '23505') {
            return res.status(409).json({ error: 'Owner email already registered' });
        }
        res.status(500).json({ error: err.message });
    }
});

// ── Get property detail ───────────────────────────────────────
router.get('/properties/:id', async (req, res) => {
    try {
        const prop = await db.getOne(
            'SELECT * FROM marketplace_properties WHERE id = $1', [req.params.id]
        );
        if (!prop) return res.status(404).json({ error: 'Not found' });

        const bookings = await db.query(
            `SELECT id, customer_email, customer_name, check_in, check_out, nights,
                    amount_cents, platform_fee_cents, owner_amount_cents, status, created_at
             FROM marketplace_bookings WHERE property_id = $1
             ORDER BY created_at DESC LIMIT 50`,
            [req.params.id]
        );
        res.json({ property: prop, bookings: bookings.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Generate Stripe Connect onboarding link ───────────────────
router.post('/properties/:id/connect', async (req, res) => {
    try {
        const prop = await db.getOne(
            'SELECT * FROM marketplace_properties WHERE id = $1', [req.params.id]
        );
        if (!prop) return res.status(404).json({ error: 'Not found' });

        const { url, account_id } = await stripeService.createProviderConnectLink(prop);
        res.json({ onboarding_url: url, stripe_account_id: account_id });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Check Connect account status ──────────────────────────────
router.get('/properties/:id/connect-status', async (req, res) => {
    try {
        const prop = await db.getOne(
            'SELECT * FROM marketplace_properties WHERE id = $1', [req.params.id]
        );
        if (!prop) return res.status(404).json({ error: 'Not found' });
        if (!prop.stripe_account_id) {
            return res.json({ status: 'not_started', is_active: false });
        }

        const status = await stripeService.getProviderConnectStatus(prop.stripe_account_id);

        // Sync status to DB if changed
        if (status.is_active && prop.connect_status !== 'active') {
            await db.query(
                "UPDATE marketplace_properties SET connect_status = 'active', connect_onboarded_at = now(), updated_at = now() WHERE id = $1",
                [prop.id]
            );
        }

        res.json({ ...status, connect_status: prop.connect_status });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Create booking + PaymentIntent ───────────────────────────
router.post('/bookings', async (req, res) => {
    try {
        const {
            property_id, customer_email, customer_name,
            check_in, check_out, nights, amount_cents
        } = req.body;

        if (!property_id || !amount_cents) {
            return res.status(400).json({ error: 'property_id and amount_cents are required' });
        }

        const prop = await db.getOne(
            'SELECT * FROM marketplace_properties WHERE id = $1 AND status = $2',
            [property_id, 'active']
        );
        if (!prop) return res.status(404).json({ error: 'Property not found or not active' });
        if (!prop.stripe_account_id || prop.connect_status !== 'active') {
            return res.status(400).json({ error: 'Property owner has not completed Stripe Connect setup' });
        }

        const commissionPct = parseFloat(prop.commission_pct) || 0.13;
        const platformFeeCents = Math.round(amount_cents * commissionPct);
        const ownerAmountCents = amount_cents - platformFeeCents;

        // Create booking record first (pending)
        const bookingRes = await db.query(
            `INSERT INTO marketplace_bookings
             (property_id, customer_email, customer_name, check_in, check_out, nights,
              amount_cents, platform_fee_cents, owner_amount_cents, status)
             VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,'pending')
             RETURNING *`,
            [property_id, customer_email || null, customer_name || null,
             check_in || null, check_out || null, nights || null,
             amount_cents, platformFeeCents, ownerAmountCents]
        );
        const booking = bookingRes.rows[0];

        // Create PaymentIntent with destination charge split
        const pi = await stripeService.createMarketplacePaymentIntent({
            property: prop,
            amountCents: amount_cents,
            customerEmail: customer_email,
            bookingId: booking.id,
        });

        // Store payment intent ID
        await db.query(
            'UPDATE marketplace_bookings SET stripe_payment_intent_id = $1 WHERE id = $2',
            [pi.id, booking.id]
        );

        res.json({
            booking_id: booking.id,
            client_secret: pi.client_secret,
            amount_cents,
            platform_fee_cents: platformFeeCents,
            owner_amount_cents: ownerAmountCents,
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── List bookings ─────────────────────────────────────────────
router.get('/bookings', async (req, res) => {
    try {
        const result = await db.query(
            `SELECT b.*, p.property_name, p.owner_name, p.owner_email
             FROM marketplace_bookings b
             JOIN marketplace_properties p ON b.property_id = p.id
             ORDER BY b.created_at DESC LIMIT 100`
        );
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Dashboard stats ───────────────────────────────────────────
router.get('/stats', async (req, res) => {
    try {
        const [propStats, bookingStats] = await Promise.all([
            db.query(
                `SELECT
                   COUNT(*) AS total_properties,
                   COUNT(*) FILTER (WHERE connect_status = 'active') AS active_properties,
                   COUNT(*) FILTER (WHERE connect_status = 'pending') AS pending_properties
                 FROM marketplace_properties`
            ),
            db.query(
                `SELECT
                   COUNT(*) AS total_bookings,
                   COALESCE(SUM(amount_cents) FILTER (WHERE status = 'paid'), 0) AS total_revenue_cents,
                   COALESCE(SUM(platform_fee_cents) FILTER (WHERE status = 'paid'), 0) AS total_fees_cents
                 FROM marketplace_bookings`
            ),
        ]);
        res.json({
            ...propStats.rows[0],
            ...bookingStats.rows[0],
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
