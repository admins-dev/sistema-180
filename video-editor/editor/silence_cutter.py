"""
VideoForge v10 — Silence Cutter
==================================
Detects and removes silent segments from video for dynamic jumpcuts.
v10: Smart protection for short videos, GPU encoding, improved detection.
"""

import numpy as np
from moviepy import VideoFileClip, concatenate_videoclips


# Cache GPU info once
_cached_gpu_info = None
_cached_write_params = None

def _get_gpu_write_params():
    """Get cached GPU write params (single FFmpeg call per session)."""
    global _cached_gpu_info, _cached_write_params
    if _cached_write_params is None:
        try:
            from editor.gpu_engine import get_gpu_info, get_moviepy_write_params
            _cached_gpu_info = get_gpu_info()
            _cached_write_params = get_moviepy_write_params(_cached_gpu_info)
        except Exception:
            _cached_write_params = {"codec": "libx264", "audio_codec": "aac", "preset": "ultrafast", "threads": 8}
    return _cached_write_params


def detect_silence(audio_clip, silence_threshold_db=-35, min_silence_duration=0.4, chunk_size=0.05):
    """
    Detect silent segments in an audio clip.
    
    Args:
        audio_clip: MoviePy AudioClip object
        silence_threshold_db: dB level below which audio is considered silence (default: -35)
        min_silence_duration: Minimum silent duration in seconds to be cut (default: 0.4s)
        chunk_size: Size of each analysis chunk in seconds (default: 0.05s = 50ms)
    
    Returns:
        List of tuples (start, end) for each silent segment
    """
    sample_rate = audio_clip.fps
    total_duration = audio_clip.duration
    
    # Convert dB threshold to amplitude
    silence_threshold = 10 ** (silence_threshold_db / 20.0)
    
    silent_segments = []
    current_silence_start = None
    
    t = 0
    while t < total_duration:
        end_t = min(t + chunk_size, total_duration)
        
        try:
            chunk_audio = audio_clip.subclipped(t, end_t).to_soundarray(fps=sample_rate)
            rms = np.sqrt(np.mean(chunk_audio ** 2))
        except Exception:
            rms = 0
        
        if rms < silence_threshold:
            if current_silence_start is None:
                current_silence_start = t
        else:
            if current_silence_start is not None:
                silence_duration = t - current_silence_start
                if silence_duration >= min_silence_duration:
                    silent_segments.append((current_silence_start, t))
                current_silence_start = None
        
        t += chunk_size
    
    # Handle trailing silence
    if current_silence_start is not None:
        silence_duration = total_duration - current_silence_start
        if silence_duration >= min_silence_duration:
            silent_segments.append((current_silence_start, total_duration))
    
    return silent_segments


def get_speaking_segments(duration, silent_segments, padding_ms=80):
    """
    From a list of silent segments, derive the speaking (non-silent) segments.
    FIX: Minimum segment duration of 0.5s to prevent micro-segments.
    FIX: Segments are validated to prevent overlap.
    """
    padding = padding_ms / 1000.0
    MIN_SEGMENT_DURATION = 0.5  # BUG-01 FIX: Minimum segment duration
    speaking_segments = []
    
    if not silent_segments:
        return [(0, duration)]
    
    # Before first silence
    first_silence_start = silent_segments[0][0]
    if first_silence_start > MIN_SEGMENT_DURATION:
        speaking_segments.append((0, min(first_silence_start + padding, duration)))
    
    # Between silences
    for i in range(len(silent_segments) - 1):
        seg_start = max(0, silent_segments[i][1] - padding)
        seg_end = min(duration, silent_segments[i + 1][0] + padding)
        if seg_end - seg_start > MIN_SEGMENT_DURATION:
            speaking_segments.append((seg_start, seg_end))
    
    # After last silence
    last_silence_end = silent_segments[-1][1]
    if last_silence_end < duration - MIN_SEGMENT_DURATION:
        speaking_segments.append((max(0, last_silence_end - padding), duration))
    
    # FIX: Remove overlapping segments
    if len(speaking_segments) > 1:
        cleaned = [speaking_segments[0]]
        for seg in speaking_segments[1:]:
            prev = cleaned[-1]
            if seg[0] < prev[1]:
                # Overlap — merge
                cleaned[-1] = (prev[0], max(prev[1], seg[1]))
            else:
                cleaned.append(seg)
        speaking_segments = cleaned
    
    return speaking_segments


def cut_silences(input_path, output_path=None, silence_threshold_db=-35,
                 min_silence_duration=0.4, padding_ms=80):
    """
    Remove silences from a video file, creating dynamic jumpcuts.
    
    v10 improvements:
    - Smart protection: skip if video < 5s or would lose > 60% duration
    - Post-concatenation validation
    - GPU encoding via gpu_engine (cached)
    - Better logging
    """
    if output_path is None:
        base = input_path.rsplit('.', 1)[0]
        output_path = f"{base}_jumpcut.mp4"
    
    # Get GPU params once (cached)
    write_params = _get_gpu_write_params()
    
    print(f"[SilenceCutter] 🎬 Cargando vídeo: {input_path}")
    video = VideoFileClip(input_path)
    original_duration = video.duration
    
    # ── SAFETY: Skip silence cutting for very short videos ──
    if original_duration < 5.0:
        print(f"[SilenceCutter] ⚡ Vídeo muy corto ({original_duration:.1f}s < 5s) — saltando corte de silencios")
        video.write_videofile(output_path, **write_params, logger="bar")
        video.close()
        return {
            "original_duration": round(original_duration, 2),
            "final_duration": round(original_duration, 2),
            "segments_count": 1,
            "time_saved": 0,
            "skipped": True,
            "reason": "video_too_short"
        }
    
    if video.audio is None:
        print("[SilenceCutter] ⚠ El vídeo no tiene audio. No se pueden detectar silencios.")
        video.write_videofile(output_path, **write_params, logger="bar")
        video.close()
        return {"original_duration": round(original_duration, 2), "final_duration": round(original_duration, 2),
                "segments_count": 1, "time_saved": 0}
    
    print(f"[SilenceCutter] 🔍 Analizando audio (umbral: {silence_threshold_db}dB, silencio mínimo: {min_silence_duration}s)...")
    silent_segments = detect_silence(video.audio, silence_threshold_db, min_silence_duration)
    
    print(f"[SilenceCutter] 📊 Encontrados {len(silent_segments)} silencios")
    
    if not silent_segments:
        print("[SilenceCutter] ✅ No hay silencios que cortar")
        video.write_videofile(output_path, **write_params, logger="bar")
        video.close()
        return {"original_duration": round(original_duration, 2), "final_duration": round(original_duration, 2),
                "segments_count": 1, "time_saved": 0}
    
    speaking_segments = get_speaking_segments(video.duration, silent_segments, padding_ms)
    
    if not speaking_segments:
        print("[SilenceCutter] ⚠ No se encontraron segmentos con audio — devolviendo vídeo original")
        video.write_videofile(output_path, **write_params, logger="bar")
        video.close()
        return {"original_duration": round(original_duration, 2), "final_duration": round(original_duration, 2),
                "segments_count": 1, "time_saved": 0}
    
    # Calculate what we'd end up with
    estimated_final = sum(end - start for start, end in speaking_segments)
    cut_ratio = estimated_final / original_duration
    
    # ── SAFETY: Don't cut more than 50% of the video ──
    if cut_ratio < 0.5:
        print(f"[SilenceCutter] ⚠️ Cortaría {(1-cut_ratio)*100:.0f}% del vídeo — demasiado. Saltando.")
        video.write_videofile(output_path, **write_params, logger="bar")
        video.close()
        return {
            "original_duration": round(original_duration, 2),
            "final_duration": round(original_duration, 2),
            "segments_count": 1,
            "time_saved": 0,
            "skipped": True,
            "reason": "would_cut_too_much"
        }
    
    print(f"[SilenceCutter] ✂️ Cortando a {len(speaking_segments)} segmentos ({estimated_final:.1f}s de {original_duration:.1f}s)...")
    
    # Extract and concatenate speaking segments
    clips = []
    for start, end in speaking_segments:
        clip = video.subclipped(start, min(end, video.duration))
        clips.append(clip)
    
    final = concatenate_videoclips(clips, method="compose")
    
    # ── BUG-01 FIX: Post-concatenation safety check ──
    if final.duration < original_duration * 0.5:
        print(f"[SilenceCutter] ⚠️ Resultado ({final.duration:.1f}s) es menos del 50% del original ({original_duration:.1f}s) — devolviendo original")
        for clip in clips:
            clip.close()
        final.close()
        video.write_videofile(output_path, **write_params, logger="bar")
        video.close()
        return {
            "original_duration": round(original_duration, 2),
            "final_duration": round(original_duration, 2),
            "segments_count": 1,
            "time_saved": 0,
            "skipped": True,
            "reason": "post_concat_too_short"
        }
    
    print(f"[SilenceCutter] 📤 Exportando: {output_path}")
    final.write_videofile(output_path, **write_params, logger="bar")
    
    stats = {
        "original_duration": round(video.duration, 2),
        "final_duration": round(final.duration, 2),
        "segments_count": len(speaking_segments),
        "time_saved": round(video.duration - final.duration, 2)
    }
    
    print(f"[SilenceCutter] ✅ Listo — {stats['time_saved']}s eliminados ({stats['segments_count']} segmentos)")
    
    # Cleanup
    for clip in clips:
        clip.close()
    final.close()
    video.close()
    
    return stats


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python silence_cutter.py <video.mp4> [umbral_db] [silencio_min_seg]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else -35
    min_sil = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
    
    result = cut_silences(input_file, silence_threshold_db=threshold, min_silence_duration=min_sil)
    print(f"\nResultado: {result}")
