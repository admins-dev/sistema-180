// SISTEMA180 — QA Integration Tests
// Runs all 8 test scenarios against the live staging backend
require('dotenv').config();
const BASE = 'http://localhost:3000';

async function request(method, path, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${BASE}${path}`, opts);
    const text = await res.text();
    try { return { status: res.status, data: JSON.parse(text) }; }
    catch { return { status: res.status, data: text }; }
}

let pass = 0, fail = 0;
function ok(name, cond, detail = '') {
    if (cond) { pass++; console.log(`  PASS  ${name}${detail ? ' — ' + detail : ''}`); }
    else { fail++; console.log(`  FAIL  ${name}${detail ? ' — ' + detail : ''}`); }
}

async function run() {
    console.log('==============================================');
    console.log(' SISTEMA180 — QA Integration Tests');
    console.log(' Target: ' + BASE);
    console.log(' Time: ' + new Date().toISOString());
    console.log('==============================================\n');

    // ── TEST 1: Health Check ──────────────────────────────────
    console.log('TEST 1: Health Check');
    const h = await request('GET', '/admin/health');
    ok('Health endpoint returns 200', h.status === 200);
    ok('Health returns ok: true', h.data?.ok === true);

    // ── TEST 2: Create Affiliate → AF-XXXXXX ─────────────────
    console.log('\nTEST 2: Create Affiliate');
    const ts = Date.now();
    const af = await request('POST', '/admin/affiliates', {
        name: `QA Test ${ts}`, email: `qa-${ts}@test.com`, phone: '+34600000001'
    });
    ok('Create returns 200', af.status === 200);
    ok('Has AF- code', af.data?.code?.startsWith('AF-'), af.data?.code);
    ok('Level is plata', af.data?.level === 'plata');
    ok('Status is active', af.data?.status === 'active');
    ok('Balance starts at 0', af.data?.balance_cents === 0);
    const affiliateId = af.data?.id;
    const affiliateCode = af.data?.code;

    // ── TEST 3: List Affiliates ──────────────────────────────
    console.log('\nTEST 3: List Affiliates');
    const list = await request('GET', '/admin/affiliates');
    ok('List returns 200', list.status === 200);
    ok('List is array', Array.isArray(list.data));
    ok('Contains our affiliate', list.data?.some(a => a.code === affiliateCode), `Found ${affiliateCode} in list of ${list.data?.length}`);

    // ── TEST 4: Get Affiliate Detail ─────────────────────────
    console.log('\nTEST 4: Affiliate Detail');
    const det = await request('GET', `/admin/affiliates/${affiliateId}`);
    ok('Detail returns 200', det.status === 200);
    ok('Has affiliate object', det.data?.affiliate?.id === affiliateId);
    ok('Has commissions array', Array.isArray(det.data?.commissions));
    ok('Email matches', det.data?.affiliate?.email === `qa-${ts}@test.com`);

    // ── TEST 5: Checkout Session ──────────────────────────────
    console.log('\nTEST 5: Checkout Session with Affiliate');
    const checkout = await request('POST', '/create-checkout-session', {
        priceId: 'price_1T7yxaCetqXM41XwJOMq3X26',
        affiliate_code: affiliateCode,
        customer_email: 'customer@test.com',
        mode: 'payment'
    });
    ok('Checkout returns 200', checkout.status === 200);
    ok('Has session URL', checkout.data?.url?.includes('checkout.stripe.com'), checkout.data?.url?.substring(0, 60));
    ok('Has session ID', checkout.data?.id?.startsWith('cs_test'), checkout.data?.id?.substring(0, 20));

    // ── TEST 6: Payout without balance → Error ───────────────
    console.log('\nTEST 6: Payout with Zero Balance (should fail)');
    const payout = await request('POST', `/admin/affiliates/${affiliateId}/payout`, {});
    ok('Returns 400 (no balance)', payout.status === 400);
    ok('Error message correct', payout.data?.error?.includes('No balance'), payout.data?.error);

    // ── TEST 7: Toggle Payouts Config ────────────────────────
    console.log('\nTEST 7: Config Toggle');
    const disable = await request('POST', '/admin/config/payouts', { enabled: false });
    ok('Disable payouts returns 200', disable.status === 200);
    ok('Payouts disabled', disable.data?.payouts_enabled === false);

    // Try payout while disabled
    const blocked = await request('POST', `/admin/affiliates/${affiliateId}/payout`, {});
    ok('Payout blocked when disabled', blocked.status === 403);
    ok('Error says payouts disabled', blocked.data?.error?.includes('Payouts disabled'), blocked.data?.error);

    // Re-enable
    const enable = await request('POST', '/admin/config/payouts', { enabled: true });
    ok('Re-enable payouts returns 200', enable.status === 200);
    ok('Payouts re-enabled', enable.data?.payouts_enabled === true);

    // ── TEST 8: List Orders ──────────────────────────────────
    console.log('\nTEST 8: Orders & Webhook Log');
    const orders = await request('GET', '/admin/orders');
    ok('Orders endpoint returns 200', orders.status === 200);
    ok('Orders is array', Array.isArray(orders.data));

    // ── RESULTS ──────────────────────────────────────────────
    console.log('\n==============================================');
    console.log(` RESULTS: ${pass} PASSED, ${fail} FAILED, ${pass + fail} TOTAL`);
    console.log('==============================================');

    if (fail > 0) process.exit(1);
}

run().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
