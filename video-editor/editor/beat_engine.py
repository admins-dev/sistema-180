"""
VideoForge v10 — Beat-Sync Engine
===================================
Detects BPM from audio, generates beat map, and synchronizes
video effects (cuts, zooms, flashes) to the rhythm.
"""

import numpy as np
import math


# ─── Beat Detection ─────────────────────────────────────────────────

def detect_beats(audio_clip, sensitivity=1.3):
    """
    Detect beat positions in an audio clip using onset detection.
    
    Args:
        audio_clip: MoviePy AudioClip
        sensitivity: Beat detection sensitivity (1.0 = strict, 2.0 = loose)
    
    Returns:
        dict with:
            - beats: list of beat timestamps (seconds)
            - bpm: estimated BPM
            - energy_profile: energy over time
    """
    print("[BEAT] 🎵 Analizando ritmo del audio...")
    
    sr = audio_clip.fps
    duration = audio_clip.duration
    
    # Get audio samples
    try:
        samples = audio_clip.to_soundarray(fps=sr)
        if samples.ndim > 1:
            samples = samples.mean(axis=1)  # Mono
    except Exception as e:
        print(f"[BEAT] ⚠️ Error leyendo audio: {e}")
        return {"beats": [], "bpm": 0, "energy_profile": []}
    
    # Parameters
    hop_size = int(sr * 0.01)  # 10ms hops
    win_size = int(sr * 0.03)  # 30ms windows
    
    # Calculate spectral flux (onset detection function)
    energy = []
    for i in range(0, len(samples) - win_size, hop_size):
        window = samples[i:i + win_size]
        e = np.sqrt(np.mean(window ** 2))
        energy.append(e)
    
    energy = np.array(energy, dtype=np.float32)
    if len(energy) == 0:
        return {"beats": [], "bpm": 0, "energy_profile": []}
    
    # Normalize
    max_e = energy.max()
    if max_e > 0:
        energy = energy / max_e
    
    # Compute onset strength (difference)
    onset_strength = np.zeros_like(energy)
    onset_strength[1:] = np.maximum(0, energy[1:] - energy[:-1])
    
    # Adaptive threshold
    window = int(sr * 0.3 / hop_size)  # 300ms window
    if window < 1:
        window = 1
    
    # Moving average threshold
    threshold = np.convolve(onset_strength, np.ones(window) / window, mode='same')
    threshold *= sensitivity
    
    # Find peaks above threshold
    beats = []
    min_beat_gap = 0.15  # Minimum 150ms between beats
    last_beat = -min_beat_gap
    
    for i in range(1, len(onset_strength) - 1):
        if (onset_strength[i] > threshold[i] and 
            onset_strength[i] > onset_strength[i-1] and 
            onset_strength[i] > onset_strength[i+1]):
            
            t = i * hop_size / sr
            if t - last_beat >= min_beat_gap:
                beats.append(t)
                last_beat = t
    
    # Estimate BPM
    bpm = 0
    if len(beats) > 2:
        intervals = np.diff(beats)
        median_interval = np.median(intervals)
        # BUG-17 FIX: Guard against zero/infinity 
        if median_interval > 0.05:  # At least 50ms between beats
            bpm = round(60.0 / median_interval)
            # Constrain to reasonable BPM range (with max iterations to prevent infinite loop)
            for _ in range(10):
                if bpm < 60:
                    bpm *= 2
                elif bpm > 200:
                    bpm //= 2
                else:
                    break
    
    # Create energy profile with timestamps
    energy_profile = []
    for i, e in enumerate(energy):
        t = i * hop_size / sr
        energy_profile.append({"time": t, "energy": float(e)})
    
    print(f"[BEAT] 🎵 Detectados {len(beats)} beats — BPM estimado: {bpm}")
    
    return {
        "beats": beats,
        "bpm": round(bpm),
        "energy_profile": energy_profile
    }


# ─── Beat-Synced Effects ────────────────────────────────────────────

def get_nearest_beat(t, beats, max_distance=0.15):
    """Check if time t is near a beat. Returns distance or None.
    BUG-14 FIX: Uses binary search O(log n) instead of linear scan O(n).
    """
    from bisect import bisect_left
    if not beats:
        return None
    idx = bisect_left(beats, t)
    best = None
    for i in (idx - 1, idx):
        if 0 <= i < len(beats):
            dist = abs(t - beats[i])
            if dist <= max_distance:
                if best is None or dist < best:
                    best = dist
    return best


def beat_flash(frame, beat_distance, max_distance=0.15):
    """White flash on beat, fades out quickly."""
    if beat_distance is None:
        return frame
    
    # Intensity based on distance from beat (stronger = closer)
    progress = beat_distance / max_distance
    alpha = max(0, 1 - progress) * 0.4  # Max 40% white
    
    result = frame.astype(np.float32)
    result += alpha * 255
    return np.clip(result, 0, 255).astype(np.uint8)


def beat_zoom(frame, beat_distance, max_distance=0.15, max_scale=1.08):
    """Quick zoom punch on beat."""
    if beat_distance is None:
        return frame
    
    progress = beat_distance / max_distance
    scale = 1 + (max_scale - 1) * max(0, 1 - progress)
    
    if scale <= 1.001:
        return frame
    
    h, w = frame.shape[:2]
    new_w, new_h = int(w / scale), int(h / scale)
    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2
    
    cropped = frame[y1:y1+new_h, x1:x1+new_w]
    import cv2
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


def beat_shake(frame, beat_distance, max_distance=0.15, intensity=8):
    """Camera shake on beat."""
    if beat_distance is None:
        return frame
    
    progress = beat_distance / max_distance
    shake_amount = max(0, 1 - progress) * intensity
    
    if shake_amount < 0.5:
        return frame
    
    import cv2
    dx = int(np.random.normal(0, shake_amount))
    dy = int(np.random.normal(0, shake_amount))
    h, w = frame.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def beat_rgb_split(frame, beat_distance, max_distance=0.15, max_shift=6):
    """RGB split on beat."""
    if beat_distance is None:
        return frame
    
    progress = beat_distance / max_distance
    shift = int(max(0, 1 - progress) * max_shift)
    
    if shift < 1:
        return frame
    
    result = frame.copy()
    h, w = frame.shape[:2]
    result[:, shift:, 0] = frame[:, :-shift, 0]
    result[:, :-shift, 2] = frame[:, shift:, 2]
    return result


# ─── Beat-Sync Pipeline ────────────────────────────────────────────

def apply_beat_sync(video_clip, beat_data=None, effects=None):
    """
    Apply beat-synchronized effects to a video clip.
    
    Args:
        video_clip: MoviePy video clip
        beat_data: dict from detect_beats() (or None to auto-detect)
        effects: list of effect names to apply on beats:
            ["flash", "zoom", "shake", "rgb_split"]
    
    Returns: Modified video clip
    """
    if effects is None:
        effects = ["zoom", "flash"]
    
    # Auto-detect beats if not provided
    if beat_data is None:
        if video_clip.audio is None:
            print("[BEAT] ⚠️ No hay audio para detección de ritmo")
            return video_clip
        beat_data = detect_beats(video_clip.audio)
    
    beats = beat_data.get("beats", [])
    bpm = beat_data.get("bpm", 0)
    
    if not beats:
        print("[BEAT] ⚠️ No se detectaron beats")
        return video_clip
    
    print(f"[BEAT] ⚡ Sincronizando {len(effects)} efectos a {len(beats)} beats ({bpm} BPM)")
    
    fps = video_clip.fps
    max_dist = 0.12  # 120ms window around each beat
    
    def process_frame(get_frame, t):
        frame = get_frame(t)
        
        # Check proximity to nearest beat
        bd = get_nearest_beat(t, beats, max_dist)
        
        if bd is not None:
            if "flash" in effects:
                frame = beat_flash(frame, bd, max_dist)
            if "zoom" in effects:
                frame = beat_zoom(frame, bd, max_dist)
            if "shake" in effects:
                frame = beat_shake(frame, bd, max_dist)
            if "rgb_split" in effects:
                frame = beat_rgb_split(frame, bd, max_dist)
        
        return frame
    
    modified = video_clip.transform(process_frame)
    modified = modified.with_audio(video_clip.audio)
    
    print(f"[BEAT] ✅ Beat-sync aplicado ({bpm} BPM, {len(beats)} beats)")
    return modified
