"""
VideoForge Pro — API Server
================================
Unified server: single pipeline, no toggles, no API keys.
"""

import os
import sys
import uuid
import json
import threading
import traceback
from flask import Flask, request, jsonify, send_file, send_from_directory

# Ensure editor package is importable
sys.path.insert(0, os.path.dirname(__file__))

from editor.pipeline import run_pipeline, PRESETS

app = Flask(__name__, static_folder='web')

# Allow large video uploads (up to 500 MB)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# CORS — allow all origins
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Error handler for file too large
@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "El vídeo es demasiado grande (máximo 500 MB)"}), 413

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Job tracking
jobs = {}

# ════════════════════════════════════════════════════════════════════════
# UNIFIED PRESETS — VideoForge Pro
# ════════════════════════════════════════════════════════════════════════

PRO_PRESETS = {
    "viral_max": {
        "name": "🔥 Viral Max",
        "icon": "🔥",
        "description": "Todo al máximo: 12+ efectos, beat sync, retención brutal",
        "tags": ["Cortes IA", "VFX Max", "Beat Sync", "SFX", "Subtítulos", "Retención"],
        "category": "god_mode",
    },
    "cinematic_pro": {
        "name": "🎬 Cinematic Pro",
        "icon": "🎬",
        "description": "Color grade cine, grain, letterbox, SFX épico",
        "tags": ["Color Grade", "Film Grain", "Light Leaks", "SFX", "Subtítulos"],
        "category": "god_mode",
    },
    "aggressive_v10": {
        "name": "⚡ Aggressive",
        "icon": "⚡",
        "description": "Cortes 0.05s, glitch, bass drops, RGB split",
        "tags": ["Cortes Ultra", "Glitch", "RGB Split", "Bass Drop", "Beat Sync"],
        "category": "god_mode",
    },
    "hormozi": {
        "name": "💰 Hormozi",
        "icon": "💰",
        "description": "Estilo Alex Hormozi: zooms, subtítulos grandes, ritmo",
        "tags": ["Smart Zoom", "Subtítulos XL", "Retención", "Compositing"],
        "category": "creator",
    },
    "mrbeast": {
        "name": "🧲 MrBeast",
        "icon": "🧲",
        "description": "Colorido, rápido, SFX pesados, máxima energía",
        "tags": ["SFX Pro", "Zoom", "Beat Sync", "Color"],
        "category": "creator",
    },
    "music_video": {
        "name": "🎵 Music Video",
        "icon": "🎵",
        "description": "Beat-sync total, VFX reactivos al ritmo",
        "tags": ["Beat Sync", "VFX Reactivos", "Particles", "RGB"],
        "category": "creator",
    },
    "reel_pro": {
        "name": "📱 Reel Pro",
        "icon": "📱",
        "description": "Instagram vertical, subtítulos, retención, VFX",
        "tags": ["9:16", "Subtítulos", "VFX", "Retención"],
        "category": "platform",
    },
    "tiktok_pro": {
        "name": "🎶 TikTok Pro",
        "icon": "🎶",
        "description": "Vertical, beat-sync, retención, SFX",
        "tags": ["9:16", "Beat Sync", "SFX", "Subtítulos", "Retención"],
        "category": "platform",
    },
    "youtube_pro": {
        "name": "▶️ YouTube Pro",
        "icon": "▶️",
        "description": "Horizontal, zoom Ken Burns, retención, audio pro",
        "tags": ["Ken Burns", "Retención", "Audio Pro", "Compositing"],
        "category": "platform",
    },
    "ad_killer": {
        "name": "📢 Ad Killer",
        "icon": "📢",
        "description": "Anuncio con retención máxima, B-Roll, CTA",
        "tags": ["B-Roll", "SFX", "Retención", "CTA"],
        "category": "platform",
    },
    "podcast_pro": {
        "name": "🎙️ Podcast",
        "icon": "🎙️",
        "description": "Horizontal, cortes limpios, subtítulos discretos",
        "tags": ["Cortes Limpio", "Subtítulos", "Audio Pro"],
        "category": "platform",
    },
    "speed_only": {
        "name": "⏩ Speed Cut",
        "icon": "⏩",
        "description": "Solo corte de silencios + GPU (ultra rápido)",
        "tags": ["Cortes", "GPU"],
        "category": "quick",
    },
}


# ════════════════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')


@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Return all VideoForge Pro presets."""
    return jsonify(PRO_PRESETS)


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload a video file for processing."""
    try:
        if 'video' not in request.files:
            return jsonify({"error": "No se envió ningún vídeo"}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400

        job_id = str(uuid.uuid4())[:8]
        ext = os.path.splitext(file.filename)[1] or '.mp4'
        input_filename = f"{job_id}_input{ext}"
        input_path = os.path.join(UPLOAD_DIR, input_filename)

        print(f"📤 Subiendo: {file.filename} → {input_path}")
        file.save(input_path)
        file_size = os.path.getsize(input_path)
        print(f"✅ Upload OK: {round(file_size / (1024*1024), 1)} MB")

        return jsonify({
            "job_id": job_id,
            "filename": file.filename,
            "size_mb": round(file_size / (1024 * 1024), 2),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error al subir: {str(e)}"}), 500


@app.route('/api/process', methods=['POST'])
def process_video():
    """Start video processing with VideoForge Pro pipeline."""
    data = request.json
    job_id = data.get("job_id")
    preset = data.get("preset", "youtube_pro")

    if not job_id:
        return jsonify({"error": "Falta job_id"}), 400

    # Find input file
    input_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(job_id)]
    if not input_files:
        return jsonify({"error": "Archivo no encontrado"}), 404

    input_path = os.path.join(UPLOAD_DIR, input_files[0])
    output_filename = f"{job_id}_pro_{preset}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Track job
    jobs[job_id] = {
        "status": "processing",
        "preset": preset,
        "progress": 0,
        "message": "🎬 Iniciando VideoForge Pro...",
        "output_path": None,
        "error": None,
    }

    def process_async():
        try:
            jobs[job_id]["message"] = "⚡ Preparando motor Pro..."
            jobs[job_id]["progress"] = 10

            def on_progress(pct, msg):
                # Clamp between 10 and 95 so we control start/end
                clamped = max(10, min(95, pct))
                jobs[job_id]["progress"] = clamped
                jobs[job_id]["message"] = msg

            result = run_pipeline(
                input_path=input_path,
                output_path=output_path,
                preset=preset,
                progress_callback=on_progress,
            )

            jobs[job_id]["status"] = "done"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["message"] = "✅ ¡Edición completada!"
            jobs[job_id]["output_path"] = output_path
            jobs[job_id]["result"] = result

        except Exception as e:
            import traceback
            traceback.print_exc()
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)
            jobs[job_id]["message"] = f"❌ Error: {str(e)}"

    thread = threading.Thread(target=process_async, daemon=True)
    thread.start()

    return jsonify({"job_id": job_id, "status": "processing"})


@app.route('/api/status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Check the status of a processing job."""
    if job_id not in jobs:
        return jsonify({"error": "Job no encontrado"}), 404
    return jsonify(jobs[job_id])


@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    """Download the processed video."""
    if job_id not in jobs:
        return jsonify({"error": "Job no encontrado"}), 404

    job = jobs[job_id]
    if job["status"] != "done" or not job.get("output_path"):
        return jsonify({"error": "El vídeo aún no está listo"}), 400

    return send_file(
        job["output_path"],
        as_attachment=True,
        download_name=f"videoforge_pro_{job['preset']}_{job_id}.mp4"
    )


if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🎬 VideoForge Pro — Editor Profesional de Vídeo             ║
║                                                               ║
║   Motor: MoviePy + FFmpeg + GPU (100% local)                  ║
║   12 presets profesionales integrados                         ║
║                                                               ║
║   Abre tu navegador en: http://localhost:5000                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
