// ============================================================
// SISTEMA180 — Slack Service
// Alerts, leaderboard, payout notifications
// ============================================================
const { WebClient } = require('@slack/web-api');

let web = null;
function getClient() {
    if (!web && process.env.SLACK_BOT_TOKEN) {
        web = new WebClient(process.env.SLACK_BOT_TOKEN);
        console.log('[SLACK] Client initialized');
    }
    if (!web) {
        console.warn('[SLACK] No SLACK_BOT_TOKEN configured — notifications disabled');
    }
    return web;
}

const CHANNELS = {
    alerts: process.env.SLACK_AFFILIATION_ALERTS || '#afiliacion-alerts',
    ranking: process.env.SLACK_AFFILIATION_RANKING || '#afiliados-ranking',
    payouts: process.env.SLACK_OPS_PAYOUTS || '#ops-payouts'
};

// ── Post sale alert ──────────────────────────────────────────
async function postAffiliateSale(affiliate, order, commissionCents) {
    try {
        const client = getClient(); if (!client) return;
        await client.chat.postMessage({
            channel: CHANNELS.alerts,
            blocks: [
                {
                    type: 'section',
                    text: {
                        type: 'mrkdwn',
                        text: `🎉 *Nueva venta* | \`${order.product_type}\`\n` +
                            `• Afiliado: *${affiliate.name || affiliate.code}* (${affiliate.level})\n` +
                            `• Importe: *${(order.amount_cents / 100).toFixed(2)}€*\n` +
                            `• Comisión reservada: *${(commissionCents / 100).toFixed(2)}€*\n` +
                            `• Order ID: ${order.id}`
                    }
                }
            ],
            text: `Nueva venta: ${order.product_type} — Affiliate: ${affiliate.code} — Comisión: ${(commissionCents / 100).toFixed(2)}€`
        });
    } catch (err) {
        console.error('[SLACK] Error posting sale alert:', err.message);
    }
}

// ── Post leaderboard ─────────────────────────────────────────
async function postLeaderboard(rows, period = '7 días') {
    try {
        let text = `📊 *Leaderboard — últimos ${period}*\n\n`;
        rows.forEach((r, i) => {
            const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`;
            text += `${medal} *${r.name || r.code}* — ${r.sales} ventas — ${(r.revenue / 100).toFixed(2)}€ comisiones\n`;
        });
        if (rows.length === 0) text += '_No hay ventas en este periodo._';

        const client = getClient(); if (!client) return;
        await client.chat.postMessage({ channel: CHANNELS.ranking, text });
    } catch (err) {
        console.error('[SLACK] Error posting leaderboard:', err.message);
    }
}

// ── Post payout notification ─────────────────────────────────
async function postPayoutNotification(affiliate, amountCents, transferId, status) {
    try {
        const emoji = status === 'completed' ? '✅' : status === 'failed' ? '❌' : '⏳';
        const client = getClient(); if (!client) return;
        await client.chat.postMessage({
            channel: CHANNELS.payouts,
            text: `${emoji} *Payout ${status}*\n` +
                `• Afiliado: ${affiliate.name || affiliate.code}\n` +
                `• Importe: ${(amountCents / 100).toFixed(2)}€\n` +
                `• Transfer ID: ${transferId || 'N/A'}`
        });
    } catch (err) {
        console.error('[SLACK] Error posting payout:', err.message);
    }
}

// ── Post refund alert ────────────────────────────────────────
async function postRefundAlert(order) {
    try {
        const client = getClient(); if (!client) return;
        await client.chat.postMessage({
            channel: CHANNELS.alerts,
            text: `⚠️ *Reembolso/Disputa* — Order ${order.id} — ${(order.amount_cents / 100).toFixed(2)}€ — Comisiones anuladas`
        });
    } catch (err) {
        console.error('[SLACK] Error posting refund alert:', err.message);
    }
}

// ── Post KYC alert ───────────────────────────────────────────
async function postKYCAlert(affiliate) {
    try {
        const client = getClient(); if (!client) return;
        await client.chat.postMessage({
            channel: CHANNELS.payouts,
            text: `🔐 *KYC requerido* — Afiliado ${affiliate.name || affiliate.code} (${affiliate.code}) ha superado el umbral. Verificar documentación.`
        });
    } catch (err) {
        console.error('[SLACK] Error posting KYC alert:', err.message);
    }
}

module.exports = { postAffiliateSale, postLeaderboard, postPayoutNotification, postRefundAlert, postKYCAlert };
