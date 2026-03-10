// ═══════════════════════════════════════════════
// Videos Page — UGC Video Generator
// ═══════════════════════════════════════════════
import { storage } from '../services/storage.js';

export function renderVideos(container) {
  const avatars = storage.getAvatars();
  const scripts = storage.getScripts();

  container.innerHTML = `
    <div class="page-header">
      <h2>🎬 Generador de Vídeos UGC</h2>
      <p>Combina tu avatar + guion viral para crear vídeos sin cámara</p>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px;">
      <div class="card">
        <h3 style="font-weight:700; margin-bottom:20px;">Configuración del Vídeo</h3>

        <div class="input-group">
          <label>Avatar</label>
          <select id="vid-avatar">
            ${avatars.length === 0
      ? '<option value="">— Primero genera un avatar —</option>'
      : avatars.map((a, i) => `<option value="${i}">Avatar ${i + 1} — ${new Date(a.createdAt).toLocaleDateString('es-ES')}</option>`).join('')
    }
          </select>
        </div>

        <div class="input-group">
          <label>Guion</label>
          <select id="vid-script">
            ${scripts.length === 0
      ? '<option value="">— Primero genera un guion —</option>'
      : scripts.map((s, i) => `<option value="${i}">${s.config?.nicho || 'Guion'} — ${s.config?.hookType || ''} (${new Date(s.timestamp).toLocaleDateString('es-ES')})</option>`).join('')
    }
          </select>
        </div>

        <div class="input-group">
          <label>Formato</label>
          <select id="vid-format">
            <option value="9:16">Vertical 9:16 (TikTok / Reels / Stories)</option>
            <option value="1:1">Cuadrado 1:1 (Feed Instagram)</option>
            <option value="16:9">Horizontal 16:9 (YouTube)</option>
          </select>
        </div>

        <div class="input-group">
          <label>Subtítulos</label>
          <select id="vid-subs">
            <option value="bold">Grandes y Bold (TikTok style)</option>
            <option value="minimal">Minimalistas</option>
            <option value="karaoke">Karaoke (destacar palabra)</option>
            <option value="none">Sin subtítulos</option>
          </select>
        </div>

        <div class="input-group">
          <label>Música de fondo</label>
          <select id="vid-music">
            <option value="trending">Trending (popular)</option>
            <option value="motivacional">Motivacional</option>
            <option value="chill">Chill / Lo-fi</option>
            <option value="drama">Dramática</option>
            <option value="none">Sin música</option>
          </select>
        </div>

        <button class="btn btn-primary btn-lg w-full" id="gen-video-btn" ${avatars.length === 0 || scripts.length === 0 ? 'disabled' : ''}>
          🎬 Generar Vídeo
        </button>

        ${avatars.length === 0 || scripts.length === 0 ? `
          <p style="margin-top:12px; color:var(--orange); font-size:13px; text-align:center;">
            ⚠️ Necesitas al menos 1 avatar y 1 guion para generar un vídeo
          </p>
        ` : ''}
      </div>

      <!-- Preview Panel -->
      <div>
        <div class="card" style="padding:32px;">
          <h3 style="font-weight:700; margin-bottom:20px;">Preview</h3>

          ${scripts.length > 0 ? `
            <div style="background:var(--bg-secondary); border-radius:var(--radius); padding:20px; margin-bottom:16px;">
              <h4 style="font-size:13px; color:var(--accent); margin-bottom:8px;">🪝 GANCHO</h4>
              <p style="font-size:14px;" id="preview-hook">${scripts[0]?.hook || ''}</p>
            </div>
            <div style="background:var(--bg-secondary); border-radius:var(--radius); padding:20px;">
              <h4 style="font-size:13px; color:var(--green); margin-bottom:8px;">📢 CTA</h4>
              <p style="font-size:14px;" id="preview-cta">${scripts[0]?.cta || ''}</p>
            </div>
          ` : `
            <div class="text-center" style="padding:40px;">
              <div style="font-size:48px; margin-bottom:12px;">🎬</div>
              <p style="color:var(--text-muted);">Genera un avatar y un guion primero</p>
            </div>
          `}

          ${avatars.length > 0 ? `
            <div style="margin-top:16px;">
              <img src="${avatars[0]?.url}" style="width:100%; max-height:300px; object-fit:cover; border-radius:var(--radius); border:2px solid var(--border);" />
            </div>
          ` : ''}
        </div>

        <div class="card mt-16" style="border-left:3px solid var(--orange);">
          <h4 style="font-weight:700; margin-bottom:8px;">🚀 Próximamente</h4>
          <p style="font-size:14px; color:var(--text-secondary); line-height:1.6;">
            Generación automática de vídeo con lip-sync (el avatar hablando). 
            Integración con Kling Pro v2.1 y HeyGen para animación completa.
          </p>
        </div>
      </div>
    </div>
  `;

  // Update preview when script selection changes
  const scriptSelect = container.querySelector('#vid-script');
  if (scriptSelect && scripts.length > 0) {
    scriptSelect.addEventListener('change', () => {
      const idx = parseInt(scriptSelect.value);
      const s = scripts[idx];
      if (s) {
        const hookEl = container.querySelector('#preview-hook');
        const ctaEl = container.querySelector('#preview-cta');
        if (hookEl) hookEl.textContent = s.hook;
        if (ctaEl) ctaEl.textContent = s.cta;
      }
    });
  }

  // Update avatar preview on selection change
  const avatarSelect = container.querySelector('#vid-avatar');
  if (avatarSelect && avatars.length > 0) {
    avatarSelect.addEventListener('change', () => {
      const idx = parseInt(avatarSelect.value);
      const av = avatars[idx];
      const imgEl = container.querySelector('#preview-avatar-img');
      if (av && imgEl) imgEl.src = av.url;
    });
  }

  // C-07 FIX: Connect "Generar Vídeo" button
  const genVideoBtn = container.querySelector('#gen-video-btn');
  if (genVideoBtn && !genVideoBtn.disabled) {
    genVideoBtn.addEventListener('click', async () => {
      const avatarIdx = parseInt(container.querySelector('#vid-avatar')?.value || '0');
      const scriptIdx = parseInt(container.querySelector('#vid-script')?.value || '0');
      const format = container.querySelector('#vid-format')?.value || '9:16';
      const subs = container.querySelector('#vid-subs')?.value || 'bold';
      const music = container.querySelector('#vid-music')?.value || 'trending';

      const avatar = avatars[avatarIdx];
      const script = scripts[scriptIdx];

      if (!avatar || !script) {
        alert('Selecciona un avatar y un guion.');
        return;
      }

      genVideoBtn.disabled = true;
      genVideoBtn.innerHTML = '<div class="spinner" style="display:inline-block;margin-right:8px;"></div> Generando...';

      // Save video config to storage
      const videoConfig = {
        id: Date.now(),
        avatarUrl: avatar.url,
        script: { hook: script.hook, story: script.story, moraleja: script.moraleja, cta: script.cta },
        format,
        subtitles: subs,
        music,
        status: 'pending',
        createdAt: new Date().toISOString(),
      };

      const videos = storage.get('videos') || [];
      videos.unshift(videoConfig);
      storage.set('videos', videos);

      // Simulate progress (real generation would use HeyGen/Kling API)
      const steps = [
        '🎙️ Preparando audio del guion...',
        '🤖 Configurando avatar...',
        '🎬 Renderizando escenas...',
        '📝 Añadiendo subtítulos...',
        '🎵 Mezclando música...',
        '✅ ¡Vídeo configurado!'
      ];

      for (const step of steps) {
        genVideoBtn.innerHTML = `<div class="spinner" style="display:inline-block;margin-right:8px;"></div> ${step}`;
        await new Promise(r => setTimeout(r, 800));
      }

      genVideoBtn.disabled = false;
      genVideoBtn.innerHTML = '🎬 Generar Vídeo';

      alert('✅ Configuración guardada.\n\nPara generar el vídeo real con lip-sync, necesitas integrar HeyGen o Kling API (próximamente).\n\nEl guion y avatar están listos.');
    });
  }
}
