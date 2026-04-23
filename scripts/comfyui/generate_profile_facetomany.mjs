import Replicate from "replicate";
import fs from "fs/promises";

// Usamos el modelo estable fofr/face-to-many que integra FaceID/ControlNet
const REAL_FACE_PATH = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/media__1772913739002.jpg';
const OUTPUT_FILE = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/CLON_PERFIL_FACETOMANY.jpg';

const replicate = new Replicate({
    auth: process.env.REPLICATE_API_TOKEN,
});

async function runProfileClone() {
    console.log("🔥 INICIANDO GENERACIÓN DE PERFIL (Face-to-Many)...");

    try {
        const faceBuffer = await fs.readFile(REAL_FACE_PATH);
        const base64Image = `data:image/jpeg;base64,${faceBuffer.toString('base64')}`;

        // Using the highly popular and stable fofr/face-to-many model
        const modelOwner = "fofr";
        const modelName = "face-to-many";

        const model = await replicate.models.get(modelOwner, modelName);
        const latestVersion = model.latest_version.id;

        console.log("Forzando estilo realista y ángulo de perfil en la GPU...");

        const output = await replicate.run(
            `${modelOwner}/${modelName}:${latestVersion}`,
            {
                input: {
                    image: base64Image,
                    prompt: "A strictly side profile 90-degree portrait of a black man wearing a light grey sports t-shirt. He is looking completely away from the camera. Neutral serious expression, closed mouth. Natural daylight room lighting, highly realistic photography, highly detailed.",
                    negative_prompt: "looking at camera, front facing, smiling, 3d, cartoon, anime, depth of field, blur",
                    style: "Photography", // Force photorealism
                    prompt_strength: 6.5,
                    denoising_strength: 0.65 // Balance between identity and the new prompt
                }
            }
        );

        console.log("✅ Generación Completada! Output:", output);

        if (output && output.length > 0) {
            const url = output[0];
            const fetchReq = await fetch(url);
            const arrayBuffer = await fetchReq.arrayBuffer();
            const buffer = Buffer.from(arrayBuffer);

            await fs.writeFile(OUTPUT_FILE, buffer);
            console.log(`🎉 ¡ÉXITO! Tu clon de perfil perfecto (Face-to-Many) está guardado en: ${OUTPUT_FILE}`);
        } else {
            console.log("No se pudo extraer la imagen final. Output:", output);
        }

    } catch (error) {
        console.error("❌ FAILED:", error.message);
    }
}

runProfileClone();
