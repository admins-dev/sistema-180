const express = require('express');
const router = express.Router();
const stripeService = require('../services/stripeService');
const db = require('../db');

// Raw body needed for Stripe signature verification
router.post('/', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    try {
        const event = stripeService.constructEvent(req.body, sig);

        // Log raw event
        await db.query(
            'INSERT INTO webhooks_log (provider, event_type, event_id, payload) VALUES ($1,$2,$3,$4)',
            ['stripe', event.type, event.id, JSON.stringify(event)]
        );

        await stripeService.handleWebhook(event);
        res.status(200).send('ok');
    } catch (err) {
        console.error('[WEBHOOK] Error:', err.message);
        res.status(400).send(`Webhook Error: ${err.message}`);
    }
});

module.exports = router;
