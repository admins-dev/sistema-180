// ============================================================
// SISTEMA180 — Cron Jobs
// Daily leaderboard + commission settlement
// ============================================================
const cron = require('node-cron');
const db = require('../db');
const slack = require('../services/slackService');

function start() {
    // ── Daily leaderboard at 08:00 CET ─────────────────────────
    cron.schedule('0 8 * * *', async () => {

        console.log('[CRON] Running daily leaderboard...');
        try {
            const res = await db.query(`
        SELECT a.id, a.name, a.code,
               COUNT(o.id) AS sales,
               COALESCE(SUM(ac.commission_cents), 0) AS revenue
        FROM affiliates a
        LEFT JOIN orders o ON o.affiliate_id = a.id AND o.created_at > now() - interval '7 days'
        LEFT JOIN affiliate_commissions ac ON ac.order_id = o.id
        GROUP BY a.id
        HAVING COUNT(o.id) > 0
        ORDER BY sales DESC LIMIT 10
      `);
            await slack.postLeaderboard(res.rows, '7 días');
        } catch (err) {
            console.error('[CRON] Leaderboard error:', err.message);
        }
    });

    // ── Hourly commission settlement ───────────────────────────
    // Settle commissions past their hold period
    cron.schedule('0 * * * *', async () => {
        try {
            const res = await db.query(`
        SELECT ac.*, a.code, a.name
        FROM affiliate_commissions ac
        JOIN affiliates a ON a.id = ac.affiliate_id
        WHERE ac.status = 'reserved' AND ac.reserved_until <= now()
      `);

            for (const comm of res.rows) {
                await db.query("UPDATE affiliate_commissions SET status = 'settled', settled_at = now() WHERE id = $1", [comm.id]);
                await db.query(`
          UPDATE affiliates SET
            balance_cents = balance_cents + $1,
            reserved_cents = reserved_cents - $1,
            total_earned_cents = total_earned_cents + $1
          WHERE id = $2
        `, [comm.commission_cents, comm.affiliate_id]);
            }

            if (res.rows.length > 0) {
                console.log(`[CRON] Settled ${res.rows.length} commissions`);
            }
        } catch (err) {
            console.error('[CRON] Settlement error:', err.message);
        }
    });

    console.log('[CRON] Jobs scheduled: leaderboard (08:00 daily), settlement (hourly)');
}

module.exports = { start };
