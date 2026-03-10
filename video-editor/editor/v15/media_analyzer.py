"""
VideoForge V15 — Media Analyzer
=================================
Extrae metadatos del vídeo fuente via ffprobe.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from typing import Optional

from .models import SourceMediaMetadata

logger = logging.getLogger("v15.media")


def analyze_media(file_path: str) -> SourceMediaMetadata:
    """
    Analiza un archivo de vídeo con ffprobe y retorna SourceMediaMetadata.
    """
    logger.info(f"Analizando: {file_path}")
    
    # ffprobe JSON
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        file_path
    ]
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            raise RuntimeError(f"ffprobe falló: {r.stderr}")
        data = json.loads(r.stdout)
    except FileNotFoundError:
        raise RuntimeError("ffprobe no encontrado. Instala FFmpeg.")
    
    fmt = data.get("format", {})
    streams = data.get("streams", [])
    
    # Video stream
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    
    # FPS
    fps = 30.0
    r_frame = video_stream.get("r_frame_rate", "30/1")
    if "/" in r_frame:
        parts = r_frame.split("/")
        fps = float(parts[0]) / max(float(parts[1]), 1)
    
    # MD5
    md5 = _file_md5(file_path)
    
    meta = SourceMediaMetadata(
        file_path=file_path,
        duration=float(fmt.get("duration", 0)),
        fps=round(fps, 2),
        width=int(video_stream.get("width", 1920)),
        height=int(video_stream.get("height", 1080)),
        codec_video=video_stream.get("codec_name", "unknown"),
        codec_audio=audio_stream.get("codec_name", "unknown"),
        sample_rate=int(audio_stream.get("sample_rate", 44100)),
        channels=int(audio_stream.get("channels", 2)),
        file_size_bytes=int(fmt.get("size", 0)),
        md5_hash=md5,
        has_multiple_speakers=False,
    )
    
    logger.info(
        f"✅ {meta.width}x{meta.height} @ {meta.fps}fps, "
        f"{meta.duration:.1f}s, {meta.codec_video}/{meta.codec_audio}"
    )
    return meta


def _file_md5(path: str, chunk_size: int = 8192) -> str:
    """Calcula MD5 parcial (primeros 10MB) para velocidad."""
    h = hashlib.md5()
    read = 0
    max_read = 10 * 1024 * 1024  # 10MB
    try:
        with open(path, "rb") as f:
            while read < max_read:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
                read += len(chunk)
    except Exception:
        return "unknown"
    return h.hexdigest()
