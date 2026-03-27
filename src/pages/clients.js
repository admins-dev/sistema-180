// ═══════════════════════════════════════════════
// Clientes — Sistema180 HQ
// ═══════════════════════════════════════════════

function getClients() {
  const saved = localStorage.getItem('s180_clients');
  const defaults = [
    { id:1, name:'Restaurante Bohemia', contact:'Carmen Ruiz', phone:'+34 655 777 888', nicho:'Restaurante', plan:'web+bot', mrr:300, status:'active', since:'2026-03-20', bot_active:true, web_url:'restaurantebohemia.es', next_payment:'2026-04-20' },
    { id:2, name:'Óptica Visión Clara', contact:'Jorge Sánchez', phone:'+34 699 222 333', nicho:'Óptica', plan:'web', mrr:0, status:'active', since:'2026-03-19', bot_active:false, web_url:'opticavisionclara.es', next_payment:null },
    { id:3, name:'Peluquería Sol', contact:'Ana Morales', phone:'+34 612 555 666', nicho:'Peluquería', plan:'web+bot', mrr:300, status:'active', since:'2026-03-15', bot_active:true, web_url:'peluqueriasol.es', next_payment:'2026-04-15' },
  ];
  try { return JSON.parse(saved || 'null') || defaults; } catch { return defaults; }
}

export function renderClients(container) {
  const clients = getClients();
  const totalMrr = clients.filter(c=>c.status==='active').reduce((s,c)=>s+c.mrr,0);
  const withBot = clients.filter(c=>c.bot_active).length;

  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
      <div>
        <h2 style="font-size:22px;font-weight:800;">👥 Clientes Activos</h2>
        <p style="color:var(--text-muted);font-size:13px;">${clients.length} clientes · MRR ${totalMrr}€/mes · ${withBot} con bot IA activo</p>
      </div>
      <button onclick="alert('Formulario onboarding — próximamente')"
        style="padding:8px 18px;background:var(--accent);color:#fff;border:none;border-radius:10px;font-weight:700;font-size:13px;cursor:pointer;">
        + Nuevo cliente
      </button>
    </div>

    <!-- Stats -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px;">
      ${[
        { label:'Clientes activos', val: clients.filter(c=>c.status==='active').length, color:'var(--green)', icon:'✅' },
        { label:'MRR recurrente', val: totalMrr+'€', color:'var(--green)', icon:'💰' },
        { label:'Con bot IA', val: withBot, color:'var(--accent)', icon:'🤖' },
        { label:'Solo web', val: clients.filter(c=>!c.bot_active).length, color:'var(--orange)', icon:'🌐' },
      ].map(s=>`
        <div class="card" style="text-align:center;">
          <div style="font-size:24px;margin-bottom:4px;">${s.icon}</div>
          <div style="font-size:28px;font-weight:800;color:${s.color};">${s.val}</div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${s.label}</div>
        </div>
      `).join('')}
    </div>

    <!-- Lista clientes -->
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;">
      ${clients.map(c => `
        <div class="card" style="border-left:3px solid ${c.status==='active' ? 'var(--green)' : 'var(--red)'};">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px;">
            <div>
              <div style="font-size:15px;font-weight:700;">${c.name}</div>
              <div style="font-size:11px;color:var(--text-muted);">${c.nicho} · ${c.contact}</div>
            </div>
            <span style="padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700;
                         background:${c.status==='active' ? 'rgba(16,185,129,.15)' : 'rgba(239,68,68,.15)'};
                         color:${c.status==='active' ? 'var(--green)' : 'var(--red)'};">
              ${c.status === 'active' ? '● ACTIVO' : '● PAUSADO'}
            </span>
          </div>
          <div style="display:flex;flex-direction:column;gap:6px;font-size:12px;">
            <div style="display:flex;justify-content:space-between;">
              <span style="color:var(--text-muted);">Plan:</span>
              <span style="font-weight:600;">${c.plan}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="color:var(--text-muted);">MRR:</span>
              <span style="font-weight:700;color:var(--green);">${c.mrr > 0 ? c.mrr+'€/mes' : 'Pago único'}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="color:var(--text-muted);">Bot IA:</span>
              <span style="color:${c.bot_active ? 'var(--green)' : 'var(--text-muted)'};">${c.bot_active ? '✅ Activo' : '❌ Sin bot'}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="color:var(--text-muted);">Web:</span>
              <span style="color:var(--accent);">${c.web_url}</span>
            </div>
            ${c.next_payment ? `
            <div style="display:flex;justify-content:space-between;">
              <span style="color:var(--text-muted);">Próximo cobro:</span>
              <span style="color:var(--orange);font-weight:600;">${c.next_payment}</span>
            </div>` : ''}
          </div>
          <div style="display:flex;gap:8px;margin-top:12px;">
            <button style="flex:1;padding:7px;background:rgba(99,102,241,.1);color:var(--accent);border:1px solid rgba(99,102,241,.2);
                           border-radius:7px;font-size:11px;font-weight:700;cursor:pointer;"
                    onclick="alert('Informe del cliente — próximamente')">
              📊 Informe
            </button>
            <button style="flex:1;padding:7px;background:rgba(255,255,255,.04);color:var(--text-secondary);border:1px solid var(--border);
                           border-radius:7px;font-size:11px;cursor:pointer;"
                    onclick="alert('Chat WhatsApp — próximamente')">
              💬 WhatsApp
            </button>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}
