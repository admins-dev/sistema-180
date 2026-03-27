// ═══════════════════════════════════════════════
// Afiliados — Sistema180 HQ
// ═══════════════════════════════════════════════

const LEVELS = {
  starter: { label:'Starter', pct:15, color:'#94a3b8', min:0 },
  pro:     { label:'Pro',     pct:25, color:'#6366f1', min:5 },
  elite:   { label:'Elite',   pct:33, color:'#f59e0b', min:10 },
};

function getAffiliates() {
  const saved = localStorage.getItem('s180_affiliates');
  const defaults = [
    { id:1, name:'Carlos Ruiz', code:'CARLOS33', email:'carlos@email.com', level:'elite', sales:14, revenue:4200, commission:1386, hold:0, status:'active', joined:'2026-01-15' },
    { id:2, name:'María Soler', code:'MARIA25',  email:'maria@email.com',  level:'pro',   sales:7,  revenue:2079, commission:519,  hold:99,  status:'active', joined:'2026-02-10' },
    { id:3, name:'Juan Torres', code:'JUAN15',   email:'juan@email.com',   level:'starter',sales:2, revenue:594,  commission:89,   hold:0,  status:'active', joined:'2026-03-01' },
    { id:4, name:'Ana Vega',    code:'ANA180',   email:'ana@email.com',    level:'starter',sales:0, revenue:0,    commission:0,    hold:0,  status:'pending', joined:'2026-03-25' },
  ];
  try { return JSON.parse(saved || 'null') || defaults; } catch { return defaults; }
}

export function renderAffiliates(container) {
  const affiliates = getAffiliates();
  const totalCommissions = affiliates.reduce((s,a)=>s+a.commission,0);
  const totalSales = affiliates.reduce((s,a)=>s+a.sales,0);
  const totalRevenue = affiliates.reduce((s,a)=>s+a.revenue,0);

  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
      <div>
        <h2 style="font-size:22px;font-weight:800;">🤝 Afiliados</h2>
        <p style="color:var(--text-muted);font-size:13px;">${affiliates.length} afiliados · ${totalSales} ventas · ${totalRevenue.toLocaleString('es-ES')}€ generados</p>
      </div>
      <button onclick="alert('Registro de nuevo afiliado — próximamente')"
        style="padding:8px 18px;background:var(--accent);color:#fff;border:none;border-radius:10px;font-weight:700;font-size:13px;cursor:pointer;">
        + Añadir afiliado
      </button>
    </div>

    <!-- KPIs -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px;">
      ${[
        { label:'Comisiones pagadas', val: totalCommissions.toLocaleString('es-ES')+'€', color:'var(--green)', icon:'💰' },
        { label:'Ventas generadas', val: totalSales, color:'var(--accent)', icon:'🛒' },
        { label:'Revenue total', val: totalRevenue.toLocaleString('es-ES')+'€', color:'var(--orange)', icon:'📈' },
        { label:'En hold (14d)', val: affiliates.reduce((s,a)=>s+a.hold,0)+'€', color:'#f59e0b', icon:'⏳' },
      ].map(s=>`
        <div class="card" style="text-align:center;">
          <div style="font-size:22px;margin-bottom:6px;">${s.icon}</div>
          <div style="font-size:24px;font-weight:800;color:${s.color};">${s.val}</div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${s.label}</div>
        </div>
      `).join('')}
    </div>

    <!-- Niveles info -->
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;">
      ${Object.entries(LEVELS).map(([key,lv])=>`
        <div class="card" style="text-align:center;border-top:3px solid ${lv.color};">
          <div style="font-size:18px;font-weight:900;color:${lv.color};margin-bottom:4px;">${lv.pct}%</div>
          <div style="font-size:14px;font-weight:700;">${lv.label}</div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">Desde ${lv.min} ventas</div>
          <div style="font-size:11px;color:${lv.color};margin-top:6px;font-weight:600;">
            ${affiliates.filter(a=>a.level===key).length} afiliados
          </div>
        </div>
      `).join('')}
    </div>

    <!-- Lista afiliados -->
    <div class="card">
      <div style="font-size:13px;font-weight:800;margin-bottom:14px;">Afiliados activos</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;">
        ${affiliates.map(a => {
          const lv = LEVELS[a.level];
          const chargebacks = 0;
          return `
          <div style="padding:16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:12px;
                      border-left:3px solid ${lv.color};">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px;">
              <div>
                <div style="font-size:14px;font-weight:700;">${a.name}</div>
                <div style="font-size:12px;color:var(--text-muted);">${a.email}</div>
              </div>
              <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
                <span style="padding:2px 10px;border-radius:20px;font-size:10px;font-weight:800;
                             background:${lv.color}22;color:${lv.color};">${lv.label} ${lv.pct}%</span>
                <span style="padding:2px 10px;border-radius:20px;font-size:10px;font-weight:700;
                             background:${a.status==='active' ? 'rgba(16,185,129,.15)' : 'rgba(239,68,68,.15)'};
                             color:${a.status==='active' ? 'var(--green)' : 'var(--red)'};">
                  ${a.status === 'active' ? '● ACTIVO' : '● PENDIENTE'}
                </span>
              </div>
            </div>
            <div style="font-family:monospace;font-size:13px;font-weight:800;color:${lv.color};
                        background:${lv.color}15;padding:6px 12px;border-radius:6px;margin-bottom:10px;
                        letter-spacing:.05em;">
              🔗 ${a.code}
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;">
              <div style="background:rgba(255,255,255,.03);padding:8px;border-radius:6px;">
                <div style="color:var(--text-muted);font-size:10px;">Ventas</div>
                <div style="font-weight:800;color:var(--accent);">${a.sales}</div>
              </div>
              <div style="background:rgba(255,255,255,.03);padding:8px;border-radius:6px;">
                <div style="color:var(--text-muted);font-size:10px;">Comisiones</div>
                <div style="font-weight:800;color:var(--green);">${a.commission.toLocaleString('es-ES')}€</div>
              </div>
              ${a.hold > 0 ? `
              <div style="background:rgba(245,158,11,.06);padding:8px;border-radius:6px;border:1px solid rgba(245,158,11,.2);">
                <div style="color:var(--text-muted);font-size:10px;">En hold</div>
                <div style="font-weight:800;color:#f59e0b;">${a.hold}€</div>
              </div>` : ''}
              <div style="background:rgba(255,255,255,.03);padding:8px;border-radius:6px;">
                <div style="color:var(--text-muted);font-size:10px;">Revenue gen.</div>
                <div style="font-weight:800;">${a.revenue.toLocaleString('es-ES')}€</div>
              </div>
            </div>
            <div style="margin-top:10px;font-size:11px;color:var(--text-muted);">Miembro desde ${a.joined}</div>
          </div>
        `}).join('')}
      </div>
    </div>

    <!-- Protecciones -->
    <div class="card" style="margin-top:16px;border-top:3px solid var(--red);">
      <div style="font-size:13px;font-weight:800;margin-bottom:12px;">🛡️ Protecciones activas</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;">
        ${[
          { icon:'⏳', label:'Hold 14 días', desc:'Cada comisión espera 14 días antes de transferirse', color:'var(--orange)' },
          { icon:'🔍', label:'KYC +2.000€/mes', desc:'Verificación obligatoria si supera 2.000€/mes', color:'var(--accent)' },
          { icon:'⚡', label:'Circuit breaker ×3', desc:'3 chargebacks = afiliado suspendido automáticamente', color:'var(--red)' },
          { icon:'🔄', label:'Reembolso reversible', desc:'Si hay devolución, la comisión también se revierte', color:'var(--cyan)' },
        ].map(p=>`
          <div style="padding:12px;background:rgba(255,255,255,.03);border-radius:8px;border:1px solid rgba(255,255,255,.06);">
            <div style="font-size:18px;margin-bottom:6px;">${p.icon}</div>
            <div style="font-size:12px;font-weight:700;color:${p.color};margin-bottom:4px;">${p.label}</div>
            <div style="font-size:11px;color:var(--text-muted);line-height:1.4;">${p.desc}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}
