// ============================================================
// SISTEMA180 — Backend Server
// ============================================================
require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');

// Routes
const checkout = require('./routes/checkout');
const webhook = require('./routes/webhook');
const admin = require('./routes/admin');
const avatars = require('./routes/avatars');
const cron = require('./cron/jobs');

const path = require('path');
const app = express();

// ── Static files (dashboard, assets) ─────────────────────────
app.use(express.static(path.join(__dirname, '..', 'public')));
app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'public', 'dashboard.html'));
});

// ── Webhook route MUST use raw body (before json parser) ─────
app.use('/webhook', webhook);

// ── Standard middleware ──────────────────────────────────────
app.use(bodyParser.json());
app.use(cookieParser(process.env.COOKIE_SECRET));

// ── Affiliate cookie tracking middleware ─────────────────────
app.use((req, res, next) => {
    // Capture affiliate code from URL param ?af=AF-XXXXXX
    const af = req.query.af;
    if (af && af.startsWith('AF-')) {
        const days = parseInt(process.env.AFFILIATE_COOKIE_DAYS || '30');
        res.cookie('affiliate_code', af, {
            maxAge: days * 24 * 60 * 60 * 1000,
            httpOnly: true,
            sameSite: 'lax'
        });
    }
    next();
});

// ── Routes ───────────────────────────────────────────────────
app.use('/create-checkout-session', checkout);
app.use('/admin', admin);
app.use('/api/avatars', avatars);

// ── Start ────────────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`[SISTEMA180] Server running on port ${PORT}`);
    console.log(`[SISTEMA180] Environment: ${process.env.NODE_ENV || 'development'}`);
    cron.start();
});
