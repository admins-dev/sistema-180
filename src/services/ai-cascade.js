// ===============================================
// AI Cascade Engine — Gemini 2.0 Flash + Perplexity
// ===============================================
import { storage } from './storage.js';

const GEMINI_MODEL = 'gemini-2.0-flash';
const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

export const aiCascade = {

    // Gemini call with auto-retry on 429
    async callGemini(prompt, systemPrompt = 'Eres un experto copywriter viral.') {
        const key = storage.getGeminiKey();
        if (!key) throw new Error('API Key de Gemini no configurada. Ve a Configuracion.');

        for (let attempt = 1; attempt <= 3; attempt++) {
            const res = await fetch(`${GEMINI_ENDPOINT}?key=${key}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    system_instruction: { parts: { text: systemPrompt } },
                    contents: [{ parts: [{ text: prompt }] }]
                })
            });

            if (res.ok) {
                const data = await res.json();
                return data.candidates[0].content.parts[0].text;
            }

            const errData = await res.json().catch(() => ({}));

            if (res.status === 429) {
                if (attempt < 3) {
                    await new Promise(r => setTimeout(r, 15000 * attempt));
                    continue;
                }
                throw new Error('Gemini: Demasiadas llamadas. Espera 1 minuto e intentalo de nuevo.');
            }

            if (res.status === 400) {
                throw new Error('Gemini: Peticion invalida. Revisa la API Key en Configuracion.');
            }

            throw new Error(`Gemini Error ${res.status}: ${errData.error?.message || 'Error desconocido'}`);
        }
    },

    // Perplexity call
    async callPerplexity(prompt) {
        const key = storage.getPerplexityKey();
        if (!key) throw new Error('API Key de Perplexity no configurada. Ve a Configuracion.');

        const res = await fetch('https://api.perplexity.ai/chat/completions', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${key}`
            },
            body: JSON.stringify({
                model: 'sonar-pro',
                messages: [
                    { role: 'system', content: 'Eres un investigador experto. Busca en Reddit, foros y metricas reales de 2026. Devuelve datos crudos y reales.' },
                    { role: 'user', content: prompt }
                ]
            })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            if (res.status === 401) throw new Error('Perplexity: API Key invalida. Revisala en Configuracion.');
            throw new Error(`Perplexity Error ${res.status}: ${errData.error?.message || 'Error desconocido'}`);
        }
        const data = await res.json();
        return data.choices[0].message.content;
    },

    // Main cascade: Gemini structure -> Perplexity deep research -> Gemini final script
    async generateViralScriptSequence(topic, nicho, hookType, sddPillar, logCallback) {

        logCallback('1/3: Gemini 2.0 Flash creando estructura de investigacion...');
        const step1Prompt = `
      Quiero hacer un guion viral (60s) sobre "${topic}" para el nicho de "${nicho}",
      usando un gancho tipo "${hookType}" y el motivador universal de "${sddPillar}".
      Genera UNICAMENTE una lista de 3 preguntas de investigacion muy profundas para 
      encontrar datos reales, dolor real en foros (ej. Reddit) y estadisticas impactantes.
      No respondas las preguntas, solo dimalas.
    `;
        const structure = await this.callGemini(step1Prompt);

        logCallback('2/3: Perplexity buscando datos reales y foros en vivo (Sonar Pro)...');
        const step2Prompt = `
      Investiga a fondo lo siguiente usando la web actual:
      ${structure}
      
      Dame un resumen con datos cuantitativos, ejemplos reales de dolor que la gente 
      cuenta en Reddit / foros sobre este tema en el nicho de ${nicho}.
    `;
        const deepData = await this.callPerplexity(step2Prompt);

        logCallback('3/3: Gemini escribiendo el guion final con metodologia UMV...');
        const step3Prompt = `
      Aqui tienes la investigacion profunda de Perplexity sobre el nicho ${nicho}:
        ${deepData}

      Escribe un guion para un Reel de Instagram (60 segundos maximo).
      Sigue EXACTAMENTE la metodologia UMV (Umbral Minimo de Viralidad):
      1. GANCHO (0-3s): Frase polemica o dolor alineada al pilar ${sddPillar}. (Mainstream).
      2. DESARROLLO (3-30s): Historia/datos usando LA INVESTIGACION QUE TE HE PASADO.
      3. MORALEJA (30-45s): Posicionamiento como experto.
      4. CTA (45-60s): Que comenten "INFO".

      Devuelve el resultado en formato JSON estricto (sin markdown, sin bloques de codigo):
      {
        "hook": "texto del gancho",
        "story": "texto del desarrollo",
        "moraleja": "texto de la moraleja",
        "cta": "texto del cta"
      }
    `;

        let finalRaw = await this.callGemini(step3Prompt,
            'Eres un copywriter experto. Responde solo con JSON valido. No incluyas markdown, solo el objeto JSON crudo.');

        finalRaw = finalRaw.replace(/```json/g, '').replace(/```/g, '').trim();

        return JSON.parse(finalRaw);
    }
};
