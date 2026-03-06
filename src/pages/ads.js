import { getAvatars, getVideos, getScripts } from '../services/storage.js';

const PLATFORMS = [
    { id: 'instagram-stories', name: 'Instagram Stories', icon: '📱', aspect: '9:16', size: '1080×1920' },
    { id: 'instagram-feed', name: 'Instagram Feed', icon: '📸', aspect: '1:1', size: '1080×1080' },
    { id: 'instagram-reels', name: 'Instagram Reels', icon: '🎞️', aspect: '9:16', size: '1080×1920' },
    { id: 'tiktok', name: 'TikTok', icon: '🎵', aspect: '9:16', size: '1080×1920' },
    { id: 'youtube-shorts', name: 'YouTube Shorts', icon: '▶️', aspect: '9:16', size: '1080×1920' },
    { id: 'youtube', name: 'YouTube', icon: '🎬', aspect: '16:9', size: '1920×1080' },
    { id: 'facebook-feed', name: 'Facebook Feed', icon: '👤', aspect: '1:1', size: '1080×1080' },
    { id: 'facebook-stories', name: 'Facebook Stories', icon: '📖', aspect: '9:16', size: '1080×1920' },
    { id: 'google-ads', name: 'Google Ads', icon: '🔍', aspect: '16:9', size: '1200×628' },
];

export function renderAds() {
    const avatars = getAvatars();
    const videos = getVideos();
    const scripts = getScripts();

    return `
    <div class="page-header">
      <h1>📢 Diseñador de <span class="gradient-text">Anuncios</span></h1>
      <p>Configura tus vídeos UGC para cada plataforma. Selecciona formato, añade overlay de texto y exporta listo para publicar.</p>
    </div>

    <div class="grid-2" style="grid-template-columns:1fr 1fr;align-items:start">
      <!-- Ad Builder -->
      <div>
        <!-- Platform Selection -->
        <div class="card mb-lg">
          <h3 class="mb-lg">📱 Selecciona plataforma(s)</h3>
          <div class="platform-grid" id="platform-grid">
            ${PLATFORMS.map(p => `
              <div class="platform-card" data-platform="${p.id}" data-aspect="${p.aspect}" data-size="${p.size}">
                <div class="platform-icon">${p.icon}</div>
                <span>${p.name}</span>
                <span class="text-xs text-muted">${p.aspect}</span>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Ad Content -->
        <div class="card mb-lg">
          <h3 class="mb-lg">✏️ Contenido del anuncio</h3>

          <div class="form-group">
            <label class="form-label">Headline / Gancho</label>
            <input type="text" id="ad-headline" class="form-input" placeholder='Ej: "¡Esto me cambió la vida!"' />
          </div>

          <div class="form-group">
            <label class="form-label">CTA (Call to Action)</label>
            <input type="text" id="ad-cta" class="form-input" value="🔗 Link en bio" placeholder="Ej: Compra ahora, Link en bio, Usa código..." />
          </div>

          <div class="form-group">
            <label class="form-label">Guion para subtítulos</label>
            <select id="ad-script" class="form-select">
              <option value="">Sin subtítulos</option>
              ${scripts.map(s => `
                <option value="${s.id}">${s.text.substring(0, 50)}... (${s.tone})</option>
              `).join('')}
            </select>
          </div>

          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">Color del texto</label>
              <input type="color" id="ad-text-color" class="form-input" value="#ffffff" style="height:44px;padding:4px" />
            </div>
            <div class="form-group">
              <label class="form-label">Color de fondo CTA</label>
              <input type="color" id="ad-cta-color" class="form-input" value="#a855f7" style="height:44px;padding:4px" />
            </div>
          </div>
        </div>

        <!-- Asset Selection -->
        <div class="card">
          <h3 class="mb-lg">🎨 Asset del anuncio</h3>

          <div class="form-group">
            <label class="form-label">Vídeo UGC</label>
            ${videos.length > 0 ? `
              <select id="ad-video" class="form-select">
                <option value="">Seleccionar vídeo</option>
                ${videos.filter(v => v.videoUrl).map(v => `
                  <option value="${v.videoUrl}">${v.name} — ${new Date(v.createdAt).toLocaleDateString('es-ES')}</option>
                `).join('')}
              </select>
            ` : `
              <p class="text-sm text-muted">No tienes vídeos. <a href="#videos" data-page="videos" style="color:var(--accent-purple-light)">Crea uno →</a></p>
            `}
          </div>

          <div class="form-group">
            <label class="form-label">O usa un Avatar (imagen)</label>
            ${avatars.length > 0 ? `
              <div class="flex gap-sm flex-wrap" id="ad-avatar-selector">
                ${avatars.slice(0, 8).map(a => `
                  <div class="avatar-select-item" data-url="${a.imageUrl}" style="cursor:pointer;border:2px solid var(--border-subtle);border-radius:var(--radius-md);overflow:hidden;width:60px;height:60px;transition:all var(--transition-fast)">
                    <img src="${a.imageUrl}" alt="${a.name}" style="width:100%;height:100%;object-fit:cover" />
                  </div>
                `).join('')}
              </div>
            ` : `
              <p class="text-sm text-muted">No tienes avatares. <a href="#avatars" data-page="avatars" style="color:var(--accent-purple-light)">Crea uno →</a></p>
            `}
          </div>

          <button id="btn-preview-ad" class="btn btn-primary btn-lg" style="width:100%">
            👁️ Previsualizar Anuncio
          </button>
        </div>
      </div>

      <!-- Preview -->
      <div class="card" style="position:sticky;top:var(--space-xl)">
        <div class="flex justify-between items-center mb-lg">
          <h3>👁️ Vista previa</h3>
          <div id="preview-platform-info" class="text-xs text-muted"></div>
        </div>

        <div id="ad-preview" style="display:flex;justify-content:center">
          <div id="ad-preview-frame" style="width:270px;height:480px;background:var(--bg-glass);border-radius:var(--radius-lg);border:2px solid var(--border-subtle);display:flex;align-items:center;justify-content:center;flex-direction:column;position:relative;overflow:hidden">
            <div class="empty-state" style="padding:var(--space-lg)">
              <div class="empty-icon" style="font-size:48px">📱</div>
              <h3 style="font-size:var(--font-size-sm)">Preview del anuncio</h3>
              <p style="font-size:var(--font-size-xs)">Selecciona plataforma y contenido</p>
            </div>
          </div>
        </div>

        <hr class="section-divider" />

        <h4 class="mb-md text-sm font-bold" style="color:var(--text-secondary)">📋 Checklist de publicación</h4>
        <div class="flex flex-col gap-sm" id="ad-checklist">
          <div class="flex items-center gap-sm text-sm">
            <span id="check-platform">⬜</span> Plataforma seleccionada
          </div>
          <div class="flex items-center gap-sm text-sm">
            <span id="check-content">⬜</span> Contenido configurado
          </div>
          <div class="flex items-center gap-sm text-sm">
            <span id="check-asset">⬜</span> Asset (vídeo o imagen) listo
          </div>
          <div class="flex items-center gap-sm text-sm">
            <span id="check-cta">⬜</span> CTA definido
          </div>
        </div>

        <hr class="section-divider" />

        <h4 class="mb-md text-sm font-bold" style="color:var(--text-secondary)">📐 Especificaciones seleccionadas</h4>
        <div id="ad-specs" class="text-sm text-muted">
          Selecciona una plataforma arriba para ver las especificaciones.
        </div>
      </div>
    </div>
  `;
}

let selectedPlatforms = [];
let selectedAdAvatarUrl = null;

export function initAds() {
    // Platform selection
    document.querySelectorAll('.platform-card').forEach(card => {
        card.addEventListener('click', () => {
            card.classList.toggle('selected');
            const pid = card.dataset.platform;
            if (selectedPlatforms.includes(pid)) {
                selectedPlatforms = selectedPlatforms.filter(p => p !== pid);
            } else {
                selectedPlatforms.push(pid);
            }
            updateChecklist();
            updateSpecs();
        });
    });

    // Avatar selector
    document.querySelectorAll('#ad-avatar-selector .avatar-select-item')?.forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('#ad-avatar-selector .avatar-select-item').forEach(i => {
                i.style.borderColor = 'var(--border-subtle)';
            });
            item.style.borderColor = 'var(--accent-purple)';
            selectedAdAvatarUrl = item.dataset.url;
            updateChecklist();
        });
    });

    // Preview button
    document.getElementById('btn-preview-ad')?.addEventListener('click', generatePreview);

    // Live checklist updates
    ['ad-headline', 'ad-cta'].forEach(id => {
        document.getElementById(id)?.addEventListener('input', updateChecklist);
    });
}

function updateChecklist() {
    const headline = document.getElementById('ad-headline')?.value;
    const cta = document.getElementById('ad-cta')?.value;
    const video = document.getElementById('ad-video')?.value;

    document.getElementById('check-platform').textContent = selectedPlatforms.length > 0 ? '✅' : '⬜';
    document.getElementById('check-content').textContent = headline ? '✅' : '⬜';
    document.getElementById('check-asset').textContent = (video || selectedAdAvatarUrl) ? '✅' : '⬜';
    document.getElementById('check-cta').textContent = cta ? '✅' : '⬜';
}

function updateSpecs() {
    const specsEl = document.getElementById('ad-specs');
    const infoEl = document.getElementById('preview-platform-info');

    if (selectedPlatforms.length === 0) {
        specsEl.innerHTML = 'Selecciona una plataforma.';
        infoEl.textContent = '';
        return;
    }

    const specs = selectedPlatforms.map(pid => {
        const p = PLATFORMS.find(pl => pl.id === pid);
        return p ? `<div class="flex justify-between mb-sm"><span>${p.icon} ${p.name}</span><span>${p.size} (${p.aspect})</span></div>` : '';
    }).join('');

    specsEl.innerHTML = specs;
    infoEl.textContent = `${selectedPlatforms.length} plataforma(s)`;
}

function generatePreview() {
    const frame = document.getElementById('ad-preview-frame');
    const headline = document.getElementById('ad-headline')?.value || '';
    const cta = document.getElementById('ad-cta')?.value || '';
    const textColor = document.getElementById('ad-text-color')?.value || '#ffffff';
    const ctaColor = document.getElementById('ad-cta-color')?.value || '#a855f7';
    const videoUrl = document.getElementById('ad-video')?.value;
    const imageUrl = selectedAdAvatarUrl;

    // Determine aspect ratio from first selected platform
    const firstPlatform = selectedPlatforms[0];
    const pConfig = PLATFORMS.find(p => p.id === firstPlatform);
    const aspect = pConfig?.aspect || '9:16';

    let width = 270, height = 480;
    if (aspect === '1:1') { height = 270; }
    else if (aspect === '16:9') { width = 340; height = 191; }
    else if (aspect === '4:3') { width = 320; height = 240; }

    frame.style.width = width + 'px';
    frame.style.height = height + 'px';

    const bgContent = videoUrl
        ? `<video src="${videoUrl}" autoplay loop muted style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"></video>`
        : imageUrl
            ? `<img src="${imageUrl}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover" />`
            : `<div style="position:absolute;inset:0;background:linear-gradient(180deg,#1a1a2e,#0a0a0f)"></div>`;

    frame.innerHTML = `
    ${bgContent}
    <div style="position:absolute;inset:0;background:linear-gradient(transparent 50%, rgba(0,0,0,0.7))"></div>
    ${headline ? `
      <div style="position:absolute;top:20px;left:12px;right:12px;color:${textColor};font-size:14px;font-weight:800;text-shadow:0 1px 4px rgba(0,0,0,0.8);line-height:1.3">
        ${headline}
      </div>
    ` : ''}
    ${cta ? `
      <div style="position:absolute;bottom:20px;left:12px;right:12px">
        <div style="background:${ctaColor};color:white;padding:8px 16px;border-radius:8px;text-align:center;font-size:13px;font-weight:700;box-shadow:0 4px 15px rgba(0,0,0,0.3)">
          ${cta}
        </div>
      </div>
    ` : ''}
  `;

    window.__showToast?.('Preview generado', 'success');
}
