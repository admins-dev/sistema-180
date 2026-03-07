require('dotenv').config();
const { Pool } = require('pg');
const fs = require('fs');

async function migrate() {
    const pool = new Pool({ connectionString: process.env.DATABASE_URL });
    try {
        const sql = fs.readFileSync('src/migrations/001_init.sql', 'utf8');
        await pool.query(sql);
        console.log('MIGRATION OK - Tables created');

        const tables = await pool.query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
        );
        console.log('\nTables:');
        tables.rows.forEach(r => console.log('  -', r.table_name));

        const config = await pool.query('SELECT * FROM system_config');
        console.log('\nConfig:');
        config.rows.forEach(r => console.log(' ', r.key, '=', r.value));

        console.log('\nDONE - ' + tables.rows.length + ' tables in database');
    } catch (err) {
        console.error('ERROR:', err.message);
    } finally {
        await pool.end();
    }
}

migrate();
