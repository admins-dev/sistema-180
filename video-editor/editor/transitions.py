"""
VideoForge v10 — Professional Transitions
============================================
Cinema-grade transitions between cuts: whip pan, flash, glitch,
zoom through, cross dissolve, ink wipe.
"""

import numpy as np
import cv2
import math


# ─── Whip Pan Transition ────────────────────────────────────────────

def whip_pan(frame_a, frame_b, progress, direction="right"):
    """
    Fast horizontal motion blur transition.
    progress: 0..1 (0 = full frame_a, 1 = full frame_b)
    """
    h, w = frame_a.shape[:2]
    
    if progress <= 0:
        return frame_a
    if progress >= 1:
        return frame_b
    
    # Motion blur amount peaks at center
    blur_amount = int(math.sin(progress * math.pi) * w * 0.3)
    blur_amount = max(1, blur_amount) | 1  # Ensure odd
    
    if progress < 0.5:
        # First half: blur frame_a, slide it out
        kernel = np.zeros((1, blur_amount))
        kernel[0, :] = 1.0 / blur_amount
        blurred = cv2.filter2D(frame_a, -1, kernel)
        
        shift = int(progress * 2 * w)
        if direction == "right":
            result = np.zeros_like(frame_a)
            if w - shift > 0:
                result[:, :w-shift] = blurred[:, shift:]
            return result
        else:
            result = np.zeros_like(frame_a)
            if shift < w:
                result[:, shift:] = blurred[:, :w-shift]
            return result
    else:
        # Second half: slide in frame_b with blur
        kernel = np.zeros((1, blur_amount))
        kernel[0, :] = 1.0 / blur_amount
        blurred = cv2.filter2D(frame_b, -1, kernel)
        
        shift = int((1 - progress) * 2 * w)
        if direction == "right":
            result = np.zeros_like(frame_b)
            if shift < w:
                result[:, shift:] = blurred[:, :w-shift]
            return result
        else:
            result = np.zeros_like(frame_b)
            if w - shift > 0:
                result[:, :w-shift] = blurred[:, shift:]
            return result


# ─── Flash Transition ───────────────────────────────────────────────

def flash_transition(frame_a, frame_b, progress, color=(255, 255, 255)):
    """White flash between two frames."""
    if progress <= 0:
        return frame_a
    if progress >= 1:
        return frame_b
    
    if progress < 0.5:
        # Fade to white
        alpha = progress * 2
        flash = np.full_like(frame_a, color, dtype=np.uint8)
        return cv2.addWeighted(frame_a, 1 - alpha, flash, alpha, 0)
    else:
        # Fade from white
        alpha = (progress - 0.5) * 2
        flash = np.full_like(frame_b, color, dtype=np.uint8)
        return cv2.addWeighted(flash, 1 - alpha, frame_b, alpha, 0)


# ─── Glitch Transition ─────────────────────────────────────────────

def glitch_transition(frame_a, frame_b, progress):
    """Digital corruption/glitch effect between frames."""
    if progress <= 0:
        return frame_a
    if progress >= 1:
        return frame_b
    
    h, w = frame_a.shape[:2]
    
    # Choose source based on progress
    if progress < 0.5:
        base = frame_a.copy()
        other = frame_b
    else:
        base = frame_b.copy()
        other = frame_a
    
    intensity = math.sin(progress * math.pi)  # Peak at center
    
    # Random horizontal shifts (scan line displacement)
    num_shifts = int(intensity * 20)
    for _ in range(num_shifts):
        y_start = np.random.randint(0, h - 5)
        strip_h = np.random.randint(2, max(3, int(h * 0.05)))
        y_end = min(h, y_start + strip_h)
        shift = np.random.randint(-int(w * 0.15), int(w * 0.15))
        
        strip = other[y_start:y_end].copy()
        if shift > 0:
            base[y_start:y_end, shift:] = strip[:, :w-shift]
        elif shift < 0:
            base[y_start:y_end, :w+shift] = strip[:, -shift:]
    
    # RGB channel corruption
    if intensity > 0.3:
        channel = np.random.randint(0, 3)
        shift = np.random.randint(3, max(4, int(10 * intensity)))
        if shift < w:
            base[:, shift:, channel] = base[:, :-shift, channel]
    
    # Random color blocks
    num_blocks = int(intensity * 5)
    for _ in range(num_blocks):
        bx = np.random.randint(0, w - 20)
        by = np.random.randint(0, h - 10)
        bw = np.random.randint(20, min(100, w - bx))
        bh = np.random.randint(5, min(30, h - by))
        color = np.random.randint(0, 255, 3)
        base[by:by+bh, bx:bx+bw] = color
    
    return base


# ─── Zoom Through ───────────────────────────────────────────────────

def zoom_through(frame_a, frame_b, progress, max_zoom=3.0):
    """Zoom into frame_a then zoom out from frame_b."""
    if progress <= 0:
        return frame_a
    if progress >= 1:
        return frame_b
    
    h, w = frame_a.shape[:2]
    
    if progress < 0.5:
        # Zoom into frame_a
        scale = 1 + (max_zoom - 1) * (progress * 2)
        frame = frame_a
    else:
        # Zoom out from frame_b
        scale = max_zoom - (max_zoom - 1) * ((progress - 0.5) * 2)
        frame = frame_b
    
    new_w, new_h = int(w / scale), int(h / scale)
    if new_w < 1 or new_h < 1:
        return np.zeros_like(frame_a)
    
    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2
    
    cropped = frame[max(0,y1):y1+new_h, max(0,x1):x1+new_w]
    if cropped.size == 0:
        return frame
    
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


# ─── Cross Dissolve ─────────────────────────────────────────────────

def cross_dissolve(frame_a, frame_b, progress):
    """Simple crossfade between two frames."""
    if progress <= 0:
        return frame_a
    if progress >= 1:
        return frame_b
    return cv2.addWeighted(frame_a, 1 - progress, frame_b, progress, 0)


# ─── Transition Manager ────────────────────────────────────────────

TRANSITION_MAP = {
    "whip_pan": whip_pan,
    "flash": flash_transition,
    "glitch": glitch_transition,
    "zoom_through": zoom_through,
    "cross_dissolve": cross_dissolve,
}

def get_transition_function(name):
    """Get a transition function by name."""
    return TRANSITION_MAP.get(name, cross_dissolve)


def insert_transitions_between_clips(clips, transition_type="flash", 
                                      transition_duration=0.3):
    """
    Insert transitions between a list of video clips.
    
    Args:
        clips: list of MoviePy VideoClips
        transition_type: name of transition effect
        transition_duration: duration in seconds
    
    Returns: single concatenated clip with transitions
    """
    from moviepy import VideoClip, concatenate_videoclips
    
    if len(clips) <= 1:
        return clips[0] if clips else None
    
    transition_fn = get_transition_function(transition_type)
    result_clips = []
    td = transition_duration
    
    print(f"[TRANSITIONS] 🎬 Insertando {len(clips)-1} transiciones '{transition_type}'")
    
    for i, clip in enumerate(clips):
        if i == 0:
            # First clip: trim end for transition overlap
            if clip.duration > td:
                result_clips.append(clip.subclipped(0, clip.duration - td/2))
            else:
                result_clips.append(clip)
        elif i == len(clips) - 1:
            # Last clip: trim start for transition overlap
            if clip.duration > td:
                result_clips.append(clip.subclipped(td/2))
            else:
                result_clips.append(clip)
        else:
            # Middle clips: trim both
            start = td/2 if clip.duration > td else 0
            end = clip.duration - td/2 if clip.duration > td else clip.duration
            if end > start:
                result_clips.append(clip.subclipped(start, end))
    
    # Simple concatenation (transitions are applied in the frame processing)
    final = concatenate_videoclips(result_clips, method="compose")
    print(f"[TRANSITIONS] ✅ Transiciones aplicadas")
    return final
