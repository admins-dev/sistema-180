// ═══════════════════════════════════════════════
// Agentes IA — AI Command Center — Sistema 180
// Connected to ClaudeFlow/Ruflo V3 Swarm
// ═══════════════════════════════════════════════
import { claudeflow } from '../services/claudeflow.js';

const DEPARTMENTS = [
  {
    dept: 'Orquestadores', icon: 'O', color: '#f59e0b', floor: 'Planta 4',
    agents: [
      { name: 'Alejandro', role: 'CEO Agent',   desc: 'Dirección estratégica, objetivos, KPIs globales', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Rafael',    role: 'COO Agent',   desc: 'Operaciones, flujos, coordinación entre departamentos', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Valentina', role: 'CMO Agent',   desc: 'Marketing, contenido, Meta Ads, marca personal Ares', model: 'Gemini 2.5 Flash', status: 'ready' },
    ]
  },
  {
    dept: 'Jefes de Área', icon: 'J', color: '#6366f1', floor: 'Planta 3',
    agents: [
      { name: 'Marcos',   role: 'Sales Head',       desc: 'Coordina SDR, Closer Support, Lead Scout', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Sofía',    role: 'Content Head',     desc: 'Coordina toda la producción de contenido', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Eduardo',  role: 'Finance Head',     desc: 'Facturación, cobros, afiliados, splits — Stripe Connect', model: 'Stripe + Gemini', status: 'ready' },
      { name: 'Lucía',    role: 'Client Success',   desc: 'Onboarding, soporte, retención de clientes', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Diego',    role: 'Marketplace Head', desc: 'Gestión negocios y alquileres del marketplace', model: 'Gemini 2.5 Flash', status: 'ready' },
    ]
  },
  {
    dept: 'Edición de Vídeo', icon: 'V', color: '#06b6d4', floor: 'Planta 2',
    agents: [
      { name: 'Carlos',  role: 'Edit Orchestrator', desc: 'Coordina el pipeline completo de edición', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Mateo',   role: 'Cut Agent',         desc: 'Cortes automáticos de silencios (FFmpeg + Whisper)', model: 'Local/FFmpeg', status: 'ready' },
      { name: 'Álvaro',  role: 'Audio Agent',       desc: 'Limpieza audio, música de fondo, FX', model: 'Local', status: 'ready' },
      { name: 'Bruno',   role: 'Color Agent',       desc: 'Corrección de color y grading automático', model: 'Local', status: 'ready' },
      { name: 'Carmen',  role: 'Subtitle Agent',    desc: 'Subtítulos animados en español', model: 'Whisper', status: 'ready' },
      { name: 'Hugo',    role: 'Zoom Agent',        desc: 'Zoom dinámico automático sobre el orador', model: 'Local', status: 'ready' },
      { name: 'Marta',   role: 'Thumbnail Agent',   desc: 'Generación automática de thumbnails', model: 'ComfyUI', status: 'ready' },
      { name: 'Iván',    role: 'Format Agent',      desc: 'Adapta vídeo a 9:16, 1:1, 16:9 automáticamente', model: 'FFmpeg', status: 'ready' },
      { name: 'Elena',   role: 'Quality Agent',     desc: 'QA final antes de publicar', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Noa',     role: 'Publisher Agent',   desc: 'Auto-publicación vía Metricool API', model: 'Metricool API', status: 'ready' },
    ]
  },
  {
    dept: 'Copy & Guiones', icon: 'C', color: '#10b981', floor: 'Planta 2',
    agents: [
      { name: 'Adriana',  role: 'Copy Orchestrator', desc: 'Coordina todos los agentes de copy', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Pablo',    role: 'Script Agent',      desc: 'Guiones virales Método Heras (Hook→Historia→Moraleja→CTA)', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Sergio',   role: 'Ads Agent',         desc: 'Copy para Meta Ads + Pixel tracking + ROAS optimizer', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Alba',     role: 'Caption Agent',     desc: 'Pies de foto para Instagram, TikTok, LinkedIn', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Tomás',    role: 'Email Agent',       desc: 'Secuencias de email marketing y newsletter', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Claudia',  role: 'WhatsApp Agent',    desc: 'Mensajes de venta y seguimiento por WhatsApp', model: 'Gemini 2.5 Flash', status: 'ready' },
    ]
  },
  {
    dept: 'Ventas', icon: 'S', color: '#ec4899', floor: 'Planta 2',
    agents: [
      { name: 'Roberto',  role: 'Sales Orchestrator', desc: 'Coordina todo el pipeline de ventas', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Javier',   role: 'Lead Scout',         desc: 'Busca negocios en Google Maps (webs rotas, malas reseñas)', model: 'Gemini 2.5 + Maps API', status: 'ready' },
      { name: 'Ares',     role: 'SDR Agent',          desc: 'Mensajes WhatsApp personalizados en frío', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Natalia',  role: 'CRM Agent',          desc: 'Gestiona el pipeline, mueve leads entre etapas', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Gonzalo',  role: 'Closer Support',     desc: 'Briefings para closers, objeciones, argumentarios', model: 'Gemini 2.5 Flash', status: 'ready' },
    ]
  },
  {
    dept: 'Atención al Cliente', icon: 'A', color: '#f97316', floor: 'Planta 2',
    agents: [
      { name: 'Isabel',   role: 'Client Orchestrator', desc: 'Coordina toda la experiencia del cliente', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Miguel',   role: 'Onboarding Agent',    desc: 'Bienvenida, configuración inicial, primeros pasos', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Andrea',   role: 'Support Agent',       desc: 'Responde dudas y tickets de soporte 24/7', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Fernando', role: 'Billing Agent',       desc: 'Facturación, cobros, IVA 21%, gestión pagos Stripe', model: 'Stripe + Gemini', status: 'ready' },
      { name: 'Cristina', role: 'Report Agent',        desc: 'Informes mensuales de resultados por cliente', model: 'Gemini 2.5 Flash', status: 'ready' },
    ]
  },
  {
    dept: 'Afiliados', icon: 'AF', color: '#818cf8', floor: 'Planta 2',
    agents: [
      { name: 'Antonio',  role: 'Affiliate Orchestrator', desc: 'Gestiona todo el programa de afiliados', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Raquel',   role: 'Commission Agent',       desc: 'Calcula y registra comisiones por nivel', model: 'Stripe + DB', status: 'ready' },
      { name: 'David',    role: 'Payment Agent',          desc: 'Transfers automáticos día 15 (hold 14d)', model: 'Stripe Connect', status: 'ready' },
      { name: 'Víctor',   role: 'Fraud Agent',            desc: 'Detecta chargebacks, suspende circuit breaker ×3', model: 'Stripe + Gemini', status: 'ready' },
    ]
  },
  {
    dept: 'Marketplace', icon: 'M', color: '#34d399', floor: 'Planta 2',
    agents: [
      { name: 'Beatriz',   role: 'Marketplace Orchestrator', desc: 'Gestiona toda la plataforma marketplace', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Guillermo', role: 'Booking Agent',            desc: 'Gestiona reservas y disponibilidad', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Irene',     role: 'Split Agent',              desc: 'Split automático Stripe Connect propietario/S180', model: 'Stripe Connect', status: 'ready' },
      { name: 'Mario',     role: 'Review Agent',             desc: 'Modera y gestiona reseñas de la plataforma', model: 'Gemini 2.5 Flash', status: 'ready' },
    ]
  },
  {
    dept: 'Legal', icon: 'L', color: '#f87171', floor: 'Planta 2',
    agents: [
      { name: 'Amparo', role: 'Legal Agent', desc: 'Genera GDPR/LSSI automáticamente para cada web cliente', model: 'Gemini 2.5 Flash', status: 'ready' },
    ]
  },
  {
    dept: 'Pixel & Tracking', icon: 'P', color: '#f472b6', floor: 'Planta 1',
    agents: [
      { name: 'Luna',     role: 'Pixel Agent',       desc: 'Meta Pixel, eventos de conversión, tracking del funnel completo', model: 'Meta API + n8n', status: 'ready' },
      { name: 'Omar',     role: 'Analytics Agent',    desc: 'Dashboard de métricas: CPL, ROAS, CAC, LTV en tiempo real', model: 'Gemini 2.5 Flash', status: 'ready' },
      { name: 'Daniela',  role: 'A/B Test Agent',     desc: 'Tests A/B en landing pages, emails y ads — auto-optimiza', model: 'Gemini 2.5 Flash', status: 'ready' },
    ]
  },
  {
    dept: 'Ruflo Swarm', icon: 'R', color: '#a78bfa', floor: 'Subsuelo',
    agents: [
      { name: 'Ruflo-Queen',   role: 'Hive Mind',          desc: 'Reina del enjambre — orquesta todos los sub-agentes de ClaudeFlow', model: 'ClaudeFlow v3', status: 'ready' },
      { name: 'Ruflo-Coder',   role: 'Code Agent',         desc: 'Generación de código, commits a GitHub, deploys Vercel', model: 'Haiku $0.01', status: 'ready' },
      { name: 'Ruflo-Research', role: 'Research Agent',     desc: 'Investigación web profunda, scraping de competidores con Apify', model: 'Haiku $0.01', status: 'ready' },
      { name: 'Ruflo-Writer',  role: 'Content Writer',     desc: 'Generación masiva de copys, emails y guiones en lote', model: 'Haiku $0.01', status: 'ready' },
      { name: 'Ruflo-Auditor', role: 'Audit Agent',        desc: 'Auditoría de rendimiento: analiza métricas y propone mejoras', model: 'Haiku $0.01', status: 'ready' },
      { name: 'Ruflo-Router',  role: 'Q-Learning Router',  desc: 'Enrutamiento inteligente de tareas al agente óptimo via Q-Learning', model: 'ClaudeFlow v3', status: 'ready' },
      { name: 'Ruflo-Memory',  role: 'Memory Agent',       desc: 'Base de datos vectorial HNSW — memoria persistente del enjambre', model: 'SQLite + HNSW', status: 'ready' },
      { name: 'Ruflo-Guard',   role: 'Security Agent',     desc: 'Circuit breaker, rate limiting, protección contra bucles infinitos', model: 'ClaudeFlow v3', status: 'ready' },
    ]
  },
  {
    dept: 'Antigravity IDE', icon: 'AG', color: '#22d3ee', floor: 'Subsuelo',
    agents: [
      { name: 'Antigravity',  role: 'Lead Architect',    desc: 'Arquitecto principal — Gemini 3.1 Pro — programación ilimitada gratuita', model: 'Gemini 3.1 Pro', status: 'ready' },
      { name: 'Cowork',       role: 'Strategy Brain',    desc: 'Cerebro estratégico — Claude Sonnet — 160M tokens para planificación', model: 'Claude Sonnet', status: 'ready' },
      { name: 'Claude-Code',  role: 'CLI Executor',      desc: 'Ejecutor CLI — Haiku — micro-tareas de terminal $0.01/tarea', model: 'Claude Haiku', status: 'ready' },
    ]
  },
];

// ─── Pixel Avatar SVG ───────────────────────────────────────────────────────
function pixelAvatar(color, status) {
  const glow = status === 'ready' ? `filter:drop-shadow(0 0 6px ${color}66)` : '';
  return `<svg width="48" height="48" viewBox="0 0 16 16" style="image-rendering:pixelated;${glow}">
    <rect x="5" y="1" width="6" height="5" fill="${color}" rx="1"/>
    <rect x="6" y="2.5" width="1.5" height="1.5" fill="#fff" rx="0.2"/>
    <rect x="8.5" y="2.5" width="1.5" height="1.5" fill="#fff" rx="0.2"/>
    <rect x="6.4" y="2.8" width="0.7" height="0.7" fill="#0f172a"/>
    <rect x="8.9" y="2.8" width="0.7" height="0.7" fill="#0f172a"/>
    ${status === 'ready'
      ? '<path d="M6.5 4.3 Q8 5.2 9.5 4.3" stroke="#fff" stroke-width="0.5" fill="none"/>'
      : '<rect x="6.3" y="4.3" width="3.4" height="0.4" fill="#ffffff33" rx="0.2"/>'}
    <rect x="4" y="7" width="8" height="5" fill="${color}cc" rx="1"/>
    <rect x="2" y="7.5" width="2" height="3" fill="${color}99" rx="0.5"/>
    <rect x="12" y="7.5" width="2" height="3" fill="${color}99" rx="0.5"/>
    <rect x="5" y="12" width="2.5" height="3" fill="${color}77" rx="0.5"/>
    <rect x="8.5" y="12" width="2.5" height="3" fill="${color}77" rx="0.5"/>
    <circle cx="13.5" cy="1.5" r="1.5" fill="${status === 'ready' ? '#10b981' : '#f59e0b'}"/>
  </svg>`;
}

// ─── Big Pixel Avatar (modal) ────────────────────────────────────────────────
function pixelAvatarLarge(color, status) {
  const glow = status === 'ready' ? `filter:drop-shadow(0 0 12px ${color}88)` : '';
  return `<svg width="80" height="80" viewBox="0 0 16 16" style="image-rendering:pixelated;${glow}">
    <rect x="5" y="1" width="6" height="5" fill="${color}" rx="1"/>
    <rect x="6" y="2.5" width="1.5" height="1.5" fill="#fff" rx="0.2"/>
    <rect x="8.5" y="2.5" width="1.5" height="1.5" fill="#fff" rx="0.2"/>
    <rect x="6.4" y="2.8" width="0.7" height="0.7" fill="#0f172a"/>
    <rect x="8.9" y="2.8" width="0.7" height="0.7" fill="#0f172a"/>
    ${status === 'ready'
      ? '<path d="M6.5 4.3 Q8 5.2 9.5 4.3" stroke="#fff" stroke-width="0.5" fill="none"/>'
      : '<rect x="6.3" y="4.3" width="3.4" height="0.4" fill="#ffffff33" rx="0.2"/>'}
    <rect x="4" y="7" width="8" height="5" fill="${color}cc" rx="1"/>
    <rect x="2" y="7.5" width="2" height="3" fill="${color}99" rx="0.5"/>
    <rect x="12" y="7.5" width="2" height="3" fill="${color}99" rx="0.5"/>
    <rect x="5" y="12" width="2.5" height="3" fill="${color}77" rx="0.5"/>
    <rect x="8.5" y="12" width="2.5" height="3" fill="${color}77" rx="0.5"/>
    <circle cx="13.5" cy="1.5" r="1.5" fill="${status === 'ready' ? '#10b981' : '#f59e0b'}"/>
  </svg>`;
}

// ─── Circular SVG progress ───────────────────────────────────────────────────
function circularProgress(value, total, color) {
  const pct = value / total;
  const r = 42;
  const circ = 2 * Math.PI * r;
  const dash = circ * pct;
  const gap  = circ - dash;
  return `<svg width="120" height="120" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="${r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
    <circle cx="50" cy="50" r="${r}" fill="none" stroke="${color}" stroke-width="8"
      stroke-dasharray="${dash} ${gap}"
      stroke-dashoffset="${circ * 0.25}"
      stroke-linecap="round"
      style="filter:drop-shadow(0 0 6px ${color}88);transition:stroke-dasharray 1s ease"/>
    <text x="50" y="44" text-anchor="middle" fill="#fff" font-size="18" font-weight="900"
      font-family="system-ui,sans-serif">${value}</text>
    <text x="50" y="58" text-anchor="middle" fill="rgba(255,255,255,0.4)" font-size="10"
      font-family="system-ui,sans-serif">/ ${total}</text>
  </svg>`;
}

// ─── Simulated AI responses ───────────────────────────────────────────────────
const AI_RESPONSES = {
  'CEO': ['Estrategia activada. Revisando KPIs del trimestre...', 'Objetivos claros. Delegando a Rafael para ejecución.', 'Dashboard actualizado. Revenue target: 50 clientes en 40 días.'],
  'COO': ['Flujos optimizados. Coordinando departamentos...', 'Pipeline operativo al 94%. Sin bloqueos críticos.', 'Automatizaciones n8n sincronizadas. Todos los sistemas GO.'],
  'CMO': ['Campaña Meta Ads lista. Audiencia: 3 segmentos activos.', 'Contenido programado: 3 vídeos/día. Método Heras aplicado.', 'Brand awareness +23% esta semana. CTA: ANÁLISIS gratis.'],
  'SDR': ['Mensaje personalizado preparado. Calentamiento: semana 3 (100-150/día).', 'Lead identificado: barbería sin web en Marbella. Score: 87/100.', 'Secuencia WhatsApp activada. Follow-up en 48h automático.'],
  'Script': ['Guión generado: GANCHO → HISTORIA → MORALEJA → CTA. Duración: 60s.', 'Hook viral detectado. Pilares SDD aplicados: Dinero + Desarrollo.', 'Adaptado para TikTok 9:16. Subtítulos automáticos listos.'],
  'Pixel': ['Meta Pixel disparando eventos: PageView, Lead, Purchase. CAPI server-side activo.', 'Conversión detectada: lead → cliente en 48h. Atribución correcta.', 'Funnel tracking completo: Landing → WhatsApp → Cierre. CPL actual: 4.80€.'],
  'Analytics': ['Dashboard de métricas actualizado. ROAS: 4.2x · CPL: 4.80€ · CAC: 12.30€.', 'LTV estimado por cliente: 3.600€ (12 meses × 300€). Margen: 82%.', 'Anomalía detectada: CTR bajó 15% ayer. Recomendación: rotar creativos.'],
  'A/B': ['Test A/B en landing: variante B (+17% conversión). Ganadora declarada en 72h.', 'Split test activo en 3 emails de bienvenida. Muestra: 1.200 envíos.', 'Landing optimizada: headline "Más citas sin esfuerzo" > "IA para tu negocio" (+42%).'],
  'Hive': ['Enjambre inicializado. 8 sub-agentes asignados. Cola de tareas: 12 pendientes.', 'Q-Learning router optimizado. Eficiencia del enjambre: 94%. Coste: $0.08 total.', 'Memoria vectorial HNSW sincronizada. 2.847 embeddings indexados.'],
  'Code': ['Commit pushado a main. Deploy Vercel activado automáticamente. Build: OK.', 'Feature branch creada: fix/landing-responsiva. PR listo para review.', 'Código generado y testeado. 0 errores de lint. Coverage: 87%.'],
  'Research': ['Scraping completado: 47 clínicas estéticas en Málaga sin web profesional.', 'Competidor analizado: ofrecen landing a 500€. Nuestro pricing: 300€ → ventaja clara.', 'Tendencia detectada: "automatización WhatsApp" +340% en Google Trends España.'],
  'Lead': ['15 negocios identificados en Google Maps: 8 sin web, 4 con webs rotas, 3 sin reseñas.', 'Lead scout activo en zona: Marbella Centro. Score medio: 72/100.', 'Lista de leads actualizada: 23 nuevos negocios listos para contactar.'],
  'Billing': ['Factura #S180-028 generada: 300€ + IVA (363€). Stripe payment link enviado.', 'Cobro exitoso: Peluquería Sol — 300€/mes. Recurrente activado.', 'Alerta: pago fallido para Cliente #14. Reintento programado en 48h.'],
  'Architect': ['Arquitectura revisada. 12 módulos, 57 agentes, 0 dependencias circulares.', 'Refactoring completado: reducción 23% en bundle size. Build: 257kb.', 'Nuevo componente creado: MeetingRoom.js — sala de reuniones virtual.'],
  'default': ['Sistema activo. Procesando solicitud...', 'Módulo operativo. Tarea recibida y en cola.', 'Recibido. Coordinando con agentes del departamento.'],
};

function getAIResponse(role) {
  if (role.includes('CEO')) return AI_RESPONSES['CEO'][Math.floor(Math.random() * 3)];
  if (role.includes('COO')) return AI_RESPONSES['COO'][Math.floor(Math.random() * 3)];
  if (role.includes('CMO')) return AI_RESPONSES['CMO'][Math.floor(Math.random() * 3)];
  if (role.includes('SDR')) return AI_RESPONSES['SDR'][Math.floor(Math.random() * 3)];
  if (role.includes('Script')) return AI_RESPONSES['Script'][Math.floor(Math.random() * 3)];
  if (role.includes('Pixel')) return AI_RESPONSES['Pixel'][Math.floor(Math.random() * 3)];
  if (role.includes('Analytics')) return AI_RESPONSES['Analytics'][Math.floor(Math.random() * 3)];
  if (role.includes('A/B')) return AI_RESPONSES['A/B'][Math.floor(Math.random() * 3)];
  if (role.includes('Hive')) return AI_RESPONSES['Hive'][Math.floor(Math.random() * 3)];
  if (role.includes('Code')) return AI_RESPONSES['Code'][Math.floor(Math.random() * 3)];
  if (role.includes('Research')) return AI_RESPONSES['Research'][Math.floor(Math.random() * 3)];
  if (role.includes('Lead Scout')) return AI_RESPONSES['Lead'][Math.floor(Math.random() * 3)];
  if (role.includes('Billing')) return AI_RESPONSES['Billing'][Math.floor(Math.random() * 3)];
  if (role.includes('Architect')) return AI_RESPONSES['Architect'][Math.floor(Math.random() * 3)];
  return AI_RESPONSES['default'][Math.floor(Math.random() * 3)];
}

// ─── Agent Card HTML ──────────────────────────────────────────────────────────
function agentCard(agent, dept, size = 'normal') {
  const c = dept.color;
  const isReady = agent.status === 'ready';
  const bg = isReady
    ? `linear-gradient(135deg, rgba(16,185,129,0.08), rgba(16,185,129,0.02))`
    : `linear-gradient(135deg, rgba(${hexToRgb(c)},0.08), rgba(${hexToRgb(c)},0.02))`;
  const border = isReady ? 'rgba(16,185,129,0.2)' : `rgba(${hexToRgb(c)},0.2)`;
  const borderLeft = isReady ? '#10b981' : c;
  const minH = size === 'large' ? '140px' : size === 'medium' ? '120px' : '110px';
  const nameSize = size === 'large' ? '20px' : '16px';

  const idx = DEPARTMENTS.findIndex(d => d.dept === dept.dept);
  const dIdx = DEPARTMENTS[idx].agents.findIndex(a => a.name === agent.name);

  return `<div
    class="agent-card ${isReady ? 'agent-ready' : 'agent-building'}"
    data-dept="${idx}" data-agent="${dIdx}"
    style="
      background:${bg};
      border:1px solid ${border};
      border-left:3px solid ${borderLeft};
      border-radius:12px;
      padding:16px;
      position:relative;
      overflow:hidden;
      cursor:pointer;
      min-height:${minH};
      transition:transform 0.2s,box-shadow 0.2s;
    "
    onmouseenter="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 32px rgba(${hexToRgb(c)},0.15)';this.querySelector('.shimmer').style.animation='shimmer 0.8s ease';"
    onmouseleave="this.style.transform='';this.style.boxShadow='';this.querySelector('.shimmer').style.animation='';"
    onclick="openAgentModal(${idx},${dIdx})"
  >
    <!-- shimmer overlay -->
    <div class="shimmer" style="
      position:absolute;top:0;left:0;width:60%;height:100%;
      background:linear-gradient(90deg,transparent,rgba(255,255,255,0.04),transparent);
      pointer-events:none;
    "></div>

    <!-- glow bg -->
    <div style="
      position:absolute;bottom:-20px;right:-20px;width:80px;height:80px;
      background:radial-gradient(circle, ${c}18 0%, transparent 70%);
      pointer-events:none;
    "></div>

    <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:8px;">
      <!-- pixel avatar -->
      <div style="flex-shrink:0;">${pixelAvatar(isReady ? '#10b981' : c, agent.status)}</div>

      <div style="flex:1;min-width:0;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:4px;">
          <div>
            <div style="font-size:${nameSize};font-weight:900;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${agent.name}</div>
            <div style="font-size:11px;font-weight:700;color:${c};letter-spacing:0.04em;margin-top:1px;">${agent.role}</div>
          </div>
          <span class="${isReady ? 'status-dot' : ''}" style="
            display:inline-flex;align-items:center;gap:4px;
            padding:3px 8px;border-radius:20px;font-size:9px;font-weight:800;white-space:nowrap;flex-shrink:0;
            background:${isReady ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.15)'};
            color:${isReady ? '#10b981' : '#f59e0b'};
          ">
            <span style="font-size:7px;">${isReady ? '●' : '⚙'}</span>
            ${isReady ? 'LIVE' : 'BUILD'}
          </span>
        </div>
      </div>
    </div>

    <div style="font-size:11px;color:var(--text-muted);line-height:1.5;margin-bottom:8px;">${agent.desc}</div>

    <div style="display:flex;align-items:center;justify-content:space-between;">
      <span style="
        font-size:9px;font-weight:700;color:${c};opacity:0.7;
        background:rgba(${hexToRgb(c)},0.08);padding:2px 8px;border-radius:6px;
      ">${agent.model}</span>
      <span style="font-size:9px;color:rgba(255,255,255,0.2);">${dept.floor}</span>
    </div>
  </div>`;
}

// ─── Hex to RGB helper ────────────────────────────────────────────────────────
function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r},${g},${b}`;
}

// ─── Modal ────────────────────────────────────────────────────────────────────
function openAgentModal(deptIdx, agentIdx) {
  const dept = DEPARTMENTS[deptIdx];
  const agent = dept.agents[agentIdx];
  const c = dept.color;
  const isReady = agent.status === 'ready';

  const overlay = document.createElement('div');
  overlay.id = 'agent-modal-overlay';
  overlay.style.cssText = `
    position:fixed;inset:0;z-index:9999;
    background:rgba(0,0,0,0.7);backdrop-filter:blur(8px);
    display:flex;align-items:center;justify-content:center;padding:20px;
    animation:fadeIn 0.2s ease;
  `;

  overlay.innerHTML = `
    <div style="
      background:linear-gradient(135deg, #0f1729, #0a1120);
      border:1px solid rgba(${hexToRgb(c)},0.3);
      border-radius:20px;
      padding:32px;
      width:100%;max-width:480px;
      position:relative;
      box-shadow:0 24px 64px rgba(0,0,0,0.6), 0 0 40px rgba(${hexToRgb(c)},0.1);
    ">
      <!-- close -->
      <button onclick="document.getElementById('agent-modal-overlay').remove()" style="
        position:absolute;top:16px;right:16px;
        background:rgba(255,255,255,0.06);border:none;border-radius:8px;
        color:rgba(255,255,255,0.5);width:32px;height:32px;
        font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;
      ">x</button>

      <!-- header -->
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
        <div>${pixelAvatarLarge(isReady ? '#10b981' : c, agent.status)}</div>
        <div>
          <div style="font-size:26px;font-weight:900;color:var(--text-primary);">${agent.name}</div>
          <div style="font-size:13px;font-weight:700;color:${c};margin-top:2px;">${agent.role}</div>
          <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
            <span style="padding:3px 10px;border-radius:12px;font-size:10px;font-weight:700;
              background:${isReady ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.15)'};
              color:${isReady ? '#10b981' : '#f59e0b'};">
              ${isReady ? '● LIVE' : '⚙ BUILD'}
            </span>
            <span style="padding:3px 10px;border-radius:12px;font-size:10px;
              background:rgba(${hexToRgb(c)},0.1);color:${c};">${dept.dept}</span>
            <span style="padding:3px 10px;border-radius:12px;font-size:10px;
              background:rgba(255,255,255,0.04);color:rgba(255,255,255,0.4);">${dept.floor}</span>
          </div>
        </div>
      </div>

      <!-- desc -->
      <div style="
        background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
        border-radius:12px;padding:16px;margin-bottom:16px;
        font-size:13px;color:var(--text-secondary);line-height:1.6;
      ">${agent.desc}</div>

      <!-- model -->
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px;">
        <span style="font-size:11px;color:rgba(255,255,255,0.4);">Modelo:</span>
        <span style="padding:4px 12px;border-radius:8px;font-size:11px;font-weight:700;
          background:rgba(${hexToRgb(c)},0.1);color:${c};">${agent.model}</span>
      </div>

      <!-- chat area -->
      <div id="modal-chat-area" style="
        background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.06);
        border-radius:12px;padding:12px;margin-bottom:12px;min-height:60px;
        font-size:12px;color:var(--text-secondary);line-height:1.5;display:none;
      "></div>

      <!-- CTA -->
      <button id="modal-chat-btn" onclick="handleModalChat('${agent.name}','${agent.role}')" style="
        width:100%;padding:14px;border-radius:12px;border:none;cursor:pointer;
        background:linear-gradient(135deg, ${c}, ${c}88);
        color:#0f172a;font-size:14px;font-weight:800;
        box-shadow:0 4px 20px rgba(${hexToRgb(c)},0.3);
        transition:opacity 0.2s,transform 0.1s;
      "
      onmouseenter="this.style.opacity='0.9'"
      onmouseleave="this.style.opacity='1'"
      >Iniciar chat con ${agent.name}</button>
    </div>
  `;

  document.body.appendChild(overlay);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
}

// ─── Modal chat handler — connected to ClaudeFlow swarm ─────────────────────
window.handleModalChat = async function(name, role) {
  const msg = prompt(`Tarea para ${name} (${role}):`);
  if (!msg) return;

  const chatArea = document.getElementById('modal-chat-area');
  const btn = document.getElementById('modal-chat-btn');
  if (!chatArea || !btn) return;

  chatArea.style.display = 'block';
  chatArea.innerHTML = `
    <div style="color:rgba(255,255,255,0.3);margin-bottom:8px;font-size:11px;">📤 Tu tarea:</div>
    <div style="color:var(--text-primary);margin-bottom:12px;">${msg}</div>
    <div style="color:rgba(255,255,255,0.3);margin-bottom:6px;font-size:11px;">⏳ Enviando al swarm ClaudeFlow...</div>
    <div id="typing-dots" style="color:var(--text-muted);"><span style="animation:pulse-dot 1s infinite;">● ● ●</span></div>
  `;
  btn.disabled = true;
  btn.style.opacity = '0.5';

  // Send real task to ClaudeFlow swarm
  try {
    const task = await claudeflow.sendTask(name, msg);
    claudeflow.updateAgentStatus(name, 'running', { currentTask: task.id });

    setTimeout(() => {
      const typingEl = document.getElementById('typing-dots');
      if (typingEl) {
        typingEl.innerHTML = `
          <div style="color:#10b981;font-weight:700;margin-bottom:6px;">✅ Tarea #${task.id.slice(-6)} enviada al enjambre</div>
          <div style="color:var(--text-secondary);">${getAIResponse(role)}</div>
          <div style="margin-top:8px;padding:6px 10px;background:rgba(16,185,129,0.1);border-radius:8px;font-size:10px;color:#10b981;">
            📋 Estado: En cola · Prioridad: normal · Agente: ${name}
          </div>
        `;
      }
      btn.disabled = false;
      btn.style.opacity = '1';
      btn.textContent = 'Enviar otra tarea';
    }, 1200);
  } catch (err) {
    const typingEl = document.getElementById('typing-dots');
    if (typingEl) typingEl.innerHTML = `<span style="color:#f87171;">❌ Error: ${err.message}</span>`;
    btn.disabled = false;
    btn.style.opacity = '1';
  }
};

window.openAgentModal = openAgentModal;

// ─── Dept filter bar ──────────────────────────────────────────────────────────
function deptFilterBar(activeDept, activeStatus) {
  return `
    <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
      ${['Todos','Operativos','En Construcción'].map(f => `
        <button onclick="applyAgentFilter('${f}','${activeDept}')"
          style="padding:5px 12px;border-radius:20px;border:1px solid ${activeStatus===f?'var(--accent)':'rgba(255,255,255,0.1)'};
            background:${activeStatus===f?'rgba(99,102,241,0.2)':'transparent'};
            color:${activeStatus===f?'var(--accent)':'var(--text-muted)'};
            font-size:11px;font-weight:700;cursor:pointer;transition:all 0.15s;">
          ${f}
        </button>
      `).join('')}
      <span style="width:1px;height:16px;background:rgba(255,255,255,0.1);"></span>
      ${DEPARTMENTS.map(d => `
        <button onclick="applyAgentFilter('${activeStatus}','${d.dept}')"
          style="padding:5px 12px;border-radius:20px;border:1px solid ${activeDept===d.dept?d.color+'66':'rgba(255,255,255,0.08)'};
            background:${activeDept===d.dept?`rgba(${hexToRgb(d.color)},0.15)`:'transparent'};
            color:${activeDept===d.dept?d.color:'var(--text-muted)'};
            font-size:10px;font-weight:700;cursor:pointer;transition:all 0.15s;">
          ${d.dept}
        </button>
      `).join('')}
    </div>
  `;
}

// ─── Dept progress grid (mini cards) ─────────────────────────────────────────
function deptProgressGrid() {
  return `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:24px;">
    ${DEPARTMENTS.map((d) => {
      const r = d.agents.filter(a => a.status === 'ready').length;
      const t = d.agents.length;
      const pct = Math.round((r / t) * 100);
      return `
        <div onclick="applyAgentFilter('Todos','${d.dept}')"
          style="
            padding:12px;border-radius:12px;cursor:pointer;
            background:linear-gradient(135deg,rgba(${hexToRgb(d.color)},0.06),rgba(${hexToRgb(d.color)},0.02));
            border:1px solid rgba(${hexToRgb(d.color)},0.15);
            transition:transform 0.15s,box-shadow 0.15s;
          "
          onmouseenter="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 16px rgba(${hexToRgb(d.color)},0.12)';"
          onmouseleave="this.style.transform='';this.style.boxShadow='';"
        >
          <div style="font-size:11px;font-weight:800;color:${d.color};margin-bottom:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${d.dept}</div>
          <div style="font-size:18px;font-weight:900;color:var(--text-primary);">${r}<span style="font-size:11px;color:var(--text-muted);">/${t}</span></div>
          <div style="margin-top:6px;background:rgba(255,255,255,0.06);border-radius:99px;height:3px;">
            <div style="background:${d.color};height:3px;border-radius:99px;width:${pct}%;
              box-shadow:0 0 6px ${d.color}66;transition:width 1s;"></div>
          </div>
        </div>
      `;
    }).join('')}
  </div>`;
}

// ─── Building view ────────────────────────────────────────────────────────────
function buildingView(filteredDepts) {
  const floor4 = filteredDepts.filter(d => d.dept === 'Orquestadores');
  const floor3 = filteredDepts.filter(d => d.dept === 'Jefes de Área');
  const floor2 = filteredDepts.filter(d => d.floor === 'Planta 2' && d.dept !== 'Orquestadores' && d.dept !== 'Jefes de Área');
  const floor1 = filteredDepts.filter(d => d.floor === 'Planta 1');
  const subsuelo = filteredDepts.filter(d => d.floor === 'Subsuelo');

  let html = '';

  if (floor4.length > 0) {
    html += `
      <div style="margin-bottom:28px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
          <div style="width:3px;height:20px;background:#f59e0b;border-radius:2px;box-shadow:0 0 8px #f59e0b66;"></div>
          <span style="font-size:13px;font-weight:800;color:#f59e0b;letter-spacing:0.08em;">PLANTA 4 — ORQUESTADORES</span>
          <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(245,158,11,0.2),transparent);"></div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;">
          ${floor4.flatMap(d => d.agents.map(a => agentCard(a, d, 'large'))).join('')}
        </div>
      </div>
    `;
  }

  if (floor3.length > 0) {
    html += `
      <div style="margin-bottom:28px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
          <div style="width:3px;height:20px;background:#6366f1;border-radius:2px;box-shadow:0 0 8px #6366f166;"></div>
          <span style="font-size:13px;font-weight:800;color:#6366f1;letter-spacing:0.08em;">PLANTA 3 — JEFES DE ÁREA</span>
          <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(99,102,241,0.2),transparent);"></div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;">
          ${floor3.flatMap(d => d.agents.map(a => agentCard(a, d, 'medium'))).join('')}
        </div>
      </div>
    `;
  }

  if (floor2.length > 0) {
    html += `
      <div style="margin-bottom:28px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
          <div style="width:3px;height:20px;background:rgba(255,255,255,0.3);border-radius:2px;"></div>
          <span style="font-size:13px;font-weight:800;color:rgba(255,255,255,0.5);letter-spacing:0.08em;">PLANTA 2 — AGENTES ESPECIALIZADOS</span>
          <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(255,255,255,0.08),transparent);"></div>
        </div>
        ${floor2.map(dept => {
          const r = dept.agents.filter(a => a.status === 'ready').length;
          return `
            <div style="margin-bottom:20px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <span style="font-size:11px;font-weight:800;color:${dept.color};">${dept.dept}</span>
                <span style="font-size:10px;color:var(--text-muted);">${r}/${dept.agents.length}</span>
                <div style="flex:1;height:1px;background:rgba(${hexToRgb(dept.color)},0.1);"></div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;">
                ${dept.agents.map(a => agentCard(a, dept, 'normal')).join('')}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  if (floor1.length > 0) {
    html += `
      <div style="margin-bottom:28px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
          <div style="width:3px;height:20px;background:#f472b6;border-radius:2px;box-shadow:0 0 8px #f472b666;"></div>
          <span style="font-size:13px;font-weight:800;color:#f472b6;letter-spacing:0.08em;">PLANTA 1 — PIXEL & TRACKING</span>
          <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(244,114,182,0.2),transparent);"></div>
        </div>
        ${floor1.map(dept => {
          const r = dept.agents.filter(a => a.status === 'ready').length;
          return `
            <div style="margin-bottom:20px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <span style="font-size:11px;font-weight:800;color:${dept.color};">${dept.dept}</span>
                <span style="font-size:10px;color:var(--text-muted);">${r}/${dept.agents.length}</span>
                <div style="flex:1;height:1px;background:rgba(${hexToRgb(dept.color)},0.1);"></div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;">
                ${dept.agents.map(a => agentCard(a, dept, 'normal')).join('')}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  if (subsuelo.length > 0) {
    html += `
      <div style="margin-bottom:28px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
          <div style="width:3px;height:20px;background:#a78bfa;border-radius:2px;box-shadow:0 0 8px #a78bfa66;"></div>
          <span style="font-size:13px;font-weight:800;color:#a78bfa;letter-spacing:0.08em;">SUBSUELO — ENJAMBRE & INFRAESTRUCTURA</span>
          <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(167,139,250,0.2),transparent);"></div>
        </div>
        ${subsuelo.map(dept => {
          const r = dept.agents.filter(a => a.status === 'ready').length;
          return `
            <div style="margin-bottom:20px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <span style="font-size:11px;font-weight:800;color:${dept.color};">${dept.dept}</span>
                <span style="font-size:10px;color:var(--text-muted);">${r}/${dept.agents.length}</span>
                <div style="flex:1;height:1px;background:rgba(${hexToRgb(dept.color)},0.1);"></div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;">
                ${dept.agents.map(a => agentCard(a, dept, 'normal')).join('')}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  return html || `<div style="text-align:center;padding:40px;color:var(--text-muted);">No hay agentes en esta vista.</div>`;
}

// ─── Main render ───────────────────────────────────────────────────────────────
let _currentStatus = 'Todos';
let _currentDept = 'Todos';

window.applyAgentFilter = function(status, dept) {
  _currentStatus = status;
  _currentDept = dept;
  const container = document.getElementById('agents-root');
  if (container) renderAgents(container);
};

export function renderAgents(container) {
  container.id = 'agents-root';

  const allAgents = DEPARTMENTS.flatMap(d => d.agents);
  const ready = allAgents.filter(a => a.status === 'ready').length;
  const total = allAgents.length;
  const pct = Math.round((ready / total) * 100);

  // Filter logic
  let filteredDepts = DEPARTMENTS.map(d => {
    let agents = d.agents;
    if (_currentStatus === 'Operativos') agents = agents.filter(a => a.status === 'ready');
    if (_currentStatus === 'En Construcción') agents = agents.filter(a => a.status === 'building');
    if (_currentDept !== 'Todos') agents = d.dept === _currentDept ? agents : [];
    return { ...d, agents };
  }).filter(d => d.agents.length > 0);

  container.innerHTML = `
    <style>
      @keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:.4} }
      @keyframes shimmer { 0%{transform:translateX(-100%)} 100%{transform:translateX(100%)} }
      @keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }
      @keyframes system-pulse { 0%,100%{opacity:1;text-shadow:0 0 8px #10b98188} 50%{opacity:0.6;text-shadow:none} }
      .agent-ready .status-dot { animation: pulse-dot 2s infinite; }
      .agent-card { animation: fadeIn 0.3s ease both; }
      .agent-card:hover .shimmer { animation: shimmer 0.8s ease; }
    </style>

    <!-- ═══ HEADER ══════════════════════════════════════════════════════ -->
    <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:16px;margin-bottom:24px;">
      <div style="display:flex;align-items:center;gap:20px;">
        <!-- circular progress -->
        <div style="flex-shrink:0;">${circularProgress(ready, total, '#10b981')}</div>

        <div>
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <h2 style="font-size:24px;font-weight:900;margin:0;">AI Command Center</h2>
            <span style="
              font-size:11px;font-weight:800;color:#10b981;letter-spacing:0.12em;
              animation:system-pulse 2.5s infinite;
            ">SISTEMA OPERATIVO</span>
          </div>
          <div style="font-size:13px;color:var(--text-muted);margin-bottom:8px;">
            <span style="color:#10b981;font-weight:700;">${ready} agentes LIVE</span>
            &nbsp;·&nbsp;
            <span style="color:#f59e0b;font-weight:700;">${total - ready} en construcción</span>
            &nbsp;·&nbsp;
            <span style="color:rgba(255,255,255,0.3);">${pct}% operativo</span>
          </div>
          <!-- global progress bar -->
          <div style="width:280px;max-width:100%;">
            <div style="background:rgba(255,255,255,0.06);border-radius:99px;height:6px;overflow:hidden;">
              <div style="background:linear-gradient(90deg,#10b981,#34d399);height:6px;border-radius:99px;
                width:${pct}%;box-shadow:0 0 10px rgba(16,185,129,0.4);transition:width 1s;"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- ClaudeFlow Swarm Control Panel -->
      <div style="display:flex;gap:10px;align-items:stretch;">
        <div style="
          padding:12px 16px;
          background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.25);
          border-radius:14px;text-align:center;min-width:120px;
        ">
          <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-bottom:4px;letter-spacing:0.08em;">CLAUDEFLOW</div>
          <div id="swarm-status-indicator" style="font-size:16px;font-weight:900;color:#a78bfa;margin-bottom:4px;">🐝 SWARM</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.3);">Ruflo v3.5.78</div>
          <div style="margin-top:8px;display:flex;gap:4px;justify-content:center;">
            <button id="btn-swarm-start" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(16,185,129,0.3);
              background:rgba(16,185,129,0.1);color:#10b981;font-size:9px;font-weight:800;cursor:pointer;">▶ START</button>
            <button id="btn-swarm-stop" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(248,113,113,0.3);
              background:rgba(248,113,113,0.1);color:#f87171;font-size:9px;font-weight:800;cursor:pointer;">■ STOP</button>
          </div>
        </div>
        <div style="
          padding:12px 20px;
          background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
          border-radius:14px;text-align:center;
        ">
          <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:4px;">COSTE MENSUAL IA</div>
          <div style="font-size:22px;font-weight:900;color:#10b981;">~0€</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.3);">Gemini 2.5 Flash</div>
        </div>
      </div>
    </div>

    <!-- ═══ DEPT PROGRESS GRID ════════════════════════════════════════════ -->
    ${deptProgressGrid()}

    <!-- ═══ FILTER BAR ════════════════════════════════════════════════════ -->
    <div style="margin-bottom:20px;padding:12px 16px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;">
      ${deptFilterBar(_currentStatus, _currentDept)}
    </div>

    <!-- ═══ BUILDING VIEW ════════════════════════════════════════════════ -->
    <div id="building-view">
      ${buildingView(filteredDepts)}
    </div>

    <!-- ═══ SWARM ACTIVITY LOG ══════════════════════════════════════════ -->
    <div style="margin-top:24px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
        <div style="width:3px;height:20px;background:#a78bfa;border-radius:2px;box-shadow:0 0 8px #a78bfa66;"></div>
        <span style="font-size:13px;font-weight:800;color:#a78bfa;letter-spacing:0.08em;">ACTIVIDAD DEL ENJAMBRE</span>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(167,139,250,0.2),transparent);"></div>
      </div>
      <div id="swarm-activity-log" style="
        background:rgba(0,0,0,0.2);border:1px solid rgba(167,139,250,0.15);border-radius:12px;
        padding:16px;min-height:80px;max-height:300px;overflow-y:auto;
        font-family:'Courier New',monospace;font-size:11px;color:var(--text-muted);line-height:1.8;
      ">
        ${(() => {
          const activity = claudeflow.getRecentActivity();
          if (activity.length === 0) return '<div style="text-align:center;color:rgba(255,255,255,0.2);padding:20px;">Sin actividad reciente · Envía una tarea a un agente para empezar</div>';
          return activity.slice(0, 15).map(a => `
            <div style="display:flex;gap:8px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.03);">
              <span style="color:rgba(255,255,255,0.2);min-width:50px;">${a.time}</span>
              <span>${a.msg}</span>
            </div>
          `).join('');
        })()}
      </div>
    </div>
  `;

  // ── Swarm control buttons ────────────────────────
  const btnStart = container.querySelector('#btn-swarm-start');
  const btnStop = container.querySelector('#btn-swarm-stop');
  if (btnStart) {
    btnStart.addEventListener('click', () => {
      claudeflow.queueCommand('npx claude-flow daemon start');
      claudeflow.updateAgentStatus('Ruflo-Queen', 'running', { role: 'Hive Mind' });
      const indicator = container.querySelector('#swarm-status-indicator');
      if (indicator) { indicator.textContent = '🟢 LIVE'; indicator.style.color = '#10b981'; }
      // Log activity
      const log = container.querySelector('#swarm-activity-log');
      if (log) {
        const time = new Date().toLocaleTimeString('es-ES', { hour:'2-digit', minute:'2-digit', second:'2-digit' });
        log.innerHTML = `<div style="color:#10b981;"><span style="color:rgba(255,255,255,0.2);min-width:50px;">${time}</span> 🐝 Enjambre ClaudeFlow iniciado · Ruflo-Queen activa</div>` + log.innerHTML;
      }
    });
  }
  if (btnStop) {
    btnStop.addEventListener('click', () => {
      claudeflow.queueCommand('npx claude-flow daemon stop');
      claudeflow.updateAgentStatus('Ruflo-Queen', 'idle');
      const indicator = container.querySelector('#swarm-status-indicator');
      if (indicator) { indicator.textContent = '⏸ PAUSED'; indicator.style.color = '#f59e0b'; }
    });
  }

  // ── Subscribe to swarm state changes ─────────────
  claudeflow.onStateChange((state) => {
    const indicator = container.querySelector('#swarm-status-indicator');
    if (indicator && state.swarmStatus === 'running') {
      indicator.textContent = '🟢 LIVE';
      indicator.style.color = '#10b981';
    }
  });
}
