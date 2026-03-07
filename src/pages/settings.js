// ═══════════════════════════════════════════════
// Settings Page — API keys config
// ═══════════════════════════════════════════════
import { storage } from '../services/storage.js';
import { freepikApi } from '../services/freepik-api.js';

export function renderSettings(container) {
  const currentKey = storage.getFreepikKey();
  const stats = storage.getStats();

  container.innerHTML = `
    <div class="page-header">
      <h2>⚙️ Configuración</h2>
      <p>API keys y ajustes del sistema</p>
    </div>

    <div style="max-width:600px;">
      <!-- API Keys Panel -->
      <div class="card" style="margin-bottom:20px;">
        <h3 style="font-weight:700; margin-bottom:20px;">🔑 Claves de API</h3>

        <div class="input-group">
          <label>🎨 Freepik API (Premium+ Mystic)</label>
          <input type="password" id="freepik-key" value="${currentKey}" placeholder="fpk_XXXXXX...">
        </div>

        <div class="input-group" style="margin-top:16px;">
          <label>🤖 Google Gemini API (3.1 Pro / Ultra)</label>
          <input type="password" id="gemini-key" value="${storage.getGeminiKey()}" placeholder="AIzaSy...">
          <p style="font-size:12px; color:var(--text-muted); margin-top:4px;">Para generar estructura y síntesis de guiones.</p>
        </div>

        <div class="input-group" style="margin-top:16px;">
          <label>🔎 Perplexity API (Enterprise Pro / Sonar)</label>
          <input type="password" id="perplexity-key" value="${storage.getPerplexityKey()}" placeholder="pplx-XXXXXX...">
          <p style="font-size:12px; color:var(--text-muted); margin-top:4px;">Para investigación profunda en foros (Reddit, etc) de tu nicho en tiempo real.</p>
        </div>

        <div class="flex gap-8 mt-24">
          <button class="btn btn-primary" id="save-key-btn">💾 Guardar APIs</button>
          <button class="btn btn-secondary" id="test-key-btn">🔌 Test Freepik</button>
        </div>

        <div id="key-status" style="margin-top:12px; display:none;"></div>
      </div>

      <!-- Data Management -->
      <div class="card" style="margin-bottom:20px;">
        <h3 style="font-weight:700; margin-bottom:20px;">📊 Datos Locales</h3>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">
          <div style="padding:12px; background:var(--bg-secondary); border-radius:var(--radius-sm);">
            <div style="font-size:20px; font-weight:800;">${stats.avatars}</div>
            <div style="font-size:12px; color:var(--text-muted);">Avatares</div>
          </div>
          <div style="padding:12px; background:var(--bg-secondary); border-radius:var(--radius-sm);">
            <div style="font-size:20px; font-weight:800;">${stats.scripts}</div>
            <div style="font-size:12px; color:var(--text-muted);">Guiones</div>
          </div>
          <div style="padding:12px; background:var(--bg-secondary); border-radius:var(--radius-sm);">
            <div style="font-size:20px; font-weight:800;">${stats.videos}</div>
            <div style="font-size:12px; color:var(--text-muted);">Vídeos</div>
          </div>
          <div style="padding:12px; background:var(--bg-secondary); border-radius:var(--radius-sm);">
            <div style="font-size:20px; font-weight:800;">${stats.ads}</div>
            <div style="font-size:12px; color:var(--text-muted);">Anuncios</div>
          </div>
        </div>
        <button class="btn btn-danger" id="clear-btn">🗑️ Borrar todos los datos</button>
      </div>

      <!-- Info -->
      <div class="card" style="border-left:3px solid var(--accent);">
        <h4 style="font-weight:700; margin-bottom:8px;">ℹ️ Sobre el Hub</h4>
        <p style="font-size:14px; color:var(--text-secondary); line-height:1.6;">
          <strong>SISTEMA180 UGC Avatar Hub</strong> — Fábrica de contenido viral con IA.<br>
          Método Víctor Heras (UMV) + Freepik Mystic para avatares 4K.<br><br>
          Los datos se guardan localmente en tu navegador.<br>
          Las API keys nunca se envían a servidores de terceros.
        </p>
      </div>
    </div>
  `;

  // Save key
  container.querySelector('#save-key-btn').addEventListener('click', () => {
    const fpKey = container.querySelector('#freepik-key').value.trim();
    const geminiKey = container.querySelector('#gemini-key').value.trim();
    const pplxKey = container.querySelector('#perplexity-key').value.trim();

    storage.setFreepikKey(fpKey);
    storage.setGeminiKey(geminiKey);
    storage.setPerplexityKey(pplxKey);

    const status = container.querySelector('#key-status');
    status.style.display = 'block';
    status.innerHTML = '<span class="tag tag-green">✅ API keys guardadas</span>';
  });

  // Test connection
  container.querySelector('#test-key-btn').addEventListener('click', async () => {
    const status = container.querySelector('#key-status');
    status.style.display = 'block';
    status.innerHTML = '<div class="spinner" style="display:inline-block;"></div> <span style="margin-left:8px; color:var(--text-muted);">Testeando conexión...</span>';

    const result = await freepikApi.testConnection();
    if (result.ok) {
      status.innerHTML = '<span class="tag tag-green">✅ Conexión OK — Freepik Premium+ activa</span>';
    } else {
      status.innerHTML = `<span class="tag tag-red">❌ Error: ${result.error || 'Status ' + result.status}</span>`;
    }
  });

  // Clear data
  container.querySelector('#clear-btn').addEventListener('click', () => {
    if (confirm('¿Borrar todos los avatares, guiones y datos? Esta acción no se puede deshacer.')) {
      localStorage.clear();
      renderSettings(container);
    }
  });
}
