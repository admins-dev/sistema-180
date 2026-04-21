// ══════════════════════════════════════════════════════════════
// GHOST MOUSE — Dashboard Real-time Client
// Conecta via WebSocket al server Python y actualiza la UI
// ══════════════════════════════════════════════════════════════

const WS_URL = `ws://${location.hostname || 'localhost'}:8765`;
let ws = null;
let reconnectTimer = null;
let campaignRunning = false;

// ── State ────────────────────────────────────────────────────
const state = {
  sentToday: 0,
  totalSent: 0,
  responses: 0,
  calls: 0,
  revenue: 0,
  accounts: {},
  recentDMs: [],
};

// ── Clock ────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

// ── WebSocket Connection ─────────────────────────────────────
function connect() {
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    setConnectionStatus(true);
    addTerminalLine('Conexión establecida con Ghost Mouse Server', 'success');
  };

  ws.onclose = () => {
    setConnectionStatus(false);
    addTerminalLine('Conexión perdida. Reconectando en 3s...', 'warning');
    reconnectTimer = setTimeout(connect, 3000);
  };

  ws.onerror = () => {
    addTerminalLine('Error de conexión WebSocket', 'error');
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleEvent(data);
    } catch (e) {
      console.error('Parse error:', e);
    }
  };
}

function setConnectionStatus(connected) {
  const el = document.getElementById('connection-status');
  if (connected) {
    el.classList.add('connected');
    el.innerHTML = '<span class="pulse"></span> CONECTADO';
  } else {
    el.classList.remove('connected');
    el.innerHTML = '<span class="pulse"></span> DESCONECTADO';
  }
}

// ── Event Handler ────────────────────────────────────────────
function handleEvent(data) {
  const t = data.type;
  const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString('es-ES', {hour:'2-digit',minute:'2-digit',second:'2-digit'}) : '';

  switch (t) {
    case 'init_stats':
      state.sentToday = data.sent_today || 0;
      state.totalSent = data.total_sent || 0;
      state.responses = data.responses || 0;
      state.calls = data.calls_booked || 0;
      updateKPIs();
      addTerminalLine('Estado inicial cargado', 'system');
      break;

    case 'campaign_start':
      campaignRunning = true;
      document.getElementById('btn-start').disabled = true;
      document.getElementById('btn-stop').disabled = false;
      addTerminalLine(`🚀 CAMPAÑA INICIADA | ${data.accounts} cuentas | ${data.existing_targets || 0} targets`, 'success');
      break;

    case 'login_ok':
      updateAccount(data.account, 'active', 'Conectado');
      addTerminalLine(`✅ @${data.account} — Login exitoso`, 'success');
      break;

    case 'login_failed':
      updateAccount(data.account, 'error', 'Login fallido');
      addTerminalLine(`❌ @${data.account} — Login fallido`, 'error');
      break;

    case 'scraping':
      addTerminalLine(`🔍 @${data.account} → Analizando @${data.target}...`, 'info');
      updateAccount(data.account, 'sending', `→ @${data.target}`);
      break;

    case 'generating_dm':
      addTerminalLine(`🧠 LLM generando DM para @${data.target} (${data.followers} seg.)`, 'info');
      break;

    case 'sending_dm':
      addTerminalLine(`🖱️ @${data.account} → Tecleando DM a @${data.target}...`, 'dm');
      break;

    case 'dm_sent':
      state.sentToday = data.total_today || state.sentToday + 1;
      state.totalSent = data.total_all || state.totalSent + 1;
      updateKPIs();
      addTerminalLine(`✅ @${data.account} → DM #${state.sentToday} enviado a @${data.target}`, 'success');
      addDMCard(data);
      updateAccount(data.account, 'active', `${getAccountSent(data.account)} DMs`);
      // Flash en el KPI
      flashElement('kpi-sent-today');
      break;

    case 'dm_failed':
      addTerminalLine(`❌ @${data.account} → Fallo enviando a @${data.target}`, 'error');
      break;

    case 'waiting':
      addTerminalLine(`⏱ @${data.account} — Esperando ${data.seconds}s (anti-ban)`, 'system');
      updateAccount(data.account, 'active', `Pausa ${data.seconds}s`);
      break;

    case 'account_banned':
      updateAccount(data.account, 'error', '🚫 BANNED');
      addTerminalLine(`🚨 @${data.account} — POSIBLE BAN DETECTADO: ${data.error}`, 'error');
      break;

    case 'limit_reached':
      updateAccount(data.account, 'active', 'Límite ✅');
      addTerminalLine(`📊 @${data.account} — Límite diario alcanzado`, 'warning');
      break;

    case 'searching_hashtag':
      addTerminalLine(`🔎 Buscando targets en #${data.hashtag}...`, 'info');
      break;

    case 'targets_distributed':
      addTerminalLine(`📋 ${data.total_targets} targets repartidos entre ${data.accounts} cuentas`, 'info');
      break;

    case 'campaign_done':
      campaignRunning = false;
      document.getElementById('btn-start').disabled = false;
      document.getElementById('btn-stop').disabled = true;
      addTerminalLine(
        `🏁 CAMPAÑA TERMINADA | ` +
        `Enviados: ${data.sent} | Fallidos: ${data.failed} | ` +
        `Hoy total: ${data.total_today}`,
        'success'
      );
      break;

    case 'error':
      addTerminalLine(`❌ ERROR: ${data.message}`, 'error');
      break;

    default:
      addTerminalLine(`[${t}] ${JSON.stringify(data).substring(0, 100)}`, 'system');
  }
}

// ── UI Updates ───────────────────────────────────────────────
function updateKPIs() {
  document.getElementById('kpi-sent-today').textContent = state.sentToday;
  document.getElementById('kpi-total-sent').textContent = state.totalSent;
  document.getElementById('kpi-responses').textContent = state.responses;
  document.getElementById('kpi-calls').textContent = state.calls;
  document.getElementById('kpi-revenue').textContent = state.revenue.toLocaleString('es-ES') + '€';

  // Funnel
  document.getElementById('funnel-sent-val').textContent = state.sentToday;
  document.getElementById('funnel-response-val').textContent = state.responses;
  document.getElementById('funnel-calls-val').textContent = state.calls;

  const maxW = Math.max(state.sentToday, 1);
  document.getElementById('funnel-response').style.width = Math.min(100, (state.responses / maxW) * 100) + '%';
  document.getElementById('funnel-calls').style.width = Math.min(100, (state.calls / maxW) * 100) + '%';
}

function addTerminalLine(text, type = 'info') {
  const terminal = document.getElementById('terminal');
  const line = document.createElement('div');
  const time = new Date().toLocaleTimeString('es-ES', {hour:'2-digit',minute:'2-digit',second:'2-digit'});
  line.className = `term-line ${type}`;
  line.textContent = `[${time}] ${text}`;
  terminal.appendChild(line);

  // Auto-scroll + limitar a 200 líneas
  while (terminal.children.length > 200) {
    terminal.removeChild(terminal.firstChild);
  }
  terminal.scrollTop = terminal.scrollHeight;
}

function updateAccount(username, status, detail = '') {
  const grid = document.getElementById('accounts-grid');
  let card = grid.querySelector(`[data-account="${username}"]`);

  if (!card) {
    // Limpiar empty state
    const empty = grid.querySelector('.empty-state');
    if (empty) empty.remove();

    card = document.createElement('div');
    card.className = 'account-card';
    card.dataset.account = username;
    grid.appendChild(card);
    state.accounts[username] = { sent: 0 };
  }

  card.className = `account-card ${status}`;
  card.innerHTML = `
    <div class="account-name">@${username}</div>
    <div class="account-stat">${detail}</div>
  `;

  // Actualizar counter
  const total = grid.querySelectorAll('.account-card').length;
  document.getElementById('accounts-counter').textContent = `${total}/20`;
}

function getAccountSent(username) {
  const acc = state.accounts[username];
  if (acc) {
    acc.sent = (acc.sent || 0) + 1;
    return acc.sent;
  }
  return 1;
}

function addDMCard(data) {
  const list = document.getElementById('dm-list');
  const empty = list.querySelector('.empty-state');
  if (empty) empty.remove();

  const item = document.createElement('div');
  item.className = 'dm-item';
  item.innerHTML = `
    <div class="dm-target">@${data.target}</div>
    <div class="dm-preview">${data.message || ''}</div>
    <div class="dm-meta">
      <span>desde @${data.account}</span>
      <span>${new Date().toLocaleTimeString('es-ES', {hour:'2-digit',minute:'2-digit'})}</span>
    </div>
  `;

  list.insertBefore(item, list.firstChild);

  // Limitar a 50 DMs en la lista
  while (list.children.length > 50) {
    list.removeChild(list.lastChild);
  }
}

function flashElement(id) {
  const el = document.getElementById(id);
  el.style.transition = 'color 0.15s';
  el.style.color = '#22d3ee';
  setTimeout(() => { el.style.color = ''; }, 600);
}

// ── Controls ─────────────────────────────────────────────────
function startCampaign() {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    addTerminalLine('⚠️ No conectado al servidor', 'error');
    return;
  }
  ws.send(JSON.stringify({
    action: 'start_campaign',
    hashtags: [],  // Usa los defaults de config.py
    targets: [],
  }));
  addTerminalLine('📡 Comando de campaña enviado al servidor...', 'info');
}

function stopCampaign() {
  // TODO: implementar stop vía WebSocket
  addTerminalLine('⏹ Solicitando parada de campaña...', 'warning');
}

// ── Init ─────────────────────────────────────────────────────
connect();
