import Replicate from "replicate";
import fs from "fs/promises";

const REAL_FACE_PATH = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/media__1772913739002.jpg';
const OUTPUT_FILE = 'C:/Users/Jose/.gemini/antigravity/brain/ea34c020-cf34-4c37-b944-e34055718d7e/CLON_PERFIL_PULID.jpg';

const replicate = new Replicate({
    auth: process.env.REPLICATE_API_TOKEN,
});

async function runProfileClone() {
    console.log("🔥 INICIANDO GENERACIÓN DE PERFIL (PuLID-FLUX)...");

    try {
        const faceBuffer = await fs.readFile(REAL_FACE_PATH);

        // Official working PuLID implementation on Replicate
        const modelOwner = "yanze";
        const modelName = "pulid";

        const model = await replicate.models.get(modelOwner, modelName);
        const latestVersion = model.latest_version.id;

        console.log("Forzando ángulo de perfil y renderizando identidad en la GPU...");

        // Using the correct inputs for yanze/pulid
        const output = await replicate.run(
            `${modelOwner}/${modelName}:${latestVersion}`,
            {
                input: {
                    main_face_image: faceBuffer,
                    prompt: "A strictly medium-shot photograph of a black man wearing a light grey sports t-shirt. He is captured from a clear 90-degree side profile angle, looking completely away from the camera to his left. Neutral serious expression, closed mouth. Natural daylight room lighting, ultra-realistic documentary photography, DSLR, 85mm lens, high fidelity skin texture, film grain.",
                    negative_prompt: "looking at camera, front facing, smiling, 3/4 turn, cartoon, illustration, synthetic skin, 3d render",
                    id_weight: 1.05,
                    guidance_scale: 3.5,
                    num_inference_steps: 25,
                    width: 768,
                    height: 1024
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
            console.log(`🎉 ¡ÉXITO! Tu clon de perfil perfecto está guardado en: ${OUTPUT_FILE}`);
        } else {
            console.log("No se pudo extraer la imagen final. Output:", output);
        }

    } catch (error) {
        console.error("❌ FAILED:", error.message);
    }
}

runProfileClone();
