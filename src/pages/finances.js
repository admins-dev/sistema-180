// ═══════════════════════════════════════════════
// Finanzas — Sistema180 HQ
// ═══════════════════════════════════════════════

export function renderFinances(container) {
  const data = {
    mrr: 2679,
    mrr_goal: 90000,
    one_time: 894,
    costs: 340,
    profit: 3233,
    months: ['Sep','Oct','Nov','Dic','Ene','Feb','Mar'],
    revenue: [890, 1200, 1680, 1900, 2100, 2400, 2679],
    costs_arr: [200, 220, 280, 300, 310, 330, 340],
    pending_payments: [
      { client:'Fisio Centro Málaga', amount:497, due:'2026-04-02', status:'pending' },
      { client:'Clínica Estética Mar', amount:1500, due:'2026-04-05', status:'pending' },
      { client:'Auto Taller Jiménez', amount:497, due:'2026-04-08', status:'pending' },
    ],
    transactions: [
      { date:'2026-03-26', desc:'Stripe — Peluquería Sol MRR', amount:300, type:'income' },
      { date:'2026-03-25', desc:'Stripe — Restaurante Bohemia MRR', amount:300, type:'income' },
      { date:'2026-03-22', desc:'Stripe — Óptica Visión Clara (web)', amount:297, type:'income' },
      { date:'2026-03-20', desc:'Afiliado CARLOS33 — comisión', amount:99, type:'income' },
      { date:'2026-03-20', desc:'n8n plan avanzado', amount:-80, type:'cost' },
      { date:'2026-03-18', desc:'ElevenLabs — voz', amount:-55, type:'cost' },
      { date:'2026-03-15', desc:'Vercel Pro', amount:-25, type:'cost' },
    ],
  };

  const maxRev = Math.max(...data.revenue, 1);
  const barW = 28, gap = 8;
  const chartH = 80;

  const bars = data.revenue.map((v, i) => {
    const h = Math.round((v / maxRev) * chartH);
    const x = i * (barW + gap);
    const isLast = i === data.revenue.length - 1;
    return `
      <g>
        <rect x="${x}" y="${chartH - h}" width="${barW}" height="${h}" rx="4"
          fill="${isLast ? 'var(--green)' : 'rgba(99,102,241,.5)'}"
          ${isLast ? 'filter="drop-shadow(0 0 8px rgba(16,185,129,.5))"' : ''}/>
        ${isLast ? `<rect x="${x}" y="${chartH - h}" width="${barW}" height="3" rx="2" fill="rgba(255,255,255,.3)"/>` : ''}
        <text x="${x + barW/2}" y="${chartH + 14}" text-anchor="middle" fill="var(--text-muted)" font-size="9">${data.months[i]}</text>
        ${isLast ? `<text x="${x + barW/2}" y="${chartH - h - 6}" text-anchor="middle" fill="var(--green)" font-size="9" font-weight="bold">${v.toLocaleString('es-ES')}</text>` : ''}
      </g>`;
  }).join('');

  const projections = [
    { clients: 50,  mrr: 15000 },
    { clients: 100, mrr: 30000 },
    { clients: 150, mrr: 45000 },
    { clients: 200, mrr: 60000 },
    { clients: 300, mrr: 90000 },
  ];

  container.innerHTML = `
    <div style="margin-bottom:20px;">
      <h2 style="font-size:22px;font-weight:800;">💰 Finanzas</h2>
      <p style="color:var(--text-muted);font-size:13px;">Control de ingresos, gastos y proyecciones</p>
    </div>

    <!-- KPIs -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px;">
      ${[
        { label:'MRR Recurrente', val: data.mrr.toLocaleString('es-ES')+'€', sub:'/mes', color:'var(--green)', icon:'🔄' },
        { label:'Ingresos únicos', val: data.one_time.toLocaleString('es-ES')+'€', sub:'este mes', color:'var(--accent)', icon:'💳' },
        { label:'Costes fijos', val: data.costs+'€', sub:'/mes', color:'var(--red)', icon:'📉' },
        { label:'Beneficio neto', val: data.profit.toLocaleString('es-ES')+'€', sub:'este mes', color:'var(--orange)', icon:'📊' },
      ].map(s=>`
        <div class="card" style="border-left:3px solid ${s.color};">
          <div style="font-size:20px;margin-bottom:6px;">${s.icon}</div>
          <div style="font-size:26px;font-weight:800;color:${s.color};">${s.val}</div>
          <div style="font-size:11px;color:var(--text-muted);">${s.label} <span style="color:${s.color};">${s.sub}</span></div>
        </div>
      `).join('')}
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">

      <!-- Gráfica revenue -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:16px;">📈 Revenue mensual</div>
        <div style="display:flex;justify-content:center;">
          <svg width="${data.revenue.length * (barW + gap)}" height="${chartH + 24}" viewBox="0 0 ${data.revenue.length * (barW + gap)} ${chartH + 24}" style="overflow:visible">
            ${bars}
          </svg>
        </div>
        <div style="margin-top:16px;padding:10px;background:rgba(16,185,129,.06);border-radius:8px;font-size:11px;color:var(--text-muted);">
          Crecimiento MoM: <strong style="color:var(--green)">+${Math.round(((data.mrr - data.revenue[data.revenue.length-2]) / data.revenue[data.revenue.length-2]) * 100)}%</strong>
          vs mes anterior
        </div>
      </div>

      <!-- Proyecciones -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:16px;">🎯 Proyecciones</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          ${projections.map(p => {
            const pctBar = Math.min(100, Math.round((9 / p.clients) * 100));
            const isCurrent = p.clients === 300;
            return `
            <div style="padding:8px 12px;border-radius:8px;background:${isCurrent ? 'rgba(16,185,129,.08)' : 'rgba(255,255,255,.03)'};
                        border:1px solid ${isCurrent ? 'rgba(16,185,129,.2)' : 'rgba(255,255,255,.05)'};">
              <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:5px;">
                <span style="color:${isCurrent ? 'var(--green)' : 'var(--text-secondary)'};">${p.clients} clientes</span>
                <span style="font-weight:700;color:${isCurrent ? 'var(--green)' : 'var(--text-primary)'};">${p.mrr.toLocaleString('es-ES')}€/mes</span>
              </div>
              <div style="background:rgba(255,255,255,.06);border-radius:99px;height:4px;">
                <div style="background:${isCurrent ? 'var(--green)' : 'var(--accent)'};height:4px;border-radius:99px;width:${pctBar}%;"></div>
              </div>
            </div>`;
          }).join('')}
        </div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">

      <!-- Cobros pendientes -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:14px;">⏳ Cobros pendientes</div>
        ${data.pending_payments.map(p=>`
          <div style="display:flex;align-items:center;justify-content:space-between;padding:10px;
                      background:rgba(245,158,11,.06);border:1px solid rgba(245,158,11,.15);
                      border-radius:8px;margin-bottom:8px;">
            <div>
              <div style="font-size:13px;font-weight:600;">${p.client}</div>
              <div style="font-size:11px;color:var(--text-muted);">Vence: ${p.due}</div>
            </div>
            <div style="font-size:16px;font-weight:800;color:var(--orange);">${p.amount}€</div>
          </div>
        `).join('')}
        <div style="margin-top:8px;font-size:12px;color:var(--text-muted);text-align:right;">
          Total pendiente: <strong style="color:var(--orange);">${data.pending_payments.reduce((s,p)=>s+p.amount,0)}€</strong>
        </div>
      </div>

      <!-- Últimas transacciones -->
      <div class="card">
        <div style="font-size:13px;font-weight:800;margin-bottom:14px;">🧾 Últimas transacciones</div>
        ${data.transactions.map(t=>`
          <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;
                      border-bottom:1px solid rgba(255,255,255,.04);">
            <div>
              <div style="font-size:12px;color:var(--text-primary);">${t.desc}</div>
              <div style="font-size:10px;color:var(--text-muted);">${t.date}</div>
            </div>
            <div style="font-size:14px;font-weight:700;color:${t.type==='income' ? 'var(--green)' : 'var(--red)'};">
              ${t.type==='income' ? '+' : ''}${t.amount}€
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}
