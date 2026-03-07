// ============================================================
// SISTEMA180 — Stripe Service
// Handles checkout, webhooks, commissions, Connect, payouts
// ============================================================
const Stripe = require('stripe');
const stripe = Stripe(process.env.STRIPE_KEY);
const db = require('../db');
const slack = require('./slackService');

// Commission rates by affiliate level
const COMMISSION_RATES = {
    bronce: 0.20,   // 20% (~60€ on 300€ web)
    plata: 0.33,   // 33% (~100€ on 300€ web) — current default
    gold: 0.40    // 40%
};

// ── Create Checkout Session ──────────────────────────────────
async function createCheckoutSession({ priceId, affiliate_code, customer_email, lead_id, mode }) {
    const params = {
        payment_method_types: ['card'],
        mode: mode || 'payment',
        line_items: [{ price: priceId, quantity: 1 }],
        success_url: `${process.env.FRONT_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${process.env.FRONT_URL}/cancel`,
        customer_email: customer_email || undefined,
        metadata: {}
    };
    if (affiliate_code) params.metadata.affiliate_code = affiliate_code;
    if (lead_id) params.client_reference_id = lead_id;
    const session = await stripe.checkout.sessions.create(params);
    return session;
}

// ── Handle Webhook Events ────────────────────────────────────
async function handleWebhook(event) {
    switch (event.type) {
        case 'checkout.session.completed':
            await handleCheckoutCompleted(event.data.object);
            break;
        case 'invoice.paid':
            await handleInvoicePaid(event.data.object);
            break;
        case 'charge.refunded':
            await handleRefund(event.data.object);
            break;
        case 'charge.dispute.created':
            await handleDispute(event.data.object);
            break;
        default:
            console.log(`[STRIPE] Unhandled event: ${event.type}`);
    }
}

// ── Checkout Completed ───────────────────────────────────────
async function handleCheckoutCompleted(session) {
    const affiliate_code = session.metadata?.affiliate_code || null;
    const affiliate = affiliate_code ? await db.getAffiliateByCode(affiliate_code) : null;
    const amount = session.amount_total || 0;
    const product_type = session.mode === 'subscription' ? 'subscription' : 'web';

    // Create order
    const orderRes = await db.query(
        `INSERT INTO orders (stripe_payment_intent_id, stripe_checkout_session_id, stripe_subscription_id,
     affiliate_id, customer_email, amount_cents, currency, product_type, status, metadata)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) RETURNING *`,
        [
            session.payment_intent, session.id, session.subscription || null,
            affiliate ? affiliate.id : null, session.customer_email || '',
            amount, session.currency || 'eur', product_type, 'paid', JSON.stringify(session)
        ]
    );
    const order = orderRes.rows[0];

    // Reserve commission if affiliate
    if (affiliate) {
        await reserveCommission(affiliate, order);
    }
}

// ── Reserve Commission (14-day hold) ─────────────────────────
async function reserveCommission(affiliate, order) {
    const holdDays = parseInt(await db.getConfig('commission_hold_days') || '14');
    const rate = COMMISSION_RATES[affiliate.level] || COMMISSION_RATES.plata;
    const commission = Math.round(order.amount_cents * rate);
    const reserved_until = new Date(Date.now() + holdDays * 24 * 60 * 60 * 1000);

    await db.query(
        `INSERT INTO affiliate_commissions (affiliate_id, order_id, commission_cents, commission_pct, status, reserved_until)
     VALUES ($1,$2,$3,$4,$5,$6)`,
        [affiliate.id, order.id, commission, rate, 'reserved', reserved_until]
    );

    await db.query(
        'UPDATE affiliates SET reserved_cents = reserved_cents + $1, total_sales = total_sales + 1 WHERE id = $2',
        [commission, affiliate.id]
    );

    // Slack alert
    await slack.postAffiliateSale(affiliate, order, commission);

    // Check KYC threshold
    const kycThreshold = parseInt(await db.getConfig('kyc_threshold_cents') || '200000');
    if (affiliate.total_earned_cents + commission > kycThreshold && !affiliate.kyc_verified) {
        await db.query("UPDATE affiliates SET status = 'kyc_required' WHERE id = $1", [affiliate.id]);
        await slack.postKYCAlert(affiliate);
    }
}

// ── Invoice Paid (subscription renewal) ──────────────────────
async function handleInvoicePaid(invoice) {
    // Only process if has affiliate metadata from original checkout
    if (invoice.subscription) {
        const existing = await db.getOne(
            'SELECT affiliate_id FROM orders WHERE stripe_subscription_id = $1 LIMIT 1',
            [invoice.subscription]
        );
        if (existing && existing.affiliate_id) {
            const affiliate = await db.getOne('SELECT * FROM affiliates WHERE id = $1', [existing.affiliate_id]);
            if (affiliate) {
                const orderRes = await db.query(
                    `INSERT INTO orders (stripe_payment_intent_id, affiliate_id, customer_email, amount_cents,
           currency, product_type, status, stripe_subscription_id)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING *`,
                    [invoice.payment_intent, affiliate.id, invoice.customer_email,
                    invoice.amount_paid, invoice.currency, 'subscription_renewal', 'paid', invoice.subscription]
                );
                // Commission on renewal (same rate)
                await reserveCommission(affiliate, orderRes.rows[0]);
            }
        }
    }
}

// ── Refund → Void Commission ─────────────────────────────────
async function handleRefund(charge) {
    const order = await db.getOne(
        'SELECT * FROM orders WHERE stripe_payment_intent_id = $1', [charge.payment_intent]
    );
    if (order) {
        await db.query("UPDATE orders SET status = 'refunded' WHERE id = $1", [order.id]);
        // Void reserved commissions
        const comms = await db.query(
            "SELECT * FROM affiliate_commissions WHERE order_id = $1 AND status = 'reserved'", [order.id]
        );
        for (const c of comms.rows) {
            await db.query("UPDATE affiliate_commissions SET status = 'void' WHERE id = $1", [c.id]);
            await db.query('UPDATE affiliates SET reserved_cents = reserved_cents - $1 WHERE id = $2',
                [c.commission_cents, c.affiliate_id]);
        }
        if (order.affiliate_id) {
            await slack.postRefundAlert(order);
        }
    }
}

// ── Dispute → Void + Circuit Breaker ─────────────────────────
async function handleDispute(dispute) {
    // Similar to refund but also check for fraud patterns
    const charge = dispute.charge;
    if (typeof charge === 'string') {
        const fullCharge = await stripe.charges.retrieve(charge);
        await handleRefund(fullCharge);
    }
    // Circuit breaker: check if affiliate has >3 disputes in 30 days
    // If so, suspend affiliate
    // (implemented in affiliateService.checkFraud)
}

// ── Stripe Connect: Create onboarding link ───────────────────
async function createConnectOnboardingLink(affiliate) {
    const account = await stripe.accounts.create({
        type: 'express',
        country: affiliate.country || 'ES',
        email: affiliate.email,
        metadata: { affiliate_code: affiliate.code }
    });

    await db.query('UPDATE affiliates SET stripe_account_id = $1 WHERE id = $2',
        [account.id, affiliate.id]);

    const link = await stripe.accountLinks.create({
        account: account.id,
        refresh_url: `${process.env.FRONT_URL}/connect/refresh`,
        return_url: `${process.env.FRONT_URL}/connect/return?code=${affiliate.code}`,
        type: 'account_onboarding',
    });
    return link.url;
}

// ── Transfer payout to connected account ─────────────────────
async function transferToAffiliate(affiliate, amountCents) {
    if (!affiliate.stripe_account_id) {
        throw new Error(`Affiliate ${affiliate.code} has no Stripe Connect account`);
    }

    const transfer = await stripe.transfers.create({
        amount: amountCents,
        currency: 'eur',
        destination: affiliate.stripe_account_id,
        transfer_group: `affiliate_${affiliate.id}`,
        metadata: { affiliate_code: affiliate.code }
    });

    return transfer;
}

// ── Construct webhook event ──────────────────────────────────
function constructEvent(rawBody, signature) {
    return stripe.webhooks.constructEvent(rawBody, signature, process.env.STRIPE_WEBHOOK_SECRET);
}

module.exports = {
    createCheckoutSession,
    handleWebhook,
    createConnectOnboardingLink,
    transferToAffiliate,
    constructEvent,
    stripe
};
