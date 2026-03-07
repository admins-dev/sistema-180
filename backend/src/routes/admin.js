const express = require('express');
const router = express.Router();
const db = require('../db');
const stripeService = require('../services/stripeService');
const slack = require('../services/slackService');

// ── Health check ─────────────────────────────────────────────
router.get('/health', (req, res) => res.json({ ok: true, time: new Date().toISOString() }));

// ── List affiliates ──────────────────────────────────────────
router.get('/affiliates', async (req, res) => {
    try {
        const result = await db.query(
            'SELECT id, code, name, email, level, balance_cents, reserved_cents, total_sales, status, created_at FROM affiliates ORDER BY total_sales DESC'
        );
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Create affiliate ─────────────────────────────────────────
router.post('/affiliates', async (req, res) => {
    try {
        const { name, email, phone, level } = req.body;
        const code = 'AF-' + Math.random().toString(36).substring(2, 8).toUpperCase();
        const result = await db.query(
            'INSERT INTO affiliates (code, name, email, phone, level) VALUES ($1,$2,$3,$4,$5) RETURNING *',
            [code, name, email, phone, level || 'plata']
        );
        res.json(result.rows[0]);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Get affiliate detail ─────────────────────────────────────
router.get('/affiliates/:id', async (req, res) => {
    try {
        const aff = await db.getOne('SELECT * FROM affiliates WHERE id = $1', [req.params.id]);
        if (!aff) return res.status(404).json({ error: 'Not found' });
        const comms = await db.query(
            'SELECT * FROM affiliate_commissions WHERE affiliate_id = $1 ORDER BY created_at DESC LIMIT 50',
            [req.params.id]
        );
        res.json({ affiliate: aff, commissions: comms.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Create Connect onboarding link ───────────────────────────
router.post('/affiliates/:id/connect', async (req, res) => {
    try {
        const aff = await db.getOne('SELECT * FROM affiliates WHERE id = $1', [req.params.id]);
        if (!aff) return res.status(404).json({ error: 'Not found' });
        const url = await stripeService.createConnectOnboardingLink(aff);
        res.json({ onboarding_url: url });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Process payout ───────────────────────────────────────────
router.post('/affiliates/:id/payout', async (req, res) => {
    try {
        // Check payouts enabled
        const enabled = await db.getConfig('payouts_enabled');
        if (enabled !== 'true') return res.status(403).json({ error: 'Payouts disabled' });

        const aff = await db.getOne('SELECT * FROM affiliates WHERE id = $1', [req.params.id]);
        if (!aff) return res.status(404).json({ error: 'Not found' });
        if (aff.balance_cents <= 0) return res.status(400).json({ error: 'No balance available' });

        const amount = req.body.amount_cents || aff.balance_cents;

        // Create payout record
        const payoutRes = await db.query(
            'INSERT INTO affiliate_payouts (affiliate_id, amount_cents, status) VALUES ($1,$2,$3) RETURNING *',
            [aff.id, amount, 'processing']
        );
        const payout = payoutRes.rows[0];

        try {
            const transfer = await stripeService.transferToAffiliate(aff, amount);
            await db.query(
                "UPDATE affiliate_payouts SET status = 'completed', stripe_transfer_id = $1 WHERE id = $2",
                [transfer.id, payout.id]
            );
            await db.query('UPDATE affiliates SET balance_cents = balance_cents - $1 WHERE id = $2', [amount, aff.id]);
            await slack.postPayoutNotification(aff, amount, transfer.id, 'completed');
            res.json({ payout: { ...payout, status: 'completed', transfer_id: transfer.id } });
        } catch (stripeErr) {
            await db.query("UPDATE affiliate_payouts SET status = 'failed', notes = $1 WHERE id = $2",
                [stripeErr.message, payout.id]);
            await slack.postPayoutNotification(aff, amount, null, 'failed');
            res.status(500).json({ error: 'Payout failed', detail: stripeErr.message });
        }
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── List orders ──────────────────────────────────────────────
router.get('/orders', async (req, res) => {
    try {
        const result = await db.query(
            `SELECT o.*, a.code as affiliate_code, a.name as affiliate_name
       FROM orders o LEFT JOIN affiliates a ON o.affiliate_id = a.id
       ORDER BY o.created_at DESC LIMIT 100`
        );
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Toggle payouts ───────────────────────────────────────────
router.post('/config/payouts', async (req, res) => {
    try {
        const { enabled } = req.body;
        await db.query("UPDATE system_config SET value = $1, updated_at = now() WHERE key = 'payouts_enabled'",
            [enabled ? 'true' : 'false']);
        res.json({ payouts_enabled: enabled });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
