import axios from 'axios';
import fs from 'fs';

const BASE_HQ_IMAGE_PATH = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/media__1772899849795.jpg';
const OUTPUT_FILE = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/BASE_SERIA_SUDADERA.jpg';
const apiKey = 'FPSX03c8141aa0eb554cc75376208f194af4';
const API_URL = 'https://api.freepik.com/v1/ai/mystic';

async function generateSeriousBase() {
    console.log("Transformando la Sudadera Azul a expresión seria con Freepik Mystic...");
    const base64Image = fs.readFileSync(BASE_HQ_IMAGE_PATH, { encoding: 'base64' });

    const payload = {
        prompt: "A strictly serious and completely neutral expression of a black man, mouth completely closed, not smiling at all. He is wearing a light blue Nike hoodie, sitting in a podcast studio with a microphone. Same composition, realistic 4k, serious.",
        negative_prompt: "smiling, smile, teeth, grinning, laughing, happy, open mouth, caricaturized",
        image: {
            image_base64: `data:image/jpeg;base64,${base64Image}`,
            strength: 0.8 // high strength to change the mouth
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
        console.log(`Generación iniciada (Task ID: ${taskId}). Esperando base seria...`);

        for (let i = 0; i < 30; i++) {
            await new Promise(r => setTimeout(r, 2000));
            const pollRes = await axios.get(`${API_URL}/${taskId}`, { headers: { 'x-freepik-api-key': apiKey } });
            const data = pollRes.data;

            if (data.data?.status === 'COMPLETED' || data.status === 'COMPLETED') {
                const imgUrl = data.data?.generated?.[0] || data.generated?.[0];
                console.log(`¡Generación Completada! Descargando de: ${imgUrl}`);

                const imgFetch = await axios.get(imgUrl, { responseType: 'arraybuffer' });
                fs.writeFileSync(OUTPUT_FILE, Buffer.from(imgFetch.data));
                console.log(`✅ Base seria guardada en: ${OUTPUT_FILE}`);
                return;
            }
            if (data.status === 'FAILED') {
                console.log("Fallo:", data);
                return;
            }
            console.log("Procesando imagen seria...");
        }
    } catch (e) {
        console.error("Error catastrófico:", e.response?.data || e.message);
    }
}

generateSeriousBase();
