// ═══════════════════════════════════════════════
// VideoForge Pro — Editor Page (Integrated into SPA)
// ═══════════════════════════════════════════════
import { storage } from '../services/storage.js';

// ─── VideoForge Backend URL ───────────────────
function getVideoForgeURL() {
    return storage.get('videoforge_url') || 'http://localhost:5000';
}

// ─── Preset Category Config ──────────────────
const CATEGORY_LABELS = {
    god_mode: '🔥 God Mode',
    creator: '🎯 Creadores',
    platform: '📱 Plataformas',
    quick: '⚡ Rápidos',
};
const CATEGORY_ORDER = ['god_mode', 'creator', 'platform', 'quick'];

// ─── State ───────────────────────────────────
let editorState = {
    jobId: null,
    selectedPreset: null,
    selectedPresetName: null,
    file: null,
    polling: null,
};

function resetState() {
    if (editorState.polling) clearInterval(editorState.polling);
    editorState = { jobId: null, selectedPreset: null, selectedPresetName: null, file: null, polling: null };
}

// ═══════════════════════════════════════════════
// RENDER
// ═══════════════════════════════════════════════
export function renderEditor(container) {
    resetState();
    const API = getVideoForgeURL();

    container.innerHTML = `
    <div class="page-header">
      <div class="vf-header-row">
        <div>
          <h2 class="vf-title">
            <span class="vf-logo-icon">🎬</span>
            VideoForge <span class="vf-accent">Pro</span>
          </h2>
          <p>Editor profesional de vídeo con IA — 12 presets, motor GPU integrado</p>
        </div>
        <div class="vf-header-badge">✦ PRO</div>
      </div>
    </div>

    <!-- Connection Status -->
    <div class="vf-connection" id="vfConnection">
      <span class="vf-conn-dot" id="vfConnDot"></span>
      <span id="vfConnText">Conectando a VideoForge...</span>
      <span class="vf-conn-url">${API}</span>
    </div>

    <!-- Upload Zone -->
    <div class="vf-upload-zone" id="vfUploadZone">
      <div class="vf-upload-icon">📁</div>
      <h3>Arrastra tu vídeo aquí</h3>
      <p>o haz clic para seleccionar — MP4, MOV, AVI, MKV, WebM</p>
      <button class="vf-upload-btn" id="vfBtnSelectFile">Seleccionar archivo</button>
      <input type="file" id="vfFileInput" accept="video/*" hidden>
    </div>

    <!-- Video Preview -->
    <div class="vf-video-preview" id="vfVideoPreview">
      <video id="vfPreviewPlayer" controls></video>
      <div class="vf-file-info" id="vfFileInfo"></div>
    </div>

    <!-- Presets Section -->
    <div class="vf-presets-section" id="vfPresetsSection">
      <div class="vf-section-header">
        <h3 class="vf-section-title">Elige tu estilo</h3>
        <p class="vf-section-subtitle">12 presets profesionales con motor GPU integrado</p>
      </div>
      <div id="vfPresetsContainer"></div>
    </div>

    <!-- Action Bar -->
    <div class="vf-action-bar" id="vfActionBar">
      <div class="vf-action-info">
        <span class="vf-action-preset" id="vfSelectedPresetName"></span>
        <span class="vf-action-file" id="vfSelectedFileName"></span>
      </div>
      <button class="vf-btn-process" id="vfBtnProcess">
        <span class="vf-btn-icon">✦</span> Editar vídeo
      </button>
    </div>

    <!-- Progress Section -->
    <div class="vf-progress-section" id="vfProgressSection">
      <div class="vf-progress-ring">
        <svg viewBox="0 0 120 120">
          <circle class="vf-progress-bg" cx="60" cy="60" r="54"/>
          <circle class="vf-progress-bar" cx="60" cy="60" r="54" id="vfProgressCircle"/>
        </svg>
        <span class="vf-progress-pct" id="vfProgressPct">0%</span>
      </div>
      <p class="vf-progress-msg" id="vfProgressMsg">Iniciando...</p>
      <div class="vf-progress-steps" id="vfProgressSteps"></div>
    </div>

    <!-- Result Section -->
    <div class="vf-result-section" id="vfResultSection">
      <div id="vfResultIcon"></div>
      <h2 id="vfResultTitle"></h2>
      <p class="vf-result-msg" id="vfResultMsg"></p>
      <div id="vfResultActions"></div>
    </div>
    `;

    // ─── Element References ────────────────────
    const els = {
        connection: container.querySelector('#vfConnection'),
        connDot: container.querySelector('#vfConnDot'),
        connText: container.querySelector('#vfConnText'),
        uploadZone: container.querySelector('#vfUploadZone'),
        fileInput: container.querySelector('#vfFileInput'),
        videoPreview: container.querySelector('#vfVideoPreview'),
        previewPlayer: container.querySelector('#vfPreviewPlayer'),
        fileInfo: container.querySelector('#vfFileInfo'),
        presetsSection: container.querySelector('#vfPresetsSection'),
        presetsContainer: container.querySelector('#vfPresetsContainer'),
        actionBar: container.querySelector('#vfActionBar'),
        selectedPresetName: container.querySelector('#vfSelectedPresetName'),
        selectedFileName: container.querySelector('#vfSelectedFileName'),
        btnProcess: container.querySelector('#vfBtnProcess'),
        progressSection: container.querySelector('#vfProgressSection'),
        progressPct: container.querySelector('#vfProgressPct'),
        progressCircle: container.querySelector('#vfProgressCircle'),
        progressMsg: container.querySelector('#vfProgressMsg'),
        progressSteps: container.querySelector('#vfProgressSteps'),
        resultSection: container.querySelector('#vfResultSection'),
        resultIcon: container.querySelector('#vfResultIcon'),
        resultTitle: container.querySelector('#vfResultTitle'),
        resultMsg: container.querySelector('#vfResultMsg'),
        resultActions: container.querySelector('#vfResultActions'),
    };

    // ─── SVG Progress Circle Setup ─────────────
    const circumference = 2 * Math.PI * 54;
    els.progressCircle.style.strokeDasharray = circumference;
    els.progressCircle.style.strokeDashoffset = circumference;

    function setProgressCircle(pct) {
        const offset = circumference - (pct / 100) * circumference;
        els.progressCircle.style.strokeDashoffset = offset;
    }

    // ─── Check Connection ──────────────────────
    async function checkConnection() {
        try {
            const res = await fetch(`${API}/api/presets`, { signal: AbortSignal.timeout(5000) });
            if (res.ok) {
                els.connDot.classList.add('connected');
                els.connText.textContent = 'VideoForge Pro conectado';
                const presets = await res.json();
                renderPresets(presets);
                return true;
            }
        } catch (e) { /* ignore */ }
        els.connDot.classList.add('disconnected');
        els.connText.textContent = 'VideoForge Pro no disponible — arranca el servidor (python server.py)';
        return false;
    }

    // ─── Render Presets ────────────────────────
    function renderPresets(presets) {
        els.presetsContainer.innerHTML = '';
        const groups = {};
        for (const [key, preset] of Object.entries(presets)) {
            const cat = preset.category || 'platform';
            if (!groups[cat]) groups[cat] = [];
            groups[cat].push({ key, ...preset });
        }

        for (const cat of CATEGORY_ORDER) {
            if (!groups[cat] || groups[cat].length === 0) continue;

            const label = document.createElement('div');
            label.className = 'vf-category-label';
            label.textContent = CATEGORY_LABELS[cat] || cat;
            els.presetsContainer.appendChild(label);

            const grid = document.createElement('div');
            grid.className = 'vf-presets-grid';

            for (const p of groups[cat]) {
                const card = document.createElement('div');
                card.className = 'vf-preset-card';
                card.dataset.preset = p.key;

                const tags = (p.tags || []).map(t =>
                    `<span class="vf-preset-tag">${t}</span>`
                ).join('');

                card.innerHTML = `
                    <div class="vf-preset-content">
                        <span class="vf-preset-icon">${p.icon || '🎬'}</span>
                        <div class="vf-preset-name">${p.name}</div>
                        <div class="vf-preset-desc">${p.description}</div>
                        <div class="vf-preset-tags">${tags}</div>
                    </div>
                `;

                card.addEventListener('click', () => selectPreset(p.key, p.name, card));
                grid.appendChild(card);
            }
            els.presetsContainer.appendChild(grid);
        }
    }

    // ─── Select Preset ─────────────────────────
    function selectPreset(key, name, cardEl) {
        editorState.selectedPreset = key;
        editorState.selectedPresetName = name;
        container.querySelectorAll('.vf-preset-card').forEach(c => c.classList.remove('selected'));
        cardEl.classList.add('selected');
        els.selectedPresetName.textContent = name;
        updateActionBar();
    }

    // ─── Action Bar ────────────────────────────
    function updateActionBar() {
        if (editorState.file && editorState.selectedPreset) {
            els.actionBar.classList.add('active');
        }
    }

    // ─── Format File Size ──────────────────────
    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
        return (bytes / 1073741824).toFixed(2) + ' GB';
    }

    // ─── File Handling ─────────────────────────
    function handleFile(file) {
        const validExts = /\.(mp4|mov|avi|mkv|webm)$/i;
        const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm', 'video/x-matroska'];
        if (!validTypes.includes(file.type) && !file.name.match(validExts)) {
            showToast('⚠️ Formato no soportado. Usa MP4, MOV, AVI, MKV o WebM.', 'error');
            return;
        }

        editorState.file = file;

        // Preview
        const url = URL.createObjectURL(file);
        els.previewPlayer.src = url;
        els.videoPreview.classList.add('active');
        els.uploadZone.style.display = 'none';
        els.fileInfo.textContent = `${file.name} — ${formatSize(file.size)}`;
        els.selectedFileName.textContent = file.name;

        // Show presets
        els.presetsSection.classList.add('active');
        updateActionBar();
    }

    // Upload zone events
    container.querySelector('#vfBtnSelectFile').addEventListener('click', (e) => {
        e.stopPropagation();
        els.fileInput.click();
    });
    els.uploadZone.addEventListener('click', () => els.fileInput.click());
    els.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        els.uploadZone.classList.add('drag-over');
    });
    els.uploadZone.addEventListener('dragleave', () => {
        els.uploadZone.classList.remove('drag-over');
    });
    els.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        els.uploadZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });
    els.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    // ─── Progress ──────────────────────────────
    function updateProgress(pct, msg) {
        els.progressPct.textContent = `${pct}%`;
        els.progressMsg.textContent = msg;
        setProgressCircle(pct);
    }

    function addProgressStep(msg, status = 'done') {
        const icon = status === 'done' ? '✅' : status === 'active' ? '⏳' : '⬜';
        const step = document.createElement('div');
        step.className = `vf-step ${status}`;
        step.innerHTML = `<span>${icon}</span> <span>${msg}</span>`;
        els.progressSteps.appendChild(step);
        els.progressSteps.scrollTop = els.progressSteps.scrollHeight;
    }

    function startPolling() {
        let lastMsg = '';
        editorState.polling = setInterval(async () => {
            try {
                const res = await fetch(`${API}/api/status/${editorState.jobId}`);
                if (!res.ok) return;
                const data = await res.json();

                updateProgress(data.progress || 0, data.message || 'Procesando...');

                if (data.message && data.message !== lastMsg) {
                    addProgressStep(data.message, 'done');
                    lastMsg = data.message;
                }

                if (data.status === 'done') {
                    clearInterval(editorState.polling);
                    showResult(true);
                } else if (data.status === 'error') {
                    clearInterval(editorState.polling);
                    showResult(false, data.error || data.message);
                }
            } catch (e) {
                console.error('Polling error:', e);
            }
        }, 1500);
    }

    // ─── Process ───────────────────────────────
    els.btnProcess.addEventListener('click', async () => {
        if (!editorState.file || !editorState.selectedPreset) return;

        // Switch to progress view
        els.actionBar.classList.remove('active');
        els.presetsSection.classList.remove('active');
        els.videoPreview.classList.remove('active');
        els.progressSection.classList.add('active');
        els.progressSteps.innerHTML = '';
        updateProgress(5, 'Subiendo vídeo...');
        addProgressStep('Subiendo vídeo al servidor...', 'active');

        try {
            // Upload
            const formData = new FormData();
            formData.append('video', editorState.file);

            const uploadRes = await fetch(`${API}/api/upload`, {
                method: 'POST',
                body: formData
            });

            if (!uploadRes.ok) throw new Error('Error al subir el vídeo');

            const ct = uploadRes.headers.get('content-type') || '';
            if (!ct.includes('application/json')) throw new Error('Servidor no responde correctamente.');

            const uploadData = await uploadRes.json();
            editorState.jobId = uploadData.job_id;
            addProgressStep(`Vídeo subido (${formatSize(editorState.file.size)})`, 'done');
            updateProgress(15, 'Vídeo subido. Iniciando edición...');

            // Start processing
            const processRes = await fetch(`${API}/api/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_id: editorState.jobId,
                    preset: editorState.selectedPreset,
                })
            });

            if (!processRes.ok) {
                const err = await processRes.json().catch(() => ({}));
                throw new Error(err.error || 'Error al iniciar el procesamiento');
            }

            addProgressStep(`Preset: ${editorState.selectedPresetName}`, 'done');
            updateProgress(20, '⚡ Motor Pro procesando...');
            startPolling();

        } catch (e) {
            showResult(false, e.message);
        }
    });

    // ─── Result ────────────────────────────────
    function showResult(success, errorMsg) {
        els.progressSection.classList.remove('active');
        els.resultSection.classList.add('active');

        if (success) {
            els.resultIcon.innerHTML = '<div class="vf-result-success">✅</div>';
            els.resultTitle.textContent = '¡Edición completada!';
            els.resultMsg.textContent = `Preset: ${editorState.selectedPresetName}`;
            els.resultActions.innerHTML = `
                <a class="vf-btn-download" href="${API}/api/download/${editorState.jobId}" download>
                    📥 Descargar vídeo
                </a>
                <button class="vf-btn-secondary" id="vfBtnNew">
                    🔄 Editar otro vídeo
                </button>
            `;
            container.querySelector('#vfBtnNew').addEventListener('click', resetToUpload);
        } else {
            els.resultIcon.innerHTML = '<div class="vf-result-error">❌</div>';
            els.resultTitle.textContent = 'Error en el procesamiento';
            els.resultMsg.textContent = errorMsg || 'Error desconocido';
            els.resultActions.innerHTML = `
                <button class="vf-btn-secondary" id="vfBtnRetry">
                    🔄 Volver a intentar
                </button>
            `;
            container.querySelector('#vfBtnRetry').addEventListener('click', resetToUpload);
        }
    }

    // ─── Reset ─────────────────────────────────
    function resetToUpload() {
        resetState();
        els.resultSection.classList.remove('active');
        els.progressSection.classList.remove('active');
        els.presetsSection.classList.remove('active');
        els.actionBar.classList.remove('active');
        els.videoPreview.classList.remove('active');
        els.uploadZone.style.display = '';
        els.fileInput.value = '';
        els.previewPlayer.src = '';
        container.querySelectorAll('.vf-preset-card').forEach(c => c.classList.remove('selected'));
        // Re-check connection and reload presets
        checkConnection();
    }

    // ─── Toast ─────────────────────────────────
    function showToast(msg, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `vf-toast ${type}`;
        toast.textContent = msg;
        container.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('show'));
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ─── Init ──────────────────────────────────
    checkConnection();
}
