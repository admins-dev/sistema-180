// ═══════════════════════════════════════════════
// Sidebar Component — with mobile toggle
// ═══════════════════════════════════════════════
import { navigate } from '../main.js';

export function renderSidebar(container) {
  container.innerHTML = `
    <div class="sidebar-logo">
      <div class="logo-icon">🎬</div>
      <div>
        <h1>SISTEMA180</h1>
        <span>Fábrica de Contenido IA</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-section-title">Principal</div>
      <div class="nav-item active" data-page="dashboard">
        <span class="icon">📊</span> <span class="nav-label">Dashboard</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-section-title">Producción</div>
      <div class="nav-item" data-page="avatars">
        <span class="icon">🤖</span> <span class="nav-label">Avatares IA</span>
        <span class="badge">NEW</span>
      </div>
      <div class="nav-item" data-page="scripts">
        <span class="icon">📝</span> <span class="nav-label">Guiones Virales</span>
      </div>
      <div class="nav-item" data-page="videos">
        <span class="icon">🎬</span> <span class="nav-label">Vídeos UGC</span>
      </div>
      <div class="nav-item" data-page="ads">
        <span class="icon">📢</span> <span class="nav-label">Anuncios</span>
      </div>
    </div>

    <div class="nav-section" style="margin-top:auto">
      <div class="nav-item" data-page="settings">
        <span class="icon">⚙️</span> <span class="nav-label">Configuración</span>
      </div>
      <button id="sidebar-collapse-btn" class="sidebar-collapse-btn" title="Plegar menú">
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

  // Collapse / expand toggle
  document.getElementById('sidebar-collapse-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    const isCollapsed = container.classList.toggle('collapsed');
    document.getElementById('content').classList.toggle('sidebar-collapsed', isCollapsed);
    document.getElementById('sidebar-collapse-btn').textContent = isCollapsed ? '▶' : '◀';
  });
}

export function initMobileMenu() {
  // Create hamburger button
  const hamburger = document.createElement('button');
  hamburger.id = 'hamburger-btn';
  hamburger.className = 'hamburger-btn';
  hamburger.innerHTML = '☰';
  hamburger.title = 'Abrir menú';

  // Create overlay
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
