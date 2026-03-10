"""
VideoForge v10 — Retention Engine
====================================
Analyzes audio energy, detects low-attention zones, and injects
pattern interrupts with 16 different effects. Supports beat-sync.
"""

import numpy as np
import cv2
import random
import math


# ─── Audio Energy Analysis ──────────────────────────────────────────

def analyze_energy(audio_clip, chunk_duration=0.5):
    """
    Analyze audio energy levels over time.
    
    Returns:
        List of dicts: [{"time": float, "energy": float, "is_climax": bool}, ...]
    """
    if audio_clip is None:
        return []
    
    sr = audio_clip.fps
    duration = audio_clip.duration
    energy_map = []
    
    try:
        samples = audio_clip.to_soundarray(fps=sr)
        if samples.ndim > 1:
            samples = samples.mean(axis=1)
    except Exception:
        return []
    
    chunk_samples = int(sr * chunk_duration)
    energies = []
    
    for i in range(0, len(samples) - chunk_samples, chunk_samples):
        chunk = samples[i:i + chunk_samples]
        rms = np.sqrt(np.mean(chunk ** 2))
        t = i / sr
        energies.append({"time": t, "energy": float(rms)})
    
    if not energies:
        return []
    
    # Normalize
    max_e = max(e["energy"] for e in energies) or 1.0
    for e in energies:
        e["energy"] /= max_e
    
    # Detect climax moments (top 15% energy)
    sorted_e = sorted([e["energy"] for e in energies], reverse=True)
    climax_threshold = sorted_e[max(0, int(len(sorted_e) * 0.15))] if sorted_e else 0.8
    
    for e in energies:
        e["is_climax"] = e["energy"] >= climax_threshold
    
    return energies


def detect_low_energy_zones(energy_map, max_gap_sec=3.0, low_threshold=0.35):
    """Find continuous zones where energy is below threshold."""
    zones = []
    zone_start = None
    
    for entry in energy_map:
        if entry["energy"] < low_threshold:
            if zone_start is None:
                zone_start = entry["time"]
        else:
            if zone_start is not None:
                duration = entry["time"] - zone_start
                if duration >= max_gap_sec:
                    zones.append((zone_start, entry["time"]))
                zone_start = None
    
    return zones


# ─── 16 Pattern Interrupt Effects ───────────────────────────────────

def fx_shake(frame, intensity=8):
    """Camera shake."""
    dx = int(np.random.normal(0, intensity))
    dy = int(np.random.normal(0, intensity))
    h, w = frame.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)

def fx_glitch(frame):
    """Digital glitch with scan line displacement."""
    result = frame.copy()
    h, w = result.shape[:2]
    for _ in range(random.randint(3, 8)):
        y = random.randint(0, h - 5)
        strip_h = random.randint(2, min(20, h - y))
        shift = random.randint(-30, 30)
        strip = result[y:y+strip_h].copy()
        if shift > 0 and shift < w:
            result[y:y+strip_h, shift:] = strip[:, :w-shift]
        elif shift < 0 and -shift < w:
            result[y:y+strip_h, :w+shift] = strip[:, -shift:]
    return result

def fx_flash(frame, intensity=0.6):
    """White flash overlay."""
    return np.clip(frame.astype(np.float32) + 255 * intensity, 0, 255).astype(np.uint8)

def fx_zoom_punch(frame, scale=1.2):
    """Quick zoom punch-in."""
    h, w = frame.shape[:2]
    new_w, new_h = int(w / scale), int(h / scale)
    x1, y1 = (w - new_w) // 2, (h - new_h) // 2
    cropped = frame[y1:y1+new_h, x1:x1+new_w]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

def fx_invert(frame):
    """Color inversion."""
    return (255 - frame).astype(np.uint8)

def fx_high_contrast(frame):
    """Extreme contrast boost."""
    lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
    l = clahe.apply(l)
    result = cv2.merge([l, a, b])
    return cv2.cvtColor(result, cv2.COLOR_LAB2RGB)

def fx_blur_pulse(frame):
    """Quick blur pulse."""
    return cv2.GaussianBlur(frame, (15, 15), 0)

def fx_red_flash(frame, intensity=0.4):
    """Red color flash."""
    overlay = np.zeros_like(frame)
    overlay[:, :, 0] = 255
    return cv2.addWeighted(frame, 1 - intensity, overlay, intensity, 0)

def fx_chromatic(frame, shift=5):
    """RGB split."""
    result = frame.copy()
    h, w = result.shape[:2]
    if shift < w:
        result[:, shift:, 0] = frame[:, :-shift, 0]
        result[:, :-shift, 2] = frame[:, shift:, 2]
    return result

def fx_pixelate(frame, block_size=12):
    """Pixelation effect."""
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (w // block_size, h // block_size), 
                       interpolation=cv2.INTER_NEAREST)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

def fx_vhs_noise(frame):
    """VHS-style noise lines."""
    result = frame.copy()
    h, w = result.shape[:2]
    for _ in range(random.randint(5, 15)):
        y = random.randint(0, h - 1)
        result[y:min(y+2, h), :] = np.clip(
            result[y:min(y+2, h)].astype(np.int16) + random.randint(-80, 80), 
            0, 255).astype(np.uint8)
    return result

def fx_edge_detect(frame):
    """Edge detection overlay."""
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    return cv2.addWeighted(frame, 0.7, edges_rgb, 0.3, 0)

def fx_scale_bounce(frame, t_in_effect=0.5):
    """Scale bounce animation."""
    scale = 1 + 0.15 * math.sin(t_in_effect * math.pi * 4) * math.exp(-t_in_effect * 3)
    if scale <= 1.001:
        return frame
    h, w = frame.shape[:2]
    new_w, new_h = int(w / scale), int(h / scale)
    x1, y1 = (w - new_w) // 2, (h - new_h) // 2
    cropped = frame[max(0,y1):y1+new_h, max(0,x1):x1+new_w]
    if cropped.size == 0:
        return frame
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

def fx_rotation(frame, angle=3):
    """Small rotation jitter."""
    h, w = frame.shape[:2]
    a = random.uniform(-angle, angle)
    M = cv2.getRotationMatrix2D((w/2, h/2), a, 1)
    return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)

def fx_tint_cycle(frame, t=0):
    """Color tint that cycles through hues."""
    hue = (t * 60) % 180
    overlay = np.zeros_like(frame)
    overlay[:, :, int(hue / 60) % 3] = 60
    return cv2.addWeighted(frame, 0.85, overlay, 0.15, 0)

def fx_stutter(frame):
    """Duplicate/freeze frame effect (visual stutter)."""
    return frame  # Returns same frame — pipeline handles the hold


# ─── Effect Pool ────────────────────────────────────────────────────

EFFECTS_POOL = [
    (fx_shake, 0.15, "shake"),
    (fx_glitch, 0.12, "glitch"),
    (fx_flash, 0.08, "flash"),
    (fx_zoom_punch, 0.1, "zoom_punch"),
    (fx_invert, 0.06, "invert"),
    (fx_high_contrast, 0.08, "high_contrast"),
    (fx_blur_pulse, 0.08, "blur_pulse"),
    (fx_red_flash, 0.1, "red_flash"),
    (fx_chromatic, 0.12, "chromatic"),
    (fx_pixelate, 0.08, "pixelate"),
    (fx_vhs_noise, 0.1, "vhs_noise"),
    (fx_edge_detect, 0.08, "edge_detect"),
    (fx_scale_bounce, 0.15, "scale_bounce"),
    (fx_rotation, 0.1, "rotation"),
    (fx_tint_cycle, 0.08, "tint_cycle"),
    (fx_stutter, 0.05, "stutter"),
]


def pick_interrupt_effect():
    """Randomly pick an interrupt effect."""
    fn, duration, name = random.choice(EFFECTS_POOL)
    return fn, duration, name


# ─── Climax Enhancement ────────────────────────────────────────────

def enhance_climax_moments(video_clip, energy_map):
    """
    Enhance climax moments with zoom + glow + vignette.
    """
    if not energy_map:
        return video_clip
    
    climax_times = [e["time"] for e in energy_map if e.get("is_climax")]
    if not climax_times:
        return video_clip
    
    fps = video_clip.fps
    print(f"[RETENTION] 🔥 Realzando {len(climax_times)} momentos cumbre")
    
    def process_frame(get_frame, t):
        frame = get_frame(t)
        
        # Check if near a climax moment
        for ct in climax_times:
            dist = abs(t - ct)
            if dist < 0.8:
                intensity = max(0, 1 - dist / 0.8)
                
                # Zoom punch
                scale = 1 + 0.08 * intensity
                h, w = frame.shape[:2]
                new_w, new_h = int(w / scale), int(h / scale)
                if new_w > 0 and new_h > 0:
                    x1, y1 = (w - new_w) // 2, (h - new_h) // 2
                    cropped = frame[y1:y1+new_h, x1:x1+new_w]
                    frame = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
                
                # Vignette
                Y, X = np.ogrid[:h, :w]
                cx, cy = w // 2, h // 2
                dist_map = np.sqrt((X - cx)**2 + (Y - cy)**2).astype(np.float32)
                max_dist = math.sqrt(cx**2 + cy**2)
                vignette = 1 - (dist_map / max_dist) * 0.3 * intensity
                for c in range(3):
                    frame[:, :, c] = np.clip(frame[:, :, c] * vignette, 0, 255).astype(np.uint8)
                
                break
        
        return frame
    
    modified = video_clip.transform(process_frame)
    modified = modified.with_audio(video_clip.audio)
    return modified


# ─── Main Retention Pipeline ───────────────────────────────────────

def apply_retention_effects(video_clip, max_gap_sec=3.0, low_threshold=0.35,
                            energy_map=None):
    """
    Analyze audio energy and inject pattern interrupts
    at points where attention might drop.
    
    BUG-03 FIX: Accepts pre-computed energy_map to avoid double analysis.
    v10: 16 effects, beat-aware, smarter detection.
    
    Returns: modified video clip
    """
    # BUG-03 FIX: Use provided energy_map if available
    if energy_map is None:
        print("[RETENTION] 🧠 Analizando energía del audio...")
        energy_map = analyze_energy(video_clip.audio)
    else:
        print(f"[RETENTION] 🧠 Usando energy_map pre-calculado ({len(energy_map)} puntos)")
    
    print("[RETENTION] 🔍 Detectando zonas de baja retención...")
    low_zones = detect_low_energy_zones(energy_map, max_gap_sec, low_threshold)
    print(f"[RETENTION] ⚡ Encontradas {len(low_zones)} zonas de baja retención")
    
    if not low_zones:
        print("[RETENTION] ✅ El ritmo del vídeo es bueno, no se necesitan interrupts")
        return video_clip
    
    # Plan interrupts
    interrupt_plan = []
    for start, end in low_zones:
        t = start + 0.8
        while t < end - 0.3:
            effect_fn, effect_dur, effect_name = pick_interrupt_effect()
            interrupt_plan.append({
                "time": t,
                "duration": effect_dur,
                "fn": effect_fn,
                "name": effect_name
            })
            t += random.uniform(1.5, 3.0)
    
    print(f"[RETENTION] 💥 Inyectando {len(interrupt_plan)} pattern interrupts")
    
    # Build frame lookup
    fps = video_clip.fps
    interrupt_by_frame = {}
    for intr in interrupt_plan:
        start_frame = int(intr["time"] * fps)
        end_frame = int((intr["time"] + intr["duration"]) * fps)
        for f in range(start_frame, end_frame + 1):
            interrupt_by_frame[f] = intr["fn"]
    
    def process_frame(get_frame, t):
        frame = get_frame(t)
        frame_idx = int(t * fps)
        if frame_idx in interrupt_by_frame:
            effect_fn = interrupt_by_frame[frame_idx]
            frame = effect_fn(frame)
        return frame
    
    modified = video_clip.transform(process_frame)
    modified = modified.with_audio(video_clip.audio)
    
    print("[RETENTION] ✅ Efectos de retención aplicados")
    return modified
