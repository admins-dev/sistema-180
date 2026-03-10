"""
VideoForge v10 — VFX Engine (After Effects Level)
====================================================
Professional visual effects: light leaks, lens flare, film grain,
chromatic aberration, speed ramp, glow, camera shake, particles, letterbox.
"""

import numpy as np
import cv2
import math
import random


# ─── Easing Functions ───────────────────────────────────────────────

def ease_in_out(t):
    return 0.5 * (1 - math.cos(math.pi * max(0, min(1, t))))

def ease_out_bounce(t):
    t = max(0, min(1, t))
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625 * t * t + 0.984375

def ease_out_elastic(t):
    t = max(0, min(1, t))
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1


# ─── Film Grain ─────────────────────────────────────────────────────

def apply_film_grain(frame, intensity=0.08, size=1):
    """Add cinematic film grain noise."""
    h, w = frame.shape[:2]
    if size > 1:
        gh, gw = h // size, w // size
        grain = np.random.normal(0, intensity * 255, (gh, gw, 1)).astype(np.float32)
        grain = cv2.resize(grain, (w, h))
        if len(grain.shape) == 2:
            grain = grain[:, :, np.newaxis]
    else:
        grain = np.random.normal(0, intensity * 255, (h, w, 1)).astype(np.float32)
    
    result = frame.astype(np.float32) + grain
    return np.clip(result, 0, 255).astype(np.uint8)


# ─── Light Leak ─────────────────────────────────────────────────────

_light_leak_cache = {}

def apply_light_leak(frame, t, duration, leak_color=(255, 180, 100), 
                     intensity=0.3, position="right"):
    """
    Apply warm analog light leak overlay.
    Fades in and out over the duration.
    BUG-13 FIX: Vectorized gradient with numpy broadcasting.
    """
    h, w = frame.shape[:2]
    progress = t / max(duration, 0.001)
    
    # Fade in first 20%, hold 60%, fade out last 20%
    if progress < 0.2:
        alpha = ease_in_out(progress / 0.2) * intensity
    elif progress > 0.8:
        alpha = ease_in_out((1 - progress) / 0.2) * intensity
    else:
        alpha = intensity
    
    if alpha < 0.01:
        return frame
    
    # Create gradient leak — VECTORIZED (no Python loops)
    leak = np.zeros((h, w, 3), dtype=np.float32)
    color = np.array(leak_color, dtype=np.float32)
    
    if position == "right":
        ratios = (np.linspace(0, 1, w) ** 2).reshape(1, w, 1)
        leak = color.reshape(1, 1, 3) * ratios
    elif position == "left":
        ratios = (np.linspace(1, 0, w) ** 2).reshape(1, w, 1)
        leak = color.reshape(1, 1, 3) * ratios
    elif position == "top":
        ratios = (np.linspace(1, 0, h) ** 2).reshape(h, 1, 1)
        leak = color.reshape(1, 1, 3) * ratios
    else:  # center
        cy, cx = h // 2, w // 2
        Y, X = np.ogrid[:h, :w]
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2).astype(np.float32) / max(w, h)
        falloff = np.exp(-dist * 3)[:, :, np.newaxis]
        leak = color.reshape(1, 1, 3) * falloff
    
    result = frame.astype(np.float32) + leak * alpha
    return np.clip(result, 0, 255).astype(np.uint8)


# ─── Lens Flare ─────────────────────────────────────────────────────

def apply_lens_flare(frame, x=0.7, y=0.3, intensity=0.5, radius=150):
    """Add a lens flare at the given position."""
    h, w = frame.shape[:2]
    cx, cy = int(x * w), int(y * h)
    
    result = frame.astype(np.float32)
    
    # Main flare circle
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X - cx)**2 + (Y - cy)**2).astype(np.float32)
    
    # Core bright spot
    core = np.exp(-(dist / (radius * 0.3))**2) * intensity * 255
    result[:, :, 0] += core * 0.9   # R
    result[:, :, 1] += core * 0.95  # G
    result[:, :, 2] += core         # B
    
    # Outer glow
    glow = np.exp(-(dist / radius)**2) * intensity * 128
    result[:, :, 0] += glow * 0.8
    result[:, :, 1] += glow * 0.6
    result[:, :, 2] += glow * 0.9
    
    # Streak (horizontal)
    streak_mask = np.exp(-((Y - cy) / 20)**2) * np.exp(-(dist / (radius * 3))**2)
    result[:, :, 0] += streak_mask * intensity * 100
    result[:, :, 1] += streak_mask * intensity * 80
    result[:, :, 2] += streak_mask * intensity * 120
    
    return np.clip(result, 0, 255).astype(np.uint8)


# ─── Chromatic Aberration ───────────────────────────────────────────

def apply_chromatic_aberration(frame, intensity=3):
    """RGB channel shift for dramatic edges."""
    h, w = frame.shape[:2]
    shift = max(1, int(intensity))
    
    result = frame.copy()
    # Shift red channel right
    result[:, shift:, 0] = frame[:, :-shift, 0]
    # Shift blue channel left
    result[:, :-shift, 2] = frame[:, shift:, 2]
    
    return result


# ─── Glow / Bloom ───────────────────────────────────────────────────

def apply_glow(frame, threshold=200, intensity=0.4, blur_size=51):
    """Bloom effect — bright areas bleed light."""
    # Extract bright areas
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    _, bright_mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    
    # Create glow from bright areas
    bright = cv2.bitwise_and(frame, frame, mask=bright_mask)
    blur_size = blur_size | 1  # Ensure odd
    glow = cv2.GaussianBlur(bright, (blur_size, blur_size), 0)
    
    # Blend
    result = cv2.addWeighted(frame, 1.0, glow, intensity, 0)
    return result


# ─── Camera Shake ───────────────────────────────────────────────────

_shake_offsets = {}

def apply_camera_shake(frame, t, intensity=5, frequency=15):
    """Handheld camera shake effect.
    BUG-04 FIX: Uses local RandomState instead of corrupting global seed.
    """
    # Deterministic shake based on time — LOCAL random state
    seed = int(t * frequency * 100) % (2**31)
    rng = np.random.RandomState(seed)
    
    dx = int(rng.normal(0, intensity))
    dy = int(rng.normal(0, intensity))
    
    h, w = frame.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    result = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    
    return result


# ─── Letterbox ──────────────────────────────────────────────────────

def apply_letterbox(frame, ratio=2.39):
    """Add cinematic letterbox bars."""
    h, w = frame.shape[:2]
    target_h = int(w / ratio)
    
    if target_h >= h:
        return frame
    
    bar_height = (h - target_h) // 2
    result = frame.copy()
    result[:bar_height, :] = 0
    result[h - bar_height:, :] = 0
    
    return result


# ─── Particles / Bokeh ──────────────────────────────────────────────

class ParticleSystem:
    """Floating bokeh/dust particles overlay."""
    
    def __init__(self, frame_size, count=30, seed=42):
        w, h = frame_size
        rng = np.random.RandomState(seed)
        self.particles = []
        for _ in range(count):
            self.particles.append({
                "x": rng.uniform(0, w),
                "y": rng.uniform(0, h),
                "vx": rng.uniform(-0.3, 0.3),
                "vy": rng.uniform(-0.5, -0.1),
                "size": rng.uniform(3, 12),
                "alpha": rng.uniform(0.1, 0.4),
                "phase": rng.uniform(0, math.pi * 2),
            })
        self.w, self.h = w, h
    
    def render(self, frame, t):
        overlay = frame.copy()
        for p in self.particles:
            x = (p["x"] + p["vx"] * t * 30) % self.w
            y = (p["y"] + p["vy"] * t * 30) % self.h
            size = int(p["size"] + math.sin(t * 2 + p["phase"]) * 2)
            alpha = p["alpha"] * (0.7 + 0.3 * math.sin(t * 1.5 + p["phase"]))
            
            if size > 0:
                cv2.circle(overlay, (int(x), int(y)), size, 
                          (255, 240, 220), -1)
        
        result = cv2.addWeighted(frame, 1.0, overlay, 0.15, 0)
        return result


# ─── Speed Ramp ─────────────────────────────────────────────────────

def create_speed_ramp_timeline(duration, climax_times, slow_factor=0.5, 
                                fast_factor=2.0, ramp_duration=0.5):
    """
    Create a time-remapping function for speed ramps.
    Slows down before climax, speeds up after.
    """
    def remap_time(t):
        for ct in climax_times:
            # Slow zone: 1s before climax
            if ct - 1.5 < t < ct:
                return t  # Will be processed with slow_factor
            # Fast zone: right after climax
            if ct < t < ct + 0.5:
                return t  # Will be processed with fast_factor
        return t
    
    return remap_time


# ─── VFX Pipeline ───────────────────────────────────────────────────

def apply_vfx(video_clip, effects=None, energy_map=None):
    """
    Apply After Effects-level visual effects to a video clip.
    
    Args:
        video_clip: MoviePy video clip
        effects: dict of effect configs, e.g.:
            {
                "film_grain": {"intensity": 0.06},
                "light_leak": {"intensity": 0.25, "position": "right"},
                "lens_flare": {"intensity": 0.3},
                "chromatic_aberration": {"intensity": 3},
                "glow": {"threshold": 200, "intensity": 0.3},
                "camera_shake": {"intensity": 3},
                "letterbox": {"ratio": 2.39},
                "particles": {"count": 25},
            }
        energy_map: Audio energy data for reactive effects
    
    Returns: Modified video clip
    """
    if effects is None:
        effects = {}
    
    fps = video_clip.fps
    duration = video_clip.duration
    w, h = video_clip.size
    
    # Pre-initialize particle system if needed
    particles = None
    if "particles" in effects:
        particles = ParticleSystem((w, h), effects["particles"].get("count", 25))
    
    # Detect climax moments for reactive effects
    climax_times = []
    if energy_map:
        for entry in energy_map:
            if entry.get("is_climax", False):
                climax_times.append(entry["time"])
    
    active_fx = list(effects.keys())
    print(f"[VFX] 🎬 Aplicando {len(active_fx)} efectos: {', '.join(active_fx)}")
    
    def process_frame(get_frame, t):
        frame = get_frame(t)
        
        # Check if we're near a climax moment
        near_climax = any(abs(t - ct) < 1.0 for ct in climax_times)
        
        # Film grain (subtle, always on)
        if "film_grain" in effects:
            cfg = effects["film_grain"]
            frame = apply_film_grain(frame, 
                                     intensity=cfg.get("intensity", 0.06),
                                     size=cfg.get("size", 1))
        
        # Light leak
        if "light_leak" in effects:
            cfg = effects["light_leak"]
            # Cycle light leaks every 8 seconds
            cycle_t = t % 8.0
            if cycle_t < 3.0:  # 3s leak every 8s
                frame = apply_light_leak(frame, cycle_t, 3.0,
                                         intensity=cfg.get("intensity", 0.25),
                                         position=cfg.get("position", "right"))
        
        # Lens flare (on climax moments)
        if "lens_flare" in effects and near_climax:
            cfg = effects["lens_flare"]
            frame = apply_lens_flare(frame,
                                     intensity=cfg.get("intensity", 0.4))
        
        # Chromatic aberration (on climax or always subtle)
        if "chromatic_aberration" in effects:
            cfg = effects["chromatic_aberration"]
            intensity = cfg.get("intensity", 2)
            if near_climax:
                intensity *= 2  # Double on climax
            frame = apply_chromatic_aberration(frame, intensity=intensity)
        
        # Glow / bloom
        if "glow" in effects:
            cfg = effects["glow"]
            frame = apply_glow(frame,
                               threshold=cfg.get("threshold", 200),
                               intensity=cfg.get("intensity", 0.3))
        
        # Camera shake (on climax)
        if "camera_shake" in effects:
            cfg = effects["camera_shake"]
            intensity = cfg.get("intensity", 4)
            if near_climax:
                intensity *= 2
            frame = apply_camera_shake(frame, t, intensity=intensity)
        
        # Particles / bokeh
        if particles:
            frame = particles.render(frame, t)
        
        # Letterbox (always last)
        if "letterbox" in effects:
            cfg = effects["letterbox"]
            frame = apply_letterbox(frame, ratio=cfg.get("ratio", 2.39))
        
        return frame
    
    modified = video_clip.transform(process_frame)
    modified = modified.with_audio(video_clip.audio)
    
    print(f"[VFX] ✅ {len(active_fx)} efectos aplicados")
    return modified
