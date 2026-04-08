// ═══════════════════════════════════════════════
// Sidebar — SISTEMA180 HQ Navigation
// ═══════════════════════════════════════════════
import { navigate } from '../main.js';

export function renderSidebar(container) {
  container.innerHTML = `
    <div class="sidebar-logo">
      <div class="logo-icon">🏢</div>
      <div>
        <h1>SISTEMA180</h1>
        <span>HQ · José + Ares</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-section-title">Principal</div>
      <div class="nav-item active" data-page="dashboard">
        <span class="icon">📊</span><span class="nav-label">Dashboard HQ</span>
        <span class="badge" style="background:var(--accent)">+Editor</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-section-title">Negocio</div>
      <div class="nav-item" data-page="crm">
        <span class="icon">📋</span><span class="nav-label">CRM & Leads</span>
      </div>
      <div class="nav-item" data-page="clients">
        <span class="icon">👥</span><span class="nav-label">Clientes</span>
      </div>
      <div class="nav-item" data-page="finances">
        <span class="icon">💰</span><span class="nav-label">Finanzas</span>
      </div>
      <div class="nav-item" data-page="affiliates">
        <span class="icon">🤝</span><span class="nav-label">Afiliados</span>
        <span class="badge" style="background:var(--orange)">4</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-section-title">Marketplace</div>
      <div class="nav-item" data-page="marketplace">
        <span class="icon">🏪</span><span class="nav-label">Marketplace</span>
        <span class="badge" style="background:var(--red)">!</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-section-title">Producción</div>
      <div class="nav-item" data-page="avatars">
        <span class="icon">🤖</span><span class="nav-label">Avatares IA</span>
      </div>
      <div class="nav-item" data-page="scripts">
        <span class="icon">📝</span><span class="nav-label">Guiones Virales</span>
      </div>
      <div class="nav-item" data-page="videos">
        <span class="icon">🎬</span><span class="nav-label">Vídeos UGC</span>
      </div>
      <div class="nav-item" data-page="ads">
        <span class="icon">📢</span><span class="nav-label">Anuncios</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-section-title">IA & Agentes</div>
      <div class="nav-item" data-page="despacho">
        <span class="icon">🏢</span><span class="nav-label">El Despacho</span>
        <span class="badge" style="background:var(--accent)">NEW</span>
      </div>
      <div class="nav-item" data-page="agents">
        <span class="icon">🧠</span><span class="nav-label">Los 57 Agentes</span>
        <span class="badge">57</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-section-title">Sistema</div>
      <div class="nav-item" data-page="legal">
        <span class="icon">⚖️</span><span class="nav-label">Legal & GDPR</span>
        <span class="badge" style="background:var(--red)">!</span>
      </div>
      <div class="nav-item" data-page="settings">
        <span class="icon">⚙️</span><span class="nav-label">Configuración</span>
      </div>
    </div>

    <div style="margin-top:auto;padding-top:16px;border-top:1px solid var(--border);">
      <div style="padding:10px 12px;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.15);
                  border-radius:10px;font-size:11px;color:var(--text-muted);">
        <div style="color:var(--green);font-weight:700;margin-bottom:2px;">● 57 agentes LIVE</div>
        <div>Gemini · Ruflo · Stripe · n8n</div>
      </div>
      <button id="sidebar-collapse-btn" class="sidebar-collapse-btn" title="Plegar menú" style="margin-top:10px;">
        ◀
      </button>
    </div>
  `;

  container.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      navigate(item.dataset.page);
      if (window.innerWidth <= 768) {
        container.classList.remove('open');
        document.getElementById('sidebar-overlay').classList.remove('active');
      }
    });
  });

  document.getElementById('sidebar-collapse-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    const isCollapsed = container.classList.toggle('collapsed');
    document.getElementById('content').classList.toggle('sidebar-collapsed', isCollapsed);
    document.getElementById('sidebar-collapse-btn').textContent = isCollapsed ? '▶' : '◀';
  });
}

export function initMobileMenu() {
  const hamburger = document.createElement('button');
  hamburger.id = 'hamburger-btn';
  hamburger.className = 'hamburger-btn';
  hamburger.innerHTML = '☰';
  hamburger.title = 'Abrir menú';

  const overlay = document.createElement('div');
  overlay.id = 'sidebar-overlay';
  overlay.className = 'sidebar-overlay';

  document.body.appendChild(hamburger);
  document.body.appendChild(overlay);

  hamburger.addEventListener('click', () => {
    const sidebar = document.getElementById('sidebar');
    const isOpen = sidebar.classList.toggle('open');
    overlay.classList.toggle('active', isOpen);
    hamburger.innerHTML = isOpen ? '✕' : '☰';
  });

  overlay.addEventListener('click', () => {
    document.getElementById('sidebar').classList.remove('open');
    overlay.classList.remove('active');
    hamburger.innerHTML = '☰';
  });
}
