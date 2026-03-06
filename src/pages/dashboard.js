import { getStats, getAvatars, getScripts, getVideos } from '../services/storage.js';
import { freepikAPI } from '../services/freepik-api.js';

export function renderDashboard() {
    const stats = getStats();
    const recentAvatars = getAvatars().slice(0, 4);
    const recentScripts = getScripts().slice(0, 3);
    const isConfigured = freepikAPI.isConfigured();

    return `
    <div class="section-gradient">
      ${!isConfigured ? `
        <div class="onboarding-banner">
          <div class="banner-content">
            <h2>🚀 ¡Bienvenido a <span class="gradient-text">UGC Avatar Hub</span>!</h2>
            <p>Configura tu API Key de Freepik para empezar a crear avatares ultrarrealistas, vídeos UGC y anuncios que venden.</p>
            <div class="flex gap-md">
              <a href="#settings" class="btn btn-primary btn-lg" data-page="settings">
                ⚙️ Configurar API Key
              </a>
              <a href="https://www.freepik.com/developers/dashboard/api-key" target="_blank" class="btn btn-secondary btn-lg">
                🔑 Obtener API Key gratis
              </a>
            </div>
          </div>
        </div>
      ` : ''}

      <div class="page-header">
        <h1>Tu <span class="gradient-text">Centro de Mando</span></h1>
        <p>Crea contenido UGC ultrarrealista con IA. Sin cámara, sin actores, sin complicaciones.</p>
      </div>

      <!-- Stats -->
      <div class="grid-4 mb-xl">
        <div class="stat-card">
          <div class="stat-value">${stats.totalAvatars}</div>
          <div class="stat-label">Avatares creados</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${stats.totalScripts}</div>
          <div class="stat-label">Guiones generados</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${stats.totalVideos}</div>
          <div class="stat-label">Vídeos UGC</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${isConfigured ? '✓' : '—'}</div>
          <div class="stat-label">API ${isConfigured ? 'Conectada' : 'Sin configurar'}</div>
        </div>
      </div>

      <!-- Quick Actions -->
      <h2 class="font-bold mb-lg" style="font-size:var(--font-size-xl)">⚡ Acciones rápidas</h2>
      <div class="grid-3 mb-xl">
        <a href="#scripts" class="card" data-page="scripts" style="cursor:pointer">
          <div class="card-icon purple">📝</div>
          <h3>Generar Guion</h3>
          <p>Crea guiones UGC profesionales en segundos con IA. Testimoniales, tutoriales y reviews.</p>
        </a>
        <a href="#avatars" class="card" data-page="avatars" style="cursor:pointer">
          <div class="card-icon cyan">🎨</div>
          <h3>Crear Avatar</h3>
          <p>Genera avatares ultrarrealistas con Freepik AI. Clónate o crea personajes únicos.</p>
        </a>
        <a href="#videos" class="card" data-page="videos" style="cursor:pointer">
          <div class="card-icon pink">🎬</div>
          <h3>Crear Vídeo UGC</h3>
          <p>Combina avatar + guion para producir vídeos UGC que parecen hechos por una persona real.</p>
        </a>
      </div>

      <!-- Workflow -->
      <h2 class="font-bold mb-lg" style="font-size:var(--font-size-xl)">🔄 Tu Flujo de Trabajo</h2>
      <div class="card mb-xl" style="padding:var(--space-2xl)">
        <div class="flex gap-xl items-center flex-wrap" style="justify-content:center">
          <div class="flex flex-col items-center gap-sm text-center" style="max-width:150px">
            <div style="font-size:40px">📝</div>
            <strong>1. Guion</strong>
            <span class="text-xs text-muted">Genera el texto</span>
          </div>
          <div style="font-size:24px;color:var(--accent-purple)">→</div>
          <div class="flex flex-col items-center gap-sm text-center" style="max-width:150px">
            <div style="font-size:40px">🎨</div>
            <strong>2. Avatar</strong>
            <span class="text-xs text-muted">Crea tu clon IA</span>
          </div>
          <div style="font-size:24px;color:var(--accent-purple)">→</div>
          <div class="flex flex-col items-center gap-sm text-center" style="max-width:150px">
            <div style="font-size:40px">🎬</div>
            <strong>3. Vídeo</strong>
            <span class="text-xs text-muted">Anima el avatar</span>
          </div>
          <div style="font-size:24px;color:var(--accent-purple)">→</div>
          <div class="flex flex-col items-center gap-sm text-center" style="max-width:150px">
            <div style="font-size:40px">📢</div>
            <strong>4. Anuncio</strong>
            <span class="text-xs text-muted">Publica y vende</span>
          </div>
        </div>
      </div>

      ${recentAvatars.length > 0 ? `
        <h2 class="font-bold mb-lg" style="font-size:var(--font-size-xl)">🖼️ Últimos Avatares</h2>
        <div class="gallery-grid mb-xl">
          ${recentAvatars.map(a => `
            <div class="gallery-item">
              <img src="${a.imageUrl}" alt="${a.name}" loading="lazy" />
              <div class="gallery-info">
                <h4>${a.name}</h4>
                <p>${new Date(a.createdAt).toLocaleDateString('es-ES')}</p>
              </div>
            </div>
          `).join('')}
        </div>
      ` : ''}

      ${recentScripts.length > 0 ? `
        <h2 class="font-bold mb-lg" style="font-size:var(--font-size-xl)">📄 Últimos Guiones</h2>
        <div class="flex flex-col gap-md mb-xl">
          ${recentScripts.map(s => `
            <div class="card" style="cursor:default">
              <div class="flex justify-between items-center mb-sm">
                <div class="flex gap-sm items-center">
                  <span class="chip ${s.tone === 'casual' ? 'cyan' : s.tone === 'urgent' ? 'pink' : 'purple'}">${s.tone}</span>
                  <span class="chip green">${s.format}</span>
                </div>
                <span class="text-xs text-muted">${new Date(s.createdAt).toLocaleDateString('es-ES')}</span>
              </div>
              <p class="text-sm" style="white-space:pre-wrap;max-height:80px;overflow:hidden">${s.text}</p>
            </div>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `;
}
