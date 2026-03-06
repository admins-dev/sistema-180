import { freepikAPI } from '../services/freepik-api.js';
import { saveSettings, getSettings } from '../services/storage.js';

export function renderSettings() {
    const settings = getSettings();
    const isConfigured = freepikAPI.isConfigured();
    const currentKey = freepikAPI.getApiKey();
    const maskedKey = currentKey ? currentKey.slice(0, 8) + '...' + currentKey.slice(-4) : '';

    return `
    <div class="page-header">
      <h1>⚙️ <span class="gradient-text">Configuración</span></h1>
      <p>Configura tus API Keys y preferencias. Solo necesitas la API Key de Freepik para empezar.</p>
    </div>

    <div style="max-width:700px">
      <!-- Freepik API -->
      <div class="card mb-lg" style="border-color:${isConfigured ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}">
        <div class="flex justify-between items-center mb-lg">
          <div class="flex items-center gap-md">
            <div class="card-icon ${isConfigured ? 'green' : 'pink'}" style="margin-bottom:0">
              ${isConfigured ? '✅' : '🔑'}
            </div>
            <div>
              <h3>Freepik API Key</h3>
              <p class="text-xs text-muted">${isConfigured ? 'Conectada — ' + maskedKey : 'Sin configurar'}</p>
            </div>
          </div>
          <span class="badge ${isConfigured ? 'new' : 'beta'}" style="background:${isConfigured ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'};color:${isConfigured ? 'var(--accent-green)' : 'var(--accent-red)'}">
            ${isConfigured ? 'ACTIVA' : 'PENDIENTE'}
          </span>
        </div>

        <div class="form-group">
          <label class="form-label">API Key de Freepik</label>
          <input type="password" id="freepik-key" class="form-input" value="${currentKey}" placeholder="fpk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx" />
          <p class="text-xs text-muted mt-sm">
            Obtén tu key gratis (incluye $5 en créditos): 
            <a href="https://www.freepik.com/developers/dashboard/api-key" target="_blank" style="color:var(--accent-purple-light);text-decoration:underline">freepik.com/developers →</a>
          </p>
        </div>

        <div class="flex gap-md">
          <button id="btn-save-key" class="btn btn-primary">💾 Guardar Key</button>
          <button id="btn-test-key" class="btn btn-secondary">🔌 Test Conexión</button>
        </div>

        <div id="key-test-result" class="mt-md" style="display:none"></div>
      </div>

      <!-- How to get API Key -->
      <div class="card mb-lg">
        <h3 class="mb-lg">📖 Cómo obtener tu API Key de Freepik</h3>
        <div class="flex flex-col gap-md">
          <div class="flex gap-md items-center">
            <div class="chip purple" style="min-width:28px;justify-content:center">1</div>
            <p class="text-sm">Ve a <a href="https://www.freepik.com/api" target="_blank" style="color:var(--accent-purple-light);text-decoration:underline">freepik.com/api</a> y regístrate (gratis)</p>
          </div>
          <div class="flex gap-md items-center">
            <div class="chip purple" style="min-width:28px;justify-content:center">2</div>
            <p class="text-sm">Accede al <a href="https://www.freepik.com/developers/dashboard" target="_blank" style="color:var(--accent-purple-light);text-decoration:underline">Developer Dashboard</a></p>
          </div>
          <div class="flex gap-md items-center">
            <div class="chip purple" style="min-width:28px;justify-content:center">3</div>
            <p class="text-sm">Haz clic en <strong>"Generate API Key"</strong> y cópiala</p>
          </div>
          <div class="flex gap-md items-center">
            <div class="chip purple" style="min-width:28px;justify-content:center">4</div>
            <p class="text-sm">Pega la key arriba ↑ y pulsa <strong>"Guardar"</strong></p>
          </div>
          <div class="flex gap-md items-center">
            <div class="chip green" style="min-width:28px;justify-content:center">✓</div>
            <p class="text-sm"><strong>Recibes $5 en créditos gratis</strong> para empezar a generar</p>
          </div>
        </div>
      </div>

      <!-- Pricing Info -->
      <div class="card mb-lg">
        <h3 class="mb-lg">💰 Costes de la API de Freepik</h3>
        <div class="flex flex-col gap-sm">
          <div class="flex justify-between items-center" style="padding:var(--space-sm) 0;border-bottom:1px solid var(--border-subtle)">
            <span class="text-sm">🖼️ Imagen (Mystic)</span>
            <span class="text-sm font-bold text-accent">~$0.04 / imagen</span>
          </div>
          <div class="flex justify-between items-center" style="padding:var(--space-sm) 0;border-bottom:1px solid var(--border-subtle)">
            <span class="text-sm">🎬 Vídeo (Kling Pro v2.1)</span>
            <span class="text-sm font-bold text-accent">~$0.40 / 5s vídeo</span>
          </div>
          <div class="flex justify-between items-center" style="padding:var(--space-sm) 0;border-bottom:1px solid var(--border-subtle)">
            <span class="text-sm">🔍 Upscaler (4K)</span>
            <span class="text-sm font-bold text-accent">~$0.08 / imagen</span>
          </div>
          <div class="flex justify-between items-center" style="padding:var(--space-sm) 0">
            <span class="text-sm">🗣️ Lip Sync</span>
            <span class="text-sm font-bold text-accent">Consultar precios</span>
          </div>
        </div>
        <p class="text-xs text-muted mt-md">Precios aproximados. Consulta <a href="https://docs.freepik.com/pricing" target="_blank" style="color:var(--accent-purple-light)">docs.freepik.com/pricing</a> para info actualizada.</p>
      </div>

      <!-- Optional APIs -->
      <div class="card mb-lg">
        <h3 class="mb-lg">🔌 APIs opcionales (avanzado)</h3>
        <p class="text-sm text-muted mb-lg">Estas APIs son opcionales. El hub funciona perfectamente solo con Freepik.</p>

        <div class="form-group">
          <label class="form-label">HeyGen API Key (Lip-sync avanzado)</label>
          <input type="password" id="heygen-key" class="form-input" value="${settings.heygenKey || ''}" placeholder="Opcional — para lip-sync avanzado" />
          <p class="text-xs text-muted mt-sm">
            <a href="https://www.heygen.com" target="_blank" style="color:var(--accent-purple-light)">heygen.com →</a>
          </p>
        </div>

        <div class="form-group">
          <label class="form-label">D-ID API Key (Avatares parlantes)</label>
          <input type="password" id="did-key" class="form-input" value="${settings.didKey || ''}" placeholder="Opcional — alternativa para lip-sync" />
          <p class="text-xs text-muted mt-sm">
            <a href="https://www.d-id.com" target="_blank" style="color:var(--accent-purple-light)">d-id.com →</a>
          </p>
        </div>

        <button id="btn-save-optional" class="btn btn-secondary">💾 Guardar APIs opcionales</button>
      </div>

      <!-- Danger Zone -->
      <div class="card" style="border-color:rgba(239,68,68,0.2)">
        <h3 class="mb-md" style="color:var(--accent-red)">⚠️ Zona de peligro</h3>
        <p class="text-sm text-muted mb-lg">Estas acciones son irreversibles.</p>
        <div class="flex gap-md">
          <button id="btn-clear-data" class="btn btn-secondary" style="border-color:rgba(239,68,68,0.3);color:var(--accent-red)">🗑️ Borrar todos los datos</button>
          <button id="btn-clear-keys" class="btn btn-secondary" style="border-color:rgba(239,68,68,0.3);color:var(--accent-red)">🔓 Borrar API Keys</button>
        </div>
      </div>
    </div>
  `;
}

export function initSettings() {
    // Save Freepik key
    document.getElementById('btn-save-key')?.addEventListener('click', () => {
        const key = document.getElementById('freepik-key')?.value?.trim();
        if (!key) {
            window.__showToast?.('Introduce una API key', 'error');
            return;
        }
        freepikAPI.setApiKey(key);
        window.__updateApiStatus?.();
        window.__showToast?.('API Key guardada ✓', 'success');
        window.__navigate?.('settings');
    });

    // Test connection
    document.getElementById('btn-test-key')?.addEventListener('click', async () => {
        const resultEl = document.getElementById('key-test-result');
        const btn = document.getElementById('btn-test-key');
        resultEl.style.display = 'block';
        resultEl.innerHTML = `<div class="flex items-center gap-sm"><div class="spinner"></div><span class="text-sm">Probando conexión...</span></div>`;
        btn.disabled = true;

        const result = await freepikAPI.testConnection();

        resultEl.innerHTML = `
      <div style="padding:var(--space-md);border-radius:var(--radius-md);background:${result.success ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)'};border:1px solid ${result.success ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}">
        <p class="text-sm" style="color:${result.success ? 'var(--accent-green)' : 'var(--accent-red)'}">${result.message}</p>
      </div>
    `;
        btn.disabled = false;

        if (result.success) {
            window.__updateApiStatus?.();
        }
    });

    // Save optional APIs
    document.getElementById('btn-save-optional')?.addEventListener('click', () => {
        saveSettings({
            heygenKey: document.getElementById('heygen-key')?.value?.trim(),
            didKey: document.getElementById('did-key')?.value?.trim(),
        });
        window.__showToast?.('APIs opcionales guardadas', 'success');
    });

    // Clear data
    document.getElementById('btn-clear-data')?.addEventListener('click', () => {
        if (confirm('¿Seguro? Se borrarán TODOS los avatares, guiones y vídeos guardados.')) {
            ['ugc_hub_avatars', 'ugc_hub_scripts', 'ugc_hub_videos', 'ugc_hub_projects'].forEach(k => localStorage.removeItem(k));
            window.__showToast?.('Todos los datos borrados', 'info');
            window.__navigate?.('settings');
        }
    });

    // Clear keys
    document.getElementById('btn-clear-keys')?.addEventListener('click', () => {
        if (confirm('¿Seguro? Se borrarán TODAS las API keys.')) {
            localStorage.removeItem('freepik_api_key');
            localStorage.removeItem('ugc_hub_settings');
            freepikAPI.setApiKey('');
            window.__updateApiStatus?.();
            window.__showToast?.('API Keys borradas', 'info');
            window.__navigate?.('settings');
        }
    });
}
