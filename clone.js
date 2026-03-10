import axios from 'axios';
import fs from 'fs';

const CLONE_IMAGE_PATH = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/media__1772898977840.jpg';
const API_URL = 'https://api.freepik.com/v1/ai/mystic';
const apiKey = 'FPSX03c8141aa0eb554cc75376208f194af4';

async function generateClone() {
    console.log("Enviando imagen a Freepik Mystic (Modo Literal Crop)...");
    const base64Image = fs.readFileSync(CLONE_IMAGE_PATH, { encoding: 'base64' });

    const payload = {
        prompt: "A low-quality front-facing webcam selfie of a black man. Exact structural match to the reference face. Short tight curly hair, neutral resting expression, slight facial hair, grey t-shirt visible at the very bottom. Ugly lighting, flat colors, no retouching, unfiltered.",
        negative_prompt: "beautiful, handsome, retouch, smooth skin, model, professional lighting, cinematic, 4k, 8k, highly detailed, perfect, symmetrical",
        image: {
            image_base64: `data:image/jpeg;base64,${base64Image}`,
            style_transfer: {
                reference_image: `data:image/jpeg;base64,${base64Image}`,
                weight: 1.0
            }
        },
        styling: {
            style: "photo",
            color: "none",
            framing: "portrait"
        }
    };

    try {
        const createRes = await axios.post(API_URL, payload, {
            headers: { 'x-freepik-api-key': apiKey, 'Content-Type': 'application/json' }
        });

        const taskId = createRes.data.data?.task_id || createRes.data.task_id;
        console.log(`Generación iniciada (Task ID: ${taskId}). Esperando render...`);

        for (let i = 0; i < 30; i++) {
            await new Promise(r => setTimeout(r, 2000));
            const pollRes = await axios.get(`${API_URL}/${taskId}`, { headers: { 'x-freepik-api-key': apiKey } });
            const data = pollRes.data;

            if (data.data?.status === 'COMPLETED' || data.status === 'COMPLETED') {
                console.log("¡CLON LITERAL COMPLETADO!");
                fs.writeFileSync('result.json', JSON.stringify(data, null, 2));
                console.log("JSON guardado en result.json");
                return;
            }
            if (data.status === 'FAILED') {
                console.log("Fallo:", data);
                return;
            }
            console.log("Procesando textura...");
        }

    } catch (e) {
        console.error("Error catastrófico:", e.response?.data || e.message);
    }
}

generateClone();
