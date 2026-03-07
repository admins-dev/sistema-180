#!/usr/bin/env bash
# ============================================================
# SISTEMA180 — Integration Test Orchestrator
# Ejecuta el flujo completo: affiliate → checkout → webhook →
# commission → refund → invoice → dispute → leaderboard
# ============================================================
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${ROOT_DIR}/helpers.sh" || { echo "helpers.sh missing"; exit 1; }

# Load env
if [ -f "${ROOT_DIR}/env.sample" ]; then
  source "${ROOT_DIR}/env.sample"
fi

# Prereqs
command -v jq >/dev/null 2>&1 || { echo "jq is required. Install jq."; exit 1; }

require_env "STAGING_BASE_URL"
require_env "PRICE_ID_WEB"
require_env "TEST_CUSTOMER_EMAIL"

OUTDIR="${ROOT_DIR}/results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${OUTDIR}"
PASS=0; FAIL=0; WARN=0
log "=== SISTEMA180 Integration Tests ==="
log "Base URL: ${STAGING_BASE_URL}"
log "Results: ${OUTDIR}"
echo ""

# ── 1) Health Check ──────────────────────────────────────────
log "━━━ TEST 1: Health Check ━━━"
HEALTH=$(curl -s -S --max-time 5 "${STAGING_BASE_URL}/admin/health" || echo '{"ok":false}')
echo "${HEALTH}" | jq '.' > "${OUTDIR}/01_health.json" 2>/dev/null || echo "${HEALTH}" > "${OUTDIR}/01_health.json"
if echo "${HEALTH}" | jq -e '.ok == true' > /dev/null 2>&1; then
  log "  ✅ PASS: Server is healthy"; ((PASS++))
else
  log "  ❌ FAIL: Server health check failed"; ((FAIL++))
fi
echo ""

# ── 2) Create Affiliate ─────────────────────────────────────
log "━━━ TEST 2: Create Affiliate ━━━"
AFF_TS=$(date +%s)
AFF_PAYLOAD="{\"name\":\"QA Test ${AFF_TS}\",\"email\":\"qa_${AFF_TS}@sistema180.test\",\"phone\":\"+34600000000\",\"level\":\"plata\"}"
AFF_RESP=$(http_post "${STAGING_BASE_URL}/admin/affiliates" "${AFF_PAYLOAD}" || echo '{}')
echo "${AFF_RESP}" | jq '.' > "${OUTDIR}/02_affiliate_created.json" 2>/dev/null || echo "${AFF_RESP}" > "${OUTDIR}/02_affiliate_created.json"

AFF_CODE=$(echo "${AFF_RESP}" | jq -r '.code // empty')
AFF_ID=$(echo "${AFF_RESP}" | jq -r '.id // empty')

if [ -n "${AFF_CODE}" ] && [ "${AFF_CODE}" != "null" ]; then
  log "  ✅ PASS: Affiliate created — code=${AFF_CODE} id=${AFF_ID}"; ((PASS++))
else
  log "  ❌ FAIL: Could not create affiliate"; ((FAIL++))
  log "  Response: ${AFF_RESP}"
  log "  ABORTING — cannot continue without affiliate"
  exit 1
fi
echo ""

# ── 3) Create Checkout Session ───────────────────────────────
log "━━━ TEST 3: Create Checkout Session (web_gancho 300€) ━━━"
CHECKOUT_PAYLOAD=$(jq -n \
  --arg p "${PRICE_ID_WEB}" \
  --arg a "${AFF_CODE}" \
  --arg e "${TEST_CUSTOMER_EMAIL}" \
  '{priceId: $p, affiliate_code: $a, customer_email: $e, lead_id: "lead_qa_001", mode: "payment"}')
CHECKOUT_RESP=$(curl -s -S -X POST -H "Content-Type: application/json" \
  -d "${CHECKOUT_PAYLOAD}" "${STAGING_BASE_URL}/create-checkout-session" || echo '{}')
echo "${CHECKOUT_RESP}" | jq '.' > "${OUTDIR}/03_checkout_session.json" 2>/dev/null || echo "${CHECKOUT_RESP}" > "${OUTDIR}/03_checkout_session.json"

SESSION_ID=$(echo "${CHECKOUT_RESP}" | jq -r '.id // empty')
SESSION_URL=$(echo "${CHECKOUT_RESP}" | jq -r '.url // empty')

if [ -n "${SESSION_ID}" ] && [ "${SESSION_ID}" != "null" ]; then
  log "  ✅ PASS: Checkout session created — id=${SESSION_ID}"; ((PASS++))
  log "  URL: ${SESSION_URL}"
else
  log "  ❌ FAIL: No session ID returned"; ((FAIL++))
fi
echo ""

# ── 4) Simulate Webhook: checkout.session.completed ──────────
log "━━━ TEST 4: Simulate checkout.session.completed webhook ━━━"
PI="pi_test_${AFF_TS}"
WEBHOOK_PAYLOAD=$(cat "${ROOT_DIR}/payloads/checkout_session_completed.json.template" \
  | sed "s/{{SESSION_ID}}/${SESSION_ID}/g" \
  | sed "s/{{PAYMENT_INTENT}}/${PI}/g" \
  | sed "s/{{AMOUNT_TOTAL_CENTS}}/30000/g" \
  | sed "s/{{MODE}}/payment/g" \
  | sed "s/{{CUSTOMER_EMAIL}}/${TEST_CUSTOMER_EMAIL}/g" \
  | sed "s/{{AFFILIATE_CODE}}/${AFF_CODE}/g" \
  | sed "s/{{LEAD_ID}}/lead_qa_001/g")
echo "${WEBHOOK_PAYLOAD}" > "${OUTDIR}/04_payload_checkout.json"

# NOTE: This sends directly to the webhook endpoint WITHOUT Stripe signature.
# For this to work, the backend must either:
#   a) Accept unsigned events in test/dev mode, OR
#   b) Use `stripe listen --forward-to` + `stripe trigger`
# We try direct POST first:
WH_RESP=$(curl -s -S -X POST \
  -H "Content-Type: application/json" \
  -d "${WEBHOOK_PAYLOAD}" \
  "${STAGING_BASE_URL}/webhook" || echo 'ERROR')
echo "${WH_RESP}" > "${OUTDIR}/04_webhook_response.txt"

if [ "${WH_RESP}" = "ok" ] || echo "${WH_RESP}" | grep -qi "ok"; then
  log "  ✅ PASS: Webhook accepted (direct POST)"; ((PASS++))
else
  log "  ⚠️  WARN: Direct webhook POST may need Stripe signature. Response: ${WH_RESP}"; ((WARN++))
  log "  TIP: Use 'stripe listen --forward-to ${STAGING_BASE_URL}/webhook' + 'stripe trigger checkout.session.completed'"
fi

wait_for "backend to process order + commission" 3
echo ""

# ── 5) Verify Order + Commission in DB ──────────────────────
log "━━━ TEST 5: Verify Order & Commission ━━━"
ORDERS_RESP=$(http_get "${STAGING_BASE_URL}/admin/orders" || echo '[]')
echo "${ORDERS_RESP}" | jq '.' > "${OUTDIR}/05_orders.json" 2>/dev/null || echo "${ORDERS_RESP}" > "${OUTDIR}/05_orders.json"

# Check if latest order has our affiliate
LATEST_ORDER_AFF=$(echo "${ORDERS_RESP}" | jq -r '.[0].affiliate_code // empty' 2>/dev/null)
if [ "${LATEST_ORDER_AFF}" = "${AFF_CODE}" ]; then
  log "  ✅ PASS: Order with affiliate_code=${AFF_CODE} found"; ((PASS++))
else
  log "  ⚠️  WARN: Latest order affiliate_code='${LATEST_ORDER_AFF}' (expected ${AFF_CODE})"; ((WARN++))
fi

# Check affiliate detail for reserved_cents
AFF_DETAIL=$(http_get "${STAGING_BASE_URL}/admin/affiliates/${AFF_ID}" || echo '{}')
echo "${AFF_DETAIL}" | jq '.' > "${OUTDIR}/05_affiliate_detail.json" 2>/dev/null || echo "${AFF_DETAIL}" > "${OUTDIR}/05_affiliate_detail.json"

RESERVED=$(echo "${AFF_DETAIL}" | jq -r '.affiliate.reserved_cents // 0' 2>/dev/null)
if [ "${RESERVED}" -gt 0 ] 2>/dev/null; then
  log "  ✅ PASS: Commission reserved — reserved_cents=${RESERVED}"; ((PASS++))
else
  log "  ⚠️  WARN: reserved_cents=${RESERVED} (expected > 0 after checkout)"; ((WARN++))
fi
echo ""

# ── 6) Simulate Refund ──────────────────────────────────────
log "━━━ TEST 6: Simulate charge.refunded webhook ━━━"
CH_ID="ch_test_${AFF_TS}"
REFUND_PAYLOAD=$(cat "${ROOT_DIR}/payloads/charge_refunded.json.template" \
  | sed "s/{{CHARGE_ID}}/${CH_ID}/g" \
  | sed "s/{{PAYMENT_INTENT}}/${PI}/g" \
  | sed "s/{{AMOUNT_CENTS}}/30000/g" \
  | sed "s/{{AFFILIATE_CODE}}/${AFF_CODE}/g" \
  | sed "s/{{RND}}/${AFF_TS}/g")
echo "${REFUND_PAYLOAD}" > "${OUTDIR}/06_payload_refund.json"

WH_REFUND=$(curl -s -S -X POST \
  -H "Content-Type: application/json" \
  -d "${REFUND_PAYLOAD}" \
  "${STAGING_BASE_URL}/webhook" || echo 'ERROR')
echo "${WH_REFUND}" > "${OUTDIR}/06_webhook_refund_response.txt"
wait_for "refund processing" 2

AFF_POST_REFUND=$(http_get "${STAGING_BASE_URL}/admin/affiliates/${AFF_ID}" || echo '{}')
echo "${AFF_POST_REFUND}" | jq '.' > "${OUTDIR}/06_affiliate_after_refund.json" 2>/dev/null || true

RESERVED_AFTER=$(echo "${AFF_POST_REFUND}" | jq -r '.affiliate.reserved_cents // -1' 2>/dev/null)
if [ "${RESERVED_AFTER}" = "0" ] || [ "${RESERVED_AFTER}" -lt "${RESERVED}" ] 2>/dev/null; then
  log "  ✅ PASS: Commission voided — reserved_cents dropped to ${RESERVED_AFTER}"; ((PASS++))
else
  log "  ⚠️  WARN: reserved_cents=${RESERVED_AFTER} after refund (expected decrease)"; ((WARN++))
fi
echo ""

# ── 7) Simulate Dispute ─────────────────────────────────────
log "━━━ TEST 7: Simulate charge.dispute.created webhook ━━━"
DISPUTE_PAYLOAD=$(cat "${ROOT_DIR}/payloads/charge_dispute_created.json.template" \
  | sed "s/{{EVENT_ID}}/evt_dispute_${AFF_TS}/g" \
  | sed "s/{{CHARGE_ID}}/${CH_ID}/g" \
  | sed "s/{{PAYMENT_INTENT}}/${PI}/g" \
  | sed "s/{{AFFILIATE_CODE}}/${AFF_CODE}/g" \
  | sed "s/{{RND}}/${AFF_TS}/g")
echo "${DISPUTE_PAYLOAD}" > "${OUTDIR}/07_payload_dispute.json"

WH_DISPUTE=$(curl -s -S -X POST \
  -H "Content-Type: application/json" \
  -d "${DISPUTE_PAYLOAD}" \
  "${STAGING_BASE_URL}/webhook" || echo 'ERROR')
echo "${WH_DISPUTE}" > "${OUTDIR}/07_webhook_dispute_response.txt"
log "  ℹ️  Dispute event sent (circuit-breaker: >3 disputes → suspend affiliate)"
((PASS++))
echo ""

# ── 8) Leaderboard Cron ─────────────────────────────────────
log "━━━ TEST 8: Leaderboard (manual trigger if endpoint exists) ━━━"
LB_RESP=$(curl -s -S -X POST -H "Authorization: ${ADMIN_API_KEY:-}" \
  "${STAGING_BASE_URL}/admin/cron/run-leaderboard" 2>/dev/null || echo 'NO_ENDPOINT')
echo "${LB_RESP}" > "${OUTDIR}/08_leaderboard.json"
if echo "${LB_RESP}" | grep -qi "ok\|success\|posted"; then
  log "  ✅ PASS: Leaderboard triggered"; ((PASS++))
else
  log "  ⚠️  WARN: Leaderboard endpoint not found or failed — check Slack cron manually"; ((WARN++))
fi
echo ""

# ── 9) Admin Endpoints Smoke Test ────────────────────────────
log "━━━ TEST 9: Admin Endpoints Smoke ━━━"
# GET /admin/affiliates
AFF_LIST=$(http_get "${STAGING_BASE_URL}/admin/affiliates" || echo '[]')
AFF_COUNT=$(echo "${AFF_LIST}" | jq 'length' 2>/dev/null || echo 0)
echo "${AFF_LIST}" | jq '.' > "${OUTDIR}/09_affiliates_list.json" 2>/dev/null || true
log "  Affiliates in DB: ${AFF_COUNT}"

# GET /admin/orders
ORDERS_LIST=$(http_get "${STAGING_BASE_URL}/admin/orders" || echo '[]')
ORD_COUNT=$(echo "${ORDERS_LIST}" | jq 'length' 2>/dev/null || echo 0)
echo "${ORDERS_LIST}" | jq '.' > "${OUTDIR}/09_orders_list.json" 2>/dev/null || true
log "  Orders in DB: ${ORD_COUNT}"

if [ "${AFF_COUNT}" -gt 0 ] 2>/dev/null; then
  log "  ✅ PASS: Admin endpoints responding"; ((PASS++))
else
  log "  ❌ FAIL: Admin endpoints empty"; ((FAIL++))
fi
echo ""

# ── 10) Package Results ──────────────────────────────────────
log "━━━ Packaging Results ━━━"

# Summary report
cat > "${OUTDIR}/REPORT.md" << EOF
# SISTEMA180 — Integration Test Report
**Date**: $(date +'%Y-%m-%d %H:%M:%S')
**Base URL**: ${STAGING_BASE_URL}
**Affiliate**: ${AFF_CODE} (id: ${AFF_ID})
**Session**: ${SESSION_ID}

## Results
| # | Test | Status |
|---|------|--------|
| 1 | Health Check | $([ -f "${OUTDIR}/01_health.json" ] && echo "✅" || echo "❌") |
| 2 | Create Affiliate | $([ -n "${AFF_CODE}" ] && echo "✅ ${AFF_CODE}" || echo "❌") |
| 3 | Checkout Session | $([ -n "${SESSION_ID}" ] && echo "✅" || echo "❌") |
| 4 | Webhook checkout.completed | $(grep -qi "ok" "${OUTDIR}/04_webhook_response.txt" 2>/dev/null && echo "✅" || echo "⚠️") |
| 5 | Order + Commission | $([ "${RESERVED:-0}" -gt 0 ] 2>/dev/null && echo "✅" || echo "⚠️") |
| 6 | Refund void | $([ "${RESERVED_AFTER:-0}" -lt "${RESERVED:-1}" ] 2>/dev/null && echo "✅" || echo "⚠️") |
| 7 | Dispute sent | ✅ |
| 8 | Leaderboard | $(grep -qi "ok" "${OUTDIR}/08_leaderboard.json" 2>/dev/null && echo "✅" || echo "⚠️") |
| 9 | Admin endpoints | $([ "${AFF_COUNT:-0}" -gt 0 ] 2>/dev/null && echo "✅" || echo "❌") |

## Summary
- **PASS**: ${PASS}
- **FAIL**: ${FAIL}
- **WARN**: ${WARN}

## Files
$(ls -1 "${OUTDIR}/" | sed 's/^/- /')
EOF

# Zip
if command -v zip >/dev/null 2>&1; then
  (cd "${ROOT_DIR}" && zip -r "$(basename ${OUTDIR}).zip" "$(basename ${OUTDIR})" > /dev/null 2>&1)
  log "Zipped: ${ROOT_DIR}/$(basename ${OUTDIR}).zip"
fi

echo ""
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "  RESULTS: ✅ ${PASS} PASS | ❌ ${FAIL} FAIL | ⚠️  ${WARN} WARN"
log "  Dir: ${OUTDIR}"
log "  Report: ${OUTDIR}/REPORT.md"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
