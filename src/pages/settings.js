// ═══════════════════════════════════════════════
// Settings Page — Full Integration Hub
// ═══════════════════════════════════════════════
import { storage } from '../services/storage.js';
import { freepikApi } from '../services/freepik-api.js';

export function renderSettings(container) {
  const currentKey = storage.getFreepikKey();
  const stats = storage.getStats();

  container.innerHTML = `
    <div class="page-header">
      <h2>⚙️ Centro de Integraciones</h2>
      <p>API keys, webhooks y conexiones del ecosistema SISTEMA180</p>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;max-width:1000px;">

      <!-- ═══ STRIPE ═══ -->
      <div class="card" style="border-left:3px solid #635bff;">
        <h3 style="font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
          <span style="font-size:20px;">💳</span> Stripe Connect
          <span style="font-size:10px;padding:2px 8px;border-radius:20px;background:rgba(99,91,255,.15);color:#635bff;font-weight:700;">PAGOS</span>
        </h3>
        <div class="input-group">
          <label>Stripe Publishable Key</label>
          <input type="password" id="stripe-pk" value="${storage.get('stripe_pk') || ''}" placeholder="pk_live_...">
        </div>
        <div class="input-group">
          <label>Stripe Secret Key</label>
          <input type="password" id="stripe-sk" value="${storage.get('stripe_sk') || ''}" placeholder="sk_live_...">
        </div>
        <div class="input-group">
          <label>Webhook Secret (whsec_)</label>
          <input type="password" id="stripe-wh" value="${storage.get('stripe_wh') || ''}" placeholder="whsec_...">
        </div>
        <p style="font-size:11px;color:var(--text-muted);margin-bottom:12px;">Billing Agent (Fernando) usa estas keys para facturar con IVA 21%.</p>
        <div class="flex gap-8">
          <button class="btn btn-primary" id="save-stripe" style="background:linear-gradient(135deg,#635bff,#818cf8);">💾 Guardar</button>
          <button class="btn btn-secondary" id="test-stripe">🔌 Test</button>
        </div>
        <div id="stripe-status" style="margin-top:10px;display:none;"></div>
      </div>

      <!-- ═══ META PIXEL ═══ -->
      <div class="card" style="border-left:3px solid #1877f2;">
        <h3 style="font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
          <span style="font-size:20px;">📊</span> Meta Pixel
          <span style="font-size:10px;padding:2px 8px;border-radius:20px;background:rgba(24,119,242,.15);color:#1877f2;font-weight:700;">TRACKING</span>
        </h3>
        <div class="input-group">
          <label>Pixel ID</label>
          <input type="text" id="meta-pixel-id" value="${storage.get('meta_pixel_id') || ''}" placeholder="123456789012345">
        </div>
        <div class="input-group">
          <label>Conversions API Access Token</label>
          <input type="password" id="meta-capi" value="${storage.get('meta_capi') || import.meta.env.VITE_META_CAPI || ''}" placeholder="EAABsb...">
        </div>
        <div class="input-group">
          <label>Ad Account ID</label>
          <input type="text" id="meta-ad-account" value="${storage.get('meta_ad_account') || ''}" placeholder="act_123456789">
        </div>
        <p style="font-size:11px;color:var(--text-muted);margin-bottom:12px;">Pixel Agent (Luna) inyecta el tracking y reporta CPL/ROAS en tiempo real.</p>
        <div class="flex gap-8">
          <button class="btn btn-primary" id="save-pixel" style="background:linear-gradient(135deg,#1877f2,#42a5f5);">💾 Guardar</button>
        </div>
        <div id="pixel-status" style="margin-top:10px;display:none;"></div>
      </div>

      <!-- ═══ n8n ═══ -->
      <div class="card" style="border-left:3px solid #ff6d5a;">
        <h3 style="font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
          <span style="font-size:20px;">🔗</span> n8n Workflows
          <span style="font-size:10px;padding:2px 8px;border-radius:20px;background:rgba(255,109,90,.15);color:#ff6d5a;font-weight:700;">AUTOMATIONS</span>
        </h3>
        <div class="input-group">
          <label>n8n Base URL</label>
          <input type="url" id="n8n-url" value="${storage.get('n8n_url') || ''}" placeholder="https://your-n8n.app.n8n.cloud">
        </div>
        <div class="input-group">
          <label>Webhook URL (Leads)</label>
          <input type="url" id="n8n-webhook-leads" value="${storage.get('n8n_webhook_leads') || ''}" placeholder="https://...webhook.../lead-capture">
        </div>
        <div class="input-group">
          <label>Webhook URL (Pagos)</label>
          <input type="url" id="n8n-webhook-pay" value="${storage.get('n8n_webhook_pay') || ''}" placeholder="https://...webhook.../stripe-event">
        </div>
        <p style="font-size:11px;color:var(--text-muted);margin-bottom:12px;">14 flujos configurados. CRM Agent (Natalia) dispara automáticamente.</p>
        <div class="flex gap-8">
          <button class="btn btn-primary" id="save-n8n" style="background:linear-gradient(135deg,#ff6d5a,#ff9a8b);">💾 Guardar</button>
          <button class="btn btn-secondary" id="test-n8n">🔌 Test Webhook</button>
        </div>
        <div id="n8n-status" style="margin-top:10px;display:none;"></div>
      </div>

      <!-- ═══ SLACK ═══ -->
      <div class="card" style="border-left:3px solid #4a154b;">
        <h3 style="font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
          <span style="font-size:20px;">💬</span> Slack
          <span style="font-size:10px;padding:2px 8px;border-radius:20px;background:rgba(74,21,75,.15);color:#e01e5a;font-weight:700;">ALERTAS</span>
        </h3>
        <div class="input-group">
          <label>Slack Webhook URL (#ventas)</label>
          <input type="url" id="slack-sales" value="${storage.get('slack_sales') || ''}" placeholder="https://hooks.slack.com/services/...">
        </div>
        <div class="input-group">
          <label>Slack Webhook URL (#alertas)</label>
          <input type="url" id="slack-alerts" value="${storage.get('slack_alerts') || ''}" placeholder="https://hooks.slack.com/services/...">
        </div>
        <p style="font-size:11px;color:var(--text-muted);margin-bottom:12px;">Recibe notificaciones en Slack cuando los agentes cierran ventas o detectan anomalías.</p>
        <div class="flex gap-8">
          <button class="btn btn-primary" id="save-slack" style="background:linear-gradient(135deg,#4a154b,#611f69);">💾 Guardar</button>
          <button class="btn btn-secondary" id="test-slack">📨 Test Mensaje</button>
        </div>
        <div id="slack-status" style="margin-top:10px;display:none;"></div>
      </div>

      <!-- ═══ API KEYS EXISTENTES ═══ -->
      <div class="card" style="border-left:3px solid var(--accent);">
        <h3 style="font-weight:700; margin-bottom:16px;display:flex;align-items:center;gap:8px;">
          <span style="font-size:20px;">🔑</span> Claves de IA
        </h3>
        <div class="input-group">
          <label>🎨 Freepik API (Premium+ Mystic)</label>
          <input type="password" id="freepik-key" value="${currentKey}" placeholder="fpk_XXXXXX...">
        </div>
        <div class="input-group">
          <label>🤖 Google Gemini API (2.5 Flash)</label>
          <input type="password" id="gemini-key" value="${storage.getGeminiKey()}" placeholder="AIzaSy...">
        </div>
        <div class="input-group">
          <label>🔎 Perplexity API (Sonar Pro)</label>
          <input type="password" id="perplexity-key" value="${storage.getPerplexityKey()}" placeholder="pplx-XXXXXX...">
        </div>
        <div class="flex gap-8">
          <button class="btn btn-primary" id="save-key-btn">💾 Guardar APIs</button>
          <button class="btn btn-secondary" id="test-key-btn">🔌 Test Freepik</button>
        </div>
        <div id="key-status" style="margin-top:10px;display:none;"></div>
      </div>

      <!-- ═══ CLAUDEFLOW ═══ -->
      <div class="card" style="border-left:3px solid #a78bfa;">
        <h3 style="font-weight:700; margin-bottom:16px;display:flex;align-items:center;gap:8px;">
          <span style="font-size:20px;">🐝</span> ClaudeFlow (Ruflo)
          <span style="font-size:10px;padding:2px 8px;border-radius:20px;background:rgba(167,139,250,.15);color:#a78bfa;font-weight:700;">SWARM</span>
        </h3>
        <div class="input-group">
          <label>Anthropic API Key (Haiku)</label>
          <input type="password" id="anthropic-key" value="${storage.get('anthropic_key') || ''}" placeholder="sk-ant-...">
        </div>
        <div class="input-group">
          <label>Ruflo Endpoint (local)</label>
          <input type="url" id="ruflo-url" value="${storage.get('ruflo_url') || 'http://localhost:4180'}" placeholder="http://localhost:4180">
        </div>
        <p style="font-size:11px;color:var(--text-muted);margin-bottom:12px;">8 agentes del enjambre Ruflo. Budget total: $5.00 (Haiku $0.01/tarea).</p>
        <div class="flex gap-8">
          <button class="btn btn-primary" id="save-ruflo" style="background:linear-gradient(135deg,#a78bfa,#7c3aed);">💾 Guardar</button>
        </div>
        <div id="ruflo-status" style="margin-top:10px;display:none;"></div>
      </div>

      <!-- ═══ VIDEOFORGE ═══ -->
      <div class="card" style="border-left: 3px solid #f59e0b;">
        <h3 style="font-weight:700; margin-bottom:16px;display:flex;align-items:center;gap:8px;">
          <span style="font-size:20px;">✂️</span> VideoForge <span style="color:#f59e0b">Pro</span>
        </h3>
        <div class="input-group">
          <label>🖥️ URL del servidor VideoForge</label>
          <input type="url" id="videoforge-url" value="${storage.get('videoforge_url') || 'http://localhost:5000'}" placeholder="http://localhost:5000">
        </div>
        <div class="flex gap-8">
          <button class="btn btn-primary" id="save-vf-btn" style="background: linear-gradient(135deg, #f59e0b, #ef4444);">💾 Guardar</button>
          <button class="btn btn-secondary" id="test-vf-btn">🔌 Test</button>
        </div>
        <div id="vf-status" style="margin-top:10px;display:none;"></div>
      </div>

      <!-- ═══ DATOS LOCALES ═══ -->
      <div class="card">
        <h3 style="font-weight:700; margin-bottom:16px;">📊 Datos Locales</h3>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">
          <div style="padding:12px; background:var(--bg-secondary); border-radius:var(--radius-sm);">
            <div style="font-size:20px; font-weight:800;">${stats.avatars}</div>
            <div style="font-size:12px; color:var(--text-muted);">Avatares</div>
          </div>
          <div style="padding:12px; background:var(--bg-secondary); border-radius:var(--radius-sm);">
            <div style="font-size:20px; font-weight:800;">${stats.scripts}</div>
            <div style="font-size:12px; color:var(--text-muted);">Guiones</div>
          </div>
          <div style="padding:12px; background:var(--bg-secondary); border-radius:var(--radius-sm);">
            <div style="font-size:20px; font-weight:800;">${stats.videos}</div>
            <div style="font-size:12px; color:var(--text-muted);">Vídeos</div>
          </div>
          <div style="padding:12px; background:var(--bg-secondary); border-radius:var(--radius-sm);">
            <div style="font-size:20px; font-weight:800;">${stats.ads}</div>
            <div style="font-size:12px; color:var(--text-muted);">Anuncios</div>
          </div>
        </div>
        <button class="btn btn-danger" id="clear-btn">🗑️ Borrar todos los datos</button>
      </div>
    </div>
  `;

  // ── SAVE HANDLERS ───────────────────────────
  // Stripe
  container.querySelector('#save-stripe').addEventListener('click', () => {
    storage.set('stripe_pk', container.querySelector('#stripe-pk').value.trim());
    storage.set('stripe_sk', container.querySelector('#stripe-sk').value.trim());
    storage.set('stripe_wh', container.querySelector('#stripe-wh').value.trim());
    showStatus('stripe-status', '✅ Stripe Connect configurado');
  });
  container.querySelector('#test-stripe').addEventListener('click', () => {
    const pk = container.querySelector('#stripe-pk').value.trim();
    showStatus('stripe-status', pk.startsWith('pk_live') ? '✅ Key LIVE detectada — producción' : pk.startsWith('pk_test') ? '⚠️ Key TEST — modo sandbox' : '❌ Key inválida');
  });

  // Meta Pixel
  container.querySelector('#save-pixel').addEventListener('click', () => {
    storage.set('meta_pixel_id', container.querySelector('#meta-pixel-id').value.trim());
    storage.set('meta_capi', container.querySelector('#meta-capi').value.trim());
    storage.set('meta_ad_account', container.querySelector('#meta-ad-account').value.trim());
    showStatus('pixel-status', '✅ Meta Pixel + CAPI configurado — Luna activa');
  });

  // n8n
  container.querySelector('#save-n8n').addEventListener('click', () => {
    storage.set('n8n_url', container.querySelector('#n8n-url').value.trim());
    storage.set('n8n_webhook_leads', container.querySelector('#n8n-webhook-leads').value.trim());
    storage.set('n8n_webhook_pay', container.querySelector('#n8n-webhook-pay').value.trim());
    showStatus('n8n-status', '✅ n8n webhooks guardados — Natalia conectada');
  });
  container.querySelector('#test-n8n').addEventListener('click', async () => {
    const wh = container.querySelector('#n8n-webhook-leads').value.trim();
    if (!wh) return showStatus('n8n-status', '❌ Introduce una URL de webhook primero');
    showStatus('n8n-status', '⏳ Enviando test...');
    try {
      await fetch(wh, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({test:true,source:'sistema180',ts:Date.now()}) });
      showStatus('n8n-status', '✅ Test enviado — revisa tu flujo n8n');
    } catch(e) { showStatus('n8n-status', '❌ Error: ' + e.message); }
  });

  // Slack
  container.querySelector('#save-slack').addEventListener('click', () => {
    storage.set('slack_sales', container.querySelector('#slack-sales').value.trim());
    storage.set('slack_alerts', container.querySelector('#slack-alerts').value.trim());
    showStatus('slack-status', '✅ Slack webhooks guardados');
  });
  container.querySelector('#test-slack').addEventListener('click', async () => {
    const wh = container.querySelector('#slack-sales').value.trim();
    if (!wh) return showStatus('slack-status', '❌ Introduce la URL del webhook primero');
    showStatus('slack-status', '⏳ Enviando...');
    try {
      await fetch(wh, { method:'POST', body:JSON.stringify({text:'🤖 SISTEMA180: Test de conexión ✅ — Los 57 agentes están operativos.'}) });
      showStatus('slack-status', '✅ Mensaje enviado a Slack');
    } catch(e) { showStatus('slack-status', '❌ Error: ' + e.message); }
  });

  // AI Keys (existing)
  container.querySelector('#save-key-btn').addEventListener('click', () => {
    storage.setFreepikKey(container.querySelector('#freepik-key').value.trim());
    storage.setGeminiKey(container.querySelector('#gemini-key').value.trim());
    storage.setPerplexityKey(container.querySelector('#perplexity-key').value.trim());
    showStatus('key-status', '✅ API keys guardadas');
  });
  container.querySelector('#test-key-btn').addEventListener('click', async () => {
    showStatus('key-status', '⏳ Testeando Freepik...');
    const result = await freepikApi.testConnection();
    showStatus('key-status', result.ok ? '✅ Conexión OK — Freepik Premium+ activa' : '❌ Error: ' + (result.error || 'Status ' + result.status));
  });

  // ClaudeFlow
  container.querySelector('#save-ruflo').addEventListener('click', () => {
    storage.set('anthropic_key', container.querySelector('#anthropic-key').value.trim());
    storage.set('ruflo_url', container.querySelector('#ruflo-url').value.trim());
    showStatus('ruflo-status', '✅ ClaudeFlow configurado — Enjambre Ruflo listo');
  });

  // VideoForge
  container.querySelector('#save-vf-btn').addEventListener('click', () => {
    storage.set('videoforge_url', container.querySelector('#videoforge-url').value.trim() || 'http://localhost:5000');
    showStatus('vf-status', '✅ URL de VideoForge guardada');
  });
  container.querySelector('#test-vf-btn').addEventListener('click', async () => {
    const url = container.querySelector('#videoforge-url').value.trim() || 'http://localhost:5000';
    showStatus('vf-status', '⏳ Conectando...');
    try {
      const res = await fetch(`${url}/api/presets`, { signal: AbortSignal.timeout(5000) });
      if (res.ok) {
        const presets = await res.json();
        showStatus('vf-status', `✅ VideoForge Pro conectado — ${Object.keys(presets).length} presets`);
      } else { showStatus('vf-status', `❌ Error ${res.status}`); }
    } catch (e) { showStatus('vf-status', '❌ No se pudo conectar'); }
  });

  // Clear data
  container.querySelector('#clear-btn').addEventListener('click', () => {
    if (confirm('¿Borrar todos los avatares, guiones y datos de SISTEMA180?')) {
      // Fix #24: Safe iteration — collect keys first, then remove
      const keysToRemove = Object.keys(localStorage).filter(k => k.startsWith('s180_'));
      keysToRemove.forEach(k => localStorage.removeItem(k));
      renderSettings(container);
    }
  });

  function showStatus(id, msg) {
    const el = container.querySelector('#' + id);
    if (el) {
      el.style.display = 'block';
      el.innerHTML = `<span class="tag ${msg.startsWith('✅') ? 'tag-green' : msg.startsWith('❌') ? 'tag-red' : 'tag-orange'}">${msg}</span>`;
    }
  }
}
