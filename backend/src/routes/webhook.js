const express = require('express');
const router = express.Router();
const stripeService = require('../services/stripeService');
const db = require('../db');
// ── Marketplace webhook handler ───────────────────────────────
async function handleMarketplaceWebhook(event) {
    if (event.type === 'payment_intent.succeeded') {
        const pi = event.data.object;
        const bookingId = pi.metadata?.booking_id;
        if (!bookingId) return; // not a marketplace payment

        await db.query(
            `UPDATE marketplace_bookings
             SET status = 'paid',
                 stripe_payment_intent_id = $1,
                 updated_at = now()
             WHERE id = $2 AND status = 'pending'`,
            [pi.id, bookingId]
        );

        // Resolve transfer ID from charges (destination charge creates auto transfer)
        const charges = pi.charges?.data || [];
        for (const charge of charges) {
            if (charge.transfer) {
                await db.query(
                    'UPDATE marketplace_bookings SET stripe_transfer_id = $1 WHERE id = $2',
                    [charge.transfer, bookingId]
                );
            }
        }
    }

    if (event.type === 'payment_intent.payment_failed') {
        const pi = event.data.object;
        const bookingId = pi.metadata?.booking_id;
        if (!bookingId) return;

        await db.query(
            "UPDATE marketplace_bookings SET status = 'failed', updated_at = now() WHERE id = $1",
            [bookingId]
        );
    }

    if (event.type === 'account.updated') {
        // Provider's Connect account status changed
        const account = event.data.object;
        const isActive = account.charges_enabled && account.payouts_enabled;
        const status = isActive ? 'active' : 'onboarding';
        await db.query(
            `UPDATE marketplace_properties
             SET connect_status = $1,
                 connect_onboarded_at = CASE WHEN $1 = 'active' AND connect_onboarded_at IS NULL THEN now() ELSE connect_onboarded_at END,
                 updated_at = now()
             WHERE stripe_account_id = $2`,
            [status, account.id]
        );
    }
}

// Raw body needed for Stripe signature verification
router.post('/', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    try {
        const event = stripeService.constructEvent(req.body, sig);

        // Idempotency check: insert only if event_id not already present
        const logRes = await db.query(
            `INSERT INTO webhooks_log (provider, event_type, event_id, payload)
             VALUES ($1,$2,$3,$4)
             ON CONFLICT (event_id) DO NOTHING
             RETURNING id`,
            ['stripe', event.type, event.id, JSON.stringify(event)]
        );

        // If no row returned, this event was already processed
        if (logRes.rows.length === 0) {
            return res.status(200).send('ok');
        }

        await stripeService.handleWebhook(event);
        await handleMarketplaceWebhook(event);
        res.status(200).send('ok');
    } catch (err) {
        console.error('[WEBHOOK] Error:', err.message);
        res.status(400).send(`Webhook Error: ${err.message}`);
    }
});

module.exports = router;
