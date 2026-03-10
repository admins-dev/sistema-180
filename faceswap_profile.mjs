import Replicate from "replicate";
import fs from "fs/promises";

// Usamos el molde de perfil generado y la foto de perfil cruda del usuario (Foto 3 o Foto 4)
const BASE_IMAGE_PATH = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/BASE_PERFIL_SUDADERA.jpg';
const REAL_FACE_PATH = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/media__1772913739002.jpg'; // Frontal/Slightly turned face to be swapped
const OUTPUT_FILE = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/CLON_PERFIL_DEFINITIVO.jpg';

const replicate = new Replicate({
    auth: process.env.REPLICATE_API_TOKEN,
});

async function runProfileFaceSwap() {
    console.log("🔥 INICIANDO FUSIÓN FACIAL: Molde de Perfil + Cara del Usuario...");

    try {
        const baseBuffer = await fs.readFile(BASE_IMAGE_PATH);
        const faceBuffer = await fs.readFile(REAL_FACE_PATH);

        const modelOwner = "lucataco";
        const modelName = "faceswap";

        const model = await replicate.models.get(modelOwner, modelName);
        const latestVersion = model.latest_version.id;

        console.log("Renderizando en la GPU...");

        const output = await replicate.run(
            `${modelOwner}/${modelName}:${latestVersion}`,
            {
                input: {
                    target_image: baseBuffer,
                    swap_image: faceBuffer,
                }
            }
        );

        console.log("✅ Fusión completada!");

        if (output) {
            const url = Array.isArray(output) ? output[0] : output;
            const fetchReq = await fetch(url);
            const arrayBuffer = await fetchReq.arrayBuffer();
            const buffer = Buffer.from(arrayBuffer);

            await fs.writeFile(OUTPUT_FILE, buffer);
            console.log(`🎉 ¡ÉXITO! Tu clon de perfil está guardado en: ${OUTPUT_FILE}`);
        } else {
            console.log("No se pudo extraer la imagen final. Output:", output);
        }

    } catch (error) {
        console.error("❌ FAILED:", error.message);
    }
}

runProfileFaceSwap();
