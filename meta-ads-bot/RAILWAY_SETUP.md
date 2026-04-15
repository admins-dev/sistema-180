# RAILWAY DEPLOYMENT — Sistema 180 Meta Ads Bot

## Quick Start (5 minutes)

### Option 1: Web UI (Easiest)

1. **Go to https://railway.app**
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Select your repo: `admins-dev/sistema-180`
4. Railway auto-detects Python → shows service setup
5. Click **"Add Service"** and configure:
   - **Service name**: `meta-ads-bot`
   - **Root directory**: `meta-ads-bot`
   - **Start command**: leave empty (reads from Procfile)
6. Click **"Variables"** and add from `.env.example`:
   - `META_ACCESS_TOKEN=<your_token>`
   - `TELEGRAM_BOT_TOKEN=<your_token>`
   - `META_AD_ACCOUNT_ID=act_XXXXXX`
   - `FLASK_ENV=production`
   - `TELEGRAM_ALLOWED_USER_IDS=<your_id>`
7. Click **"Deploy"** (takes 2-3 minutes)
8. Copy the generated URL: `https://<name>.railway.app`

### Option 2: CLI (Faster if you have Railway CLI)

```bash
cd /home/jose/proyectos/sistema-180/meta-ads-bot

# Login
railway login

# Create project
railway init --name "sistema-180-meta-ads"

# Set variables
railway variables set META_ACCESS_TOKEN=<token>
railway variables set TELEGRAM_BOT_TOKEN=<token>
railway variables set META_AD_ACCOUNT_ID=act_XXXXX
railway variables set FLASK_ENV=production
railway variables set TELEGRAM_ALLOWED_USER_IDS=<your_id>

# Deploy
railway up
```

---

## Configuration Details

### 1. Get Your Tokens

#### Meta Access Token
- Go to https://developers.facebook.com/apps
- Select your app
- Go to **Settings** → **Basic**
- Scroll down to **App Roles** → **Generate New Token**
- Permissions needed: `ads_read`, `ads_management`
- Copy token (valid for 60 days)

#### Telegram Bot Token
- Open Telegram
- Message @BotFather
- Send `/newbot`
- Follow prompts (name: "Sistema 180 Ads Bot")
- Copy token (format: `123456:ABC-DEF...`)

#### Your Telegram User ID
- Open Telegram
- Message @userinfobot
- Send `/start`
- It returns your user ID (e.g., `123456789`)
- This goes in `TELEGRAM_ALLOWED_USER_IDS`

#### Meta Ad Account ID
- Go to https://ads.facebook.com
- Settings → Ad Account
- Copy the ID (format: `act_XXXXXXXXX`)

---

## Security Checklist

Before deploying, verify:

- [ ] `.env` is in `.gitignore` (never commit secrets)
- [ ] `FLASK_ENV=production` (disables debug mode)
- [ ] `TELEGRAM_ALLOWED_USER_IDS` set to your ID only
- [ ] All tokens in Railway **Variables**, not hardcoded
- [ ] `FLASK_API_SECRET` auto-generated (or use strong random string)
- [ ] HTTPS enabled (Railway provides automatically)

---

## Verify Deployment

### 1. Health Check

```bash
curl https://<your-url>.railway.app/health

# Expected response:
# {"status":"ok","service":"meta-ads-bot"}
```

### 2. API Status (requires API key)

```bash
API_KEY=$(echo $FLASK_API_SECRET | head -c 16)
curl -H "X-API-Key: $API_KEY" \
  https://<your-url>.railway.app/api/meta-ads/status

# Expected response:
# {"active":true,"lastSync":null,"totalCampaigns":0}
```

### 3. Telegram Bot

- Open Telegram
- Search for your bot (e.g., @Sistema180AdsBot)
- Send `/start`
- Should respond with welcome message

### 4. View Logs

In Railway dashboard:
- Select your project
- Click **"Logs"** tab
- Should see startup messages like:
  ```
  INFO:__main__:🚀 Iniciando Flask server en puerto 5000
  INFO:__main__:Debug mode: False
  INFO:__main__:API Key para acceso: <first_16_chars>...
  INFO:__main__:Bot Meta Ads iniciado. Esperando comandos...
  ```

---

## Troubleshooting

### Error: "Connection refused"
- **Cause**: Flask server didn't start
- **Fix**: Check Logs tab, look for Python errors
- **Action**: Update requirements.txt, redeploy

### Error: "ModuleNotFoundError: nlp"
- **Cause**: Missing Python modules
- **Fix**: Update `requirements.txt` with all dependencies
- **Action**: `pip freeze > requirements.txt` in meta-ads-bot folder

### Error: "TELEGRAM_BOT_TOKEN not found"
- **Cause**: Variable not set in Railway
- **Fix**: Go to Variables, add `TELEGRAM_BOT_TOKEN=<token>`
- **Action**: Trigger redeploy after adding

### Error: "Meta API 400: Invalid token"
- **Cause**: Token expired or invalid permissions
- **Fix**: Regenerate from https://developers.facebook.com/
- **Action**: Update `META_ACCESS_TOKEN` in Railway Variables

### Telegram bot doesn't respond
- **Cause**: User ID not in allowed list
- **Fix**: Add your ID to `TELEGRAM_ALLOWED_USER_IDS`
- **Action**: Check logs for "Unauthorized" messages

---

## Advanced: Webhooks

After deployment is live, configure Meta webhooks:

1. Go to https://developers.facebook.com/apps
2. Your app → **Webhooks** → **Edit**
3. Set callback URL: `https://<your-url>.railway.app/webhooks/graph-api`
4. Verify token: (set in `WEBHOOK_VERIFY_TOKEN`)
5. Subscribe to: `campaigns`, `adsets`, `ads`
6. Click **"Verify and Save"**

---

## Environment Variables Reference

| Variable | Example | Notes |
|----------|---------|-------|
| `META_ACCESS_TOKEN` | `abc123...` | From developers.facebook.com (60 day expiry) |
| `META_AD_ACCOUNT_ID` | `act_123456789` | From Ads Manager settings |
| `META_PIXEL_ID` | `123456789` | From Events Manager |
| `TELEGRAM_BOT_TOKEN` | `123:ABC...` | From @BotFather |
| `TELEGRAM_ALLOWED_USER_IDS` | `123456,789012` | Comma-separated, no spaces |
| `FLASK_ENV` | `production` | Set to production (never development) |
| `FLASK_DEBUG` | `false` | Always false in production |
| `FLASK_API_SECRET` | auto-generated | Auto-generated if empty (optional override) |
| `WEBHOOK_URL` | `https://<name>.railway.app` | Your Railway URL |

---

## Monitoring & Alerts

### Set Up Uptime Monitoring

1. Go to https://uptimerobot.com
2. Create monitor:
   - URL: `https://<your-url>.railway.app/health`
   - Check interval: 5 minutes
   - Alert threshold: 2 failures
3. Get alerts if deployment goes down

### View Metrics in Railway

- Dashboard → your project → **Metrics** tab
- Monitor CPU, Memory, Network usage
- Alert if exceeds thresholds

---

## Token Rotation Schedule

| Token | Frequency | Action |
|-------|-----------|--------|
| `META_ACCESS_TOKEN` | Every 60 days | Auto-expires; regenerate in Developers |
| `TELEGRAM_BOT_TOKEN` | Every 90 days | Rotate manually via @BotFather |
| `FLASK_API_SECRET` | Every 6 months | Rotate in Railway Variables |

---

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Configure environment variables
3. ✅ Verify health endpoint
4. 🔄 Configure Meta Graph API webhooks
5. 🔄 Integrate with frontend dashboard
6. 🔄 Set up Ruflo agent spawning

See `/DEPLOYMENT_GUIDE.md` for full integration checklist.
