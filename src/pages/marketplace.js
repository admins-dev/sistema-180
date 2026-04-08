// ═══════════════════════════════════════════════
// Marketplace — Sistema180 (Negocios + Alquileres)
// Stripe Connect Express: propietario 87% / S180 13%
// ═══════════════════════════════════════════════
import { storage } from '../services/storage.js';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3000';
const STRIPE_PK = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '';

async function apiCall(endpoint, opts = {}) {
  const apiKey = storage.get('admin_api_key') || import.meta.env.VITE_ADMIN_API_KEY || '';
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
      ...(opts.headers || {}),
    },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Modal: Register new property owner ───────────────────────
function openRegisterModal(_container, onSuccess) {
  const modal = document.createElement('div');
  modal.style.cssText = `
    position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:1000;
    display:flex;align-items:center;justify-content:center;padding:20px;
  `;
  modal.innerHTML = `
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:16px;
                padding:28px;width:100%;max-width:480px;">
      <div style="font-size:18px;font-weight:800;margin-bottom:20px;">🏠 Registrar propietario</div>
      <div style="display:flex;flex-direction:column;gap:12px;">
        ${['owner_name:Nombre completo', 'owner_email:Email', 'owner_phone:Teléfono',
           'property_name:Nombre de la propiedad', 'location:Ubicación (ciudad/dirección)',
           'web_url:URL de la web (opcional)'].map(f => {
          const [id, label] = f.split(':');
          return `<div>
            <label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:4px;">${label}</label>
            <input id="mp_${id}" placeholder="${label}"
              style="width:100%;padding:9px 12px;background:rgba(255,255,255,.06);
                     border:1px solid var(--border);border-radius:8px;color:var(--text-primary);
                     font-size:13px;box-sizing:border-box;">
          </div>`;
        }).join('')}
        <div>
          <label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:4px;">Tipo</label>
          <select id="mp_property_type"
            style="width:100%;padding:9px 12px;background:rgba(255,255,255,.06);
                   border:1px solid var(--border);border-radius:8px;color:var(--text-primary);font-size:13px;">
            <option value="rental">Alquiler vacacional</option>
            <option value="business">Negocio local</option>
          </select>
        </div>
        <div style="display:flex;gap:10px;margin-top:8px;">
          <button id="mp_cancel_btn"
            style="flex:1;padding:10px;background:rgba(255,255,255,.06);color:var(--text-secondary);
                   border:1px solid var(--border);border-radius:8px;cursor:pointer;font-weight:600;">
            Cancelar
          </button>
          <button id="mp_save_btn"
            style="flex:2;padding:10px;background:var(--accent);color:#fff;border:none;
                   border-radius:8px;cursor:pointer;font-weight:700;font-size:14px;">
            Registrar →
          </button>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  modal.querySelector('#mp_cancel_btn').onclick = () => modal.remove();
  modal.querySelector('#mp_save_btn').onclick = async () => {
    const btn = modal.querySelector('#mp_save_btn');
    btn.textContent = 'Registrando...'; btn.disabled = true;
    try {
      const body = {};
      ['owner_name','owner_email','owner_phone','property_name','location','web_url'].forEach(k => {
        body[k] = modal.querySelector(`#mp_${k}`)?.value || '';
      });
      body.property_type = modal.querySelector('#mp_property_type').value;
      const prop = await apiCall('/api/marketplace/properties', {
        method: 'POST', body: JSON.stringify(body)
      });
      modal.remove();
      onSuccess(prop);
    } catch (err) {
      btn.textContent = `Error: ${err.message}`;
      btn.disabled = false;
    }
  };
}

// ── Property card ─────────────────────────────────────────────
function propertyCard(prop) {
  const statusColor = {
    active: 'var(--green)',
    onboarding: 'var(--orange)',
    pending: 'var(--red)',
    restricted: 'var(--red)',
  }[prop.connect_status] || 'var(--text-muted)';

  const statusLabel = {
    active: '● ACTIVO',
    onboarding: '⚙️ ONBOARDING',
    pending: '❌ PENDIENTE',
    restricted: '⚠️ RESTRINGIDO',
  }[prop.connect_status] || prop.connect_status?.toUpperCase();

  return `
    <div data-prop-id="${prop.id}"
      style="padding:18px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
             border-radius:12px;border-left:3px solid ${prop.connect_status === 'active' ? 'var(--green)' : 'var(--red)'};">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px;">
        <div>
          <div style="font-size:15px;font-weight:800;">${prop.property_name}</div>
          <div style="font-size:12px;color:var(--text-muted);">${prop.owner_name} · ${prop.owner_email}</div>
          ${prop.location ? `<div style="font-size:11px;color:var(--text-muted);margin-top:2px;">📍 ${prop.location}</div>` : ''}
        </div>
        <span style="padding:3px 10px;border-radius:20px;font-size:10px;font-weight:800;white-space:nowrap;
                     background:${statusColor}22;color:${statusColor};">${statusLabel}</span>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;margin-bottom:12px;">
        <div style="background:rgba(255,255,255,.03);padding:8px;border-radius:6px;">
          <div style="color:var(--text-muted);font-size:10px;">Tipo</div>
          <div style="font-weight:700;">${prop.property_type === 'rental' ? '🏠 Alquiler' : '🏬 Negocio'}</div>
        </div>
        <div style="background:rgba(255,255,255,.03);padding:8px;border-radius:6px;">
          <div style="color:var(--text-muted);font-size:10px;">Comisión S180</div>
          <div style="font-weight:700;color:var(--accent);">${Math.round((prop.commission_pct || 0.13) * 100)}%</div>
        </div>
        ${prop.stripe_account_id ? `
        <div style="background:rgba(255,255,255,.03);padding:8px;border-radius:6px;">
          <div style="color:var(--text-muted);font-size:10px;">Stripe Account</div>
          <div style="font-weight:600;font-size:11px;font-family:monospace;">${prop.stripe_account_id.slice(0,18)}…</div>
        </div>` : ''}
        ${prop.connect_onboarded_at ? `
        <div style="background:rgba(16,185,129,.06);padding:8px;border-radius:6px;border:1px solid rgba(16,185,129,.2);">
          <div style="color:var(--text-muted);font-size:10px;">Activo desde</div>
          <div style="font-weight:700;color:var(--green);font-size:11px;">${new Date(prop.connect_onboarded_at).toLocaleDateString('es-ES')}</div>
        </div>` : ''}
      </div>

      ${prop.connect_status !== 'active' ? `
      <button onclick="window._mpConnect(${prop.id})"
        style="width:100%;padding:10px;background:${prop.connect_status === 'onboarding' ? 'var(--orange)' : 'var(--red)'};
               color:#fff;border:none;border-radius:8px;font-weight:700;font-size:13px;cursor:pointer;">
        ${prop.connect_status === 'onboarding' ? '⚙️ Continuar configuración →' : '⚡ Conectar Stripe ahora →'}
      </button>` : `
      <div style="padding:8px 14px;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);
                  border-radius:8px;font-size:12px;color:var(--green);text-align:center;font-weight:700;">
        ✅ Stripe Connect activo — pagos automáticos habilitados
      </div>`}
    </div>
  `;
}

export async function renderMarketplace(container) {
  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
      <div>
        <h2 style="font-size:22px;font-weight:800;">🏪 Marketplace</h2>
        <p style="color:var(--text-muted);font-size:13px;">Directorio de negocios locales + alquileres vacacionales</p>
      </div>
      <button id="mp_add_btn"
        style="padding:9px 18px;background:var(--accent);color:#fff;border:none;
               border-radius:10px;font-weight:700;font-size:13px;cursor:pointer;">
        + Registrar propietario
      </button>
    </div>

    <!-- KPI stats -->
    <div id="mp_stats" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px;">
      <div class="card" style="text-align:center;">
        <div style="font-size:22px;margin-bottom:4px;">⏳</div>
        <div style="font-size:18px;font-weight:800;">—</div>
        <div style="font-size:11px;color:var(--text-muted);">Cargando stats...</div>
      </div>
    </div>

    <!-- Model visual -->
    <div class="card" style="margin-bottom:20px;">
      <div style="font-size:13px;font-weight:800;margin-bottom:16px;">💸 Split automático por cada pago</div>
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
        ${[
          { icon:'👤', label:'Cliente paga', val:'100€', color:'var(--accent)' },
          { arrow: true },
          { icon:'🏢', label:'Stripe recibe', val:'entra a S180', color:'var(--text-muted)', small:true },
          { arrow: true },
          { icon:'🏠', label:'Propietario', val:'87€', color:'var(--green)', sub:'automático · mismo día' },
          { plus: true },
          { icon:'💰', label:'S180 retiene', val:'13€', color:'var(--orange)', sub:'comisión' },
        ].map(item => {
          if (item.arrow) return `<div style="font-size:20px;color:var(--text-muted);flex-shrink:0;">→</div>`;
          if (item.plus) return `<div style="font-size:20px;color:var(--text-muted);flex-shrink:0;">+</div>`;
          return `<div style="flex:1;min-width:140px;text-align:center;padding:14px;
                              background:rgba(255,255,255,.03);border-radius:10px;border:1px solid var(--border);">
            <div style="font-size:22px;margin-bottom:6px;">${item.icon}</div>
            <div style="font-size:12px;font-weight:700;">${item.label}</div>
            <div style="font-size:${item.small ? '13px' : '20px'};font-weight:800;color:${item.color};margin-top:4px;">${item.val}</div>
            ${item.sub ? `<div style="font-size:10px;color:var(--text-muted);">${item.sub}</div>` : ''}
          </div>`;
        }).join('')}
      </div>
    </div>

    <!-- Properties list -->
    <div class="card">
      <div style="font-size:13px;font-weight:800;margin-bottom:14px;">🏘️ Propiedades registradas</div>
      <div id="mp_properties_list">
        <div style="text-align:center;padding:30px;color:var(--text-muted);font-size:13px;">
          Cargando propiedades...
        </div>
      </div>
    </div>

    <!-- Stripe Connect info -->
    <div class="card" style="margin-top:16px;border-top:3px solid var(--accent);">
      <div style="font-size:13px;font-weight:800;margin-bottom:12px;">🔗 Cómo funciona Stripe Connect Express</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;">
        ${[
          { n:'1', label:'Registro', desc:'El propietario se registra en el sistema (nombre, email, propiedad)', color:'var(--accent)' },
          { n:'2', label:'Onboarding', desc:'Recibe un link de Stripe → completa KYC + añade cuenta bancaria en 5 min', color:'var(--orange)' },
          { n:'3', label:'Activo', desc:'Stripe confirma — la propiedad aparece como activa con pagos habilitados', color:'var(--green)' },
          { n:'4', label:'Cobros automáticos', desc:'Cada reserva: S180 cobra 100%, transfiere 87% al propietario automáticamente', color:'var(--cyan)' },
        ].map(s=>`
          <div style="padding:12px;background:rgba(255,255,255,.03);border-radius:8px;border:1px solid var(--border);">
            <div style="width:24px;height:24px;border-radius:50%;background:${s.color}22;color:${s.color};
                        font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center;margin-bottom:8px;">
              ${s.n}
            </div>
            <div style="font-size:12px;font-weight:700;color:${s.color};margin-bottom:4px;">${s.label}</div>
            <div style="font-size:11px;color:var(--text-muted);line-height:1.4;">${s.desc}</div>
          </div>
        `).join('')}
      </div>
      ${STRIPE_PK ? `
      <div style="margin-top:12px;padding:8px 14px;background:rgba(16,185,129,.06);border-radius:8px;font-size:11px;color:var(--green);font-weight:600;">
        ✅ Stripe Live conectado · ${STRIPE_PK.slice(0,18)}...
      </div>` : `
      <div style="margin-top:12px;padding:8px 14px;background:rgba(245,158,11,.06);border-radius:8px;font-size:11px;color:var(--orange);">
        ⚠️ VITE_STRIPE_PUBLISHABLE_KEY no configurado
      </div>`}
    </div>
  `;

  // ── Load stats ───────────────────────────────────────────
  async function loadStats() {
    try {
      const stats = await apiCall('/api/marketplace/stats');
      document.getElementById('mp_stats').innerHTML = `
        ${[
          { icon:'🏘️', val: stats.total_properties, label:'Propiedades totales', color:'var(--accent)' },
          { icon:'✅', val: stats.active_properties, label:'Connect activo', color:'var(--green)' },
          { icon:'⏳', val: stats.pending_properties, label:'Pendientes', color:'var(--orange)' },
          { icon:'💰', val: (parseInt(stats.total_fees_cents||0)/100).toLocaleString('es-ES')+'€', label:'Comisiones cobradas', color:'var(--cyan)' },
          { icon:'💳', val: (parseInt(stats.total_revenue_cents||0)/100).toLocaleString('es-ES')+'€', label:'Revenue total', color:'var(--green)' },
        ].map(s=>`
          <div class="card" style="text-align:center;">
            <div style="font-size:22px;margin-bottom:6px;">${s.icon}</div>
            <div style="font-size:22px;font-weight:800;color:${s.color};">${s.val}</div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${s.label}</div>
          </div>
        `).join('')}
      `;
    } catch (_) {
      document.getElementById('mp_stats').innerHTML = `
        <div class="card" style="text-align:center;grid-column:1/-1;color:var(--text-muted);font-size:12px;">
          Stats no disponibles (backend offline)
        </div>
      `;
    }
  }

  // ── Load properties ──────────────────────────────────────
  async function loadProperties() {
    const list = document.getElementById('mp_properties_list');
    if (!list) return;
    try {
      const props = await apiCall('/api/marketplace/properties');
      if (!props.length) {
        list.innerHTML = `
          <div style="text-align:center;padding:30px;color:var(--text-muted);font-size:13px;">
            No hay propiedades registradas aún.<br>
            <span style="font-size:12px;">Haz clic en "+ Registrar propietario" para empezar.</span>
          </div>
        `;
        return;
      }
      list.innerHTML = `
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;">
          ${props.map(p => propertyCard(p)).join('')}
        </div>
      `;
    } catch (err) {
      list.innerHTML = `
        <div style="text-align:center;padding:30px;color:var(--text-muted);font-size:12px;">
          Backend no disponible: ${err.message}<br>
          <span style="font-size:11px;">Inicia el servidor con: cd backend && npm start</span>
        </div>
      `;
    }
  }

  // ── Connect handler ──────────────────────────────────────
  window._mpConnect = async (propId) => {
    const btn = document.querySelector(`[data-prop-id="${propId}"] button`);
    if (btn) { btn.textContent = 'Generando link...'; btn.disabled = true; }
    try {
      const result = await apiCall(`/api/marketplace/properties/${propId}/connect`, { method: 'POST' });
      window.open(result.onboarding_url, '_blank');
      await loadProperties();
    } catch (err) {
      if (btn) { btn.textContent = `Error: ${err.message}`; btn.disabled = false; }
    }
  };

  // ── Add button ───────────────────────────────────────────
  document.getElementById('mp_add_btn')?.addEventListener('click', () => {
    openRegisterModal(container, async (_prop) => {
      await loadProperties();
      await loadStats();
    });
  });

  // Fix #16: Use allSettled so one failure doesn't block the other
  await Promise.allSettled([loadStats(), loadProperties()]);
}
