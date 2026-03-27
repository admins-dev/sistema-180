// ═══════════════════════════════════════════════
// CRM & Leads — Sistema180 HQ
// ═══════════════════════════════════════════════
import { navigate } from '../main.js';

const STATUSES = [
  { key:'cold',      label:'Frío',        icon:'❄️', color:'#64748b' },
  { key:'contacted', label:'Contactado',  icon:'📞', color:'#06b6d4' },
  { key:'proposal',  label:'Propuesta',   icon:'📄', color:'#f59e0b' },
  { key:'closed',    label:'Cerrado',     icon:'✅', color:'#10b981' },
  { key:'lost',      label:'Perdido',     icon:'❌', color:'#ef4444' },
];

function getLeads() {
  const saved = localStorage.getItem('s180_leads');
  const defaults = [
    { id:1, name:'Peluquería Glow', contact:'María García', phone:'+34 612 345 678', nicho:'Peluquería', status:'contacted', amount:497, source:'Meta Ads', created:'2026-03-25', notes:'Interesada en web + recepcionista IA' },
    { id:2, name:'Clínica Estética Mar', contact:'Dr. Ramírez', phone:'+34 622 111 222', nicho:'Estética', status:'proposal', amount:1500, source:'WhatsApp frío', created:'2026-03-22', notes:'Quiere web high-ticket + bot IA' },
    { id:3, name:'Barbería Kings', contact:'Andrés López', phone:'+34 644 333 444', nicho:'Barbería', status:'cold', amount:297, source:'Google Maps', created:'2026-03-27', notes:'Web rota, sin Google Maps' },
    { id:4, name:'Restaurante Bohemia', contact:'Carmen Ruiz', phone:'+34 655 777 888', nicho:'Restaurante', status:'closed', amount:300, source:'Referido', created:'2026-03-20', notes:'Cerrado, pagó 300€' },
    { id:5, name:'Fisio Centro Málaga', contact:'Pablo Fernández', phone:'+34 633 999 000', nicho:'Fisioterapia', status:'contacted', amount:497, source:'Meta Ads', created:'2026-03-26', notes:'Demo programada' },
    { id:6, name:'Academia Danza Sur', contact:'Laura Martín', phone:'+34 611 444 555', nicho:'Academia', status:'cold', amount:297, source:'Instagram', created:'2026-03-27', notes:'DM enviado' },
    { id:7, name:'Óptica Visión Clara', contact:'Jorge Sánchez', phone:'+34 699 222 333', nicho:'Óptica', status:'closed', amount:300, source:'Afiliado', created:'2026-03-19', notes:'Firmado, onboarding activo' },
    { id:8, name:'Auto Taller Jiménez', contact:'Miguel Jiménez', phone:'+34 677 888 999', nicho:'Taller', status:'proposal', amount:497, source:'WhatsApp frío', created:'2026-03-24', notes:'Propuesta enviada por email' },
    { id:9, name:'Clínica Dental Norte', contact:'Dra. Vega', phone:'+34 666 123 456', nicho:'Dental', status:'cold', amount:1500, source:'Google Maps', created:'2026-03-27', notes:'3 reseñas negativas' },
    { id:10, name:'Gym PowerFit', contact:'Raúl Torres', phone:'+34 644 987 654', nicho:'Gimnasio', status:'contacted', amount:497, source:'TikTok', created:'2026-03-26', notes:'Vio nuestro reel, escribió él' },
  ];
  try { return JSON.parse(saved || 'null') || defaults; } catch { return defaults; }
}

function saveLeads(leads) {
  localStorage.setItem('s180_leads', JSON.stringify(leads));
}

export function renderCrm(container) {
  let leads = getLeads();
  let filter = 'all';
  let search = '';

  function filtered() {
    return leads.filter(l =>
      (filter === 'all' || l.status === filter) &&
      (l.name.toLowerCase().includes(search.toLowerCase()) || l.nicho.toLowerCase().includes(search.toLowerCase()))
    );
  }

  function totalByStatus(status) { return leads.filter(l => l.status === status).reduce((s, l) => s + l.amount, 0); }

  function render() {
    const data = filtered();
    const pipelineValue = leads.filter(l => l.status !== 'closed' && l.status !== 'lost').reduce((s,l) => s + l.amount, 0);

    container.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
        <div>
          <h2 style="font-size:22px;font-weight:800;">📋 CRM & Pipeline</h2>
          <p style="color:var(--text-muted);font-size:13px;">${leads.length} leads totales · ${leads.filter(l=>l.status==='closed').length} cerrados · Pipeline ${pipelineValue.toLocaleString('es-ES')}€</p>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <input id="crm-search" type="text" placeholder="Buscar negocio o nicho..." value="${search}"
            style="padding:8px 14px;background:var(--bg-glass);border:1px solid var(--border);color:var(--text-primary);
                   border-radius:10px;font-size:13px;outline:none;width:220px;">
          <button id="btn-new-lead" style="padding:8px 18px;background:var(--accent);color:#fff;border:none;border-radius:10px;font-weight:700;font-size:13px;cursor:pointer;">
            + Nuevo lead
          </button>
        </div>
      </div>

      <!-- KPIs pipeline -->
      <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:20px;">
        ${STATUSES.map(s => `
          <div class="card crm-filter-btn" data-status="${s.key}"
            style="text-align:center;cursor:pointer;border:2px solid ${filter === s.key ? s.color : 'transparent'};padding:12px 8px;">
            <div style="font-size:20px;margin-bottom:4px;">${s.icon}</div>
            <div style="font-size:22px;font-weight:800;color:${s.color};">${leads.filter(l=>l.status===s.key).length}</div>
            <div style="font-size:10px;color:var(--text-muted);margin-top:2px;">${s.label}</div>
            <div style="font-size:10px;color:${s.color};margin-top:2px;">${totalByStatus(s.key).toLocaleString('es-ES')}€</div>
          </div>
        `).join('')}
      </div>

      <!-- Tabla de leads -->
      <div class="card">
        <div style="overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid var(--border);">
                ${['Negocio','Contacto','Nicho','Estado','Valor','Fuente','Fecha','Acciones'].map(h=>
                  `<th style="text-align:left;padding:10px 12px;font-size:11px;font-weight:700;color:var(--text-muted);letter-spacing:.06em;">${h.toUpperCase()}</th>`
                ).join('')}
              </tr>
            </thead>
            <tbody>
              ${data.length === 0 ? `<tr><td colspan="8" style="text-align:center;padding:30px;color:var(--text-muted);">Sin resultados</td></tr>` :
              data.map(l => {
                const st = STATUSES.find(s => s.key === l.status);
                return `
                <tr style="border-bottom:1px solid rgba(255,255,255,.04);" class="lead-row"
                    onmouseenter="this.style.background='rgba(255,255,255,.03)'"
                    onmouseleave="this.style.background='transparent'">
                  <td style="padding:10px 12px;font-size:13px;font-weight:600;">${l.name}</td>
                  <td style="padding:10px 12px;font-size:12px;color:var(--text-secondary);">${l.contact}<br><span style="font-size:10px;color:var(--text-muted);">${l.phone}</span></td>
                  <td style="padding:10px 12px;font-size:12px;color:var(--text-muted);">${l.nicho}</td>
                  <td style="padding:10px 12px;">
                    <span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;
                                 background:${st.color}22;color:${st.color};">
                      ${st.icon} ${st.label}
                    </span>
                  </td>
                  <td style="padding:10px 12px;font-size:13px;font-weight:700;color:var(--green);">${l.amount}€</td>
                  <td style="padding:10px 12px;font-size:11px;color:var(--text-muted);">${l.source}</td>
                  <td style="padding:10px 12px;font-size:11px;color:var(--text-muted);">${l.created}</td>
                  <td style="padding:10px 12px;">
                    <div style="display:flex;gap:6px;">
                      ${l.status !== 'closed' && l.status !== 'lost' ? `
                        <button class="lead-advance" data-id="${l.id}"
                          style="padding:4px 10px;background:rgba(16,185,129,.15);color:var(--green);border:1px solid rgba(16,185,129,.3);
                                 border-radius:6px;font-size:10px;font-weight:700;cursor:pointer;">
                          Avanzar →
                        </button>
                      ` : ''}
                      <button class="lead-delete" data-id="${l.id}"
                        style="padding:4px 8px;background:rgba(239,68,68,.1);color:var(--red);border:1px solid rgba(239,68,68,.2);
                               border-radius:6px;font-size:10px;cursor:pointer;">
                        ✕
                      </button>
                    </div>
                  </td>
                </tr>
              `}).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    // Events
    container.querySelector('#crm-search').addEventListener('input', e => { search = e.target.value; render(); });

    container.querySelectorAll('.crm-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        filter = btn.dataset.status === filter ? 'all' : btn.dataset.status;
        render();
      });
    });

    container.querySelectorAll('.lead-advance').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = Number(btn.dataset.id);
        const order = ['cold','contacted','proposal','closed'];
        const lead = leads.find(l => l.id === id);
        if (lead) {
          const idx = order.indexOf(lead.status);
          if (idx < order.length - 1) lead.status = order[idx + 1];
          saveLeads(leads);
          render();
        }
      });
    });

    container.querySelectorAll('.lead-delete').forEach(btn => {
      btn.addEventListener('click', () => {
        leads = leads.filter(l => l.id !== Number(btn.dataset.id));
        saveLeads(leads);
        render();
      });
    });

    container.querySelector('#btn-new-lead').addEventListener('click', () => {
      const name = prompt('Nombre del negocio:');
      if (!name) return;
      const contact = prompt('Nombre del contacto:') || '';
      const phone = prompt('Teléfono:') || '';
      const nicho = prompt('Nicho (ej: Peluquería):') || '';
      const amount = Number(prompt('Valor estimado (€):') || '297');
      leads.push({ id: Date.now(), name, contact, phone, nicho, status:'cold', amount, source:'Manual', created: new Date().toISOString().split('T')[0], notes:'' });
      saveLeads(leads);
      render();
    });
  }

  render();
}
