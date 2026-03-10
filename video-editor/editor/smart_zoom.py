"""
VideoForge — Smart Zoom Module
Ken Burns effect and automatic punch-in/out for dynamic editing.
"""

import math
import numpy as np
from moviepy import VideoFileClip, VideoClip, CompositeVideoClip


def ease_in_out(t):
    """Smooth ease-in-out interpolation (sinusoidal)."""
    return 0.5 * (1 - math.cos(math.pi * t))


def apply_zoom(frame, scale, center_x=0.5, center_y=0.5):
    """
    Apply a zoom (scale) to a single frame, cropping around a center point.
    
    Args:
        frame: numpy array (H, W, C)
        scale: zoom factor (1.0 = no zoom, 1.15 = 15% zoom in)
        center_x: horizontal center (0.0 = left, 1.0 = right)
        center_y: vertical center (0.0 = top, 1.0 = bottom)
    
    Returns:
        Cropped and resized numpy array with the same dimensions
    """
    h, w = frame.shape[:2]
    
    if scale <= 1.0:
        return frame
    
    # Calculate crop dimensions
    new_w = int(w / scale)
    new_h = int(h / scale)
    
    # Calculate crop position centered on (center_x, center_y)
    x1 = int(center_x * w - new_w / 2)
    y1 = int(center_y * h - new_h / 2)
    
    # Clamp to bounds
    x1 = max(0, min(x1, w - new_w))
    y1 = max(0, min(y1, h - new_h))
    x2 = x1 + new_w
    y2 = y1 + new_h
    
    # Crop
    cropped = frame[y1:y2, x1:x2]
    
    # Resize back to original dimensions using simple interpolation
    try:
        import cv2
        resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)
    except ImportError:
        # Fallback: nearest-neighbor resize with numpy
        row_indices = (np.arange(h) * new_h / h).astype(int)
        col_indices = (np.arange(w) * new_w / w).astype(int)
        resized = cropped[np.ix_(row_indices, col_indices)]
    
    return resized


def ken_burns_effect(video_clip, start_scale=1.0, end_scale=1.15, center_x=0.5, center_y=0.4):
    """
    Apply a slow progressive zoom (Ken Burns effect) across the entire clip.
    
    Args:
        video_clip: MoviePy VideoClip
        start_scale: Initial zoom level (1.0 = no zoom)
        end_scale: Final zoom level (1.15 = 15% zoom)
        center_x: Horizontal center of zoom (0-1)
        center_y: Vertical center of zoom (0-1)
    
    Returns:
        New VideoClip with Ken Burns effect applied
    """
    duration = video_clip.duration
    
    def make_frame(t):
        progress = t / duration if duration > 0 else 0
        smooth_progress = ease_in_out(progress)
        current_scale = start_scale + (end_scale - start_scale) * smooth_progress
        
        original_frame = video_clip.get_frame(t)
        return apply_zoom(original_frame, current_scale, center_x, center_y)
    
    return VideoClip(make_frame, duration=duration).with_fps(video_clip.fps).with_audio(video_clip.audio)


def alternating_punch_in(video_clip, segments=None, scale_a=1.0, scale_b=1.15,
                          transition_duration=0.2):
    """
    Apply alternating zoom levels between segments, creating the professional
    'punch-in on cut' effect. If no segments provided, splits video evenly.
    
    Args:
        video_clip: MoviePy VideoClip
        segments: List of (start_time, end_time) tuples. If None, auto-detects.
        scale_a: Zoom level for odd segments (default: 1.0 = no zoom)
        scale_b: Zoom level for even segments (default: 1.15 = punched in)
        transition_duration: Smooth transition duration between zooms (seconds)
    
    Returns:
        New VideoClip with alternating punch-in effect
    """
    duration = video_clip.duration
    
    if segments is None:
        # Default: alternate every 4 seconds
        seg_duration = 4.0
        segments = []
        t = 0
        while t < duration:
            segments.append((t, min(t + seg_duration, duration)))
            t += seg_duration
    
    def get_target_scale(t):
        """Determine target scale at time t based on which segment we're in."""
        for i, (seg_start, seg_end) in enumerate(segments):
            if seg_start <= t < seg_end:
                return scale_b if i % 2 == 1 else scale_a
        return scale_a
    
    def make_frame(t):
        # Check if we're in a transition zone
        current_scale = get_target_scale(t)
        
        # Smooth transition: check if we're near a segment boundary
        for i, (seg_start, seg_end) in enumerate(segments):
            if i > 0:
                prev_seg_end = segments[i-1][1]
                if abs(t - seg_start) < transition_duration:
                    prev_scale = scale_b if (i-1) % 2 == 1 else scale_a
                    next_scale = scale_b if i % 2 == 1 else scale_a
                    progress = (t - (seg_start - transition_duration)) / (transition_duration * 2)
                    progress = max(0, min(1, progress))
                    current_scale = prev_scale + (next_scale - prev_scale) * ease_in_out(progress)
                    break
        
        original_frame = video_clip.get_frame(t)
        return apply_zoom(original_frame, current_scale)
    
    return VideoClip(make_frame, duration=duration).with_fps(video_clip.fps).with_audio(video_clip.audio)


def apply_smart_zoom(input_path, output_path=None, mode="punch_in", segments=None,
                      start_scale=1.0, end_scale=1.15):
    """
    Apply smart zoom effects to a video.
    
    Args:
        input_path: Path to input video
        output_path: Path to output video
        mode: "ken_burns" for slow progressive zoom, "punch_in" for alternating cuts
        segments: Optional list of (start, end) for punch_in mode
        start_scale/end_scale: Scale range
    
    Returns:
        dict with stats
    """
    if output_path is None:
        base = input_path.rsplit('.', 1)[0]
        output_path = f"{base}_zoomed.mp4"
    
    print(f"[SmartZoom] Cargando vídeo: {input_path}")
    video = VideoFileClip(input_path)
    
    if mode == "ken_burns":
        print(f"[SmartZoom] Aplicando Ken Burns ({start_scale}x → {end_scale}x)...")
        result = ken_burns_effect(video, start_scale, end_scale)
    elif mode == "punch_in":
        print(f"[SmartZoom] Aplicando Punch-In alternante ({start_scale}x / {end_scale}x)...")
        result = alternating_punch_in(video, segments, start_scale, end_scale)
    else:
        print(f"[SmartZoom] ⚠ Modo desconocido: {mode}")
        video.close()
        return {}
    
    print(f"[SmartZoom] Exportando: {output_path}")
    try:
        from editor.gpu_engine import detect_gpu, get_moviepy_write_params
        gpu_info = detect_gpu()
        write_params = get_moviepy_write_params(gpu_info)
    except Exception:
        write_params = {"codec": "libx264", "audio_codec": "aac", "preset": "ultrafast", "threads": 8}
    
    result.write_videofile(output_path, **write_params, logger="bar")
    
    stats = {
        "mode": mode,
        "duration": round(video.duration, 2),
        "output_path": output_path
    }
    
    print(f"[SmartZoom] ✅ Zoom aplicado — modo: {mode}")
    
    video.close()
    result.close()
    
    return stats


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python smart_zoom.py <video.mp4> [ken_burns|punch_in]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    zoom_mode = sys.argv[2] if len(sys.argv) > 2 else "punch_in"
    
    result = apply_smart_zoom(input_file, mode=zoom_mode)
    print(f"\nResultado: {result}")
