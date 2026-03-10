// ═══════════════════════════════════════════════
// Ads Page — Multi-platform ad designer
// ═══════════════════════════════════════════════
import { storage } from '../services/storage.js';

const PLATFORMS = [
  { id: 'tiktok', name: 'TikTok', icon: '🎵', format: '9:16', w: 1080, h: 1920, maxDur: '60s', color: '#ee1d52' },
  { id: 'reels', name: 'Instagram Reels', icon: '📸', format: '9:16', w: 1080, h: 1920, maxDur: '90s', color: '#e4405f' },
  { id: 'stories', name: 'Instagram Stories', icon: '📱', format: '9:16', w: 1080, h: 1920, maxDur: '15s', color: '#833ab4' },
  { id: 'feed', name: 'Instagram Feed', icon: '🖼️', format: '1:1', w: 1080, h: 1080, maxDur: '60s', color: '#c13584' },
  { id: 'youtube_shorts', name: 'YouTube Shorts', icon: '🎬', format: '9:16', w: 1080, h: 1920, maxDur: '60s', color: '#ff0000' },
  { id: 'youtube', name: 'YouTube', icon: '▶️', format: '16:9', w: 1920, h: 1080, maxDur: '10min', color: '#ff0000' },
  { id: 'facebook_feed', name: 'Facebook Feed', icon: '👥', format: '1:1', w: 1080, h: 1080, maxDur: '240s', color: '#1877f2' },
  { id: 'facebook_stories', name: 'Facebook Stories', icon: '📖', format: '9:16', w: 1080, h: 1920, maxDur: '20s', color: '#1877f2' },
  { id: 'twitter', name: 'X (Twitter)', icon: '𝕏', format: '16:9', w: 1920, h: 1080, maxDur: '140s', color: '#000000' },
];

export function renderAds(container) {
  const scripts = storage.getScripts();
  const avatars = storage.getAvatars();

  container.innerHTML = `
    <div class="page-header">
      <h2>📢 Diseñador de Anuncios</h2>
      <p>Crea anuncios para 9 plataformas con tu avatar y guion viral</p>
    </div>

    <!-- Platform Grid -->
    <h3 style="margin-bottom:16px; font-weight:700;">Selecciona Plataforma</h3>
    <div class="card-grid" style="grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); margin-bottom:24px;">
      ${PLATFORMS.map(p => `
        <div class="card platform-card" data-platform="${p.id}" style="cursor:pointer; text-align:center; padding:20px;">
          <div style="font-size:32px; margin-bottom:8px;">${p.icon}</div>
          <h4 style="font-weight:700; font-size:14px; margin-bottom:4px;">${p.name}</h4>
          <div style="display:flex; gap:8px; justify-content:center; margin-top:8px;">
            <span class="tag tag-purple">${p.format}</span>
            <span class="tag tag-cyan">${p.maxDur}</span>
          </div>
          <p style="color:var(--text-muted); font-size:11px; margin-top:6px;">${p.w}×${p.h}px</p>
        </div>
      `).join('')}
    </div>

    <!-- Selected Platform Detail -->
    <div id="ad-config" style="display:none;">
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px;">
        <div class="card">
          <h3 style="font-weight:700; margin-bottom:20px;" id="ad-platform-title">Configuración</h3>

          <div class="input-group">
            <label>Avatar para el anuncio</label>
            <select id="ad-avatar">
              ${avatars.length === 0
      ? '<option>— Genera un avatar primero —</option>'
      : avatars.map((a, i) => `<option value="${i}">Avatar ${i + 1}</option>`).join('')
    }
            </select>
          </div>

          <div class="input-group">
            <label>Guion viral</label>
            <select id="ad-script">
              ${scripts.length === 0
      ? '<option>— Genera un guion primero —</option>'
      : scripts.map((s, i) => `<option value="${i}">[${s.config?.hookType}] ${s.config?.nicho} — ${s.hook?.substring(0, 50)}...</option>`).join('')
    }
            </select>
          </div>

          <div class="input-group">
            <label>Texto overlay principal</label>
            <input type="text" id="ad-headline" value="¿Tu negocio necesita más clientes?" placeholder="Headline del anuncio">
          </div>

          <div class="input-group">
            <label>CTA del anuncio</label>
            <input type="text" id="ad-cta-text" value="Más info ↗" placeholder="Texto del botón">
          </div>

          <div class="input-group">
            <label>URL destino</label>
            <input type="url" id="ad-url" value="https://sistema180.com" placeholder="https://...">
          </div>

          <button class="btn btn-primary btn-lg w-full" id="export-ad-btn">📤 Exportar Especificaciones</button>
        </div>

        <!-- Preview -->
        <div class="card" id="ad-preview-card" style="display:flex; flex-direction:column; align-items:center;">
          <h3 style="font-weight:700; margin-bottom:16px; align-self:flex-start;">Preview</h3>
          <div id="ad-preview" style="background:var(--bg-secondary); border-radius:var(--radius); overflow:hidden; position:relative; width:270px; height:480px; border:2px solid var(--border);">
            ${avatars.length > 0
      ? `<img src="${avatars[0]?.url}" style="width:100%; height:100%; object-fit:cover; opacity:0.8;" />`
      : '<div style="display:flex; align-items:center; justify-content:center; height:100%; color:var(--text-muted);">Sin avatar</div>'
    }
            <div style="position:absolute; bottom:0; left:0; right:0; background:linear-gradient(transparent, rgba(0,0,0,0.9)); padding:20px;">
              <p style="font-size:16px; font-weight:700; margin-bottom:8px;" id="preview-headline">¿Tu negocio necesita más clientes?</p>
              <div style="background:var(--accent); color:white; padding:8px 16px; border-radius:var(--radius-xs); display:inline-block; font-size:13px; font-weight:600;" id="preview-cta-btn">Más info ↗</div>
            </div>
          </div>
          <p style="color:var(--text-muted); font-size:12px; margin-top:12px;" id="ad-format-info">1080×1920px • 9:16 • TikTok</p>
        </div>
      </div>
    </div>
  `;

  // Platform selection
  container.querySelectorAll('.platform-card').forEach(card => {
    card.addEventListener('click', () => {
      container.querySelectorAll('.platform-card').forEach(c => c.style.borderColor = '');
      card.style.borderColor = 'var(--accent)';
      const platform = PLATFORMS.find(p => p.id === card.dataset.platform);
      if (platform) {
        container.querySelector('#ad-config').style.display = 'block';
        container.querySelector('#ad-platform-title').textContent = `Configuración — ${platform.name}`;
        container.querySelector('#ad-format-info').textContent = `${platform.w}×${platform.h}px • ${platform.format} • ${platform.name}`;
      }
    });
  });

  // Live preview updates
  const headline = container.querySelector('#ad-headline');
  const ctaText = container.querySelector('#ad-cta-text');
  if (headline) {
    headline.addEventListener('input', () => {
      const el = container.querySelector('#preview-headline');
      if (el) el.textContent = headline.value;
    });
  }
  if (ctaText) {
    ctaText.addEventListener('input', () => {
      const el = container.querySelector('#preview-cta-btn');
      if (el) el.textContent = ctaText.value;
    });
  }

  // C-06 FIX: Export ad specifications as JSON download
  let selectedPlatform = null;
  container.querySelectorAll('.platform-card').forEach(card => {
    card.addEventListener('click', () => {
      selectedPlatform = PLATFORMS.find(p => p.id === card.dataset.platform);
    });
  });

  const exportBtn = container.querySelector('#export-ad-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      if (!selectedPlatform) {
        alert('Selecciona una plataforma primero.');
        return;
      }
      const specs = {
        platform: selectedPlatform.name,
        format: selectedPlatform.format,
        resolution: `${selectedPlatform.w}x${selectedPlatform.h}`,
        maxDuration: selectedPlatform.maxDur,
        headline: container.querySelector('#ad-headline')?.value || '',
        cta: container.querySelector('#ad-cta-text')?.value || '',
        destinationUrl: container.querySelector('#ad-url')?.value || '',
        avatarIndex: container.querySelector('#ad-avatar')?.value || '0',
        scriptIndex: container.querySelector('#ad-script')?.value || '0',
        exportedAt: new Date().toISOString(),
      };
      const blob = new Blob([JSON.stringify(specs, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ad-${selectedPlatform.id}-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }
}
