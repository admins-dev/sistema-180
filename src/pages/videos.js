import { freepikAPI } from '../services/freepik-api.js';
import { getAvatars, getScripts, saveVideo, getVideos } from '../services/storage.js';

export function renderVideos() {
    const avatars = getAvatars();
    const scripts = getScripts();
    const videos = getVideos();
    const isConfigured = freepikAPI.isConfigured();

    return `
    <div class="page-header">
      <h1>🎬 Generador de <span class="gradient-text">Vídeos UGC</span></h1>
      <p>Combina tu avatar + guion para crear vídeos UGC ultrarrealistas. Anima tu avatar con Freepik AI (Kling Pro v2.1).</p>
    </div>

    ${!isConfigured ? `
      <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:var(--radius-md);padding:var(--space-lg);margin-bottom:var(--space-xl)">
        <p class="text-sm" style="color:var(--accent-red)">⚠️ API Key no configurada. <a href="#settings" data-page="settings" style="color:var(--accent-purple-light);text-decoration:underline">Configurar ahora →</a></p>
      </div>
    ` : ''}

    <div class="grid-2" style="grid-template-columns:1fr 1fr;align-items:start">
      <!-- Create Video -->
      <div class="card" style="position:sticky;top:var(--space-xl)">
        <h3 class="mb-lg">🎥 Crear nuevo vídeo</h3>

        <!-- Step 1: Select Avatar -->
        <div class="form-group">
          <label class="form-label">1️⃣ Selecciona un Avatar</label>
          ${avatars.length > 0 ? `
            <div class="flex gap-md flex-wrap" id="avatar-selector">
              ${avatars.map(a => `
                <div class="avatar-select-item" data-url="${a.imageUrl}" data-name="${a.name}" style="cursor:pointer;border:2px solid var(--border-subtle);border-radius:var(--radius-md);overflow:hidden;width:80px;height:80px;transition:all var(--transition-fast)">
                  <img src="${a.imageUrl}" alt="${a.name}" style="width:100%;height:100%;object-fit:cover" />
                </div>
              `).join('')}
            </div>
          ` : `
            <p class="text-sm text-muted">No tienes avatares. <a href="#avatars" data-page="avatars" style="color:var(--accent-purple-light)">Crea uno primero →</a></p>
          `}
        </div>

        <!-- Step 2: Select Script -->
        <div class="form-group">
          <label class="form-label">2️⃣ Selecciona un Guion (texto para overlay)</label>
          ${scripts.length > 0 ? `
            <select id="video-script" class="form-select">
              <option value="">Sin guion</option>
              ${scripts.map(s => `
                <option value="${s.id}">${s.text.substring(0, 60)}... (${s.tone}/${s.format})</option>
              `).join('')}
            </select>
          ` : `
            <p class="text-sm text-muted">No tienes guiones. <a href="#scripts" data-page="scripts" style="color:var(--accent-purple-light)">Genera uno →</a></p>
          `}
        </div>

        <!-- Step 3: Motion Prompt -->
        <div class="form-group">
          <label class="form-label">3️⃣ Prompt de movimiento</label>
          <textarea id="video-motion-prompt" class="form-textarea" rows="3" placeholder="Describe el movimiento del avatar. Ej:&#10;Person talking naturally to camera, subtle head movements, hand gestures, friendly expression, natural lip movements"></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Duración</label>
          <select id="video-duration" class="form-select">
            <option value="5">5 segundos</option>
            <option value="10" selected>10 segundos</option>
          </select>
        </div>

        <button id="btn-generate-video" class="btn btn-primary btn-lg" style="width:100%" ${!isConfigured || avatars.length === 0 ? 'disabled' : ''}>
          🎬 Generar Vídeo con IA
        </button>

        <div id="video-loading" style="display:none" class="mt-lg">
          <div class="flex items-center gap-md">
            <div class="spinner"></div>
            <div>
              <p class="text-sm font-bold">Generando vídeo...</p>
              <p class="text-xs text-muted">Kling Pro v2.1 está animando tu avatar. Puede tardar 1-3 minutos.</p>
            </div>
          </div>
          <div class="progress-bar mt-md">
            <div class="progress-fill" id="video-progress" style="width:0%"></div>
          </div>
        </div>

        <!-- Quick Motion Presets -->
        <hr class="section-divider" />
        <h4 class="mb-md text-sm font-bold" style="color:var(--text-secondary)">⚡ Movimientos predefinidos</h4>
        <div class="flex flex-col gap-sm">
          <button class="btn btn-secondary motion-preset" data-prompt="Person talking naturally and enthusiastically to camera, subtle nodding, natural hand gestures explaining something, warm friendly smile, slight body movement, professional indoor lighting">
            🗣️ Hablando a cámara (natural)
          </button>
          <button class="btn btn-secondary motion-preset" data-prompt="Person showing a product to camera with excited expression, holding item up, pointing at features, nodding approvingly, enthusiastic UGC style review, natural lighting">
            📦 Mostrando producto (UGC)
          </button>
          <button class="btn btn-secondary motion-preset" data-prompt="Person reacting with surprise and excitement, eyebrows raised, mouth open, then transitioning to a big smile, looking directly at camera, social media reaction style">
            😱 Reacción sorpresa
          </button>
          <button class="btn btn-secondary motion-preset" data-prompt="Person sitting at desk, calm professional demeanor, slight head movements, occasional hand gestures, explaining concept, video call style, looking at camera">
            💼 Estilo profesional
          </button>
        </div>
      </div>

      <!-- Videos Output / Gallery -->
      <div>
        <div class="card mb-lg" id="video-result-card">
          <h3 class="mb-lg">📺 Resultado</h3>
          <div id="video-output">
            <div class="empty-state">
              <div class="empty-icon">🎬</div>
              <h3>Tu vídeo aparecerá aquí</h3>
              <p>Selecciona un avatar, un guion y un tipo de movimiento. Freepik AI animará tu avatar para crear un vídeo UGC ultrarrealista.</p>
            </div>
          </div>
        </div>

        ${videos.length > 0 ? `
          <h3 class="mb-md">📹 Vídeos generados (${videos.length})</h3>
          <div class="flex flex-col gap-md">
            ${videos.map(v => `
              <div class="card">
                <div class="flex justify-between items-center mb-sm">
                  <h4 class="text-sm font-bold">${v.name || 'Vídeo UGC'}</h4>
                  <span class="text-xs text-muted">${new Date(v.createdAt).toLocaleDateString('es-ES')}</span>
                </div>
                ${v.videoUrl ? `
                  <video src="${v.videoUrl}" controls style="width:100%;border-radius:var(--radius-md);max-height:300px"></video>
                ` : `
                  <div class="flex items-center gap-sm">
                    <span class="chip ${v.status === 'completed' ? 'green' : v.status === 'failed' ? 'pink' : 'cyan'}">${v.status}</span>
                    ${v.taskId ? `<span class="text-xs text-muted">Task: ${v.taskId}</span>` : ''}
                  </div>
                `}
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

let selectedAvatarUrl = null;

export function initVideos() {
    // Avatar selector
    document.querySelectorAll('.avatar-select-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.avatar-select-item').forEach(i => {
                i.style.borderColor = 'var(--border-subtle)';
                i.style.boxShadow = 'none';
            });
            item.style.borderColor = 'var(--accent-purple)';
            item.style.boxShadow = '0 0 15px rgba(168,85,247,0.3)';
            selectedAvatarUrl = item.dataset.url;
        });
    });

    // Motion presets
    document.querySelectorAll('.motion-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('video-motion-prompt').value = btn.dataset.prompt;
            window.__showToast?.('Preset de movimiento cargado', 'info');
        });
    });

    // Generate video
    document.getElementById('btn-generate-video')?.addEventListener('click', handleGenerateVideo);
}

async function handleGenerateVideo() {
    if (!selectedAvatarUrl) {
        window.__showToast?.('Selecciona un avatar primero', 'error');
        return;
    }

    const motionPrompt = document.getElementById('video-motion-prompt')?.value || '';
    const duration = document.getElementById('video-duration')?.value || '5';
    const btn = document.getElementById('btn-generate-video');
    const loading = document.getElementById('video-loading');
    const output = document.getElementById('video-output');
    const progressEl = document.getElementById('video-progress');

    btn.disabled = true;
    btn.textContent = '⏳ Enviando a Freepik AI...';
    loading.style.display = 'block';

    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress = Math.min(progress + Math.random() * 5, 90);
        progressEl.style.width = progress + '%';
    }, 2000);

    try {
        // Start video generation task
        const result = await freepikAPI.generateVideo(selectedAvatarUrl, {
            prompt: motionPrompt,
            duration,
        });

        const taskId = result.data?.task_id || result.task_id;

        if (taskId) {
            // Poll for task completion
            btn.textContent = '⏳ Procesando vídeo...';
            let taskResult = null;
            let attempts = 0;

            while (attempts < 60) {
                await new Promise(r => setTimeout(r, 3000));
                attempts++;
                try {
                    taskResult = await freepikAPI.getVideoTaskStatus(taskId);
                    const status = taskResult.data?.status || taskResult.status;

                    if (status === 'completed' || status === 'COMPLETED') {
                        break;
                    } else if (status === 'failed' || status === 'FAILED') {
                        throw new Error('La generación del vídeo falló. Intenta con otro prompt o avatar.');
                    }
                } catch (pollErr) {
                    if (pollErr.message.includes('falló')) throw pollErr;
                }
            }

            clearInterval(progressInterval);
            progressEl.style.width = '100%';

            const videoUrl = taskResult?.data?.video?.url || taskResult?.data?.output?.video;

            if (videoUrl) {
                output.innerHTML = `
          <video src="${videoUrl}" controls autoplay loop style="width:100%;border-radius:var(--radius-lg);box-shadow:var(--shadow-lg)"></video>
          <div class="flex gap-md mt-lg">
            <a href="${videoUrl}" download class="btn btn-primary">⬇️ Descargar vídeo</a>
            <button class="btn btn-secondary" id="btn-save-video">💾 Guardar en galería</button>
          </div>
        `;

                document.getElementById('btn-save-video')?.addEventListener('click', () => {
                    saveVideo({ name: 'Vídeo UGC', videoUrl, taskId, status: 'completed' });
                    window.__showToast?.('Vídeo guardado', 'success');
                });

                window.__showToast?.('¡Vídeo generado con éxito!', 'success');
            } else {
                // Save with taskId for later retrieval
                saveVideo({ name: 'Vídeo UGC', taskId, status: 'processing' });
                output.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">⏳</div>
            <h3>Vídeo en proceso</h3>
            <p>El vídeo se está generando. Task ID: ${taskId}. Vuelve más tarde para descargarlo.</p>
          </div>
        `;
                window.__showToast?.('Vídeo en cola de procesamiento', 'info');
            }
        } else {
            throw new Error('No se recibió un task ID. Revisa tu API key y créditos.');
        }
    } catch (err) {
        clearInterval(progressInterval);
        output.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">❌</div>
        <h3>Error</h3>
        <p>${err.message}</p>
      </div>
    `;
        window.__showToast?.(err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '🎬 Generar Vídeo con IA';
        loading.style.display = 'none';
    }
}
