// ═══════════════════════════════════════════════
// Agentes IA — Los 43 Agentes de Sistema180
// ═══════════════════════════════════════════════

const DEPARTMENTS = [
  {
    dept: 'Orquestadores', icon:'🧠', color:'#f59e0b', floor:'Planta 4',
    agents: [
      { name:'Alejandro', role:'CEO Agent',   desc:'Dirección estratégica, objetivos, KPIs globales', model:'Gemini 2.5 Flash', status:'ready' },
      { name:'Rafael',    role:'COO Agent',   desc:'Operaciones, flujos, coordinación entre departamentos', model:'Gemini 2.5 Flash', status:'ready' },
      { name:'Valentina', role:'CMO Agent',   desc:'Marketing, contenido, Meta Ads, marca personal Ares', model:'Gemini 2.5 Flash', status:'ready' },
    ]
  },
  {
    dept: 'Jefes de Área', icon:'📋', color:'#6366f1', floor:'Planta 3',
    agents: [
      { name:'Marcos',   role:'Sales Head',       desc:'Coordina SDR, Closer Support, Lead Scout', model:'Gemini 2.5 Flash', status:'ready' },
      { name:'Sofía',    role:'Content Head',     desc:'Coordina toda la producción de contenido', model:'Gemini 2.5 Flash', status:'ready' },
      { name:'Eduardo',  role:'Finance Head',     desc:'Facturación, cobros, afiliados, splits', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Lucía',    role:'Client Success',   desc:'Onboarding, soporte, retención de clientes', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Diego',    role:'Marketplace Head', desc:'Gestión negocios y alquileres del marketplace', model:'Gemini 2.5 Flash', status:'building' },
    ]
  },
  {
    dept: 'Edición de Vídeo', icon:'✂️', color:'#06b6d4', floor:'Planta 2',
    agents: [
      { name:'Carlos',  role:'Edit Orchestrator', desc:'Coordina el pipeline completo de edición', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Mateo',   role:'Cut Agent',         desc:'Cortes automáticos de silencios (FFmpeg + Whisper)', model:'Local/FFmpeg', status:'building' },
      { name:'Álvaro',  role:'Audio Agent',       desc:'Limpieza audio, música de fondo, FX', model:'Local', status:'building' },
      { name:'Bruno',   role:'Color Agent',       desc:'Corrección de color y grading automático', model:'Local', status:'building' },
      { name:'Carmen',  role:'Subtitle Agent',    desc:'Subtítulos animados en español', model:'Whisper', status:'building' },
      { name:'Hugo',    role:'Zoom Agent',        desc:'Zoom dinámico automático sobre el orador', model:'Local', status:'building' },
      { name:'Marta',   role:'Thumbnail Agent',  desc:'Generación automática de thumbnails', model:'ComfyUI', status:'building' },
      { name:'Iván',    role:'Format Agent',      desc:'Adapta vídeo a 9:16, 1:1, 16:9 automáticamente', model:'FFmpeg', status:'building' },
      { name:'Elena',   role:'Quality Agent',     desc:'QA final antes de publicar', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Noa',     role:'Publisher Agent',   desc:'Auto-publicación vía Metricool API', model:'Metricool API', status:'building' },
    ]
  },
  {
    dept: 'Copy & Guiones', icon:'📝', color:'#10b981', floor:'Planta 2',
    agents: [
      { name:'Adriana',  role:'Copy Orchestrator', desc:'Coordina todos los agentes de copy', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Pablo',    role:'Script Agent',      desc:'Guiones virales Método Heras (Hook→Historia→Moraleja→CTA)', model:'Gemini 2.5 Flash', status:'ready' },
      { name:'Sergio',   role:'Ads Agent',         desc:'Copy para Meta Ads, TikTok Ads, Google Ads', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Alba',     role:'Caption Agent',     desc:'Pies de foto para Instagram, TikTok, LinkedIn', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Tomás',    role:'Email Agent',       desc:'Secuencias de email marketing y newsletter', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Claudia',  role:'WhatsApp Agent',    desc:'Mensajes de venta y seguimiento por WhatsApp', model:'Gemini 2.5 Flash', status:'building' },
    ]
  },
  {
    dept: 'Ventas', icon:'💼', color:'#ec4899', floor:'Planta 2',
    agents: [
      { name:'Roberto',  role:'Sales Orchestrator', desc:'Coordina todo el pipeline de ventas', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Javier',   role:'Lead Scout',         desc:'Busca negocios en Google Maps (webs rotas, malas reseñas)', model:'Gemini 2.5 + Maps API', status:'building' },
      { name:'Ares',     role:'SDR Agent',          desc:'Mensajes WhatsApp personalizados en frío', model:'Gemini 2.5 Flash', status:'ready' },
      { name:'Natalia',  role:'CRM Agent',          desc:'Gestiona el pipeline, mueve leads entre etapas', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Gonzalo',  role:'Closer Support',     desc:'Briefings para closers, objeciones, argumentarios', model:'Gemini 2.5 Flash', status:'building' },
    ]
  },
  {
    dept: 'Atención al Cliente', icon:'🎧', color:'#f97316', floor:'Planta 2',
    agents: [
      { name:'Isabel',   role:'Client Orchestrator', desc:'Coordina toda la experiencia del cliente', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Miguel',   role:'Onboarding Agent',    desc:'Bienvenida, configuración inicial, primeros pasos', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Andrea',   role:'Support Agent',       desc:'Responde dudas y tickets de soporte 24/7', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Fernando', role:'Billing Agent',       desc:'Facturación, cobros fallidos, gestión pagos', model:'Stripe + Gemini', status:'building' },
      { name:'Cristina', role:'Report Agent',        desc:'Informes mensuales de resultados por cliente', model:'Gemini 2.5 Flash', status:'building' },
    ]
  },
  {
    dept: 'Afiliados', icon:'🤝', color:'#818cf8', floor:'Planta 2',
    agents: [
      { name:'Antonio',  role:'Affiliate Orchestrator', desc:'Gestiona todo el programa de afiliados', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Raquel',   role:'Commission Agent',       desc:'Calcula y registra comisiones por nivel', model:'Stripe + DB', status:'building' },
      { name:'David',    role:'Payment Agent',          desc:'Transfers automáticos día 15 (hold 14d)', model:'Stripe Connect', status:'building' },
      { name:'Víctor',   role:'Fraud Agent',            desc:'Detecta chargebacks, suspende circuit breaker ×3', model:'Stripe + Gemini', status:'building' },
    ]
  },
  {
    dept: 'Marketplace', icon:'🏪', color:'#34d399', floor:'Planta 2',
    agents: [
      { name:'Beatriz',   role:'Marketplace Orchestrator', desc:'Gestiona toda la plataforma marketplace', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Guillermo', role:'Booking Agent',            desc:'Gestiona reservas y disponibilidad', model:'Gemini 2.5 Flash', status:'building' },
      { name:'Irene',     role:'Split Agent',              desc:'Split automático Stripe Connect propietario/S180', model:'Stripe Connect', status:'building' },
      { name:'Mario',     role:'Review Agent',             desc:'Modera y gestiona reseñas de la plataforma', model:'Gemini 2.5 Flash', status:'building' },
    ]
  },
  {
    dept: 'Legal', icon:'⚖️', color:'#f87171', floor:'Planta 2',
    agents: [
      { name:'Amparo', role:'Legal Agent', desc:'Genera GDPR/LSSI automáticamente para cada web cliente', model:'Gemini 2.5 Flash', status:'building' },
    ]
  },
];

export function renderAgents(container) {
  const allAgents = DEPARTMENTS.flatMap(d => d.agents);
  const ready = allAgents.filter(a => a.status === 'ready').length;
  const building = allAgents.filter(a => a.status === 'building').length;

  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
      <div>
        <h2 style="font-size:22px;font-weight:800;">🤖 Los 43 Agentes</h2>
        <p style="color:var(--text-muted);font-size:13px;">
          <span style="color:var(--green)">● ${ready} operativos</span>
          &nbsp;·&nbsp;
          <span style="color:var(--orange)">⚙️ ${building} en construcción</span>
          &nbsp;·&nbsp; Todos usan Gemini 2.5 Flash (coste ~0)
        </p>
      </div>
      <div style="padding:8px 16px;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.2);
                  border-radius:10px;font-size:12px;color:var(--green);font-weight:700;">
        ${ready}/${allAgents.length} listos · ${Math.round(ready/allAgents.length*100)}%
      </div>
    </div>

    <!-- Progress bar global -->
    <div class="card" style="margin-bottom:20px;">
      <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text-muted);margin-bottom:8px;">
        <span>Progreso construcción del edificio</span>
        <span style="color:var(--green);font-weight:700;">${ready}/${allAgents.length} agentes</span>
      </div>
      <div style="background:rgba(255,255,255,.06);border-radius:99px;height:8px;">
        <div style="background:linear-gradient(90deg,var(--green),#34d399);height:8px;border-radius:99px;
                    width:${Math.round(ready/allAgents.length*100)}%;transition:width .8s;
                    box-shadow:0 0 10px rgba(16,185,129,.4);"></div>
      </div>
      <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;">
        ${DEPARTMENTS.map(d=>{
          const r = d.agents.filter(a=>a.status==='ready').length;
          const t = d.agents.length;
          return `<span title="${d.dept}: ${r}/${t}" style="font-size:10px;padding:2px 8px;border-radius:20px;
                  background:${r===t?'rgba(16,185,129,.15)':'rgba(255,255,255,.04)'};
                  border:1px solid ${r===t?'rgba(16,185,129,.3)':'rgba(255,255,255,.06)'};
                  color:${r===t?'var(--green)':'var(--text-muted)'}">${d.icon} ${d.dept}</span>`;
        }).join('')}
      </div>
    </div>

    <!-- Departments -->
    ${DEPARTMENTS.map(dept => {
      const readyInDept = dept.agents.filter(a => a.status === 'ready').length;
      return `
      <div style="margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;padding:0 4px;">
          <span style="font-size:22px;">${dept.icon}</span>
          <div>
            <div style="font-size:15px;font-weight:800;color:${dept.color};">${dept.dept}</div>
            <div style="font-size:11px;color:var(--text-muted);">${dept.floor} · ${readyInDept}/${dept.agents.length} operativos</div>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;">
          ${dept.agents.map(agent => `
            <div style="padding:14px 16px;border-radius:12px;
                        background:${agent.status==='ready' ? 'rgba(16,185,129,.06)' : 'rgba(255,255,255,.03)'};
                        border:1px solid ${agent.status==='ready' ? 'rgba(16,185,129,.2)' : 'rgba(255,255,255,.06)'};
                        border-left:3px solid ${agent.status==='ready' ? 'var(--green)' : dept.color};">
              <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:6px;">
                <div>
                  <div style="font-size:16px;font-weight:800;color:${agent.status==='ready' ? 'var(--text-primary)' : 'var(--text-secondary)'};">${agent.name}</div>
                  <div style="font-size:10px;font-weight:700;color:${dept.color};letter-spacing:.04em;margin-top:1px;">${agent.role}</div>
                </div>
                <span style="padding:2px 8px;border-radius:20px;font-size:9px;font-weight:800;white-space:nowrap;
                             background:${agent.status==='ready' ? 'rgba(16,185,129,.2)' : 'rgba(245,158,11,.15)'};
                             color:${agent.status==='ready' ? 'var(--green)' : 'var(--orange)'};">
                  ${agent.status === 'ready' ? '● READY' : '⚙️ BUILD'}
                </span>
              </div>
              <div style="font-size:11px;color:var(--text-muted);margin-bottom:8px;line-height:1.5;">${agent.desc}</div>
              <div style="font-size:10px;color:${dept.color};font-weight:600;opacity:.8;">🔧 ${agent.model}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `}).join('')}
  `;
}
