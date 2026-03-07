const express = require('express');
const router = express.Router();
const stripeService = require('../services/stripeService');

router.post('/', async (req, res) => {
    try {
        const { priceId, affiliate_code, customer_email, lead_id, mode } = req.body;
        const session = await stripeService.createCheckoutSession({
            priceId, affiliate_code, customer_email, lead_id, mode
        });
        res.json({ id: session.id, url: session.url });
    } catch (err) {
        console.error('[CHECKOUT] Error:', err.message);
        res.status(500).json({ error: 'Error creating checkout session' });
    }
});

module.exports = router;
