// ═══════════════════════════════════════════════════════════
// El Despacho — Sala de Reuniones Pixel Art
// 57 Agentes IA OPERATIVOS · Sistema 180 HQ
// ═══════════════════════════════════════════════════════════
import { aiService } from '../services/ai-service.js';
import { pixelService } from '../services/pixel-service.js';

let ws = null;
let currentMeeting = false;

function connectOrchestrator() {
    if(ws && ws.readyState !== WebSocket.CLOSED) return;
    try {
        ws = new WebSocket('ws://localhost:9000');
        ws.onopen = () => console.log('📡 [S180] Hub Conectado al Cerebro Central (Gemini)');
        ws.onmessage = (e) => {
            const dt = JSON.parse(e.data);
            if(dt.type === 'meeting' && currentMeeting) {
                const term = document.getElementById('meeting-terminal');
                if(term) {
                    const line = document.createElement('div');
                    line.style.margin = '4px 0';
                    line.style.color = dt.agent === 'JARVIS' ? 'var(--green)' : 'var(--accent)';
                    line.innerHTML = `<strong>[${dt.agent}]</strong> ${dt.content}`;
                    term.appendChild(line);
                    term.scrollTop = term.scrollHeight;
                }
            } else if(dt.type === 'chat' && dt.agent) {
                const term = document.getElementById(`chat-term-${dt.agent}`);
                if(term) {
                    const line = document.createElement('div');
                    line.style.margin = '4px 0';
                    line.style.color = 'var(--text-primary)';
                    line.innerHTML = `<strong>[${dt.agent}]</strong> ${dt.content}`;
                    term.appendChild(line);
                    term.scrollTop = term.scrollHeight;
                }
            }
        };
    } catch(e) { console.error('WS Error:', e) }
}

const DEPTS = [
  {
    dept:'Orquestadores', icon:'🧠', color:'#f59e0b', floor:'Planta 4',
    agents:[
      { name:'Alejandro', role:'CEO',    status:'ready',    emoji:'👔' },
      { name:'Rafael',    role:'COO',    status:'ready',    emoji:'📊' },
      { name:'Valentina', role:'CMO',    status:'ready',    emoji:'📣' },
    ]
  },
  {
    dept:'Jefes de Área', icon:'📋', color:'#6366f1', floor:'Planta 3',
    agents:[
      { name:'Marcos',  role:'Sales Head',    status:'ready',    emoji:'💼' },
      { name:'Sofía',   role:'Content Head',  status:'ready',    emoji:'✍️' },
      { name:'Eduardo', role:'Finance Head',  status:'ready', emoji:'💰' },
      { name:'Lucía',   role:'Client Success',status:'ready', emoji:'🎧' },
      { name:'Diego',   role:'Marketplace',   status:'ready', emoji:'🏪' },
    ]
  },
  {
    dept:'Edición de Vídeo', icon:'✂️', color:'#06b6d4', floor:'Planta 2',
    agents:[
      { name:'Carlos',  role:'Edit Orch',  status:'ready', emoji:'🎬' },
      { name:'Mateo',   role:'Cut',        status:'ready', emoji:'✂️' },
      { name:'Álvaro',  role:'Audio',      status:'ready', emoji:'🎵' },
      { name:'Bruno',   role:'Color',      status:'ready', emoji:'🎨' },
      { name:'Carmen',  role:'Subtítulos', status:'ready', emoji:'💬' },
      { name:'Hugo',    role:'Zoom',       status:'ready', emoji:'🔍' },
      { name:'Marta',   role:'Thumbnail',  status:'ready', emoji:'🖼️' },
      { name:'Iván',    role:'Format',     status:'ready', emoji:'📐' },
      { name:'Elena',   role:'QA',         status:'ready', emoji:'✅' },
      { name:'Noa',     role:'Publisher',  status:'ready', emoji:'📤' },
    ]
  },
  {
    dept:'Copy & Guiones', icon:'📝', color:'#10b981', floor:'Planta 2',
    agents:[
      { name:'Adriana', role:'Copy Orch', status:'ready', emoji:'📝' },
      { name:'Pablo',   role:'Scripts',  status:'ready',    emoji:'🎯' },
      { name:'Sergio',  role:'Ads',      status:'ready', emoji:'📢' },
      { name:'Alba',    role:'Captions', status:'ready', emoji:'📸' },
      { name:'Tomás',   role:'Email',    status:'ready', emoji:'✉️' },
      { name:'Claudia', role:'WhatsApp', status:'ready', emoji:'💬' },
    ]
  },
  {
    dept:'Ventas', icon:'💼', color:'#ec4899', floor:'Planta 2',
    agents:[
      { name:'Roberto',  role:'Sales Orch', status:'ready', emoji:'🏆' },
      { name:'Javier',   role:'Lead Scout', status:'ready', emoji:'🗺️' },
      { name:'Ares',     role:'SDR',        status:'ready',    emoji:'⚡' },
      { name:'Natalia',  role:'CRM',        status:'ready', emoji:'📋' },
      { name:'Gonzalo',  role:'Closer',     status:'ready', emoji:'🤝' },
    ]
  },
  {
    dept:'Atención al Cliente', icon:'🎧', color:'#f97316', floor:'Planta 2',
    agents:[
      { name:'Isabel',   role:'Client Orch', status:'ready', emoji:'🌟' },
      { name:'Miguel',   role:'Onboarding',  status:'ready', emoji:'🚀' },
      { name:'Andrea',   role:'Support',     status:'ready', emoji:'💪' },
      { name:'Fernando', role:'Billing',     status:'ready', emoji:'💳' },
      { name:'Cristina', role:'Reports',     status:'ready', emoji:'📊' },
    ]
  },
  {
    dept:'Afiliados', icon:'🤝', color:'#818cf8', floor:'Planta 2',
    agents:[
      { name:'Antonio', role:'Affiliate Orch', status:'ready', emoji:'🔗' },
      { name:'Raquel',  role:'Comisiones',     status:'ready', emoji:'💸' },
      { name:'David',   role:'Pagos',          status:'ready', emoji:'🏦' },
      { name:'Víctor',  role:'Fraude',         status:'ready', emoji:'🛡️' },
    ]
  },
  {
    dept:'Marketplace', icon:'🏪', color:'#34d399', floor:'Planta 2',
    agents:[
      { name:'Beatriz',   role:'Mkt Orch', status:'ready', emoji:'🏬' },
      { name:'Guillermo', role:'Booking',  status:'ready', emoji:'📅' },
      { name:'Irene',     role:'Split',    status:'ready', emoji:'⚖️' },
      { name:'Mario',     role:'Reviews',  status:'ready', emoji:'⭐' },
    ]
  },
  {
    dept:'Legal', icon:'⚖️', color:'#f87171', floor:'Planta 2',
    agents:[
      { name:'Amparo', role:'Legal', status:'ready', emoji:'⚖️' },
    ]
  },
  {
    dept:'Pixel & Tracking', icon:'📊', color:'#f472b6', floor:'Planta 1',
    agents:[
      { name:'Luna',     role:'Pixel Agent',    status:'ready', emoji:'🎯' },
      { name:'Omar',     role:'Analytics',      status:'ready', emoji:'📈' },
      { name:'Daniela',  role:'A/B Testing',    status:'ready', emoji:'🧪' },
    ]
  },
];

const ALL_AGENTS = DEPTS.flatMap(d => d.agents.map(a => ({ ...a, dept: d.dept, deptColor: d.color, floor: d.floor })));
const READY = ALL_AGENTS.filter(a => a.status === 'ready').length;

// ── Pixel character SVG ───────────────────────────────────────
function pixelAgent(agent, size = 40) {
  const color = agent.status === 'ready' ? agent.deptColor : '#4b5563';
  const glow  = agent.status === 'ready' ? `drop-shadow(0 0 4px ${agent.deptColor}88)` : 'none';
  return `
    <svg width="${size}" height="${size}" viewBox="0 0 16 16" style="filter:${glow};image-rendering:pixelated;">
      <!-- Head -->
      <rect x="5" y="1" width="6" height="5" fill="${color}" rx="1"/>
      <!-- Eyes -->
      <rect x="6" y="2.5" width="1.5" height="1.5" fill="#fff" rx="0.3"/>
      <rect x="8.5" y="2.5" width="1.5" height="1.5" fill="#fff" rx="0.3"/>
      <rect x="6.3" y="2.7" width="0.8" height="0.8" fill="#0f172a"/>
      <rect x="8.8" y="2.7" width="0.8" height="0.8" fill="#0f172a"/>
      <!-- Mouth ${agent.status==='ready' ? '(smile)' : '(flat)'} -->
      ${agent.status==='ready'
        ? `<path d="M6.5 4.5 Q8 5.5 9.5 4.5" stroke="#fff" stroke-width="0.5" fill="none"/>`
        : `<rect x="6.3" y="4.5" width="3.4" height="0.5" fill="#ffffff44" rx="0.2"/>`}
      <!-- Body -->
      <rect x="4" y="7" width="8" height="5" fill="${color}cc" rx="1"/>
      <!-- Arms -->
      <rect x="2" y="7.5" width="2" height="3.5" fill="${color}aa" rx="0.5"/>
      <rect x="12" y="7.5" width="2" height="3.5" fill="${color}aa" rx="0.5"/>
      <!-- Legs -->
      <rect x="5" y="12" width="2.5" height="3" fill="${color}88" rx="0.5"/>
      <rect x="8.5" y="12" width="2.5" height="3" fill="${color}88" rx="0.5"/>
      <!-- Status dot -->
      <circle cx="13.5" cy="2" r="1.5" fill="${agent.status==='ready' ? '#10b981' : '#f59e0b'}"/>
    </svg>`;
}

// ── Building floor visual ─────────────────────────────────────
function buildingHTML() {
  const floors = [
    { label:'Penthouse', sub:'José + Ares', color:'#f59e0b', agents:[] },
    { label:'Planta 4',  sub:'Orquestadores (CEO/COO/CMO)', color:'#f59e0b', agents: DEPTS[0].agents },
    { label:'Planta 3',  sub:'Jefes de Área', color:'#6366f1', agents: DEPTS[1].agents },
    { label:'Planta 2',  sub:'Agentes operativos (35)', color:'#06b6d4', agents: ALL_AGENTS.filter(a=>a.floor==='Planta 2') },
    { label:'Planta 1',  sub:'Infraestructura (Stripe/n8n/DB)', color:'#10b981', agents:[] },
    { label:'Subsuelo',  sub:'Servidores · ComfyUI · GPUs', color:'#6b7280', agents:[] },
  ];

  return floors.map((f, i) => {
    const ready = f.agents.filter(a=>a.status==='ready').length;
    const total = f.agents.length;
    const pct = total > 0 ? Math.round(ready/total*100) : (i === 0 ? 100 : i >= 4 ? 100 : 0);
    return `
      <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                  background:rgba(255,255,255,.03);border-radius:8px;border-left:3px solid ${f.color};
                  margin-bottom:6px;">
        <div style="font-size:11px;font-weight:800;color:${f.color};width:70px;flex-shrink:0;">${f.label}</div>
        <div style="flex:1;">
          <div style="font-size:11px;color:var(--text-secondary);">${f.sub}</div>
          <div style="background:rgba(255,255,255,.05);border-radius:4px;height:4px;margin-top:4px;">
            <div style="background:${f.color};height:4px;border-radius:4px;width:${pct}%;transition:width .8s;"></div>
          </div>
        </div>
        <div style="font-size:10px;color:${f.color};font-weight:700;flex-shrink:0;">${pct}%</div>
      </div>`;
  }).join('');
}

// ── Agent detail modal ────────────────────────────────────────
function openAgentModal(agentName) {
  const agent = ALL_AGENTS.find(a => a.name === agentName);
  if (!agent) return;

  const existing = document.getElementById('despacho-modal');
  if (existing) existing.remove();

  const dept = DEPTS.find(d => d.dept === agent.dept);
  const deptAgentsFull = dept?.agents.map(a => ({
    ...a,
    deptColor: agent.deptColor,
    dept: agent.dept,
    floor: agent.floor,
    desc: '',
    model: 'Gemini 2.5 Flash',
  })) || [];

  const modal = document.createElement('div');
  modal.id = 'despacho-modal';
  modal.style.cssText = `
    position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:2000;
    display:flex;align-items:center;justify-content:center;padding:20px;
  `;

  const statusColor = agent.status === 'ready' ? 'var(--green)' : 'var(--orange)';
  const statusLabel = agent.status === 'ready' ? '● OPERATIVO' : '⚙️ EN CONSTRUCCIÓN';

  modal.innerHTML = `
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:20px;
                padding:28px;width:100%;max-width:480px;position:relative;
                border-top:3px solid ${agent.deptColor};">
      <button onclick="document.getElementById('despacho-modal').remove()"
        style="position:absolute;top:16px;right:16px;background:rgba(255,255,255,.08);
               border:none;color:var(--text-muted);width:32px;height:32px;border-radius:50%;
               cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;">×</button>

      <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
        <div style="width:64px;height:64px;display:flex;align-items:center;justify-content:center;">
          ${pixelAgent(agent, 64)}
        </div>
        <div>
          <div style="font-size:24px;font-weight:900;">${agent.emoji} ${agent.name}</div>
          <div style="font-size:13px;font-weight:700;color:${agent.deptColor};margin-top:2px;">${agent.role}</div>
          <div style="font-size:11px;color:var(--text-muted);">${agent.dept} · ${agent.floor}</div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">
        <div style="padding:10px;background:rgba(255,255,255,.04);border-radius:8px;text-align:center;">
          <div style="font-size:10px;color:var(--text-muted);">Estado</div>
          <div style="font-size:12px;font-weight:800;color:${statusColor};margin-top:4px;">${statusLabel}</div>
        </div>
        <div style="padding:10px;background:rgba(255,255,255,.04);border-radius:8px;text-align:center;">
          <div style="font-size:10px;color:var(--text-muted);">Modelo IA</div>
          <div style="font-size:11px;font-weight:700;color:${agent.deptColor};margin-top:4px;">Gemini 2.5 Flash</div>
        </div>
      </div>

      <div style="padding:12px;background:rgba(255,255,255,.03);border-radius:10px;margin-bottom:16px;">
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:8px;font-weight:600;">Equipo en ${agent.dept}</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;">
          ${deptAgentsFull.map(a => `
            <span style="padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700;cursor:pointer;
                         background:${a.name===agent.name ? agent.deptColor+'33' : 'rgba(255,255,255,.06)'};
                         color:${a.name===agent.name ? agent.deptColor : 'var(--text-muted)'};
                         border:1px solid ${a.name===agent.name ? agent.deptColor+'44' : 'transparent'};"
                  onclick="document.getElementById('despacho-modal').remove();window._openAgentModal('${a.name}')">
              ${a.emoji} ${a.name}
            </span>
          `).join('')}
        </div>
      </div>

      ${agent.status === 'ready' ? `
      <div style="padding:12px;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.2);
                  border-radius:10px;font-size:12px;color:var(--green);text-align:center;">
        ✅ Agente operativo y disponible
      </div>
      <div style="margin-top:16px;background:rgba(0,0,0,0.4);border:1px solid var(--border);border-radius:12px;padding:12px;">
        <div style="font-size:11px;font-weight:700;color:var(--accent);margin-bottom:8px;">💬 Chat 1-on-1</div>
        <div id="chat-term-${agent.name}" style="height:140px;overflow-y:auto;font-family:monospace;font-size:11px;color:var(--text-secondary);margin-bottom:8px;"></div>
        <div style="display:flex;gap:8px;">
          <input type="text" id="chat-input-${agent.name}" placeholder="Pide a ${agent.name}..." style="flex:1;background:rgba(255,255,255,0.05);border:none;border-radius:6px;padding:8px;color:#fff;font-size:11px;outline:none;">
          <button onclick="window._send1on1('${agent.name}')" style="background:var(--accent);border:none;border-radius:6px;padding:0 12px;color:#fff;font-size:10px;cursor:pointer;">Enviar</button>
        </div>
      </div>
      ` : `
      <div style="padding:12px;background:rgba(245,158,11,.06);border:1px solid rgba(245,158,11,.2);
                  border-radius:10px;font-size:12px;color:var(--orange);text-align:center;">
        ⚙️ En desarrollo — próximamente operativo
      </div>`}
    </div>
  `;

  document.body.appendChild(modal);
  modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });

  window._send1on1 = (agent) => {
    const inp = document.getElementById(`chat-input-${agent}`);
    if(!inp.value.trim() || !ws) return;
    const term = document.getElementById(`chat-term-${agent}`);
    term.innerHTML += `<div style="margin:4px 0;color:#fff;"><strong>[Tú]</strong> ${inp.value}</div>`;
    ws.send(JSON.stringify({ type: '1on1', role: 'CEO', target_agent: agent, content: inp.value }));
    inp.value = '';
    term.scrollTop = term.scrollHeight;
  };
}

// ── Main render ───────────────────────────────────────────────
export function renderDespacho(container) {
  connectOrchestrator();
  window._openAgentModal = openAgentModal;

  // Group agents for the table layout
  const tableRows = [
    // Head of table — CEO/COO/CMO
    DEPTS[0].agents.map(a => ({ ...a, deptColor: DEPTS[0].color, dept: DEPTS[0].dept, floor: DEPTS[0].floor })),
    // Left side — Sales + Ventas
    [...DEPTS[1].agents.slice(0,3), ...DEPTS[4].agents.slice(0,3)].map(a => {
      const d = DEPTS.find(dep => dep.agents.includes(a));
      return { ...a, deptColor: d?.color || '#6366f1', dept: d?.dept || '', floor: d?.floor || '' };
    }),
    // Right side — Content + Copy
    [...DEPTS[1].agents.slice(3), ...DEPTS[3].agents.slice(0,3)].map(a => {
      const d = DEPTS.find(dep => dep.agents.includes(a));
      return { ...a, deptColor: d?.color || '#10b981', dept: d?.dept || '', floor: d?.floor || '' };
    }),
  ];

  const allForTable = ALL_AGENTS;
  const byDept = DEPTS.map(d => ({
    ...d,
    agents: d.agents.map(a => ({ ...a, deptColor: d.color, dept: d.dept, floor: d.floor }))
  }));

  const pixelStatus = pixelService.runDiagnostics();
  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--green)';
    if (score >= 50) return 'var(--orange)';
    return 'var(--red)';
  };

  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
      <div>
        <h2 style="font-size:22px;font-weight:800;">🏢 El Despacho — HQ Sistema 180</h2>
        <p style="color:var(--text-muted);font-size:13px;">
          <span style="color:var(--green);">● ${READY} operativos</span>
          &nbsp;·&nbsp;
          <span style="color:var(--orange);">⚙️ ${ALL_AGENTS.length - READY} en construcción</span>
          &nbsp;·&nbsp; ${ALL_AGENTS.length} agentes totales
        </p>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button onclick="window._dView('table')" id="btn-view-table"
          style="padding:7px 14px;background:var(--accent);color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;">
          🏢 Sala
        </button>
        <button onclick="window._dView('building')" id="btn-view-building"
          style="padding:7px 14px;background:rgba(255,255,255,.06);color:var(--text-secondary);border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;">
          🏗️ Edificio
        </button>
        <button onclick="window._openMeetingModal()" id="btn-view-meeting"
          style="padding:7px 14px;background:rgba(16,185,129,.15);color:var(--green);border:1px solid rgba(16,185,129,.3);border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;">
          📣 Convocar reunión
        </button>
      </div>
    </div>

    <!-- ═══════════════════════════════════ -->
    <!-- VISTA 1: SALA DE REUNIONES         -->
    <!-- ═══════════════════════════════════ -->
    <div id="despacho-view-table">

      <!-- Office room -->
      <div style="background:linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
                  border:1px solid rgba(255,255,255,.08);border-radius:20px;
                  padding:30px 20px;margin-bottom:20px;overflow:hidden;position:relative;">

        <!-- Room decorations -->
        <div style="position:absolute;top:0;left:0;right:0;height:40px;
                    background:linear-gradient(90deg,#1e3a5f,#1a2744,#1e3a5f);
                    border-bottom:2px solid rgba(99,102,241,.3);
                    display:flex;align-items:center;justify-content:center;gap:8px;">
          <span style="font-size:10px;color:rgba(255,255,255,.4);letter-spacing:.1em;text-transform:uppercase;">Sistema 180 HQ · Sala de Reuniones · Planta Ejecutiva</span>
        </div>

        <!-- Windows left -->
        <div style="position:absolute;left:10px;top:50px;display:flex;flex-direction:column;gap:6px;">
          ${[0,1,2].map(()=>`
            <div style="width:20px;height:30px;background:rgba(147,197,253,.08);border:1px solid rgba(147,197,253,.15);
                        border-radius:3px;position:relative;overflow:hidden;">
              <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(147,197,253,.1) 0%,transparent 50%);"></div>
            </div>
          `).join('')}
        </div>
        <!-- Windows right -->
        <div style="position:absolute;right:10px;top:50px;display:flex;flex-direction:column;gap:6px;">
          ${[0,1,2].map(()=>`
            <div style="width:20px;height:30px;background:rgba(147,197,253,.08);border:1px solid rgba(147,197,253,.15);
                        border-radius:3px;"></div>
          `).join('')}
        </div>

        <!-- Screen/TV at front -->
        <div style="margin:50px auto 20px;width:fit-content;text-align:center;">
          <div style="display:inline-block;padding:10px 30px;background:rgba(99,102,241,.12);
                      border:2px solid rgba(99,102,241,.3);border-radius:8px;
                      font-size:12px;font-weight:800;color:rgba(99,102,241,.8);letter-spacing:.05em;">
            🖥️ SISTEMA 180 — REUNIÓN DIARIA
          </div>
          <div style="width:4px;height:16px;background:rgba(99,102,241,.3);margin:0 auto;"></div>
          <div style="width:60px;height:6px;background:rgba(99,102,241,.2);border-radius:3px;margin:0 auto;"></div>
        </div>

        <!-- HEAD OF TABLE — ORQUESTADORES -->
        <div style="display:flex;justify-content:center;gap:20px;margin-bottom:8px;">
          ${DEPTS[0].agents.map(a => `
            <div onclick="window._openAgentModal('${a.name}')" title="${a.name} — ${a.role}"
              style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;
                     transition:transform .15s;" onmouseover="this.style.transform='scale(1.15)'"
                     onmouseout="this.style.transform='scale(1)'">
              ${pixelAgent({...a, deptColor: DEPTS[0].color, dept: DEPTS[0].dept, floor: DEPTS[0].floor}, 52)}
              <span style="font-size:9px;font-weight:800;color:${DEPTS[0].color};">${a.name}</span>
              <span style="font-size:8px;color:var(--text-muted);">${a.role}</span>
            </div>
          `).join('')}
        </div>

        <!-- THE TABLE -->
        <div style="position:relative;margin:0 40px;">
          <!-- Table surface -->
          <div style="background:linear-gradient(180deg,#1e3a2f,#163028);
                      border:2px solid rgba(16,185,129,.25);border-radius:16px;
                      padding:20px;box-shadow:0 8px 32px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.05);">

            <!-- Table top reflection -->
            <div style="position:absolute;top:2px;left:20px;right:20px;height:3px;
                        background:linear-gradient(90deg,transparent,rgba(255,255,255,.06),transparent);
                        border-radius:2px;"></div>

            <!-- CENTER TABLE CONTENT -->
            <div style="text-align:center;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:12px;">
              <div style="font-size:11px;color:rgba(255,255,255,.25);letter-spacing:.08em;">MESA DE DIRECCIÓN · SISTEMA 180</div>
            </div>

            <!-- LEFT SIDE AGENTS (pairs) -->
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">

              <!-- LEFT COLUMN -->
              <div style="display:flex;flex-direction:column;gap:10px;width:45%;">
                ${DEPTS.slice(1,5).map(d => `
                  <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                    <span style="font-size:9px;color:${d.color};font-weight:700;width:100%;margin-bottom:2px;">${d.icon} ${d.dept}</span>
                    ${d.agents.slice(0, Math.ceil(d.agents.length/2)).map(a => `
                      <div onclick="window._openAgentModal('${a.name}')" title="${a.name}"
                        style="cursor:pointer;transition:transform .15s;display:flex;flex-direction:column;align-items:center;"
                        onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">
                        ${pixelAgent({...a, deptColor: d.color, dept: d.dept, floor: d.floor}, 34)}
                        <span style="font-size:7px;color:${a.status==='ready'?d.color:'var(--text-muted)'};font-weight:700;">${a.name}</span>
                      </div>
                    `).join('')}
                  </div>
                `).join('')}
              </div>

              <!-- TABLE CENTERPIECE -->
              <div style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:0 10px;">
                <div style="width:2px;height:60px;background:linear-gradient(180deg,transparent,rgba(16,185,129,.4),transparent);"></div>
                <div style="width:40px;height:40px;border-radius:50%;background:rgba(16,185,129,.08);
                            border:2px solid rgba(16,185,129,.2);display:flex;align-items:center;justify-content:center;
                            font-size:16px;">🏢</div>
                <div style="font-size:9px;color:rgba(16,185,129,.5);text-align:center;font-weight:700;letter-spacing:.05em;">S180</div>
                <div style="width:2px;height:60px;background:linear-gradient(180deg,rgba(16,185,129,.4),transparent);"></div>
              </div>

              <!-- RIGHT COLUMN -->
              <div style="display:flex;flex-direction:column;gap:10px;width:45%;align-items:flex-end;">
                ${DEPTS.slice(5).map(d => `
                  <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:flex-end;">
                    <span style="font-size:9px;color:${d.color};font-weight:700;width:100%;text-align:right;margin-bottom:2px;">${d.icon} ${d.dept}</span>
                    ${d.agents.map(a => `
                      <div onclick="window._openAgentModal('${a.name}')" title="${a.name}"
                        style="cursor:pointer;transition:transform .15s;display:flex;flex-direction:column;align-items:center;"
                        onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">
                        ${pixelAgent({...a, deptColor: d.color, dept: d.dept, floor: d.floor}, 34)}
                        <span style="font-size:7px;color:${a.status==='ready'?d.color:'var(--text-muted)'};font-weight:700;">${a.name}</span>
                      </div>
                    `).join('')}
                  </div>
                `).join('')}
              </div>
            </div>

          </div><!-- /table surface -->
        </div><!-- /table wrapper -->

        <!-- FOOT OF TABLE — remaining Planta 2 agents -->
        <div style="display:flex;justify-content:center;gap:12px;margin-top:12px;flex-wrap:wrap;">
          ${DEPTS.slice(1,5).map(d =>
            d.agents.slice(Math.ceil(d.agents.length/2)).map(a => `
              <div onclick="window._openAgentModal('${a.name}')" title="${a.name} — ${a.role}"
                style="display:flex;flex-direction:column;align-items:center;gap:3px;cursor:pointer;
                       transition:transform .15s;" onmouseover="this.style.transform='scale(1.15)'"
                       onmouseout="this.style.transform='scale(1)'">
                ${pixelAgent({...a, deptColor: d.color, dept: d.dept, floor: d.floor}, 36)}
                <span style="font-size:8px;font-weight:700;color:${a.status==='ready'?d.color:'var(--text-muted)'};">${a.name}</span>
              </div>
            `).join('')
          ).join('')}
        </div>

      </div><!-- /office room -->

      <!-- Legend -->
      <div style="display:flex;gap:16px;flex-wrap:wrap;justify-content:center;margin-bottom:20px;font-size:11px;color:var(--text-muted);">
        <span>● Verde = operativo</span>
        <span>● Amarillo = en construcción</span>
        <span>🖱️ Clic en cualquier agente para abrir Chat 1-on-1 privado</span>
      </div>

      <!-- Live Meeting Terminal -->
      <div id="live-meeting-box" style="display:none;margin-bottom:20px;background:rgba(0,0,0,0.6);border:1px solid var(--accent);border-radius:16px;padding:20px;">
         <div style="font-size:14px;font-weight:800;color:var(--accent);margin-bottom:12px;">📡 Sala de Reuniones Múltiple (LIVE)</div>
         <div id="meeting-terminal" style="height:200px;overflow-y:auto;font-family:monospace;font-size:12px;color:var(--text-secondary);margin-bottom:12px;"></div>
         <div style="display:flex;gap:8px;">
            <input type="text" id="meeting-input" placeholder="Escribe al equipo de la junta..." style="flex:1;background:rgba(255,255,255,0.05);border:none;border-radius:8px;padding:12px;color:#fff;font-size:12px;outline:none;">
            <button onclick="window._sendMeeting()" style="background:var(--accent);border:none;border-radius:8px;padding:0 24px;color:#fff;font-size:12px;font-weight:700;cursor:pointer;">Orden a 57 Agentes</button>
         </div>
      </div>

      <!-- Quick stats row -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;">
        ${DEPTS.map(d => {
          const r = d.agents.filter(a=>a.status==='ready').length;
          const t = d.agents.length;
          return `
            <div style="padding:10px;background:rgba(255,255,255,.03);border-radius:8px;
                        border:1px solid rgba(255,255,255,.06);border-left:2px solid ${d.color};">
              <div style="font-size:12px;font-weight:700;margin-bottom:4px;">${d.icon} ${d.dept}</div>
              <div style="font-size:10px;color:var(--text-muted);">${d.floor}</div>
              <div style="margin-top:6px;background:rgba(255,255,255,.05);border-radius:3px;height:3px;">
                <div style="background:${d.color};height:3px;border-radius:3px;width:${t>0?Math.round(r/t*100):0}%;"></div>
              </div>
              <div style="font-size:10px;color:${d.color};font-weight:700;margin-top:4px;">${r}/${t} listos</div>
            </div>`;
        }).join('')}
      </div>

      <!-- Agent Pixel (Luna) Terminal -->
      <div style="margin-top:20px;background:linear-gradient(180deg, rgba(15,23,42,0.8), rgba(30,41,59,0.8));border:1px solid rgba(244,114,182,.3);border-radius:16px;padding:20px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg, #f472b6, #db2777);"></div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;flex-wrap:wrap;gap:16px;">
          <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:48px;height:48px;border-radius:10px;background:rgba(244,114,182,.1);border:1px solid rgba(244,114,182,.2);display:flex;align-items:center;justify-content:center;box-shadow:0 0 15px rgba(244,114,182,.2);">
              ${pixelAgent({status:'ready', deptColor:'#f472b6'}, 40)}
            </div>
            <div>
              <div style="font-size:16px;font-weight:900;color:#f472b6;letter-spacing:1px;text-transform:uppercase;">🎯 AGENT PIXEL · LUNA</div>
              <div style="font-size:11px;color:var(--text-muted);font-family:monospace;">MONITOR DE TRACKING & CONVERSIONES API (CAPI)</div>
            </div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:24px;font-weight:900;color:${getScoreColor(pixelStatus.score)};">${pixelStatus.score}%</div>
            <div style="font-size:10px;color:var(--text-muted);text-transform:uppercase;">INTEGRIDAD SISTEMA</div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;">
          ${pixelStatus.checks.map(c => `
            <div style="background:rgba(255,255,255,.03);border:1px solid ${c.ok ? 'rgba(16,185,129,.2)' : 'rgba(239,68,68,.2)'};border-radius:8px;padding:12px;border-left:3px solid ${c.ok ? 'var(--green)' : 'var(--red)'};">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-size:11px;font-weight:700;color:var(--text-secondary);">${c.name}</span>
                <span style="font-size:12px;">${c.ok ? '✅' : '❌'}</span>
              </div>
              <div style="font-size:10px;color:${c.ok ? 'var(--green)' : 'var(--red)'};font-family:monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${c.value}">
                ${c.value}
              </div>
            </div>
          `).join('')}
        </div>

        ${pixelStatus.score < 100 ? `
          <div style="margin-top:16px;padding:10px;background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.3);border-radius:8px;font-size:11px;color:var(--orange);display:flex;align-items:center;gap:8px;">
            <span>⚠️</span>
            <span>Agent Luna detecta anomalías o falta de configuración en los rastreadores. Por favor, revisa el panel de Settings > Integraciones para configurar el Pixel.</span>
          </div>
        ` : `
          <div style="margin-top:16px;padding:10px;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);border-radius:8px;font-size:11px;color:var(--green);display:flex;align-items:center;gap:8px;">
            <span>🟢</span>
            <span>Agent Luna reporta: Todos los sistemas de tracking nominales. CAPI fluyendo correctamente.</span>
          </div>
        `}
      </div>
    </div>

    <!-- ═══════════════════════════════════ -->
    <!-- VISTA 2: EL EDIFICIO               -->
    <!-- ═══════════════════════════════════ -->
    <div id="despacho-view-building" style="display:none;">

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">

        <!-- Building visual -->
        <div>
          <div style="font-size:13px;font-weight:800;margin-bottom:12px;">🏗️ Planos del Edificio</div>

          <!-- Building graphic -->
          <div style="background:linear-gradient(180deg,#0f172a,#1e293b);border:1px solid rgba(255,255,255,.08);
                      border-radius:16px;padding:20px;text-align:center;margin-bottom:16px;">
            ${['Penthouse','Planta 4','Planta 3','Planta 2','Planta 1','Subsuelo'].map((floor, i) => {
              const colors = ['#f59e0b','#f59e0b','#6366f1','#06b6d4','#10b981','#6b7280'];
              const icons  = ['👑','🧠','📋','⚙️','🔧','🖥️'];
              const agents = ALL_AGENTS.filter(a => a.floor === floor);
              const ready  = agents.filter(a=>a.status==='ready').length;
              const width  = [80,70,75,100,65,60][i];
              return `
                <div style="margin:0 auto ${i<5?'2px':'0'};width:${width}%;
                            background:${colors[i]}${i===3?'22':'18'};
                            border:1px solid ${colors[i]}33;border-radius:6px 6px ${i===5?'6px':'0'} ${i===5?'6px':'0'};
                            padding:8px 12px;display:flex;align-items:center;justify-content:space-between;">
                  <span style="font-size:12px;">${icons[i]} <strong style="color:${colors[i]};font-size:11px;">${floor}</strong></span>
                  ${agents.length > 0
                    ? `<span style="font-size:10px;color:${colors[i]};font-weight:700;">${ready}/${agents.length} agentes</span>`
                    : `<span style="font-size:10px;color:rgba(255,255,255,.3);">infra</span>`}
                </div>`;
            }).join('')}
            <!-- Base -->
            <div style="width:110%;margin-left:-5%;height:6px;background:rgba(255,255,255,.06);border-radius:0 0 6px 6px;margin-top:1px;"></div>
          </div>

          <!-- Progress bars by floor -->
          <div style="font-size:12px;font-weight:800;margin-bottom:10px;color:var(--text-secondary);">Progreso por planta</div>
          ${buildingHTML()}
        </div>

        <!-- All agents list by dept -->
        <div>
          <div style="font-size:13px;font-weight:800;margin-bottom:12px;">👥 Todos los Agentes</div>
          <div style="max-height:600px;overflow-y:auto;display:flex;flex-direction:column;gap:12px;">
            ${byDept.map(d => `
              <div>
                <div style="font-size:11px;font-weight:800;color:${d.color};margin-bottom:6px;
                            padding:4px 8px;background:${d.color}11;border-radius:5px;border-left:2px solid ${d.color};">
                  ${d.icon} ${d.dept} · ${d.floor}
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;">
                  ${d.agents.map(a => `
                    <div onclick="window._openAgentModal('${a.name}')"
                      style="display:flex;align-items:center;gap:6px;padding:5px 10px;cursor:pointer;
                             background:${a.status==='ready'?d.color+'15':'rgba(255,255,255,.03)'};
                             border:1px solid ${a.status==='ready'?d.color+'33':'rgba(255,255,255,.06)'};
                             border-radius:20px;transition:all .15s;"
                      onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                      ${pixelAgent({...a, deptColor: d.color, dept: d.dept, floor: d.floor}, 24)}
                      <div>
                        <div style="font-size:11px;font-weight:700;color:${a.status==='ready'?'var(--text-primary)':'var(--text-muted)'};">${a.emoji} ${a.name}</div>
                        <div style="font-size:9px;color:${d.color};">${a.role}</div>
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        </div>

      </div>
    </div>
  `;

  // ── View toggle ────────────────────────────────────────────
  window._dView = (view) => {
    ['table', 'building'].forEach(v => {
      const el = document.getElementById(`despacho-view-${v}`);
      if (el) el.style.display = v === view ? 'block' : 'none';
    });
    ['table', 'building'].forEach(v => {
      const btn = document.getElementById(`btn-view-${v}`);
      if (btn) {
        btn.style.background = v === view ? 'var(--accent)' : 'rgba(255,255,255,.06)';
        btn.style.color = v === view ? '#fff' : 'var(--text-secondary)';
      }
    });
  };

  // ── Meeting modal ──────────────────────────────────────────
  window._openMeetingModal = () => {
    const existing = document.getElementById('meeting-modal');
    if (existing) existing.remove();

    // Preset agent selections per meeting type
    const PRESETS = {
      daily:     ALL_AGENTS.filter(a => ['CEO','COO','CMO','Sales Head','Content Head','Finance Head','Client Success','Marketplace'].includes(a.role)).map(a => a.name),
      semanal:   ALL_AGENTS.filter(a => DEPTS[0].agents.includes(ALL_AGENTS.find(x => x.name === a.name)) || DEPTS[1].agents.includes(ALL_AGENTS.find(x => x.name === a.name))).map(a => a.name),
      ventas:    ['Roberto','Javier','Ares','Natalia','Gonzalo','Marcos'],
      emergencia:['Alejandro','Rafael','Valentina'],
      custom:    [],
    };

    const presetLabels = {
      daily:     'Daily standup',
      semanal:   'Revisión semanal',
      ventas:    'Reunión de ventas',
      emergencia:'Reunión de emergencia',
      custom:    'Reunión custom',
    };

    const byDeptForModal = DEPTS.map(d => ({
      ...d,
      agents: d.agents.map(a => ({ ...a, deptColor: d.color, dept: d.dept, floor: d.floor }))
    }));

    const modal = document.createElement('div');
    modal.id = 'meeting-modal';
    modal.style.cssText = `
      position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:3000;
      display:flex;align-items:center;justify-content:center;padding:20px;overflow-y:auto;
    `;

    const checkboxRows = byDeptForModal.map(d => `
      <div style="margin-bottom:12px;">
        <div style="font-size:10px;font-weight:800;color:${d.color};
                    padding:3px 8px;background:${d.color}18;border-radius:4px;
                    border-left:2px solid ${d.color};margin-bottom:6px;">
          ${d.icon} ${d.dept}
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;">
          ${d.agents.map(a => `
            <label style="display:flex;align-items:center;gap:5px;cursor:pointer;
                          padding:4px 8px;border-radius:16px;
                          background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);
                          font-size:11px;font-weight:600;color:var(--text-secondary);
                          transition:all .15s;"
                   onmouseover="this.style.borderColor='${d.color}44'"
                   onmouseout="this.style.borderColor='rgba(255,255,255,.07)'">
              <input type="checkbox" class="meeting-agent-cb" value="${a.name}"
                     style="accent-color:${d.color};cursor:pointer;"
                     data-color="${d.color}">
              <span style="color:${d.color};">${a.emoji}</span> ${a.name}
              <span style="font-size:9px;color:var(--text-muted);">${a.role}</span>
            </label>
          `).join('')}
        </div>
      </div>
    `).join('');

    modal.innerHTML = `
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:20px;
                  padding:28px;width:100%;max-width:640px;position:relative;
                  border-top:3px solid var(--accent);max-height:90vh;overflow-y:auto;">

        <button onclick="document.getElementById('meeting-modal').remove()"
          style="position:absolute;top:16px;right:16px;background:rgba(255,255,255,.08);
                 border:none;color:var(--text-muted);width:32px;height:32px;border-radius:50%;
                 cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;">×</button>

        <div style="font-size:20px;font-weight:900;margin-bottom:4px;">📣 Convocar Reunión</div>
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:20px;">Sistema 180 HQ · Sala de Reuniones Ejecutiva</div>

        <!-- Tipo de reunión -->
        <div style="margin-bottom:18px;">
          <label style="font-size:11px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:8px;">Tipo de reunión</label>
          <div style="display:flex;flex-wrap:wrap;gap:6px;" id="meeting-type-btns">
            ${Object.entries(presetLabels).map(([key, label]) => `
              <button onclick="window._meetingSelectType('${key}')"
                id="mtype-${key}"
                style="padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;cursor:pointer;
                       background:${key==='daily'?'var(--accent)':'rgba(255,255,255,.06)'};
                       color:${key==='daily'?'#fff':'var(--text-secondary)'};
                       border:1px solid ${key==='daily'?'var(--accent)':'rgba(255,255,255,.1)'};
                       transition:all .15s;">
                ${label}
              </button>
            `).join('')}
          </div>
        </div>

        <!-- Checkboxes por dpto -->
        <div style="margin-bottom:18px;">
          <label style="font-size:11px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:8px;">
            Asistentes
            <span id="meeting-count" style="margin-left:8px;color:var(--accent);font-size:10px;"></span>
          </label>
          <div style="max-height:280px;overflow-y:auto;padding-right:4px;">
            ${checkboxRows}
          </div>
        </div>

        <!-- Orden del día -->
        <div style="margin-bottom:20px;">
          <label style="font-size:11px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:8px;">Orden del día</label>
          <textarea id="meeting-agenda"
            placeholder="Ej: Revisión KPIs semana · Bloqueos activos · Próximos lanzamientos..."
            style="width:100%;min-height:80px;background:rgba(255,255,255,.04);border:1px solid var(--border);
                   border-radius:10px;padding:10px 12px;color:var(--text-primary);font-size:12px;
                   resize:vertical;font-family:inherit;box-sizing:border-box;outline:none;"
            onfocus="this.style.borderColor='var(--accent)'" onblur="this.style.borderColor='var(--border)'">
          </textarea>
        </div>

        <!-- CTA -->
        <button onclick="window._launchMeeting()"
          style="width:100%;padding:12px;background:var(--accent);color:#fff;border:none;
                 border-radius:12px;cursor:pointer;font-size:14px;font-weight:800;
                 transition:opacity .15s;"
          onmouseover="this.style.opacity='.85'" onmouseout="this.style.opacity='1'">
          🚀 Iniciar reunión
        </button>

        <!-- Acta generada -->
        <div id="meeting-acta" style="display:none;margin-top:20px;
             padding:16px;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.2);
             border-radius:12px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
            <span style="font-size:12px;font-weight:800;color:var(--green);">📋 Acta de reunión</span>
            <button onclick="window._copyActa()"
              style="padding:4px 12px;background:rgba(16,185,129,.15);color:var(--green);
                     border:1px solid rgba(16,185,129,.3);border-radius:8px;cursor:pointer;
                     font-size:11px;font-weight:700;">
              Copiar acta
            </button>
          </div>
          <pre id="meeting-acta-text"
            style="font-family:monospace;font-size:11px;color:var(--text-primary);
                   white-space:pre-wrap;word-break:break-word;margin:0;line-height:1.6;">
          </pre>
        </div>

      </div>
    `;

    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });

    window._launchMeeting = () => {
        const agenda = document.getElementById('meeting-agenda').value || "Standup General";
        modal.remove();
        document.getElementById('live-meeting-box').style.display = 'block';
        currentMeeting = true;
        const term = document.getElementById('meeting-terminal');
        term.innerHTML = `<div style="color:var(--accent);margin-bottom:8px;"><strong>Junta Ejecutiva Iniciada.</strong><br/>Agenda: <em>${agenda}</em></div>`;
        if(ws) ws.send(JSON.stringify({type: 'meeting', content: agenda}));
    };

    window._sendMeeting = () => {
        const inp = document.getElementById('meeting-input');
        if(!inp.value.trim() || !ws) return;
        const term = document.getElementById('meeting-terminal');
        term.innerHTML += `<div style="margin:4px 0;color:#fff;"><strong>[CEO - Tú]</strong> ${inp.value}</div>`;
        ws.send(JSON.stringify({ type: 'meeting', content: inp.value }));
        inp.value = '';
        term.scrollTop = term.scrollHeight;
    };

    // Select daily preset by default
    window._meetingSelectType('daily');

    // Update count on checkbox change
    modal.querySelectorAll('.meeting-agent-cb').forEach(cb => {
      cb.addEventListener('change', () => {
        const checked = modal.querySelectorAll('.meeting-agent-cb:checked').length;
        const countEl = document.getElementById('meeting-count');
        if (countEl) countEl.textContent = `${checked} seleccionados`;
      });
    });

    // ── Preset selector ──────────────────────────────────────
    window._meetingSelectType = (type) => {
      const preset = PRESETS[type] || [];
      modal.querySelectorAll('.meeting-agent-cb').forEach(cb => {
        cb.checked = preset.includes(cb.value);
      });
      Object.keys(presetLabels).forEach(k => {
        const btn = document.getElementById(`mtype-${k}`);
        if (!btn) return;
        btn.style.background = k === type ? 'var(--accent)' : 'rgba(255,255,255,.06)';
        btn.style.color = k === type ? '#fff' : 'var(--text-secondary)';
        btn.style.borderColor = k === type ? 'var(--accent)' : 'rgba(255,255,255,.1)';
      });
      const checked = preset.length;
      const countEl = document.getElementById('meeting-count');
      if (countEl) countEl.textContent = `${checked} seleccionados`;
    };

    // ── Launch meeting — generate acta ────────────────────────
    window._launchMeeting = async () => {
      const checked = [...modal.querySelectorAll('.meeting-agent-cb:checked')].map(cb => cb.value);
      if (checked.length === 0) {
        alert('Selecciona al menos un agente para la reunión.');
        return;
      }
      const agenda = document.getElementById('meeting-agenda').value.trim() || 'Sin orden del día especificado.';
      const now = new Date();
      const fecha = now.toLocaleDateString('es-ES', { weekday:'long', year:'numeric', month:'long', day:'numeric' });
      const hora  = now.toLocaleTimeString('es-ES', { hour:'2-digit', minute:'2-digit' });

      const asistentesDetalle = checked.map(name => {
        const ag = ALL_AGENTS.find(a => a.name === name);
        return ag ? `  • ${ag.emoji} ${ag.name} — ${ag.role} (${ag.dept})` : `  • ${name}`;
      }).join('\n');

      const actaText = `ACTA DE REUNIÓN — SISTEMA 180
${'═'.repeat(45)}
Fecha:      ${fecha}
Hora:       ${hora}
Lugar:      Sala de Reuniones Ejecutiva · HQ S180
Asistentes: ${checked.length} agentes

${'─'.repeat(45)}
ASISTENTES
${'─'.repeat(45)}
${asistentesDetalle}

${'─'.repeat(45)}
ORDEN DEL DÍA
${'─'.repeat(45)}
${agenda.split('\n').map(l => `  ${l}`).join('\n')}

${'─'.repeat(45)}
ACUERDOS
${'─'.repeat(45)}
  [ Pendiente de completar tras la reunión ]

${'─'.repeat(45)}
Acta generada por Sistema 180 · ${hora}
${'═'.repeat(45)}`;

      const actaDiv  = document.getElementById('meeting-acta');
      const actaPre  = document.getElementById('meeting-acta-text');
      if (!actaDiv || !actaPre) return;

      actaPre.textContent = '';
      actaDiv.style.display = 'block';
      actaDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

      // Typewriter effect
      let i = 0;
      const speed = 8;
      const type = () => {
        if (i < actaText.length) {
          actaPre.textContent += actaText[i++];
          setTimeout(type, speed);
        }
      };

      // Try AI-powered acta first
      if (aiService.hasKey()) {
        actaPre.textContent = '🤖 Generando acta inteligente con Gemini 2.5 Flash...\n';
        try {
          const attendeesData = checked.map(agName => {
            const ag = ALL_AGENTS.find(a => a.name === agName);
            return ag ? { name: ag.name, role: ag.role, dept: ag.dept } : { name: agName, role: 'Agente', dept: 'General' };
          });
          const aiActa = await aiService.meetingActa(agenda, attendeesData);
          const fullActa = `ACTA DE REUNIÓN — SISTEMA 180\n${'═'.repeat(45)}\nFecha:      ${fecha}\nHora:       ${hora}\nAsistentes: ${checked.length} agentes\n${'═'.repeat(45)}\n\n${aiActa}\n\n${'─'.repeat(45)}\nGenerado por Gemini 2.5 Flash · ${hora}\n${'═'.repeat(45)}`;
          actaPre.textContent = '';
          window._currentActa = fullActa;
          let j = 0;
          const typeAI = () => {
            if (j < fullActa.length) {
              actaPre.textContent += fullActa[j++];
              setTimeout(typeAI, speed);
            }
          };
          typeAI();
        } catch (e) {
          // Fallback to static acta
          actaPre.textContent = '';
          type();
        }
      } else {
        type();
      }

      // Store full text for copy
      window._currentActa = actaText;
    };

    // ── Copy acta ─────────────────────────────────────────────
    window._copyActa = () => {
      if (!window._currentActa) return;
      navigator.clipboard.writeText(window._currentActa).then(() => {
        const btn = modal.querySelector('button[onclick="window._copyActa()"]');
        if (btn) {
          const prev = btn.textContent;
          btn.textContent = 'Copiado!';
          setTimeout(() => { btn.textContent = prev; }, 1500);
        }
      }).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = window._currentActa || '';
        ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none;';
        document.body.appendChild(ta);
        ta.focus(); ta.select();
        try { ta.setSelectionRange(0, 99999); } catch(_) {}
        navigator.clipboard?.writeText(ta.value).catch(()=>{});
        ta.remove();
      });
    };
  };
}
