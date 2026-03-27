const express = require('express');
const router = express.Router();
const multer = require('multer');
const Replicate = require('replicate');
const fs = require('fs');
const path = require('path');

const upload = multer({
    dest: 'uploads/',
    limits: { fileSize: 5 * 1024 * 1024 },
    fileFilter: (req, file, cb) => {
        if (['image/jpeg', 'image/png', 'image/webp'].includes(file.mimetype)) cb(null, true);
        else cb(new Error('Solo se permiten imágenes JPEG, PNG o WebP'));
    }
});
const replicate = new Replicate({
    auth: process.env.REPLICATE_API_TOKEN,
});

// Advanced Clone (Face-to-Many / PuLID) endpoint
router.post('/clone', upload.single('face_image'), async (req, res) => {
    try {
        if (!process.env.REPLICATE_API_TOKEN) {
            return res.status(500).json({ error: 'Missing Replicate API Token' });
        }

        const faceFile = req.file;
        const { prompt, negative_prompt } = req.body;

        if (!faceFile) return res.status(400).json({ error: 'face_image is required' });

        const faceBuffer = fs.readFileSync(faceFile.path);

        console.log(`[Avatars] Starting cloning process...`);

        // Using PuLID model because it proved best for profile swap in research
        const modelOwner = "yanze";
        const modelName = "pulid";

        const model = await replicate.models.get(modelOwner, modelName);
        const latestVersion = model.latest_version.id;

        const output = await replicate.run(
            `${modelOwner}/${modelName}:${latestVersion}`,
            {
                input: {
                    main_face_image: faceBuffer,
                    prompt: prompt || "A standard avatar portrait",
                    negative_prompt: negative_prompt || "",
                    id_weight: 1.05,
                    guidance_scale: 3.5,
                    num_inference_steps: 25,
                    width: 768,
                    height: 1024
                }
            }
        );

        if (output && output.length > 0) {
            console.log(`[Avatars] Success!`);
            res.json({ success: true, url: output[0] });
        } else {
            console.error('[Avatars] Replicate returned no output');
            res.status(500).json({ error: 'Failed to generate image from AI source' });
        }

    } catch (error) {
        console.error('[Avatars Error]:', error);
        res.status(500).json({ error: error.message });
    } finally {
        try { if (req.file) fs.unlinkSync(req.file.path); } catch (_) {}
    }
});

module.exports = router;
