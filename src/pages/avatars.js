// ===============================================
// Avatars Page — Multi-AI Image Generator (v3 Robust)
// ===============================================
import { freepikApi } from '../services/freepik-api.js';
import { storage } from '../services/storage.js';
import { aiCascade } from '../services/ai-cascade.js';

export function renderAvatars(container) {
  const avatars = storage.getAvatars();
  container.innerHTML = `
    <div class="page-header">
      <h2>\u{1F916} Generador de Avatares Multi-IA</h2>
      <p>Crea tu clon digital para videos UGC. Motor <span class="tag tag-green">GRATIS</span> para borradores y <span class="tag tag-purple">PREMIUM</span> para el resultado final.</p>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px;">
      <div class="card">
        <h3 style="font-weight:700; margin-bottom:20px;">Prompt Builder</h3>

        <div class="input-group" style="background:var(--bg-secondary); padding:12px; border-radius:var(--radius-sm); border-left:3px solid var(--accent)">
          <label style="display:flex; justify-content:space-between; align-items:center;">
            Motor de IA
            <span id="api-badge" class="tag tag-green">GRATIS</span>
          </label>
          <select id="api-provider" style="font-weight:600;">
            <option value="pollinations">Pollinations FLUX (Rapido, 100% GRATIS)</option>
            <option value="gemini">\u{1F9E0} Gemini + FLUX (Prompt mejorado, GRATIS)</option>
            <option value="pplx-gemini">\u{1F50D}+\u{1F9E0} Perplexity + Gemini + FLUX (Max Realismo)</option>
            <option value="freepik">Freepik Mystic 4K (Premium) \u{1F48E}</option>
          </select>
          <p style="font-size:12px; color:var(--text-muted); margin-top:8px;" id="api-hint">
            Motor FLUX open-source. Sin API Key, sin limite, sin coste.
          </p>
        </div>

        <div class="input-group">
          <label>Genero</label>
          <select id="av-gender">
            <option value="young man">Hombre joven</option>
            <option value="young woman">Mujer joven</option>
            <option value="mature man">Hombre maduro</option>
            <option value="mature woman">Mujer madura</option>
          </select>
        </div>

        <div class="input-group">
          <label>Estilo / Look</label>
          <select id="av-style">
            <option value="black polo shirt, modern professional look">Profesional moderno</option>
            <option value="casual t-shirt, entrepreneur look">Casual emprendedor</option>
            <option value="elegant suit">Elegante formal</option>
            <option value="streetwear hoodie, urban look">Streetwear urbano</option>
            <option value="sports t-shirt, fit athletic">Deportivo / Fit</option>
          </select>
        </div>

        <div class="input-group">
          <label>Fondo</label>
          <select id="av-bg">
            <option value="clean white studio background">Blanco estudio</option>
            <option value="modern office with natural light">Oficina moderna</option>
            <option value="urban exterior with buildings">Ciudad urbana</option>
            <option value="cozy coffee shop warm light">Cafeteria</option>
            <option value="dark blue gradient background">Degradado oscuro</option>
          </select>
        </div>

        <div class="input-group">
          <label>Pose</label>
          <select id="av-pose">
            <option value="arms crossed, looking at camera, confident">Brazos cruzados</option>
            <option value="talking with gestures, expressive">Hablando expresivo</option>
            <option value="natural smile, relaxed">Sonrisa natural</option>
            <option value="pointing upward, explaining">Senalando</option>
            <option value="sitting with laptop, working">Con laptop</option>
          </select>
        </div>

        <div class="input-group">
          <label>Descripcion fisica (pelo, rasgos)</label>
          <input type="text" id="av-physical" value="curly brown hair, mediterranean skin, short beard" placeholder="Ej: curly hair, brown eyes...">
        </div>

        <div class="input-group">
          <label>Detalles adicionales (opcional)</label>
          <textarea id="av-extra" rows="2" placeholder="Detalles específicos..."></textarea>
        </div>

        <div class="input-group" style="background:var(--bg-secondary); padding:12px; border-radius:var(--radius-sm); border-left:3px solid var(--purple);">
          <label style="display:flex; justify-content:space-between; align-items:center;">
            Clonación Avanzada (Face Swap)
            <span class="tag tag-purple">NUEVO</span>
          </label>
          <p style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">
            Sube tu foto de la cara para crear un clon exacto (requiere servidor Local).
          </p>
          <input type="file" id="av-face" accept="image/jpeg, image/png" style="font-size:13px; padding:8px;" />
        </div>

        <div class="input-group">
          <label>Resolución</label>
          <select id="av-resolution">
            <option value="768x1024">768×1024 (Borrador rápido)</option>
            <option value="1080x1080">1080×1080 (Instagram Feed)</option>
            <option value="1080x1920" selected>1080×1920 (Stories / TikTok)</option>
            <option value="1200x630">1200×630 (LinkedIn / Web)</option>
          </select>
        </div>

        <button class="btn btn-primary btn-lg w-full" id="generate-btn">
          \u{1F3A8} Generar Avatar
        </button>
        <div id="gen-error" style="display:none; color:var(--red); font-size:13px; margin-top:10px; padding:10px; background:rgba(239,68,68,0.1); border-radius:var(--radius-sm);"></div>
      </div>

      <div class="card" style="display:flex; flex-direction:column; gap:16px;">
        <div id="gen-status" style="display:none; text-align:center; padding:32px;">
          <div class="spinner" style="margin:0 auto 16px;"></div>
          <p id="gen-text" style="color:var(--text-secondary);">Generando...</p>
          <div class="loading-bar" style="margin-top:16px;"><div class="fill"></div></div>
        </div>

        <div id="gen-result" style="display:none; position:relative;">
          <span id="result-badge" class="tag tag-green" style="position:absolute; top:10px; left:10px; z-index:10; font-size:11px;">FLUX</span>
          <img id="gen-img" src="" alt="Avatar generado" style="width:100%; border-radius:var(--radius-sm); max-height:500px; object-fit:cover;">
          <div style="display:flex; gap:12px; margin-top:16px;">
            <button class="btn btn-success" style="flex:1;" id="save-btn">\u{1F4BE} Guardar</button>
            <button class="btn btn-secondary" id="regen-btn">\u{1F504} Regenerar</button>
          </div>
        </div>

        <div id="gen-empty" style="flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; color:var(--text-muted); text-align:center; padding:40px; min-height:300px;">
          <div style="font-size:64px; margin-bottom:16px;">\u{1F916}</div>
          <p style="font-weight:600; margin-bottom:8px;">Aun no has generado avatares.</p>
          <p style="font-size:13px;">Usa el prompt builder para crear tu primer clon.</p>
        </div>
      </div>
    </div>

    <div style="margin-top:32px;">
      <h3 style="font-weight:700; margin-bottom:16px;">Tu Libreria (${avatars.length})</h3>
      <div id="avatars-gallery" class="gallery">
        ${avatars.length === 0 ? '<p style="color:var(--text-muted);">Sin avatares guardados.</p>' : avatars.map(av => `
          <div class="gallery-item">
            <img src="${av.url}" alt="Avatar">
            <div class="overlay">
              <div style="font-size:11px; color:white; opacity:0.8;">${av.api?.toUpperCase() || 'AI'}</div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  const apiSelect = container.querySelector('#api-provider');
  const apiBadge = container.querySelector('#api-badge');
  const apiHint = container.querySelector('#api-hint');

  apiSelect.addEventListener('change', (e) => {
    const v = e.target.value;
    if (v === 'pollinations') {
      apiBadge.className = 'tag tag-green'; apiBadge.textContent = 'GRATIS';
      apiHint.textContent = 'Motor FLUX open-source. Sin API Key, sin limite, sin coste.';
    } else if (v === 'gemini') {
      apiBadge.className = 'tag tag-green'; apiBadge.textContent = 'GRATIS';
      apiHint.textContent = 'Gemini optimiza el prompt, FLUX genera. Si Gemini falla, usa FLUX directo.';
    } else if (v === 'pplx-gemini') {
      apiBadge.className = 'tag tag-green'; apiBadge.textContent = 'GRATIS';
      apiHint.textContent = 'Perplexity investiga, Gemini perfecciona, FLUX genera.';
    } else {
      apiBadge.className = 'tag tag-purple'; apiBadge.textContent = 'PREMIUM';
      apiHint.textContent = 'Consume 1 credito de Freepik. Usar cuando el diseno ya esta validado.';
    }
  });

  // --- POLLINATIONS IMAGE LOADER using Image() element (NO CORS issues) ---
  // Pollinations generates images on-the-fly, can take 30-90 seconds
  function loadPollinationsImage(prompt, statusEl) {
    const seed = Math.floor(Math.random() * 1000000);
    const resolution = container.querySelector('#av-resolution')?.value || '1080x1920';
    const [w, h] = resolution.split('x').map(Number);
    const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=${w}&height=${h}&model=flux&seed=${seed}&nologo=true`;

    return new Promise((resolve, reject) => {
      if (statusEl) statusEl.textContent = 'FLUX generando imagen (30-90s, paciencia)...';

      const img = new Image();
      let resolved = false;

      // 90 second timeout
      const timer = setTimeout(() => {
        if (!resolved) {
          resolved = true;
          img.src = '';
          reject(new Error('Pollinations tardo mas de 90s. Intenta de nuevo.'));
        }
      }, 90000);

      img.onload = () => {
        if (!resolved) {
          resolved = true;
          clearTimeout(timer);
          resolve(url);
        }
      };

      img.onerror = () => {
        if (!resolved) {
          resolved = true;
          clearTimeout(timer);
          // Retry once with a different seed
          if (statusEl) statusEl.textContent = 'Reintentando con otro seed...';
          const seed2 = Math.floor(Math.random() * 1000000);
          const url2 = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=768&height=1024&model=flux&seed=${seed2}&nologo=true`;
          const img2 = new Image();
          const timer2 = setTimeout(() => { img2.src = ''; reject(new Error('Pollinations no responde. El servidor puede estar saturado.')); }, 90000);
          img2.onload = () => { clearTimeout(timer2); resolve(url2); };
          img2.onerror = () => { clearTimeout(timer2); reject(new Error('Pollinations no responde. Intenta mas tarde o usa Freepik.')); };
          img2.src = url2;
        }
      };

      // Start loading
      img.src = url;
    });
  }

  // --- Gemini & Perplexity via shared ai-cascade service (DRY, m-01/m-02 FIX) ---
  async function callGeminiSafe(userMsg) {
    try {
      return await aiCascade.callGemini(userMsg, 'You are a professional photo director.');
    } catch (e) { return null; }
  }

  async function callPerplexitySafe(query) {
    try {
      return await aiCascade.callPerplexity(query);
    } catch (e) { return null; }
  }

  // Generate handler
  const genBtn = container.querySelector('#generate-btn');
  const status = container.querySelector('#gen-status');
  const result = container.querySelector('#gen-result');
  const genEmpty = container.querySelector('#gen-empty');
  const genError = container.querySelector('#gen-error');
  const resultBadge = container.querySelector('#result-badge');
  const genText = container.querySelector('#gen-text');

  genBtn.addEventListener('click', async () => {
    const provider = apiSelect.value;
    const gender = container.querySelector('#av-gender').value;
    const style = container.querySelector('#av-style').value;
    const bg = container.querySelector('#av-bg').value;
    const pose = container.querySelector('#av-pose').value;
    const physical = container.querySelector('#av-physical').value;
    const extra = container.querySelector('#av-extra').value;

    const basePrompt = `Ultra-realistic 4K professional photograph of a ${gender}, ${physical}, wearing ${style}, ${pose}, ${bg}. Soft studio lighting, sharp focus, high detail skin texture, natural expression, bokeh background.${extra ? ' ' + extra : ''}`;

    genBtn.disabled = true;
    genError.style.display = 'none';
    status.style.display = 'block';
    result.style.display = 'none';
    genEmpty.style.display = 'none';

    try {
      let finalUrl = '';
      let usedPrompt = basePrompt;

      if (provider === 'pollinations') {
        finalUrl = await loadPollinationsImage(basePrompt, genText);
        resultBadge.textContent = 'FLUX BORRADOR'; resultBadge.className = 'tag tag-green';

      } else if (provider === 'gemini') {
        genText.textContent = 'Gemini optimizando prompt...';
        const refined = await callGeminiSafe(
          `You are a professional photo director. Rewrite this avatar prompt to maximize PHOTOREALISM for an AI image generator. Keep it in English, max 150 words. Focus on: lighting, skin detail, camera 85mm f/1.8, color grading. Prompt: ${basePrompt}`
        );
        if (refined) {
          usedPrompt = refined;
          genText.textContent = 'Prompt mejorado. Generando con FLUX...';
        } else {
          genText.textContent = 'Gemini no disponible, usando FLUX directo...';
        }
        finalUrl = await loadPollinationsImage(usedPrompt, genText);
        resultBadge.textContent = refined ? 'GEMINI+FLUX' : 'FLUX'; resultBadge.className = refined ? 'tag tag-purple' : 'tag tag-green';

      } else if (provider === 'pplx-gemini') {
        genText.textContent = 'Perplexity buscando tendencias UGC 2026...';
        const pplxData = await callPerplexitySafe(
          `Top visual styles for UGC creator avatars 2026. Photography details: lighting, clothing, backgrounds, camera for TikTok and Instagram.`
        );
        if (pplxData) {
          genText.textContent = 'Gemini creando prompt perfecto...';
          const master = await callGeminiSafe(
            `Based on UGC research: "${pplxData}" — write an ultra-detailed photography prompt for a ${gender} UGC avatar: ${physical}, ${style}, ${pose}, ${bg}. Max 180 words, English, photorealism. Start directly.`
          );
          usedPrompt = master || basePrompt;
        } else {
          const refined = await callGeminiSafe(`Rewrite for max photorealism, 150 words, English: ${basePrompt}`);
          usedPrompt = refined || basePrompt;
        }
        finalUrl = await loadPollinationsImage(usedPrompt, genText);
        resultBadge.textContent = pplxData ? 'PPLX+GEMINI+FLUX' : 'FLUX'; resultBadge.className = 'tag tag-cyan';

      } else {
        genText.textContent = 'Generando 4K Premium con Freepik Mystic...';
        finalUrl = await freepikApi.generateAvatar(basePrompt);
        resultBadge.textContent = '4K MYSTIC'; resultBadge.className = 'tag tag-purple';
      }

      // ── ADVANCED CLONING OVERRIDE (If face image is selected) ──
      const faceFile = container.querySelector('#av-face').files[0];
      if (faceFile) {
        genText.textContent = 'Iniciando Clonación Facial Avanzada (PuLID)...';
        const formData = new FormData();
        formData.append('face_image', faceFile);
        formData.append('prompt', usedPrompt);

        const cloneRes = await fetch('/api/avatars/clone', {
          method: 'POST',
          body: formData
        });

        if (!cloneRes.ok) {
          const errData = await cloneRes.json();
          throw new Error(errData.error || 'Server error during Face Swap.');
        }

        const cloneData = await cloneRes.json();
        finalUrl = cloneData.url;
        resultBadge.textContent = 'CLON EXACTO (PuLID)';
        resultBadge.className = 'tag tag-pink';
      }

      container.querySelector('#gen-img').src = finalUrl;
      result.style.display = 'block';
      status.style.display = 'none';

      container.querySelector('#save-btn').onclick = () => {
        storage.addAvatar({ url: finalUrl, prompt: usedPrompt, api: provider });
        // M-04 FIX: Visual save feedback
        const saveBtn = container.querySelector('#save-btn');
        saveBtn.textContent = '✅ ¡Guardado!';
        saveBtn.disabled = true;
        setTimeout(() => renderAvatars(container), 1500);
      };
      container.querySelector('#regen-btn').onclick = () => genBtn.click();

    } catch (err) {
      status.style.display = 'none';
      genEmpty.style.display = 'flex';
      genError.style.display = 'block';
      genError.textContent = '\u274C ' + (err.message || 'Error desconocido');
    } finally {
      genBtn.disabled = false;
    }
  });
}
