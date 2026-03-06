import { generateScript, getFormats, getTones } from '../services/script-ai.js';
import { saveScript, getScripts, deleteScript } from '../services/storage.js';

let currentScript = null;

export function renderScripts() {
    const formats = getFormats();
    const tones = getTones();
    const savedScripts = getScripts();

    return `
    <div class="page-header">
      <h1>📝 Generador de <span class="gradient-text">Guiones IA</span></h1>
      <p>Crea guiones UGC profesionales al instante. Solo rellena los datos de tu producto y la IA hace el resto.</p>
    </div>

    <div class="grid-2" style="grid-template-columns: 1fr 1fr; align-items: start;">
      <!-- Form -->
      <div class="card" style="position:sticky;top:var(--space-xl)">
        <h3 class="mb-lg">🎯 Datos del producto</h3>

        <div class="form-group">
          <label class="form-label">Producto / Servicio *</label>
          <input type="text" id="script-product" class="form-input" placeholder="Ej: Sérum facial vitamina C" />
        </div>

        <div class="form-group">
          <label class="form-label">Beneficio principal *</label>
          <input type="text" id="script-benefit" class="form-input" placeholder="Ej: mi piel se ve más luminosa" />
        </div>

        <div class="form-group">
          <label class="form-label">Ventaja principal *</label>
          <input type="text" id="script-advantage" class="form-input" placeholder="Ej: es 100% natural y cruelty-free" />
        </div>

        <div class="form-group">
          <label class="form-label">Ventaja extra (opcional)</label>
          <input type="text" id="script-advantage-extra" class="form-input" placeholder="Ej: envío gratis en 24h" />
        </div>

        <div class="form-group">
          <label class="form-label">Necesidad del cliente</label>
          <input type="text" id="script-need" class="form-input" placeholder="Ej: mejorar vuestra rutina de skincare" />
        </div>

        <div class="form-group">
          <label class="form-label">Tiempo de uso</label>
          <input type="text" id="script-time" class="form-input" placeholder="Ej: 3 semanas" value="unas semanas" />
        </div>

        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Formato</label>
            <select id="script-format" class="form-select">
              ${formats.map(f => `<option value="${f.id}">${f.label}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Tono</label>
            <select id="script-tone" class="form-select">
              ${tones.map(t => `<option value="${t.id}" ${t.id === 'casual' ? 'selected' : ''}>${t.label}</option>`).join('')}
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Idioma</label>
          <select id="script-lang" class="form-select">
            <option value="es">🇪🇸 Español</option>
            <option value="en">🇬🇧 English</option>
          </select>
        </div>

        <button id="btn-generate-script" class="btn btn-primary btn-lg" style="width:100%">
          ✨ Generar Guion
        </button>
      </div>

      <!-- Output -->
      <div>
        <!-- Preview -->
        <div class="card mb-lg" id="script-preview-card">
          <div class="flex justify-between items-center mb-lg">
            <h3>📄 Vista previa</h3>
            <div class="flex gap-sm" id="script-actions" style="display:none">
              <button class="btn btn-ghost" id="btn-copy-script" title="Copiar">📋 Copiar</button>
              <button class="btn btn-ghost" id="btn-save-script" title="Guardar">💾 Guardar</button>
              <button class="btn btn-ghost" id="btn-regen-script" title="Regenerar">🔄 Otro</button>
            </div>
          </div>

          <div id="script-output">
            <div class="empty-state">
              <div class="empty-icon">📝</div>
              <h3>Tu guion aparecerá aquí</h3>
              <p>Rellena los datos de tu producto y pulsa "Generar Guion"</p>
            </div>
          </div>

          <div id="script-meta" class="flex gap-md mt-lg" style="display:none">
            <span class="chip purple" id="meta-words"></span>
            <span class="chip cyan" id="meta-duration"></span>
            <span class="chip green" id="meta-format"></span>
          </div>
        </div>

        <!-- Saved Scripts -->
        ${savedScripts.length > 0 ? `
          <h3 class="mb-md">💾 Guiones guardados (${savedScripts.length})</h3>
          <div class="flex flex-col gap-md">
            ${savedScripts.map(s => `
              <div class="card" style="cursor:default">
                <div class="flex justify-between items-center mb-sm">
                  <div class="flex gap-sm items-center">
                    <span class="chip ${s.tone === 'casual' ? 'cyan' : s.tone === 'urgent' ? 'pink' : 'purple'}">${s.tone}</span>
                    <span class="chip green">${s.format}</span>
                    <span class="text-xs text-muted">${s.wordCount} palabras · ~${s.estimatedDuration}s</span>
                  </div>
                  <div class="flex gap-sm">
                    <button class="btn btn-ghost btn-copy-saved" data-text="${encodeURIComponent(s.text)}">📋</button>
                    <button class="btn btn-ghost btn-delete-script" data-id="${s.id}">🗑️</button>
                  </div>
                </div>
                <p class="text-sm" style="white-space:pre-wrap;max-height:120px;overflow:hidden;color:var(--text-secondary)">${s.text}</p>
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

export function initScripts() {
    const btnGenerate = document.getElementById('btn-generate-script');
    const btnCopy = document.getElementById('btn-copy-script');
    const btnSave = document.getElementById('btn-save-script');
    const btnRegen = document.getElementById('btn-regen-script');

    btnGenerate?.addEventListener('click', handleGenerate);
    btnCopy?.addEventListener('click', handleCopy);
    btnSave?.addEventListener('click', handleSave);
    btnRegen?.addEventListener('click', handleGenerate);

    // Saved script actions
    document.querySelectorAll('.btn-copy-saved').forEach(btn => {
        btn.addEventListener('click', () => {
            const text = decodeURIComponent(btn.dataset.text);
            navigator.clipboard.writeText(text);
            window.__showToast?.('Guion copiado al portapapeles', 'success');
        });
    });

    document.querySelectorAll('.btn-delete-script').forEach(btn => {
        btn.addEventListener('click', () => {
            deleteScript(btn.dataset.id);
            window.__navigate?.('scripts');
        });
    });
}

function handleGenerate() {
    const config = {
        product: document.getElementById('script-product')?.value,
        benefit: document.getElementById('script-benefit')?.value,
        mainAdvantage: document.getElementById('script-advantage')?.value,
        extraAdvantage: document.getElementById('script-advantage-extra')?.value,
        need: document.getElementById('script-need')?.value,
        timeUsed: document.getElementById('script-time')?.value,
        format: document.getElementById('script-format')?.value,
        tone: document.getElementById('script-tone')?.value,
        language: document.getElementById('script-lang')?.value,
    };

    if (!config.product) {
        window.__showToast?.('Introduce el nombre del producto', 'error');
        return;
    }

    currentScript = generateScript(config);

    // Show output
    const output = document.getElementById('script-output');
    output.innerHTML = `<p style="white-space:pre-wrap;line-height:1.8;font-size:var(--font-size-md)">${currentScript.text}</p>`;

    // Show actions & meta
    document.getElementById('script-actions').style.display = 'flex';
    document.getElementById('script-meta').style.display = 'flex';
    document.getElementById('meta-words').textContent = `${currentScript.wordCount} palabras`;
    document.getElementById('meta-duration').textContent = `~${currentScript.estimatedDuration}s de lectura`;
    document.getElementById('meta-format').textContent = currentScript.format;

    window.__showToast?.('¡Guion generado!', 'success');
}

function handleCopy() {
    if (currentScript) {
        navigator.clipboard.writeText(currentScript.text);
        window.__showToast?.('Copiado al portapapeles', 'success');
    }
}

function handleSave() {
    if (currentScript) {
        saveScript(currentScript);
        window.__showToast?.('Guion guardado', 'success');
        window.__navigate?.('scripts'); // refresh
    }
}
