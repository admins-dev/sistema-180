import Replicate from "replicate";
import fs from "fs/promises";

const REAL_FACE_PATH = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/media__1772913739002.jpg';
const OUTPUT_FILE = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/CLON_PERFIL_INSTANTID.jpg';

const replicate = new Replicate({
    auth: process.env.REPLICATE_API_TOKEN,
});

async function runProfileClone() {
    console.log("🔥 INICIANDO GENERACIÓN DE PERFIL (InstantID)...");

    try {
        const faceBuffer = await fs.readFile(REAL_FACE_PATH);

        const modelOwner = "lucataco";
        const modelName = "instantid";

        const model = await replicate.models.get(modelOwner, modelName);
        const latestVersion = model.latest_version.id;

        console.log("Forzando ángulo de perfil y renderizando identidad en la GPU...");

        const output = await replicate.run(
            `${modelOwner}/${modelName}:${latestVersion}`,
            {
                input: {
                    image: faceBuffer,
                    prompt: "A side profile portrait of a black man wearing a light grey sports t-shirt. The camera is positioned strictly at a 90-degree angle from the side of his face. He is looking completely away from the lens. Neutral serious expression, mouth closed. Crisp studio lighting, 4k ultra realistic photograph.",
                    negative_prompt: "looking at camera, front facing, smiling, open mouth, teeth, painting, drawing, cartoon, 3d render",
                    ip_adapter_scale: 0.8,
                    controlnet_conditioning_scale: 0.8,
                    width: 1024,
                    height: 1024,
                    num_inference_steps: 30,
                    guidance_scale: 5
                }
            }
        );

        console.log("✅ Generación Completada! Output:", output);

        if (output) {
            const url = Array.isArray(output) ? output[0] : output;
            const fetchReq = await fetch(url);
            const arrayBuffer = await fetchReq.arrayBuffer();
            const buffer = Buffer.from(arrayBuffer);

            await fs.writeFile(OUTPUT_FILE, buffer);
            console.log(`🎉 ¡ÉXITO! Tu clon de perfil perfecto (InstantID) está guardado en: ${OUTPUT_FILE}`);
        } else {
            console.log("No se pudo extraer la imagen final. Output:", output);
        }

    } catch (error) {
        console.error("❌ FAILED:", error.message);
    }
}

runProfileClone();
