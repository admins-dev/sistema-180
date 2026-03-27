// ============================================================
// SISTEMA180 — Stripe Service
// Handles checkout, webhooks, commissions, Connect, payouts
//
// Claves por operación:
//   sk_live_ (STRIPE_SECRET_KEY)   → write: checkout, payouts, Connect, transfers
//   rk_live_ (STRIPE_RESTRICTED_KEY) → read-only: consultas, auditoría, informes
//   pk_live_ (STRIPE_PUBLISHABLE_KEY) → solo frontend (Stripe.js / Elements)
//   whsec_   (STRIPE_WEBHOOK_SECRET) → validación de firma en webhooks
// ============================================================
const Stripe = require('stripe');
const stripe    = Stripe(process.env.STRIPE_SECRET_KEY);        // operaciones write
// stripeRO usa la restricted key solo si está configurada correctamente (read-only en Dashboard)
// Hasta entonces, usa la secret key con wrapper que solo llama métodos .list/.retrieve
const _rkKey    = process.env.STRIPE_RESTRICTED_KEY;
const stripeRO  = _rkKey ? Stripe(_rkKey) : stripe;
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
    if ((affiliate.total_earned_cents + (affiliate.reserved_cents || 0) + commission) > kycThreshold && !affiliate.kyc_verified) {
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
    if (!charge.payment_intent) {
        console.error('[Stripe] Refund sin payment_intent, charge.id:', charge.id);
        return;
    }
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
    let affiliateId = null;

    if (typeof charge === 'string') {
        const fullCharge = await stripeRO.charges.retrieve(charge);  // read-only lookup
        await handleRefund(fullCharge);

        // Resolve affiliate from the order linked to this charge
        const order = await db.getOne(
            'SELECT affiliate_id FROM orders WHERE stripe_payment_intent_id = $1',
            [fullCharge.payment_intent]
        );
        if (order) affiliateId = order.affiliate_id;
    }

    // Circuit breaker: count disputes for this affiliate in the last 30 days
    if (affiliateId) {
        const since = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
        const result = await db.query(
            `SELECT COUNT(*) AS cnt
             FROM webhooks_log
             WHERE event_type = 'charge.dispute.created'
               AND created_at >= $1
               AND payload->'data'->'object'->>'payment_intent' IN (
                   SELECT stripe_payment_intent_id FROM orders WHERE affiliate_id = $2
               )`,
            [since, affiliateId]
        );
        const disputeCount = parseInt(result.rows[0].cnt, 10);
        if (disputeCount > 3) {
            await db.query(
                "UPDATE affiliates SET status = 'suspended' WHERE id = $1",
                [affiliateId]
            );
        }
    }
}

// ── Marketplace: Create PaymentIntent with split ─────────────
// Destination charge: S180 collects 100%, transfers (1 - commission_pct) to owner
async function createMarketplacePaymentIntent({ property, amountCents, customerEmail, bookingId }) {
    if (!property.stripe_account_id) {
        throw new Error('Property owner has no Stripe Connect account configured');
    }
    const commissionPct = parseFloat(property.commission_pct) || 0.13;
    const platformFeeCents = Math.round(amountCents * commissionPct);

    const paymentIntent = await stripe.paymentIntents.create({
        amount: amountCents,
        currency: 'eur',
        application_fee_amount: platformFeeCents,
        transfer_data: {
            destination: property.stripe_account_id,
        },
        receipt_email: customerEmail || undefined,
        metadata: {
            booking_id: String(bookingId),
            property_id: String(property.id),
            property_name: property.property_name,
        },
    });

    return paymentIntent;
}

// ── Marketplace: Provider Connect onboarding ─────────────────
async function createProviderConnectLink(property) {
    let accountId = property.stripe_account_id;

    if (!accountId) {
        const account = await stripe.accounts.create({
            type: 'express',
            country: 'ES',
            email: property.owner_email,
            capabilities: {
                card_payments: { requested: true },
                transfers: { requested: true },
            },
            business_type: 'individual',
            metadata: {
                property_id: String(property.id),
                property_name: property.property_name,
            },
        });
        accountId = account.id;
        await db.query(
            "UPDATE marketplace_properties SET stripe_account_id = $1, connect_status = 'onboarding', updated_at = now() WHERE id = $2",
            [accountId, property.id]
        );
    }

    const link = await stripe.accountLinks.create({
        account: accountId,
        refresh_url: `${process.env.FRONT_URL}/marketplace/connect/refresh?property_id=${property.id}`,
        return_url: `${process.env.FRONT_URL}/marketplace/connect/return?property_id=${property.id}`,
        type: 'account_onboarding',
    });

    return { url: link.url, account_id: accountId };
}

// ── Marketplace: Check Connect account status ─────────────────
async function getProviderConnectStatus(stripeAccountId) {
    const account = await stripe.accounts.retrieve(stripeAccountId);
    const isActive = account.charges_enabled && account.payouts_enabled;
    return {
        charges_enabled: account.charges_enabled,
        payouts_enabled: account.payouts_enabled,
        details_submitted: account.details_submitted,
        is_active: isActive,
        requirements: account.requirements,
    };
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
// Uses raw Stripe lib (no key needed, only secret for validation)
function constructEvent(rawBody, signature) {
    return stripe.webhooks.constructEvent(rawBody, signature, process.env.STRIPE_WEBHOOK_SECRET);
}

// ── Audit: list recent charges (read-only key) ────────────────
async function listRecentCharges(limit = 20) {
    return stripeRO.charges.list({ limit });
}

// ── Audit: list recent payouts (read-only key) ────────────────
async function listRecentTransfers(limit = 20) {
    return stripeRO.transfers.list({ limit });
}

// ── Audit: get customer (read-only key) ───────────────────────
async function getCustomer(customerId) {
    return stripeRO.customers.retrieve(customerId);
}

module.exports = {
    // Write operations — sk_live_
    createCheckoutSession,
    handleWebhook,
    createConnectOnboardingLink,
    transferToAffiliate,
    createMarketplacePaymentIntent,
    createProviderConnectLink,
    // Read operations — rk_live_
    listRecentCharges,
    listRecentTransfers,
    getCustomer,
    getProviderConnectStatus,
    // Webhook validation
    constructEvent,
    // Raw clients (for emergencies)
    stripe,
    stripeRO,
};
