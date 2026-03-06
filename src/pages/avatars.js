import { freepikAPI } from '../services/freepik-api.js';
import { saveAvatar, getAvatars, deleteAvatar } from '../services/storage.js';

export function renderAvatars() {
  const avatars = getAvatars();
  const isConfigured = freepikAPI.isConfigured();

  return `
    <div class="page-header">
      <h1>🎨 Creador de <span class="gradient-text">Avatares IA</span></h1>
      <p>Genera avatares ultrarrealistas con Freepik AI (modelo Mystic 4K). Clónate o crea personajes únicos para tus vídeos UGC.</p>
    </div>

    <div class="grid-2" style="grid-template-columns: 1fr 1fr; align-items: start;">
      <!-- Creator Form -->
      <div class="card" style="position:sticky;top:var(--space-xl)">
        <h3 class="mb-lg">🧑‍🎨 Construye tu Avatar</h3>

        ${!isConfigured ? `
          <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:var(--radius-md);padding:var(--space-md);margin-bottom:var(--space-lg)">
            <p class="text-sm" style="color:var(--accent-red)">⚠️ API Key no configurada. <a href="#settings" data-page="settings" style="color:var(--accent-purple-light);text-decoration:underline">Configurar ahora →</a></p>
          </div>
        ` : ''}

        <div class="form-group">
          <label class="form-label">Nombre del avatar</label>
          <input type="text" id="avatar-name" class="form-input" placeholder="Ej: Mi Clon Digital" />
        </div>

        <div class="form-group">
          <label class="form-label">Descripción detallada (Prompt) *</label>
          <textarea id="avatar-prompt" class="form-textarea" rows="5" placeholder="Describe al avatar con TODO el detalle posible. Ejemplo:&#10;&#10;Hombre español de 30 años, pelo castaño oscuro corto, barba de 3 días, ojos marrones, piel bronceada, sonrisa natural y confiable. Lleva una camiseta negra lisa. Fondo desenfocado de habitación moderna con luz natural suave. Mirando directamente a cámara. Estilo retrato fotográfico profesional iPhone, alta resolución 4K, ultrarrealista."></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Prompt negativo (qué evitar)</label>
          <input type="text" id="avatar-negative" class="form-input" value="cartoon, anime, drawing, illustration, painting, deformed, ugly, blurry, low quality, watermark, text, logo" />
        </div>

        <h4 class="mb-md text-sm font-bold" style="color:var(--text-secondary)">⚡ Ajustes rápidos</h4>

        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Estilo</label>
            <select id="avatar-style" class="form-select">
              <option value="photo">📸 Fotorrealista</option>
              <option value="digital-art">🎨 Arte digital</option>
              <option value="3d">🧊 3D Render</option>
              <option value="cinematic">🎬 Cinemático</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Formato</label>
            <select id="avatar-size" class="form-select">
              <option value="square_1_1">1:1 Cuadrado</option>
              <option value="portrait_3_4">3:4 Retrato</option>
              <option value="landscape_4_3">4:3 Paisaje</option>
              <option value="widescreen_16_9">16:9 Panorámico</option>
              <option value="portrait_9_16">9:16 Vertical</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Número de variaciones</label>
          <select id="avatar-count" class="form-select">
            <option value="1">1 imagen</option>
            <option value="2">2 imágenes</option>
            <option value="4" selected>4 imágenes</option>
          </select>
        </div>

        <button id="btn-generate-avatar" class="btn btn-primary btn-lg" style="width:100%" ${!isConfigured ? 'disabled' : ''}>
          🎨 Generar Avatar con Freepik AI
        </button>

        <hr class="section-divider" />

        <h4 class="mb-md text-sm font-bold" style="color:var(--text-secondary)">📋 Prompts rápidos para clonarte</h4>
        <div class="flex flex-col gap-sm">
          <button class="btn btn-secondary quick-prompt" data-prompt="Professional headshot of a Spanish man, 30 years old, short dark brown hair, 3-day beard, brown eyes, tanned skin, confident natural smile, wearing a plain black t-shirt. Blurred modern room background with soft natural light. Looking directly at camera. Professional iPhone portrait style photo, ultra high resolution 4K, hyperrealistic, photorealistic.">
            👨 Hombre joven profesional
          </button>
          <button class="btn btn-secondary quick-prompt" data-prompt="Professional headshot of a Spanish woman, 28 years old, long dark hair, brown eyes, natural makeup, warm genuine smile. Wearing a white blouse. Blurred bright modern office background with soft natural light. Looking directly at camera. Professional iPhone portrait style photo, ultra high resolution 4K, hyperrealistic, photorealistic.">
            👩 Mujer joven profesional
          </button>
          <button class="btn btn-secondary quick-prompt" data-prompt="Close-up selfie-style photo of a friendly Spanish person, 25 years old, trendy casual look, bright eyes, enthusiastic expression, holding phone showing product. Ring light reflection in eyes. Modern apartment background. Social media UGC style. iPhone 15 Pro quality, 4K ultrarealistic.">
            🤳 Estilo selfie UGC
          </button>
          <button class="btn btn-secondary quick-prompt" data-prompt="Video call thumbnail style photo. Confident Spanish entrepreneur, 32 years old, well-groomed, wearing smart casual shirt. Clean modern workspace behind. Webcam angle, looking at camera with friendly expression. Natural indoor lighting. Professional quality, ultrarealistic 4K.">
            💻 Estilo videollamada
          </button>
        </div>
      </div>

      <!-- Gallery / Output -->
      <div>
        <!-- Generated Result -->
        <div class="card mb-lg" id="avatar-result-card">
          <div class="flex justify-between items-center mb-lg">
            <h3>🖼️ Resultado</h3>
            <div id="avatar-loading" style="display:none">
              <div class="flex items-center gap-sm">
                <div class="spinner"></div>
                <span class="text-sm text-muted">Generando con Freepik AI...</span>
              </div>
            </div>
          </div>

          <div id="avatar-output">
            <div class="empty-state">
              <div class="empty-icon">🎨</div>
              <h3>Tu avatar aparecerá aquí</h3>
              <p>Describe cómo quieres que sea tu avatar y Freepik AI lo generará en calidad 4K ultrarrealista.</p>
            </div>
          </div>
        </div>

        <!-- Saved Avatars -->
        ${avatars.length > 0 ? `
          <h3 class="mb-md">💾 Tu Librería de Avatares (${avatars.length})</h3>
          <div class="gallery-grid">
            ${avatars.map(a => `
              <div class="gallery-item" data-avatar-id="${a.id}">
                <img src="${a.imageUrl}" alt="${a.name}" loading="lazy" />
                <div class="gallery-info">
                  <div class="flex justify-between items-center">
                    <h4>${a.name}</h4>
                    <button class="btn btn-ghost btn-delete-avatar" data-id="${a.id}" style="padding:2px 6px;font-size:12px">🗑️</button>
                  </div>
                  <p>${new Date(a.createdAt).toLocaleDateString('es-ES')}</p>
                </div>
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

export function initAvatars() {
  const btnGenerate = document.getElementById('btn-generate-avatar');
  btnGenerate?.addEventListener('click', handleGenerateAvatar);

  // Quick prompts
  document.querySelectorAll('.quick-prompt').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('avatar-prompt').value = btn.dataset.prompt;
      window.__showToast?.('Prompt cargado — ajústalo a tu gusto', 'info');
    });
  });

  // Delete avatars
  document.querySelectorAll('.btn-delete-avatar').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteAvatar(btn.dataset.id);
      window.__navigate?.('avatars');
    });
  });
}

async function handleGenerateAvatar() {
  const prompt = document.getElementById('avatar-prompt')?.value;
  const name = document.getElementById('avatar-name')?.value || 'Avatar';
  const negative = document.getElementById('avatar-negative')?.value;
  const style = document.getElementById('avatar-style')?.value;
  const size = document.getElementById('avatar-size')?.value;
  const count = parseInt(document.getElementById('avatar-count')?.value || '1');

  if (!prompt) {
    window.__showToast?.('Escribe una descripción del avatar', 'error');
    return;
  }

  if (!freepikAPI.isConfigured()) {
    window.__showToast?.('Configura tu API Key primero', 'error');
    return;
  }

  // Show loading
  const btnGenerate = document.getElementById('btn-generate-avatar');
  const loading = document.getElementById('avatar-loading');
  const output = document.getElementById('avatar-output');

  btnGenerate.disabled = true;
  btnGenerate.textContent = '⏳ Generando...';
  loading.style.display = 'block';
  output.innerHTML = `
    <div class="loading-overlay">
      <div class="spinner spinner-lg"></div>
      <p>Freepik AI está creando tu avatar ultrarrealista...</p>
      <p class="text-xs text-muted">Esto puede tardar 10-30 segundos</p>
    </div>
  `;

  try {
    const result = await freepikAPI.generateImage(prompt, {
      numImages: count,
      size,
      style,
      negativePrompt: negative,
    }, (progressMsg) => {
      // Update loading text with polling progress
      const loadingText = output.querySelector('p');
      if (loadingText) loadingText.textContent = progressMsg;
    });

    // generateImage now returns array of images directly
    const images = Array.isArray(result) ? result : [];
    if (images.length === 0) {
      throw new Error('No se generaron imágenes');
    }

    output.innerHTML = `
      <div class="gallery-grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))">
        ${images.map((img, i) => {
      // Freepik returns URLs as strings or objects with base64/url
      const url = typeof img === 'string' ? img : (img.base64 ? `data:image/png;base64,${img.base64}` : img.url);
      return `
            <div class="gallery-item generated-avatar" data-url="${url}" data-index="${i}">
              <img src="${url}" alt="Avatar generado ${i + 1}" />
              <div class="gallery-info">
                <div class="flex justify-between items-center">
                  <h4>Variación ${i + 1}</h4>
                  <button class="btn btn-primary btn-save-generated" data-url="${url}" data-name="${name} v${i + 1}" style="padding:4px 12px;font-size:12px">💾 Guardar</button>
                </div>
              </div>
            </div>
          `;
    }).join('')}
      </div>
    `;

    // Bind save buttons
    document.querySelectorAll('.btn-save-generated').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        saveAvatar({
          name: btn.dataset.name,
          imageUrl: btn.dataset.url,
          prompt,
          style,
        });
        window.__showToast?.('Avatar guardado en tu librería', 'success');
        btn.textContent = '✓ Guardado';
        btn.disabled = true;
      });
    });

    window.__showToast?.(`¡${images.length} avatar(es) generado(s)!`, 'success');
  } catch (err) {
    output.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">❌</div>
        <h3>Error al generar</h3>
        <p>${err.message}</p>
      </div>
    `;
    window.__showToast?.(err.message, 'error');
  } finally {
    btnGenerate.disabled = false;
    btnGenerate.textContent = '🎨 Generar Avatar con Freepik AI';
    loading.style.display = 'none';
  }
}
