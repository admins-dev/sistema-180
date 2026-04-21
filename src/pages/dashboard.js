// ═══════════════════════════════════════════════
// Dashboard HQ — SISTEMA180 Nerve Center
// José María Moreno + Ares Villalba — Marbella
// ═══════════════════════════════════════════════
import { storage } from '../services/storage.js';
import { navigate } from '../main.js';
import { renderEditor } from './editor.js';
import { renderDespacho } from './despacho.js';

// ── Estado del negocio ──────────────────────────
function getBizData() {
  const saved = localStorage.getItem('s180_biz');
  const defaults = {
    mrr: 0,
    mrr_goal: 90000,
    clients_active: 0,
    clients_goal: 300,
    leads: 0,
    proposals: 0,
    closed_month: 0,
    affiliates_active: 0,
    affiliate_rev: 0,
    content_videos_week: 0,
    content_clients: 0,
    last_sale_date: '-',
    last_sale_amount: 0,
    // Finanzas Reales
    cashflow_in: 0,
    cashflow_out: 0,
    // Fanbasis metrics
    fanbasis_followers: 0,
    fanbasis_revenue: 0,
    fanbasis_engagement: 0,
    revenue_history: [0, 0, 0, 0, 0, 0, 0],
    pipeline: [],
    recent_activity: [
      { time:'ahora', msg:'🚀 Sistema180 arrancado — preparado para captar clientes', type:'content' },
      { time:'ahora', msg:'🐝 ClaudeFlow v3.5.78 conectado — 57 agentes listos', type:'content' },
      { time:'ahora', msg:'📋 Pipeline de ventas vacío — a por el primer cliente', type:'lead' },
    ],
  };
  try {
    const s = JSON.parse(saved || '{}');
    return { ...defaults, ...s };
  } catch { return defaults; }
}

function pct(v, t) { return Math.min(100, Math.round((v / t) * 100)); }

// ── Micro sparkline SVG ─────────────────────────
function sparkline(data, color = 'var(--green)', svgW = 100, h = 32) {
  const w = svgW;
  const max = Math.max(...data, 1);
  const pts = data.map((v, i) =>
    `${(i / (data.length - 1)) * w},${h - (v / max) * (h - 4) - 2}`
  ).join(' ');
  const last = data[data.length - 1];
  const lx = w, ly = h - (last / max) * (h - 4) - 2;
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="overflow:visible">
    <defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${color}" stop-opacity=".3"/>
      <stop offset="100%" stop-color="${color}" stop-opacity="0"/>
    </linearGradient></defs>
    <polygon points="${pts} ${w},${h} 0,${h}" fill="url(#sg)"/>
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="${lx}" cy="${ly}" r="3.5" fill="${color}" filter="drop-shadow(0 0 4px ${color})"/>
  </svg>`;
}

// ── Revenue bar chart SVG ───────────────────────
function revenueChart(data, labels) {
  const max = Math.max(...data, 1);
  const w = 100, barW = 11, gap = 4;
  const bars = data.map((v, i) => {
    const h = Math.round((v / max) * 60);
    const x = i * (barW + gap);
    const isLast = i === data.length - 1;
    const color = isLast ? 'var(--green)' : 'rgba(99,102,241,.5)';
    return `<rect x="${x}" y="${60 - h}" width="${barW}" height="${h}" rx="3" fill="${color}" ${isLast ? 'filter="drop-shadow(0 0 6px var(--green))"' : ''}/>
    <text x="${x + barW / 2}" y="76" text-anchor="middle" fill="var(--text-muted)" font-size="7">${labels[i]}</text>`;
  }).join('');
  return `<svg width="${data.length * (barW + gap)}" height="84" viewBox="0 0 ${data.length * (barW + gap)} 84" style="overflow:visible">${bars}</svg>`;
}

// ── El Edificio visual ──────────────────────────
function edificioHTML(_biz) {
  const floors = [
    { floor: 'PENTHOUSE', icon: '👑', label: 'José + Ares', sub: 'Fundadores', agents: 2, color: '#f59e0b', active: true },
    { floor: 'PLANTA 4',  icon: '🧠', label: 'Orquestadores IA', sub: 'CEO · COO · CMO', agents: 3, color: 'var(--accent)', active: true },
    { floor: 'PLANTA 3',  icon: '📋', label: 'Jefes de Dpto.', sub: 'Sales · Content · Finance · CS · Mkt', agents: 5, color: 'var(--cyan)', active: true },
    { floor: 'PLANTA 2',  icon: '⚙️', label: 'Trabajadores IA', sub: '33 agentes especializados', agents: 33, color: 'var(--green)', active: true },
    { floor: 'PLANTA 1',  icon: '📊', label: 'Pixel & Tracking', sub: 'Luna · Omar · Daniela', agents: 3, color: 'var(--pink)', active: true },
    { floor: 'SUBSUELO',  icon: '🐝', label: 'Ruflo Swarm + IDE', sub: '8 enjambre + 3 arquitectos', agents: 11, color: '#a78bfa', active: true },
  ];
  return floors.map(f => `
    <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:8px;
                background:${f.active ? 'rgba(255,255,255,.04)' : 'rgba(255,255,255,.02)'};
                border:1px solid ${f.active ? 'rgba(255,255,255,.08)' : 'rgba(255,255,255,.03)'};
                margin-bottom:4px;opacity:${f.active ? 1 : 0.55};">
      <div style="font-size:18px;min-width:28px;text-align:center;">${f.icon}</div>
      <div style="flex:1;min-width:0;">
        <div style="font-size:10px;font-weight:800;color:${f.color};letter-spacing:.06em;">${f.floor}</div>
        <div style="font-size:12px;font-weight:600;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${f.label}</div>
        <div style="font-size:10px;color:var(--text-muted);">${f.sub}</div>
      </div>
      ${f.agents > 0 ? `<div style="min-width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,.06);
                              border:1px solid rgba(255,255,255,.1);display:flex;align-items:center;
                              justify-content:center;font-size:11px;font-weight:800;color:${f.color};">
        ${f.agents}
      </div>` : '<div style="min-width:28px;"></div>'}
    </div>
  `).join('');
}

// ── Pipeline kanban ─────────────────────────────
function pipelineKanban(pipeline) {
  const cols = [
    { key: 'cold',      label: 'Frío',       icon: '❄️', color: 'var(--text-muted)' },
    { key: 'contacted', label: 'Contactado',  icon: '📞', color: 'var(--cyan)' },
    { key: 'proposal',  label: 'Propuesta',   icon: '📄', color: 'var(--orange)' },
    { key: 'closed',    label: 'Cerrado ✅',  icon: '💰', color: 'var(--green)' },
  ];
  return `<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
    ${cols.map(col => {
      const items = pipeline.filter(p => p.status === col.key);
      const total = items.reduce((s, p) => s + p.amount, 0);
      return `
        <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <div style="font-size:11px;font-weight:800;color:${col.color};letter-spacing:.06em;">${col.icon} ${col.label.toUpperCase()}</div>
            <div style="font-size:10px;color:var(--text-muted);">${items.length} · ${total}€</div>
          </div>
          ${items.map(p => `
            <div style="background:var(--bg-glass);border:1px solid var(--border);border-radius:8px;
                        padding:8px 10px;margin-bottom:6px;cursor:pointer;"
                 onmouseenter="this.style.background='var(--bg-card-hover)'"
                 onmouseleave="this.style.background='var(--bg-glass)'">
              <div style="font-size:12px;font-weight:600;margin-bottom:2px;">${p.name}</div>
              <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);">
                <span style="color:${col.color};font-weight:700;">${p.amount}€</span>
                ${p.days > 0 ? `<span>${p.days}d</span>` : ''}
              </div>
            </div>
          `).join('')}
          ${items.length === 0 ? `<div style="text-align:center;padding:16px;font-size:11px;color:var(--text-muted);">vacío</div>` : ''}
        </div>
      `;
    }).join('')}
  </div>`;
}

// ── Agentes grid compacto ───────────────────────
function agentesGrid() {
  const agents = [
    // Orquestadores
    { name:'CEO Agent', dept:'orch', status:'ready' },
    { name:'COO Agent', dept:'orch', status:'ready' },
    { name:'CMO Agent', dept:'orch', status:'ready' },
    // Jefes
    { name:'Sales Head', dept:'head', status:'ready' },
    { name:'Content Head', dept:'head', status:'ready' },
    { name:'Finance Head', dept:'head', status:'building' },
    { name:'Client Success', dept:'head', status:'building' },
    { name:'Marketplace Head', dept:'head', status:'building' },
    // Edición
    { name:'Edit Orch', dept:'edit', status:'building' },
    { name:'Cut Agent', dept:'edit', status:'building' },
    { name:'Audio Agent', dept:'edit', status:'building' },
    { name:'Color Agent', dept:'edit', status:'building' },
    { name:'Subtitle', dept:'edit', status:'building' },
    { name:'Zoom Agent', dept:'edit', status:'building' },
    { name:'Thumbnail', dept:'edit', status:'building' },
    { name:'Format Agent', dept:'edit', status:'building' },
    { name:'Quality', dept:'edit', status:'building' },
    { name:'Publisher', dept:'edit', status:'building' },
    // Copy
    { name:'Copy Orch', dept:'copy', status:'building' },
    { name:'Script Agent', dept:'copy', status:'ready' },
    { name:'Ads Agent', dept:'copy', status:'building' },
    { name:'Caption Agent', dept:'copy', status:'building' },
    { name:'Email Agent', dept:'copy', status:'building' },
    { name:'WhatsApp Agt', dept:'copy', status:'building' },
    // Ventas
    { name:'Sales Orch', dept:'sales', status:'building' },
    { name:'Lead Scout', dept:'sales', status:'building' },
    { name:'SDR Agent', dept:'sales', status:'ready' },
    { name:'CRM Agent', dept:'sales', status:'building' },
    { name:'Closer Support', dept:'sales', status:'building' },
    // Clientes
    { name:'Client Orch', dept:'client', status:'building' },
    { name:'Onboarding', dept:'client', status:'building' },
    { name:'Support Agent', dept:'client', status:'building' },
    { name:'Billing Agent', dept:'client', status:'building' },
    { name:'Report Agent', dept:'client', status:'building' },
    // Afiliados
    { name:'Affil Orch', dept:'affil', status:'building' },
    { name:'Commission', dept:'affil', status:'building' },
    { name:'Payment Agt', dept:'affil', status:'building' },
    { name:'Fraud Agent', dept:'affil', status:'building' },
    // Marketplace
    { name:'Market Orch', dept:'mkt', status:'building' },
    { name:'Booking Agent', dept:'mkt', status:'building' },
    { name:'Split Agent', dept:'mkt', status:'building' },
    { name:'Review Agent', dept:'mkt', status:'building' },
    // Legal
    { name:'Legal Agent', dept:'legal', status:'building' },
  ];

  const deptColors = {
    orch:'#f59e0b', head:'var(--accent)', edit:'var(--cyan)', copy:'var(--green)',
    sales:'var(--pink)', client:'var(--orange)', affil:'#818cf8', mkt:'#34d399', legal:'#f87171',
  };
  const deptLabels = {
    orch:'Orquestadores', head:'Jefes', edit:'Edición', copy:'Copy',
    sales:'Ventas', client:'Clientes', affil:'Afiliados', mkt:'Marketplace', legal:'Legal',
  };

  const grouped = {};
  agents.forEach(a => {
    if (!grouped[a.dept]) grouped[a.dept] = [];
    grouped[a.dept].push(a);
  });

  const readyCount = agents.filter(a => a.status === 'ready').length;
  const total = agents.length;

  return `
    <div style="margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;">
      <div style="font-size:13px;color:var(--text-muted);">
        <span style="color:var(--green);font-weight:700;">${readyCount} operativos</span> · ${total - readyCount} en construcción
      </div>
      <div style="background:rgba(255,255,255,.05);border-radius:99px;height:5px;width:120px;">
        <div style="background:var(--green);height:5px;border-radius:99px;width:${pct(readyCount,total)}%;"></div>
      </div>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;">
      ${agents.map(a => {
        const color = deptColors[a.dept];
        const isReady = a.status === 'ready';
        return `<div title="${a.name} · ${deptLabels[a.dept]}"
          style="padding:4px 8px;border-radius:6px;font-size:10px;font-weight:600;
                 background:${isReady ? `rgba(16,185,129,.15)` : 'rgba(255,255,255,.04)'};
                 border:1px solid ${isReady ? 'rgba(16,185,129,.3)' : 'rgba(255,255,255,.06)'};
                 color:${isReady ? 'var(--green)' : 'var(--text-muted)'};
                 cursor:default;white-space:nowrap;">
          ${isReady ? '●' : '○'} ${a.name}
        </div>`;
      }).join('')}
    </div>
  `;
}

// ── Render principal ────────────────────────────
export function renderDashboard(container) {
  const biz = getBizData();
  const stats = storage.getStats();
  const revPct = pct(biz.mrr, biz.mrr_goal);
  const clientPct = pct(biz.clients_active, biz.clients_goal);
  const monthLabels = ['Sep','Oct','Nov','Dic','Ene','Feb','Mar'];
  const activityColors = { sale:'var(--green)', content:'var(--accent)', lead:'var(--cyan)', contract:'var(--orange)', affiliate:'#f59e0b' };

  container.innerHTML = `
    <!-- ── HEADER ── -->
    <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:24px;">
      <div>
        <h2 style="font-size:26px;font-weight:800;margin-bottom:4px;letter-spacing:-.02em;">
          Cuartel General 🏢
        </h2>
        <p style="color:var(--text-muted);font-size:13px;">
          Sistema 180 · José + Ares · Marbella, España
          &nbsp;·&nbsp; <span style="color:var(--orange)">🎯 Misión: 300 clientes × 300€ = 90.000€/mes</span>
        </p>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <div style="padding:6px 14px;background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.25);
                    border-radius:20px;font-size:12px;font-weight:700;color:var(--green);">
          ● LIVE
        </div>
        <div style="padding:6px 14px;background:var(--bg-glass);border:1px solid var(--border);
                    border-radius:20px;font-size:12px;color:var(--text-secondary);">
          📅 Marzo 2026
        </div>
        <button id="btn-despacho" style="padding:6px 16px;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;border:none;
                border-radius:20px;font-size:12px;font-weight:800;cursor:pointer;
                box-shadow:0 0 14px rgba(245,158,11,.35);letter-spacing:.02em;">
          🏢 Abrir El Despacho — Sala de Reuniones
        </button>
        <button id="btn-edit-metrics" style="padding:6px 14px;background:var(--accent);color:#fff;border:none;
                border-radius:20px;font-size:12px;font-weight:700;cursor:pointer;">
          ✏️ Editar métricas
        </button>
      </div>
    </div>

    <!-- ── TABS REMOVIDAS — MODO "TODO EN 1" ── -->

    <!-- ── 1. VISTA GENERAL (OVERVIEW) ── -->
    <div id="tab-overview">

    <!-- ── KPIs ── -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-bottom:20px;">

      <!-- MRR -->
      <div class="card" style="position:relative;overflow:hidden;border-left:3px solid var(--green);">
        <div style="font-size:10px;font-weight:800;color:var(--text-muted);letter-spacing:.1em;margin-bottom:6px;">MRR ACTUAL</div>
        <div style="font-size:34px;font-weight:900;color:var(--green);letter-spacing:-.02em;">${biz.mrr.toLocaleString('es-ES')}€</div>
        <div style="font-size:11px;color:var(--text-muted);margin:3px 0 10px;">objetivo: ${biz.mrr_goal.toLocaleString('es-ES')}€/mes</div>
        <div style="background:rgba(255,255,255,.06);border-radius:99px;height:5px;">
          <div style="background:linear-gradient(90deg,var(--green),#34d399);height:5px;border-radius:99px;width:${revPct}%;transition:width .8s;"></div>
        </div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:5px;">${revPct}% — faltan ${(biz.mrr_goal - biz.mrr).toLocaleString('es-ES')}€</div>
        <div style="position:absolute;bottom:10px;right:10px;opacity:.7;">${sparkline(biz.revenue_history)}</div>
      </div>

      <!-- Clientes -->
      <div class="card" style="border-left:3px solid var(--accent);">
        <div style="font-size:10px;font-weight:800;color:var(--text-muted);letter-spacing:.1em;margin-bottom:6px;">CLIENTES ACTIVOS</div>
        <div style="font-size:34px;font-weight:900;color:var(--accent);">${biz.clients_active}</div>
        <div style="font-size:11px;color:var(--text-muted);margin:3px 0 10px;">objetivo: ${biz.clients_goal} clientes</div>
        <div style="background:rgba(255,255,255,.06);border-radius:99px;height:5px;">
          <div style="background:linear-gradient(90deg,var(--accent),var(--pink));height:5px;border-radius:99px;width:${clientPct}%;"></div>
        </div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:5px;">${clientPct}% — faltan ${biz.clients_goal - biz.clients_active} clientes</div>
        <div style="margin-top:8px;font-size:11px;color:var(--text-secondary);">
          💸 Última venta <strong style="color:var(--green)">${biz.last_sale_amount}€</strong> — ${biz.last_sale_date}
        </div>
      </div>

      <!-- Pipeline -->
      <div class="card" style="border-left:3px solid var(--orange);">
        <div style="font-size:10px;font-weight:800;color:var(--text-muted);letter-spacing:.1em;margin-bottom:8px;">PIPELINE VENTAS</div>
        <div style="display:flex;flex-direction:column;gap:7px;">
          ${[
            { label:'❄️ Frío',        val: biz.pipeline.filter(p=>p.status==='cold').length,      color:'var(--text-muted)' },
            { label:'📞 Contactado',  val: biz.pipeline.filter(p=>p.status==='contacted').length,  color:'var(--cyan)' },
            { label:'📄 Propuesta',   val: biz.pipeline.filter(p=>p.status==='proposal').length,   color:'var(--orange)' },
            { label:'✅ Cerrado',     val: biz.pipeline.filter(p=>p.status==='closed').length,     color:'var(--green)' },
          ].map(s=>`
            <div style="display:flex;align-items:center;justify-content:space-between;font-size:12px;">
              <span style="color:var(--text-secondary);">${s.label}</span>
              <span style="font-weight:800;color:${s.color};font-size:16px;">${s.val}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Afiliados -->
      <div class="card" style="border-left:3px solid #f59e0b;">
        <div style="font-size:10px;font-weight:800;color:var(--text-muted);letter-spacing:.1em;margin-bottom:6px;">AFILIADOS</div>
        <div style="font-size:34px;font-weight:900;color:#f59e0b;">${biz.affiliate_rev}€</div>
        <div style="font-size:11px;color:var(--text-muted);margin:3px 0 8px;">${biz.affiliates_active} afiliados activos este mes</div>
        <div style="padding:8px 10px;background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);border-radius:8px;">
          <div style="font-size:11px;color:#f59e0b;font-weight:700;">🏆 Niveles: 15% · 25% · 33%</div>
          <div style="font-size:10px;color:var(--text-muted);margin-top:2px;">Hold 14d · KYC 2K€ · CB breaker ×3</div>
        </div>
      </div>
    </div>

    <!-- ── EL EDIFICIO + ACTIVIDAD ── -->
    <div style="display:grid;grid-template-columns:300px 1fr;gap:16px;margin-bottom:20px;">

      <!-- El Edificio -->
      <div class="card" style="border-top:3px solid var(--orange);">
        <div style="font-size:13px;font-weight:800;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
          🏢 <span>El Edificio</span>
          <span style="font-size:10px;background:rgba(16,185,129,.1);color:var(--green);padding:2px 8px;border-radius:20px;margin-left:4px;">57 agentes LIVE</span>
        </div>
        ${edificioHTML(biz)}
        <div style="margin-top:10px;padding:8px;background:rgba(245,158,11,.06);border-radius:8px;font-size:11px;color:var(--text-muted);text-align:center;">
          Penthouse → Planta 4 → 3 → 2 → 1 → Subsuelo
        </div>
      </div>

      <!-- Actividad reciente -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
          ⚡ <span>Actividad en tiempo real</span>
          <span style="font-size:10px;background:rgba(16,185,129,.1);color:var(--green);padding:2px 8px;border-radius:20px;">live</span>
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          ${biz.recent_activity.map(a => `
            <div style="display:flex;align-items:flex-start;gap:10px;padding:10px;background:rgba(255,255,255,.03);
                        border-radius:8px;border:1px solid rgba(255,255,255,.05);">
              <div style="min-width:8px;height:8px;border-radius:50%;background:${activityColors[a.type] || 'var(--accent)'};
                          margin-top:4px;box-shadow:0 0 6px ${activityColors[a.type] || 'var(--accent)'};"></div>
              <div style="flex:1;">
                <div style="font-size:13px;color:var(--text-primary);">${a.msg}</div>
                <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${a.time}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- ── PIPELINE KANBAN ── -->
    <div class="card" style="margin-bottom:20px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
        <div style="font-size:13px;font-weight:800;">📋 Pipeline de Ventas</div>
        <button onclick="window.navigate('crm')" style="font-size:11px;color:var(--accent);background:none;border:none;cursor:pointer;font-weight:700;">
          Ver CRM completo →
        </button>
      </div>
      ${pipelineKanban(biz.pipeline)}
    </div>

    <!-- ── REVENUE CHART + PRODUCCIÓN ── -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">

      <!-- Revenue chart -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:14px;">📈 Revenue mensual</div>
        <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:16px;">
          <div>
            <div style="font-size:28px;font-weight:900;color:var(--green);">${biz.mrr.toLocaleString('es-ES')}€</div>
            <div style="font-size:11px;color:var(--text-muted);">Marzo 2026</div>
            <div style="margin-top:8px;font-size:12px;color:var(--text-secondary);">
              ${biz.mrr > (biz.revenue_history[biz.revenue_history.length-2] || 0)
                ? `<span style="color:var(--green)">↑ +${(((biz.mrr - biz.revenue_history[biz.revenue_history.length-2]) / biz.revenue_history[biz.revenue_history.length-2]) * 100).toFixed(0)}%</span> vs mes anterior`
                : 'Sin cambio vs mes anterior'
              }
            </div>
            <div style="margin-top:6px;font-size:11px;color:var(--text-muted);">
              Proyección 12 meses: <strong style="color:var(--green)">${(biz.mrr * 12).toLocaleString('es-ES')}€</strong>
            </div>

            <!-- Flujo de caja real -->
            <div style="margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.1);">
                <div style="font-size:10px;font-weight:800;color:var(--text-muted);letter-spacing:1px;margin-bottom:6px;">FLUJO DE CAJA (MESH)</div>
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:11px;color:var(--text-secondary);">↓ Ingresos netos</span>
                    <strong style="color:var(--green);font-size:12px;">+${(biz.cashflow_in || 0).toLocaleString('es-ES')}€</strong>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="font-size:11px;color:var(--text-secondary);">↑ Gastos API/Costes</span>
                    <strong style="color:var(--red);font-size:12px;">-${(biz.cashflow_out || 0).toLocaleString('es-ES')}€</strong>
                </div>
            </div>
          </div>
          <div style="flex:1;display:flex;justify-content:flex-end;">
            ${revenueChart(biz.revenue_history, monthLabels)}
          </div>
        </div>
        <div style="margin-top:14px;padding:10px;background:rgba(16,185,129,.06);border-radius:8px;
                    border:1px solid rgba(16,185,129,.15);font-size:11px;color:var(--text-muted);">
          🎯 Para 90K€/mes necesitas <strong style="color:var(--green)">${biz.clients_goal} clientes × 300€</strong>
          &nbsp;·&nbsp; Faltan ${biz.clients_goal - biz.clients_active} clientes
        </div>
      </div>

      <!-- Producción -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:14px;">🏭 Producción de Contenido</div>
        <div style="display:flex;flex-direction:column;gap:12px;">
          ${[
            { icon:'🎬', label:'Vídeos esta semana', val: biz.content_videos_week, max:50, color:'var(--accent)' },
            { icon:'🤖', label:'Avatares generados', val: stats.avatars, max:50, color:'var(--green)' },
            { icon:'📝', label:'Guiones creados', val: stats.scripts, max:100, color:'var(--orange)' },
            { icon:'📢', label:'Ads activos', val: stats.ads, max:20, color:'var(--pink)' },
            { icon:'👥', label:'Clientes con contenido', val: biz.content_clients, max:300, color:'var(--cyan)' },
          ].map(s=>`
            <div>
              <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;">
                <span style="color:var(--text-secondary);">${s.icon} ${s.label}</span>
                <span style="font-weight:700;color:${s.color};">${s.val}</span>
              </div>
              <div style="background:rgba(255,255,255,.06);border-radius:99px;height:4px;">
                <div style="background:${s.color};height:4px;border-radius:99px;width:${pct(s.val,s.max)}%;transition:width .6s;"></div>
              </div>
            </div>
          `).join('')}
        </div>
        <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;">
          <button onclick="window.navigate('scripts')" style="flex:1;padding:8px;background:rgba(16,185,129,.1);color:var(--green);
                  border:1px solid rgba(16,185,129,.2);border-radius:8px;font-size:11px;font-weight:700;cursor:pointer;">
            ✍️ Crear guión
          </button>
          <button onclick="window.navigate('avatars')" style="flex:1;padding:8px;background:rgba(99,102,241,.1);color:var(--accent);
                  border:1px solid rgba(99,102,241,.2);border-radius:8px;font-size:11px;font-weight:700;cursor:pointer;">
            🤖 Crear avatar
          </button>
        </div>
      </div>
    </div>

    <!-- ── INTEGRADOR BRANDING (FANBASIS + COMUNIDAD) ── -->
    <div class="card" style="margin-bottom:20px;border-top:3px solid #8b5cf6;background:radial-gradient(ellipse at top right, rgba(139,92,246,0.1), transparent);">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
        <div style="font-size:13px;font-weight:800;display:flex;align-items:center;gap:8px;">
            <div style="width:24px;height:24px;border-radius:6px;background:linear-gradient(135deg, #8b5cf6, #3b82f6);display:flex;align-items:center;justify-content:center;font-size:12px;">F</div>
            Fanbasis Ecosistema
        </div>
        <div style="font-size:10px;background:rgba(139,92,246,.1);color:#8b5cf6;padding:2px 8px;border-radius:20px;border:1px solid rgba(139,92,246,.3);">Conectado API</div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;">
         <div style="background:rgba(0,0,0,0.3);padding:14px;border-radius:12px;border:1px solid rgba(255,255,255,0.05);">
             <div style="font-size:10px;font-weight:800;color:var(--text-muted);">👥 SEGUIDORES / AUDIENCIA</div>
             <div style="font-size:24px;font-weight:900;color:#fff;margin-top:4px;">${(biz.fanbasis_followers||0).toLocaleString('es-ES')}</div>
             <div style="font-size:11px;color:var(--green);margin-top:2px;">↑ +4.2% esta semana</div>
         </div>
         <div style="background:rgba(0,0,0,0.3);padding:14px;border-radius:12px;border:1px solid rgba(255,255,255,0.05);">
             <div style="font-size:10px;font-weight:800;color:var(--text-muted);">💰 ROYALTIES / MONETIZACIÓN</div>
             <div style="font-size:24px;font-weight:900;color:#f59e0b;margin-top:4px;">${(biz.fanbasis_revenue||0).toLocaleString('es-ES')}€</div>
             <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">Saldo pendiente de retiro</div>
         </div>
         <div style="background:rgba(0,0,0,0.3);padding:14px;border-radius:12px;border:1px solid rgba(255,255,255,0.05);">
             <div style="font-size:10px;font-weight:800;color:var(--text-muted);">❤️ ENGAGEMENT RATE</div>
             <div style="font-size:24px;font-weight:900;color:#ec4899;margin-top:4px;">${(biz.fanbasis_engagement||0).toFixed(1)}%</div>
             <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">Interacciones por contenido</div>
         </div>
      </div>
    </div>

    <!-- ── ESTADO DEL SISTEMA ── -->
    <div class="card" style="margin-bottom:20px;border-top:3px solid var(--green);">
      <div style="font-size:13px;font-weight:800;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
        🖥️ <span>Estado del Sistema</span>
        <span style="font-size:10px;background:rgba(16,185,129,.1);color:var(--green);padding:2px 8px;border-radius:20px;">operativo</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;">
        ${[
          { label:'Stripe Connect', icon:'💳', status:'✅', detail:'Billing Agent (Fernando) activo', ok:true },
          { label:'Meta Pixel', icon:'📊', status:'✅', detail:'Pixel Agent (Luna) tracking', ok:true },
          { label:'n8n Cloud', icon:'🔗', status:'✅', detail:'14 flujos — CRM Agent conectado', ok:true },
          { label:'Ruflo Swarm', icon:'🐝', status:'✅', detail:'8 agentes Haiku $0.01/tarea', ok:true },
          { label:'Gemini 2.5', icon:'🧠', status:'✅', detail:'Flash + Pro activo', ok:true },
          { label:'Slack', icon:'💬', status:'⚠️', detail:'Webhook pendiente', ok:false },
        ].map(s=>`
          <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:10px;
                      background:${s.ok ? 'rgba(16,185,129,.06)' : 'rgba(251,191,36,.06)'};
                      border:1px solid ${s.ok ? 'rgba(16,185,129,.18)' : 'rgba(251,191,36,.25)'};">
            <span style="font-size:20px;">${s.icon}</span>
            <div style="flex:1;min-width:0;">
              <div style="font-size:12px;font-weight:700;color:${s.ok ? 'var(--text-primary)' : 'var(--orange)'};">
                ${s.status} ${s.label}
              </div>
              <div style="font-size:10px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${s.detail}</div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- ── AGENTES IA ── -->
    <div class="card" style="margin-bottom:20px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
        <div style="font-size:13px;font-weight:800;">🤖 Los 57 Agentes IA</div>
        <button onclick="window.navigate('agents')" style="font-size:11px;color:var(--accent);background:none;border:none;cursor:pointer;font-weight:700;">
          Gestionar agentes →
        </button>
      </div>
      ${agentesGrid()}
    </div>

    <!-- ── STACK ACTIVO + ACCIONES ── -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">

      <!-- Stack activo -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:14px;">🔌 Stack Activo</div>
        <div style="display:flex;flex-direction:column;gap:7px;">
          ${[
            { name:'Gemini 2.5 Flash', status:'✅', note:'Guiones + Copy + Research', ok:true },
            { name:'Perplexity Sonar Pro', status:'✅', note:'Búsqueda web real', ok:true },
            { name:'n8n Cloud', status:'✅', note:'14 flujos activos', ok:true },
            { name:'Stripe Connect', status:'✅', note:'Pagos + IVA + splits afiliados', ok:true },
            { name:'Meta Pixel + CAPI', status:'✅', note:'Conversiones + ROAS tracking', ok:true },
            { name:'ClaudeFlow (Ruflo)', status:'✅', note:'8 agentes enjambre — $0.01/tarea', ok:true },
            { name:'Antigravity IDE', status:'✅', note:'Gemini 3.1 Pro — arquitectura', ok:true },
            { name:'Cowork (Sonnet)', status:'✅', note:'160M tokens — estrategia', ok:true },
            { name:'ComfyUI local', status:'✅', note:'RTX 4060 — Avatares & Thumbnails', ok:true },
            { name:'Slack', status:'⚙️', note:'Alertas — pendiente webhook', ok:false },
          ].map(s=>`
            <div style="display:flex;align-items:center;justify-content:space-between;font-size:12px;">
              <span style="color:${s.ok ? 'var(--text-secondary)' : 'var(--text-muted)'};">${s.status} ${s.name}</span>
              <span style="color:var(--text-muted);font-size:11px;">${s.note}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Acciones rápidas -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:14px;">⚡ Acciones Rápidas</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          ${[
            { page:'scripts',     icon:'📝', label:'Nuevo guión viral',     sub:'Método Heras + AI Cascade',   color:'var(--green)' },
            { page:'avatars',     icon:'🤖', label:'Crear avatar cliente',  sub:'ComfyUI + Gemini 2.5',        color:'var(--accent)' },
            { page:'editor',      icon:'✂️', label:'Editor de vídeo',       sub:'Cortes · Subs · GPU',          color:'var(--orange)' },
            { page:'ads',         icon:'📢', label:'Diseñar anuncio',       sub:'9 plataformas · Meta Ads',     color:'var(--pink)' },
            { page:'crm',         icon:'📋', label:'Ver CRM completo',      sub:'Leads · Pipeline · Closers',   color:'var(--cyan)' },
            { page:'marketplace', icon:'🏪', label:'Marketplace',           sub:'Negocios + Alquileres',        color:'#f59e0b' },
            { page:'legal',       icon:'⚖️', label:'Legal & GDPR',          sub:'Cumplimiento total España',    color:'var(--red)' },
          ].map(a=>`
            <div class="quick-action" data-page="${a.page}"
              style="display:flex;align-items:center;gap:10px;padding:9px 11px;border-radius:9px;
                     background:var(--bg-glass);border:1px solid var(--border);cursor:pointer;
                     transition:var(--transition);">
              <span style="font-size:18px;">${a.icon}</span>
              <div style="flex:1;">
                <div style="font-size:12px;font-weight:700;color:${a.color};">${a.label}</div>
                <div style="font-size:10px;color:var(--text-muted);">${a.sub}</div>
              </div>
              <span style="color:var(--text-muted);font-size:12px;">›</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    </div><!-- /tab-overview -->

    <!-- ── 2. EL DESPACHO (AGENTS LIVE) ── -->
    <div id="despacho-container" style="margin-bottom:32px;"></div>

    <!-- ── 3. VIDEO EDITOR PRO ── -->
    <div id="editor-container" style="margin-bottom:32px;"></div>

    <!-- ── MODAL EDITAR MÉTRICAS ── -->
    <div id="metrics-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);
          z-index:999;align-items:center;justify-content:center;">
      <div style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:16px;
                  padding:24px;width:min(600px,95vw);max-height:80vh;overflow-y:auto;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <h3 style="font-size:16px;font-weight:800;">✏️ Actualizar métricas</h3>
          <button id="close-modal" style="background:none;border:none;color:var(--text-muted);font-size:20px;cursor:pointer;">✕</button>
        </div>
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:16px;padding:10px;background:rgba(99,102,241,0.08);border-radius:8px;border:1px solid rgba(99,102,241,0.2);">
          💡 Introduce tus datos reales aquí. Se guardan en tu navegador y se actualizan al instante.
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;">
          ${[
            { id:'mrr', label:'💰 MRR actual (€)', val: biz.mrr },
            { id:'clients_active', label:'👥 Clientes activos', val: biz.clients_active },
            { id:'leads', label:'📋 Leads en pipeline', val: biz.leads },
            { id:'proposals', label:'📄 Propuestas enviadas', val: biz.proposals },
            { id:'closed_month', label:'✅ Cerradas este mes', val: biz.closed_month },
            { id:'affiliates_active', label:'🤝 Afiliados activos', val: biz.affiliates_active },
            { id:'affiliate_rev', label:'💎 Ingresos afiliados (€)', val: biz.affiliate_rev },
            { id:'cashflow_in', label:'🟢 Caja Entrante (€)', val: biz.cashflow_in || 0 },
            { id:'cashflow_out', label:'🔴 Caja Gastos (€)', val: biz.cashflow_out || 0 },
            { id:'content_videos_week', label:'🎬 Vídeos/semana', val: biz.content_videos_week },
            { id:'content_clients', label:'📢 Clientes con contenido', val: biz.content_clients },
            { id:'fanbasis_followers', label:'👥 Fanbasis Followers', val: biz.fanbasis_followers || 0 },
            { id:'fanbasis_revenue', label:'💰 Fanbasis Royalties (€)', val: biz.fanbasis_revenue || 0 },
            { id:'fanbasis_engagement', label:'💍 Fanbasis Engagement (%)', val: biz.fanbasis_engagement || 0 },
            { id:'last_sale_amount', label:'💳 Último importe venta (€)', val: biz.last_sale_amount },
          ].map(f=>`
            <div>
              <label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:4px;">${f.label}</label>
              <input type="number" id="m-${f.id}" value="${f.val}" min="0"
                style="width:100%;background:rgba(255,255,255,.05);border:1px solid var(--border);
                       color:var(--text-primary);padding:10px 12px;border-radius:8px;font-size:14px;font-weight:700;outline:none;
                       transition:border-color .2s;"
                onfocus="this.style.borderColor='var(--accent)'"
                onblur="this.style.borderColor='var(--border)'">
            </div>
          `).join('')}
        </div>
        <div style="margin-top:16px;">
          <label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:4px;">📅 Fecha última venta</label>
          <input type="date" id="m-last_sale_date" value="${biz.last_sale_date !== '-' ? biz.last_sale_date : ''}"
            style="width:100%;background:rgba(255,255,255,.05);border:1px solid var(--border);
                   color:var(--text-primary);padding:10px 12px;border-radius:8px;font-size:14px;outline:none;">
        </div>
        <div style="display:flex;gap:10px;margin-top:20px;">
          <button id="btn-save" style="flex:1;background:var(--green);color:#fff;border:none;padding:14px;
                  border-radius:10px;font-weight:800;cursor:pointer;font-size:15px;
                  box-shadow:0 4px 16px rgba(16,185,129,0.3);transition:transform .1s;"
                  onmousedown="this.style.transform='scale(0.98)'"
                  onmouseup="this.style.transform=''">💾 Guardar cambios</button>
          <button id="btn-reset" style="background:rgba(248,113,113,0.1);color:#f87171;border:1px solid rgba(248,113,113,0.3);
                  padding:14px 16px;border-radius:10px;font-weight:700;cursor:pointer;font-size:12px;">🗑 Reset</button>
          <button id="btn-cancel" style="background:var(--bg-glass);color:var(--text-secondary);border:1px solid var(--border);
                  padding:14px 20px;border-radius:10px;font-weight:700;cursor:pointer;">Cancelar</button>
        </div>
      </div>
    </div>
  `;

  // ── Events ──────────────────────────────────
  // Expose navigate globally for inline onclick handlers
  /** @type {any} */ (window).navigate = navigate;

  // Render subsections directly (Modo "TODO EN 1")
  const despachoContainer = container.querySelector('#despacho-container');
  if (despachoContainer) renderDespacho(despachoContainer);

  const editorContainer = container.querySelector('#editor-container');
  if (editorContainer) renderEditor(editorContainer);

  container.querySelectorAll('.quick-action').forEach(el => {
    el.addEventListener('click', () => navigate(el.dataset.page));
    el.addEventListener('mouseenter', () => { el.style.background = 'var(--bg-card-hover)'; el.style.borderColor = 'rgba(255,255,255,.15)'; });
    el.addEventListener('mouseleave', () => { el.style.background = 'var(--bg-glass)'; el.style.borderColor = 'var(--border)'; });
  });

  container.querySelector('#btn-despacho').addEventListener('click', () => navigate('despacho'));

  const modal = container.querySelector('#metrics-modal');
  container.querySelector('#btn-edit-metrics').addEventListener('click', () => {
    modal.style.display = 'flex';
  });
  container.querySelector('#close-modal').addEventListener('click', () => { modal.style.display = 'none'; });
  container.querySelector('#btn-cancel').addEventListener('click', () => { modal.style.display = 'none'; });
  modal.addEventListener('click', e => { if (e.target === modal) modal.style.display = 'none'; });

  container.querySelector('#btn-save').addEventListener('click', () => {
    const fields = ['mrr','clients_active','leads','proposals','closed_month','affiliates_active','affiliate_rev','cashflow_in','cashflow_out','fanbasis_followers','fanbasis_revenue','fanbasis_engagement','content_videos_week','content_clients','last_sale_amount'];
    const updated = {};
    fields.forEach(f => {
      const el = container.querySelector(`#m-${f}`);
      if (el) updated[f] = Number(el.value);
    });
    // Fecha última venta
    const dateEl = container.querySelector('#m-last_sale_date');
    if (dateEl && dateEl.value) updated.last_sale_date = dateEl.value;
    // Actualizar revenue_history: push el MRR actual al array
    const currentHistory = biz.revenue_history || [0,0,0,0,0,0,0];
    const newHistory = [...currentHistory.slice(1), updated.mrr || 0];
    updated.revenue_history = newHistory;
    localStorage.setItem('s180_biz', JSON.stringify({ ...biz, ...updated }));
    modal.style.display = 'none';
    navigate('dashboard');
  });

  // Reset button — clear all data to zeros
  const btnReset = container.querySelector('#btn-reset');
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      if (!confirm('¿Seguro que quieres poner todas las métricas a 0?')) return;
      localStorage.removeItem('s180_biz');
      modal.style.display = 'none';
      navigate('dashboard');
    });
  }
}
