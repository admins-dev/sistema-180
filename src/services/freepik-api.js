/** Freepik API Wrapper — Handles all communication with Freepik API */

// Use Vite proxy in dev to avoid CORS, direct URL in production
const FREEPIK_BASE = import.meta.env.DEV ? '/api/freepik' : 'https://api.freepik.com';

export class FreepikAPI {
  constructor() {
    this.apiKey = localStorage.getItem('freepik_api_key') || '';
  }

  setApiKey(key) {
    this.apiKey = key;
    localStorage.setItem('freepik_api_key', key);
  }

  getApiKey() {
    return this.apiKey;
  }

  isConfigured() {
    return !!this.apiKey;
  }

  headers() {
    return {
      'Content-Type': 'application/json',
      'x-freepik-api-key': this.apiKey,
    };
  }

  // ---------------------------------
  //  TEXT → IMAGE  (Mystic model)
  //  Async: POST creates task → poll GET for results
  // ---------------------------------
  async generateImage(prompt, options = {}, onProgress = null) {
    const body = {
      prompt,
      num_images: options.numImages || 1,
      image: {
        size: options.size || 'square_1_1',
      },
      styling: {
        style: options.style || 'photo',
      },
    };

    if (options.negativePrompt) body.negative_prompt = options.negativePrompt;

    // Step 1: Start the generation task
    const res = await fetch(`${FREEPIK_BASE}/v1/ai/mystic`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || err.message || `Freepik API error: ${res.status}`);
    }

    const taskData = await res.json();
    const taskId = taskData?.data?.task_id;

    if (!taskId) {
      // Some endpoints return images directly
      if (taskData?.data?.generated?.length > 0) {
        return taskData.data.generated;
      }
      throw new Error('No se recibió un task_id de Freepik');
    }

    // Step 2: Poll for completion
    onProgress?.('Tarea creada, esperando resultados...');
    let attempts = 0;
    const maxAttempts = 60; // max 2 minutes

    while (attempts < maxAttempts) {
      await new Promise(r => setTimeout(r, 2000)); // wait 2s between polls
      attempts++;

      const statusRes = await fetch(`${FREEPIK_BASE}/v1/ai/mystic/${taskId}`, {
        method: 'GET',
        headers: this.headers(),
      });

      if (!statusRes.ok) continue;

      const statusData = await statusRes.json();
      const status = statusData?.data?.status;

      onProgress?.(`Estado: ${status} (intento ${attempts}/${maxAttempts})`);

      if (status === 'COMPLETED' || status === 'completed') {
        const images = statusData?.data?.generated || [];
        if (images.length > 0) {
          return images; // Return array of generated images
        }
        throw new Error('Tarea completada pero sin imágenes generadas');
      }

      if (status === 'FAILED' || status === 'failed') {
        throw new Error('La generación falló en Freepik. Intenta con otro prompt.');
      }
    }

    throw new Error('Tiempo de espera agotado. La generación tardó demasiado.');
  }

  // ---------------------------------
  //  IMAGE → VIDEO  (Kling Pro v2.1)
  // ---------------------------------
  async generateVideo(imageUrl, options = {}) {
    const body = {
      image_url: imageUrl,
      duration: options.duration || '5',
    };

    if (options.prompt) body.prompt = options.prompt;

    const res = await fetch(`${FREEPIK_BASE}/v1/ai/image-to-video/kling-v2-1-pro`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `Video API error: ${res.status}`);
    }

    return res.json();
  }

  // Check video generation task status
  async getVideoTaskStatus(taskId) {
    const res = await fetch(`${FREEPIK_BASE}/v1/ai/image-to-video/kling-v2-1-pro/${taskId}`, {
      method: 'GET',
      headers: this.headers(),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `Task status error: ${res.status}`);
    }

    return res.json();
  }

  // ---------------------------------
  //  IMAGE UPSCALER
  // ---------------------------------
  async upscaleImage(imageUrl) {
    const res = await fetch(`${FREEPIK_BASE}/v1/ai/upscaler`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ image_url: imageUrl }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `Upscaler error: ${res.status}`);
    }

    return res.json();
  }

  // ---------------------------------
  //  TEST CONNECTION
  // ---------------------------------
  async testConnection() {
    try {
      // Use a simple low-cost call to verify the key works
      const res = await fetch(`${FREEPIK_BASE}/v1/ai/mystic`, {
        method: 'POST',
        headers: this.headers(),
        body: JSON.stringify({
          prompt: 'test',
          num_images: 1,
          image: { size: 'square_1_1' },
        }),
      });

      // 200 = OK, 402 = no credits (but key is valid), 401/403 = bad key
      if (res.status === 401 || res.status === 403) {
        return { success: false, message: 'API Key inválida.' };
      }

      return { success: true, message: 'Conexión exitosa ✓' };
    } catch (e) {
      return { success: false, message: `Error de conexión: ${e.message}` };
    }
  }
}

export const freepikAPI = new FreepikAPI();
