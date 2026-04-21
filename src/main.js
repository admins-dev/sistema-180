import './styles/index.css';

// ══════════════════════════════════════════════════════════════
// GHOST MOUSE — Dashboard Real-time Client (57 Agents Edition)
// ══════════════════════════════════════════════════════════════

const WS_URL = `ws://${location.hostname || 'localhost'}:8765`;
let ws = null;
let reconnectTimer = null;
let currentOfficeAgent = null;

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
  } else if (data.type === 'chat_reply') {
    renderChatMessage(data.msg, data.source, data.mode);
  }
}

function renderChatMessage(msg, source, mode) {
  const isMeeting = mode === 'reunion';
  const historyId = isMeeting ? 'meeting-history' : 'office-history';
  const history = document.getElementById(historyId);
  if (!history) return;

  const line = document.createElement('div');
  let typeClass = 'agent';
  if (source === 'CEO') typeClass = 'ceo';
  if (source === 'JARVIS') typeClass = 'jarvis';

  line.className = `chat-msg ${typeClass}`;
  const time = new Date().toLocaleTimeString('es-ES', {hour:'2-digit',minute:'2-digit'});
  line.innerHTML = `
    <div class="chat-meta">${source} • ${time}</div>
    <div class="chat-text">${msg.replace(/\n/g, '<br>')}</div>
  `;
  history.appendChild(line);
  history.scrollTop = history.scrollHeight;
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

// ── Sala / Despacho ──────────────────────────────────────────
function selectAgentDespacho(agentId, agentName) {
  currentOfficeAgent = agentId;
  document.getElementById('office-chat-title').textContent = `Despacho de ${agentName}`;
  const input = document.getElementById('office-input');
  const btn = document.getElementById('office-btn');
  input.disabled = false;
  btn.disabled = false;
  input.placeholder = `Escribe un mensaje privado a ${agentName}...`;
  document.getElementById('office-history').innerHTML = '';
  document.querySelectorAll('.agent-select-item').forEach(el => el.classList.remove('active'));
  document.querySelector(`.agent-select-item[onclick*="${agentId}"]`).classList.add('active');
}

function sendOfficeMessage() {
  const input = document.getElementById('office-input');
  const msg = input.value.trim();
  if (!msg || !currentOfficeAgent) return;
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'chat_despacho',
      agent_id: currentOfficeAgent,
      msg: msg
    }));
    renderChatMessage(msg, 'CEO', 'despacho');
    input.value = '';
  }
}

function sendMeetingMessage() {
  const input = document.getElementById('meeting-input');
  const msg = input.value.trim();
  if (!msg) return;

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'chat_reunion',
      msg: msg
    }));
    input.value = '';
  }
}

// ── Editor IA (CapCut Pro / Premiere Clone) ─────────────────
function jarvisEditStart() {
  const overlay = document.getElementById('jarvis-editing-overlay');
  const subs = document.getElementById('player-subs');
  const playhead = document.getElementById('playhead');
  
  if (!overlay || !subs || !playhead) return;

  // Fake JARVIS process
  overlay.style.display = 'flex';
  addTerminalLine("🤖 JARVIS: Iniciando motor VideoForge Pro (Layer 3)...", "system");
  addTerminalLine("✂️ Cortando silencios < -35dB...", "system");
  addTerminalLine("✨ Aplicando After Effects Layer: Smart Zoom", "system");
  
  let p = 5;
  const iv = setInterval(() => {
    p += 2;
    playhead.style.left = `${p}%`;
    if (p > 90) {
      clearInterval(iv);
      overlay.style.display = 'none';
      addTerminalLine("✅ Renderizado 4K completado. Subtítulos Hormozi (XL) sincronizados.", "success");
      
      // Simulate video playing with dynamic subtitles
      subs.style.display = 'block';
      const phrases = [
        "ESTA ES LA ÚNICA",
        "ESTRATEGIA",
        "QUE NECESITAS",
        "PARA FACTURAR",
        "10K AL MES"
      ];
      let i = 0;
      setInterval(() => {
        subs.textContent = phrases[i];
        i = (i + 1) % phrases.length;
      }, 800);
      
      const vids = document.querySelectorAll('.vid-clip');
      vids.forEach(v => v.style.borderColor = '#10b981'); // Green borders when done
    }
  }, 100);
}

// Global exposure for inline HTML events
window.switchTab = switchTab;
window.addTestClient = addTestClient;
window.runCommand = runCommand;
window.selectAgentDespacho = selectAgentDespacho;
window.sendOfficeMessage = sendOfficeMessage;
window.sendMeetingMessage = sendMeetingMessage;
window.jarvisEditStart = jarvisEditStart;

document.addEventListener('DOMContentLoaded', () => {
    connect();
});
