import axios from 'axios';
import fs from 'fs';

const BASE_HQ_IMAGE_PATH = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/media__1772899849795.jpg'; // Frontal original base for style ref
const OUTPUT_FILE = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/BASE_PERFIL_SUDADERA.jpg';
const apiKey = 'FPSX03c8141aa0eb554cc75376208f194af4';
const API_URL = 'https://api.freepik.com/v1/ai/mystic';

async function generateProfileBase() {
    console.log("Generando un molde de Sudadera Azul pero de PERFIL con Freepik Mystic...");
    const base64Image = fs.readFileSync(BASE_HQ_IMAGE_PATH, { encoding: 'base64' });

    const payload = {
        prompt: "A strictly side-profile 90-degree portrait of a black man wearing a light blue Nike hoodie. He is captured from the side, looking completely horizontally to the right. Natural daylight room lighting, highly realistic 4k photography, serious facial expression.",
        negative_prompt: "looking at camera, front facing, smiling, open mouth, teeth",
        image: {
            image_base64: `data:image/jpeg;base64,${base64Image}`,
            strength: 0.95 // Very high strength to completely change pose while loosely keeping colors
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
        console.log(`Generación iniciada (Task ID: ${taskId}). Esperando molde de perfil...`);

        for (let i = 0; i < 30; i++) {
            await new Promise(r => setTimeout(r, 2000));
            try {
                const pollRes = await axios.get(`${API_URL}/${taskId}`, { headers: { 'x-freepik-api-key': apiKey } });
                const data = pollRes.data;

                if (data.data?.status === 'COMPLETED' || data.status === 'COMPLETED') {
                    const imgUrl = data.data?.generated?.[0] || data.generated?.[0];
                    console.log(`¡Generación Completada! Descargando de: ${imgUrl}`);

                    const imgFetch = await axios.get(imgUrl, { responseType: 'arraybuffer' });
                    fs.writeFileSync(OUTPUT_FILE, Buffer.from(imgFetch.data));
                    console.log(`✅ Molde de perfil guardado en: ${OUTPUT_FILE}`);
                    return;
                }
                if (data.status === 'FAILED') {
                    console.log("Fallo:", data);
                    return;
                }
                process.stdout.write(".");
            } catch (pollErr) {
                process.stdout.write("x");
            }
        }
    } catch (e) {
        console.error("\nError catastrófico:", e.response?.data || e.message);
    }
}

generateProfileBase();
