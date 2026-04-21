import './styles/index.css';

// ══════════════════════════════════════════════════════════════
// GHOST MOUSE — Dashboard Real-time Client (57 Agents Edition)
// ══════════════════════════════════════════════════════════════

const WS_URL = `ws://${location.hostname || 'localhost'}:8765`;
let ws = null;
let reconnectTimer = null;

// ── Clock ────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  const el = document.getElementById('clock');
  if (el) {
      el.textContent = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
}
setInterval(updateClock, 1000);
updateClock();

// ── Tabs ─────────────────────────────────────────────────────
function switchTab(tabId) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  const btn = document.querySelector(`.tab[data-tab="${tabId}"]`);
  const content = document.getElementById(`tab-${tabId}`);
  if (btn) btn.classList.add('active');
  if (content) content.classList.add('active');
}

// ── WebSocket Connection ─────────────────────────────────────
function connect() {
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    setConnectionStatus(true);
    addTerminalLine('Conexión con Orquestador 57 Agentes establecida.', 'success');
  };

  ws.onclose = () => {
    setConnectionStatus(false);
    addTerminalLine('Conexión perdida. Reconectando en 3s...', 'warning');
    reconnectTimer = setTimeout(connect, 3000);
  };

  ws.onerror = () => {
      addTerminalLine('Error de conexión WebSocket.', 'error');
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
  if (!el) return;
  if (connected) {
    el.classList.add('connected');
    el.innerHTML = '<span class="pulse"></span> SISTEMA ORQUESTADOR ACTIVO';
  } else {
    el.classList.remove('connected');
    el.innerHTML = '<span class="pulse"></span> DESCONECTADO';
  }
}

// ── Event Handler ────────────────────────────────────────────
function handleEvent(data) {
  if (data.type === 'init_agents') {
    renderAgents(data.agents);
  } else if (data.type === 'agent_log') {
    updateAgentUI(data);
    addTerminalLine(`[${data.agent_id} | ${data.agent_name}] ${data.message}`, data.status === 'error' ? 'error' : 'info');
  } else if (data.type === 'terminal_log') {
    addTerminalLine(data.msg, data.level || 'info');
  } else if (data.type === 'client_added') {
    renderClient(data.client);
    const flow = document.getElementById('client-flow');
    if (flow) flow.style.display = 'block';
  }
}

function renderAgents(agentsData) {
  const layers = {
    1: document.getElementById('agents-content'),
    2: document.getElementById('agents-commercial'),
    3: document.getElementById('agents-editing'),
    4: document.getElementById('agents-ops')
  };

  for (const [a_id, a] of Object.entries(agentsData)) {
    const parent = layers[a.layer];
    if (!parent) continue;

    let el = document.getElementById(`agent-${a_id}`);
    if (!el) {
        el = document.createElement('div');
        el.className = `agent-card ${a.status}`;
        el.id = `agent-${a_id}`;
        el.innerHTML = `
          <div class="agent-id">${a_id}</div>
          <div class="agent-name">${a.name}</div>
          <div class="agent-role">${a.role}</div>
          <div class="agent-status" id="status-${a_id}">${a.status.toUpperCase()}</div>
        `;
        parent.appendChild(el);
    } else {
        document.getElementById(`status-${a_id}`).textContent = a.status.toUpperCase();
        el.className = `agent-card ${a.status}`;
    }
  }
}

function updateAgentUI(data) {
  const card = document.getElementById(`agent-${data.agent_id}`);
  if (card) {
    card.className = `agent-card ${data.status}`;
    document.getElementById(`status-${data.agent_id}`).textContent = data.status.toUpperCase();
    
    // Animar bordes si está trabajando
    if (data.status === 'working') {
        card.style.borderColor = '#22d3ee';
        card.style.boxShadow = '0 0 10px rgba(34, 211, 238, 0.5)';
    } else {
        card.style.borderColor = 'rgba(255,255,255,0.1)';
        card.style.boxShadow = 'none';
    }
  }
}

function renderClient(client) {
  const list = document.getElementById('client-list');
  const empty = document.querySelector('.clients-empty');
  if (empty) empty.style.display = 'none';
  if (!list) return;
  
  const el = document.createElement('div');
  el.className = 'panel client-card';
  el.innerHTML = `
    <h3>🏢 ${client.nombre} <span class="badge active">ACTIVO</span></h3>
    <div class="channel-stats">
        <div class="stat-row"><span>ID Cliente</span><span class="val">${client.id}</span></div>
        <div class="stat-row"><span>Nicho</span><span class="val">${client.nicho}</span></div>
        <div class="stat-row"><span>Competidores</span><span class="val">${client.competidores ? client.competidores.join(', ') : 'Ninguno'}</span></div>
        <div class="stat-row"><span>Budget Ads</span><span class="val">${client.budget_ads || '-'}</span></div>
        <div class="stat-row"><span>Tono Marca</span><span class="val">${client.tono || '-'}</span></div>
    </div>
  `;
  list.insertBefore(el, list.firstChild);
}

function addTerminalLine(text, type = 'info') {
  const terminal = document.getElementById('terminal');
  if (!terminal) return;
  const line = document.createElement('div');
  const time = new Date().toLocaleTimeString('es-ES', {hour:'2-digit',minute:'2-digit',second:'2-digit'});
  line.className = `term-line ${type}`;
  line.textContent = `[${time}] ${text}`;
  terminal.appendChild(line);

  while (terminal.children.length > 200) {
    terminal.removeChild(terminal.firstChild);
  }
  terminal.scrollTop = terminal.scrollHeight;
}

// ── Actions ──────────────────────────────────────────────────
function addTestClient() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'add_client',
      client_data: {
        nombre: "Demo Corp SA",
        nicho: "Peluquería",
        ciudad: "Málaga",
        competidores: ["@demo_comp1", "@demo_comp2"],
        precio_medio: "50€",
        tono: "Cercano y profesional",
        budget_ads: "5€/dia"
      }
    }));
    addTerminalLine('Enviando petición de Onboarding de cliente Demo...', 'system');
  } else {
    addTerminalLine('No hay conexión con el orquestador.', 'error');
  }
}

function runCommand(cmd) {
  addTerminalLine(`Ejecutando script local: ${cmd}`, 'system');
}

// Global exposure for inline HTML events
window.switchTab = switchTab;
window.addTestClient = addTestClient;
window.runCommand = runCommand;

document.addEventListener('DOMContentLoaded', () => {
    connect();
});
