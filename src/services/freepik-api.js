// ═══════════════════════════════════════════════
// Freepik API Service — Mystic model wrapper
// ═══════════════════════════════════════════════
import { storage } from './storage.js';

const PROXY_BASE = '/api/freepik';

export const freepikApi = {
    async generateAvatar(prompt, options = {}) {
        const key = storage.getFreepikKey();
        if (!key) throw new Error('Configura tu API key de Freepik en Ajustes');

        const body = {
            prompt,
            negative_prompt: options.negativePrompt || 'blurry, low quality, deformed, cartoon, anime, illustration, painting',
            image: { size: options.size || 'square_1_1' },
            styling: {
                style: 'photo',
                color: 'vibrant',
                lightning: options.lighting || 'studio',
                framing: options.framing || 'portrait'
            }
        };

        // POST to create task
        const createRes = await fetch(`${PROXY_BASE}/v1/ai/mystic`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'x-freepik-api-key': key },
            body: JSON.stringify(body)
        });

        if (!createRes.ok) {
            const err = await createRes.text();
            throw new Error(`Freepik API error: ${createRes.status} — ${err}`);
        }

        const taskData = await createRes.json();
        const taskId = taskData.data?.task_id || taskData.task_id;

        if (!taskId) {
            // Direct response (some endpoints return images directly)
            if (taskData.data?.[0]?.url || taskData.data?.url) {
                return taskData.data?.[0]?.url || taskData.data?.url;
            }
            throw new Error('No task_id en la respuesta');
        }

        // Poll for result
        return this.pollTask(taskId, key);
    },

    async pollTask(taskId, key, maxAttempts = 30) {
        for (let i = 0; i < maxAttempts; i++) {
            await new Promise(r => setTimeout(r, 2000));

            const res = await fetch(`${PROXY_BASE}/v1/ai/mystic/${taskId}`, {
                headers: { 'x-freepik-api-key': key }
            });

            if (!res.ok) continue;
            const data = await res.json();

            if (data.data?.status === 'COMPLETED' || data.status === 'COMPLETED') {
                const images = data.data?.images || data.images || data.data?.result?.images;
                if (images && images.length > 0) {
                    return typeof images[0] === 'string' ? images[0] : images[0].url;
                }
            }

            if (data.data?.status === 'FAILED' || data.status === 'FAILED') {
                throw new Error('La generación falló en Freepik');
            }
        }
        throw new Error('Timeout: la generación tardó demasiado');
    },

    async testConnection() {
        const key = storage.getFreepikKey();
        if (!key) return { ok: false, error: 'No API key' };
        try {
            const res = await fetch(`${PROXY_BASE}/v1/resources`, {
                headers: { 'x-freepik-api-key': key }
            });
            return { ok: res.ok, status: res.status };
        } catch (err) {
            return { ok: false, error: err.message };
        }
    }
};
