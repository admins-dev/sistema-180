"""
VideoForge — Smart Reframe Module
Intelligent crop from 16:9 to 9:16 with face tracking for vertical video (Reels/TikTok).
"""

import numpy as np
from moviepy import VideoFileClip, VideoClip

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


# ---------- Face Detection ---------- #

def get_face_cascade():
    """Load OpenCV's Haar Cascade for face detection."""
    if not CV2_AVAILABLE:
        raise ImportError("opencv-python no está instalado. Ejecuta: pip install opencv-python")
    
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    cascade = cv2.CascadeClassifier(cascade_path)
    return cascade


def detect_face_center(frame, cascade, last_known_center=None):
    """
    Detect the primary face in a frame and return its center position.
    
    Args:
        frame: numpy array (H, W, C) in RGB
        cascade: OpenCV CascadeClassifier
        last_known_center: Previous face center for fallback
    
    Returns:
        (center_x, center_y) as fractions (0-1), or last_known_center if no face found
    """
    h, w = frame.shape[:2]
    
    # Convert to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    # Detect faces
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(int(w * 0.05), int(h * 0.05))
    )
    
    if len(faces) > 0:
        # Use the largest face
        face = max(faces, key=lambda f: f[2] * f[3])
        fx, fy, fw, fh = face
        center_x = (fx + fw / 2) / w
        center_y = (fy + fh / 2) / h
        return (center_x, center_y)
    
    # No face found — use last known or center
    if last_known_center:
        return last_known_center
    return (0.5, 0.4)  # Default: slightly above center


# ---------- Smooth Tracking ---------- #

def smooth_positions(positions, window_size=15):
    """
    Smooth face position data to prevent jittery camera movement.
    Uses a simple moving average.
    
    Args:
        positions: List of (x, y) tuples
        window_size: Smoothing window size
    
    Returns:
        List of smoothed (x, y) tuples
    """
    if len(positions) <= window_size:
        return positions
    
    smoothed = []
    for i in range(len(positions)):
        start = max(0, i - window_size // 2)
        end = min(len(positions), i + window_size // 2 + 1)
        window = positions[start:end]
        avg_x = sum(p[0] for p in window) / len(window)
        avg_y = sum(p[1] for p in window) / len(window)
        smoothed.append((avg_x, avg_y))
    
    return smoothed


# ---------- Reframing ---------- #

def analyze_face_positions(video_clip, sample_rate=5):
    """
    Analyze a video and get face positions at regular intervals.
    
    Args:
        video_clip: MoviePy VideoClip
        sample_rate: Samples per second for face detection
    
    Returns:
        List of (time, center_x, center_y) tuples
    """
    print("[Reframe] Analizando posiciones de cara en el vídeo...")
    cascade = get_face_cascade()
    
    positions = []
    last_center = (0.5, 0.4)
    
    sample_interval = 1.0 / sample_rate
    t = 0
    total_samples = int(video_clip.duration * sample_rate)
    sample_count = 0
    
    while t < video_clip.duration:
        frame = video_clip.get_frame(t)
        center = detect_face_center(frame, cascade, last_center)
        positions.append((t, center[0], center[1]))
        last_center = center
        
        sample_count += 1
        if sample_count % 50 == 0:
            print(f"[Reframe]   Progreso: {sample_count}/{total_samples} frames analizados")
        
        t += sample_interval
    
    print(f"[Reframe] ✅ {len(positions)} posiciones de cara analizadas")
    return positions


def reframe_video(video_clip, face_positions, target_ratio=(9, 16), smoothing=15):
    """
    Crop video to target aspect ratio, following face positions.
    
    Args:
        video_clip: MoviePy VideoClip (horizontal)
        face_positions: List of (time, cx, cy) from analyze_face_positions
        target_ratio: Target aspect ratio as (w, h) tuple
        smoothing: Position smoothing window size
    
    Returns:
        New VideoClip in target aspect ratio
    """
    src_w, src_h = video_clip.w, video_clip.h
    
    # Calculate output dimensions
    target_w_ratio, target_h_ratio = target_ratio
    
    # Output size: keep height, compute width for target ratio
    out_h = src_h
    out_w = int(src_h * target_w_ratio / target_h_ratio)
    
    if out_w > src_w:
        # If wider than source, keep width and compute height
        out_w = src_w
        out_h = int(src_w * target_h_ratio / target_w_ratio)
    
    print(f"[Reframe] Recortando de {src_w}x{src_h} → {out_w}x{out_h}")
    
    # Smooth the face positions
    centers = [(p[1], p[2]) for p in face_positions]
    times = [p[0] for p in face_positions]
    smooth_centers = smooth_positions(centers, smoothing)
    
    def get_center_at_time(t):
        """Interpolate face center at any time t."""
        if not times:
            return (0.5, 0.4)
        
        # Find surrounding samples
        if t <= times[0]:
            return smooth_centers[0]
        if t >= times[-1]:
            return smooth_centers[-1]
        
        for i in range(len(times) - 1):
            if times[i] <= t <= times[i + 1]:
                alpha = (t - times[i]) / (times[i + 1] - times[i])
                cx = smooth_centers[i][0] * (1 - alpha) + smooth_centers[i + 1][0] * alpha
                cy = smooth_centers[i][1] * (1 - alpha) + smooth_centers[i + 1][1] * alpha
                return (cx, cy)
        
        return smooth_centers[-1]
    
    def make_frame(t):
        frame = video_clip.get_frame(t)
        cx, cy = get_center_at_time(t)
        
        # Calculate crop position
        x1 = int(cx * src_w - out_w / 2)
        y1 = int(cy * src_h - out_h / 2)
        
        # Clamp to bounds
        x1 = max(0, min(x1, src_w - out_w))
        y1 = max(0, min(y1, src_h - out_h))
        
        # Crop
        cropped = frame[y1:y1 + out_h, x1:x1 + out_w]
        
        return cropped
    
    reframed = VideoClip(make_frame, duration=video_clip.duration)
    reframed = reframed.with_fps(video_clip.fps)
    
    if video_clip.audio:
        reframed = reframed.with_audio(video_clip.audio)
    
    return reframed


def smart_reframe(input_path, output_path=None, target_ratio=(9, 16),
                   sample_rate=5, smoothing=15):
    """
    Full pipeline: analyze faces and reframe video to vertical format.
    
    Args:
        input_path: Path to input (horizontal) video
        output_path: Path to output video
        target_ratio: Target aspect ratio (default: 9:16 for Reels/TikTok)
        sample_rate: Face detection samples per second
        smoothing: Position smoothing window
    
    Returns:
        dict with stats
    """
    if output_path is None:
        base = input_path.rsplit('.', 1)[0]
        ratio_str = f"{target_ratio[0]}x{target_ratio[1]}"
        output_path = f"{base}_{ratio_str}.mp4"
    
    print(f"[Reframe] Cargando vídeo: {input_path}")
    video = VideoFileClip(input_path)
    
    print(f"[Reframe] Vídeo original: {video.w}x{video.h}, {round(video.duration, 2)}s")
    
    # Step 1: Analyze face positions
    face_positions = analyze_face_positions(video, sample_rate)
    
    # Step 2: Reframe
    reframed = reframe_video(video, face_positions, target_ratio, smoothing)
    
    # Step 3: Export
    print(f"[Reframe] Exportando: {output_path}")
    try:
        from editor.gpu_engine import detect_gpu, get_moviepy_write_params
        gpu_info = detect_gpu()
        write_params = get_moviepy_write_params(gpu_info)
    except Exception:
        write_params = {"codec": "libx264", "audio_codec": "aac", "preset": "ultrafast", "threads": 8}
    
    reframed.write_videofile(output_path, **write_params, logger="bar")
    
    stats = {
        "original_size": f"{video.w}x{video.h}",
        "output_size": f"{reframed.w}x{reframed.h}",
        "duration": round(video.duration, 2),
        "faces_detected": len([p for p in face_positions if p[1] != 0.5]),
        "output_path": output_path
    }
    
    print(f"[Reframe] ✅ Reframe completado — {stats['original_size']} → {stats['output_size']}")
    
    video.close()
    reframed.close()
    
    return stats


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python smart_reframe.py <video.mp4> [ancho:alto]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    ratio = (9, 16)
    if len(sys.argv) > 2:
        parts = sys.argv[2].split(':')
        ratio = (int(parts[0]), int(parts[1]))
    
    result = smart_reframe(input_file, target_ratio=ratio)
    print(f"\nResultado: {result}")
