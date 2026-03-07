const { Pool } = require('pg');

let pool = null;
let dbAvailable = false;

function getPool() {
    if (!pool && process.env.DATABASE_URL) {
        pool = new Pool({ connectionString: process.env.DATABASE_URL });
        pool.on('error', (err) => {
            console.warn('[DB] Pool error (non-fatal):', err.message);
            dbAvailable = false;
        });
        // Test connection
        pool.query('SELECT 1').then(() => {
            dbAvailable = true;
            console.log('[DB] Connected to PostgreSQL');
        }).catch((err) => {
            console.warn('[DB] Cannot connect to PostgreSQL:', err.message);
            console.warn('[DB] Server will run without DB — API calls requiring DB will fail gracefully');
            dbAvailable = false;
        });
    }
    return pool;
}

async function safeQuery(text, params) {
    const p = getPool();
    if (!p) {
        console.warn('[DB] No DATABASE_URL configured, skipping query');
        return { rows: [], rowCount: 0 };
    }
    try {
        return await p.query(text, params);
    } catch (err) {
        console.error('[DB] Query error:', err.message);
        throw err;
    }
}

module.exports = {
    query: safeQuery,
    get pool() { return getPool(); },
    get isAvailable() { return dbAvailable; },

    // Helper: get single row
    async getOne(text, params) {
        const res = await safeQuery(text, params);
        return res.rows[0] || null;
    },

    // Helper: get affiliate by code
    async getAffiliateByCode(code) {
        if (!code) return null;
        return this.getOne('SELECT * FROM affiliates WHERE code = $1 AND status != $2', [code, 'suspended']);
    },

    // Helper: get config value
    async getConfig(key) {
        const row = await this.getOne('SELECT value FROM system_config WHERE key = $1', [key]);
        return row ? row.value : null;
    }
};
