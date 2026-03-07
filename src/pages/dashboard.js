// ═══════════════════════════════════════════════
// Dashboard Page
// ═══════════════════════════════════════════════
import { storage } from '../services/storage.js';
import { navigate } from '../main.js';

export function renderDashboard(container) {
    const stats = storage.getStats();
    container.innerHTML = `
    <div class="page-header">
      <h2>Dashboard</h2>
      <p>Tu fábrica de contenido viral con IA — Método Heras + Avatares Freepik</p>
    </div>

    <div class="card-grid mb-16">
      <div class="card stat-card">
        <div class="stat-icon purple">🤖</div>
        <div><div class="stat-value">${stats.avatars}</div><div class="stat-label">Avatares creados</div></div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon green">📝</div>
        <div><div class="stat-value">${stats.scripts}</div><div class="stat-label">Guiones generados</div></div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon orange">🎬</div>
        <div><div class="stat-value">${stats.videos}</div><div class="stat-label">Vídeos creados</div></div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon pink">📢</div>
        <div><div class="stat-value">${stats.ads}</div><div class="stat-label">Anuncios activos</div></div>
      </div>
    </div>

    <h3 style="margin-bottom:16px; font-size:18px; font-weight:700;">⚡ Acceso Rápido</h3>
    <div class="card-grid mb-16">
      <div class="card quick-action" data-page="avatars" style="cursor:pointer">
        <div style="font-size:32px; margin-bottom:12px;">🤖</div>
        <h4 style="font-weight:700; margin-bottom:4px;">Crear Avatar</h4>
        <p style="color:var(--text-muted); font-size:13px;">Genera tu clon digital con Freepik Mystic AI</p>
      </div>
      <div class="card quick-action" data-page="scripts" style="cursor:pointer">
        <div style="font-size:32px; margin-bottom:12px;">📝</div>
        <h4 style="font-weight:700; margin-bottom:4px;">Guion Viral</h4>
        <p style="color:var(--text-muted); font-size:13px;">Método Heras: Hook → Historia → Moraleja → CTA</p>
      </div>
      <div class="card quick-action" data-page="ads" style="cursor:pointer">
        <div style="font-size:32px; margin-bottom:12px;">📢</div>
        <h4 style="font-weight:700; margin-bottom:4px;">Crear Anuncio</h4>
        <p style="color:var(--text-muted); font-size:13px;">TikTok, Instagram, YouTube — formatos listos</p>
      </div>
    </div>

    <h3 style="margin-bottom:16px; font-size:18px; font-weight:700;">🎯 Método UMV — Umbral Mínimo de Viralidad</h3>
    <div class="card" style="border-left:3px solid var(--accent);">
      <div class="flex gap-16" style="flex-wrap:wrap;">
        <div style="flex:1; min-width:250px;">
          <h4 style="color:var(--accent); font-size:14px; font-weight:700; margin-bottom:8px;">1ª MITAD — Mainstream</h4>
          <p style="font-size:14px; color:var(--text-secondary); line-height:1.6;">
            Contenido entretenido para TODO el mundo. El gancho engancha al mayor público posible.
            Esto es lo que hace que el vídeo sea viral.
          </p>
        </div>
        <div style="flex:1; min-width:250px;">
          <h4 style="color:var(--green); font-size:14px; font-weight:700; margin-bottom:8px;">2ª MITAD — Target</h4>
          <p style="font-size:14px; color:var(--text-secondary); line-height:1.6;">
            Redirigimos al público objetivo. Historia de valor para nuestro cliente ideal.
            Moraleja como experto + CTA para convertir.
          </p>
        </div>
      </div>
      <div style="margin-top:16px; padding-top:16px; border-top:1px solid var(--border);">
        <p style="font-size:13px; color:var(--text-muted);">
          ⏱️ Duración ideal: 45s — 1:30min &nbsp;|&nbsp;
          📱 TikTok + Reels = Viralizar &nbsp;|&nbsp;
          📸 Stories = Convertir &nbsp;|&nbsp;
          🎥 YouTube = Educar
        </p>
      </div>
    </div>
  `;

    container.querySelectorAll('.quick-action').forEach(el => {
        el.addEventListener('click', () => navigate(el.dataset.page));
    });
}
