"""
VideoForge v10 — Compositing Engine
======================================
Professional compositing: 10 color grades (LUTs), AI background removal,
text behind person, cinematic letterbox, motion blur, vignette.
"""

import numpy as np
import cv2
import math


# ─── Color Grading LUTs ────────────────────────────────────────────

def apply_color_grade(frame, style="cinematic"):
    """
    Apply professional color grading.
    v10: 10 styles available.
    """
    result = frame.astype(np.float32)
    
    if style == "cinematic":
        # Orange & teal — Hollywood standard
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.1 + 10, 0, 255)  # R warm
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.95, 0, 255)       # G down
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.15 + 8, 0, 255)   # B teal
        # Lift shadows
        result = np.where(result < 60, result * 1.1 + 5, result)
        
    elif style == "warm":
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.15 + 15, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 1.05 + 5, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.9, 0, 255)
        
    elif style == "cold":
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.85, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.95 + 5, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.2 + 15, 0, 255)
        
    elif style == "dramatic":
        # High contrast + desaturated
        gray = np.mean(result, axis=2, keepdims=True)
        result = result * 0.6 + gray * 0.4  # Partial desaturation
        result = np.clip((result - 128) * 1.4 + 128, 0, 255)
        
    elif style == "vintage":
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.05 + 20, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.9 + 10, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.8, 0, 255)
        # Fade blacks
        result = np.clip(result + 15, 0, 255)
        
    elif style == "neon":
        # Vibrant, saturated neon colors
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5, 0, 255)  # Boost saturation
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255)   # Brighter
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
        
    elif style == "noir":
        # Black and white with high contrast
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = np.clip((gray.astype(np.float32) - 128) * 1.5 + 128, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB).astype(np.float32)
        
    elif style == "sunset":
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.2 + 20, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.85 + 10, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.7, 0, 255)
        
    elif style == "matrix":
        # Green tint like The Matrix
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.3, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 1.3 + 10, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.3, 0, 255)
        
    elif style == "bleach":
        # Bleach bypass — desaturated high contrast
        gray = np.mean(result, axis=2, keepdims=True)
        result = result * 0.5 + gray * 0.5
        result = np.clip((result - 128) * 1.6 + 128 + 10, 0, 255)
    
    return np.clip(result, 0, 255).astype(np.uint8)


# ─── Vignette ───────────────────────────────────────────────────────

def apply_vignette(frame, intensity=0.35):
    """Cinematic vignette with smooth falloff."""
    h, w = frame.shape[:2]
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    
    dist = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    # Smooth falloff starting from 60% of the distance
    vignette = 1 - np.clip((dist - 0.6) / 0.8, 0, 1) * intensity
    
    result = frame.astype(np.float32)
    for c in range(3):
        result[:, :, c] *= vignette
    
    return np.clip(result, 0, 255).astype(np.uint8)


# ─── Letterbox ──────────────────────────────────────────────────────

def apply_letterbox(frame, ratio=2.39):
    """Cinematic widescreen bars."""
    h, w = frame.shape[:2]
    target_h = int(w / ratio)
    if target_h >= h:
        return frame
    
    bar_height = (h - target_h) // 2
    result = frame.copy()
    result[:bar_height, :] = 0
    result[h - bar_height:, :] = 0
    return result


# ─── Motion Blur ────────────────────────────────────────────────────

def apply_motion_blur(frame, amount=15, angle=0):
    """Directional motion blur."""
    kernel_size = max(1, int(amount)) | 1
    
    if angle == 0:  # Horizontal
        kernel = np.zeros((1, kernel_size))
        kernel[0, :] = 1.0 / kernel_size
    elif angle == 90:  # Vertical
        kernel = np.zeros((kernel_size, 1))
        kernel[:, 0] = 1.0 / kernel_size
    else:
        # Angled blur
        kernel = np.zeros((kernel_size, kernel_size))
        center = kernel_size // 2
        rad = math.radians(angle)
        for i in range(kernel_size):
            x = int(center + (i - center) * math.cos(rad))
            y = int(center + (i - center) * math.sin(rad))
            if 0 <= x < kernel_size and 0 <= y < kernel_size:
                kernel[y, x] = 1
        s = kernel.sum()
        if s > 0:
            kernel /= s
    
    return cv2.filter2D(frame, -1, kernel)


# ─── Background Removal (AI) ───────────────────────────────────────

_bg_model = None

def remove_background(frame):
    """Remove background using MediaPipe (fast) or rembg (quality)."""
    global _bg_model
    
    try:
        import mediapipe as mp
        if _bg_model is None:
            _bg_model = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)
        
        results = _bg_model.process(frame)
        mask = results.segmentation_mask
        mask = (mask > 0.5).astype(np.uint8) * 255
        return mask
    except ImportError:
        pass
    
    try:
        from rembg import remove
        result = remove(frame)
        if result.shape[2] == 4:
            return result[:, :, 3]
        return np.ones(frame.shape[:2], dtype=np.uint8) * 255
    except ImportError:
        return np.ones(frame.shape[:2], dtype=np.uint8) * 255


def text_behind_person(frame, text, frame_idx):
    """Place text behind the person (3D effect)."""
    from PIL import Image, ImageDraw, ImageFont
    
    h, w = frame.shape[:2]
    mask = remove_background(frame)
    
    # Create text layer
    text_layer = np.zeros((h, w, 3), dtype=np.uint8)
    pil_img = Image.fromarray(text_layer)
    draw = ImageDraw.Draw(pil_img)
    
    try:
        font = ImageFont.truetype("arial.ttf", min(w // 6, 120))
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (w - tw) // 2, (h - th) // 2
    
    draw.text((tx, ty), text, fill=(255, 255, 255), font=font)
    text_frame = np.array(pil_img)
    
    # BUG-06 FIX: Correct composite — text where no person, person on top
    mask_3d = np.stack([mask] * 3, axis=2).astype(np.float32) / 255
    result = text_frame.astype(np.float32) * (1 - mask_3d) + frame.astype(np.float32) * mask_3d
    
    return np.clip(result, 0, 255).astype(np.uint8)


# ─── Main Compositing Pipeline ─────────────────────────────────────

def apply_compositing(video_clip, text_behind=None, color_grade="cinematic",
                      vignette=True, letterbox=False, output_path=None):
    """
    Apply professional compositing effects.
    
    v10: 10 color grades, letterbox option, improved vignette.
    """
    fps = video_clip.fps
    effects = []
    
    if color_grade:
        effects.append(f"color_{color_grade}")
    if text_behind:
        effects.append("text_behind")
    if vignette:
        effects.append("vignette")
    if letterbox:
        effects.append("letterbox")
    
    print(f"[COMPOSITING] 🎨 Aplicando: {', '.join(effects)}")
    
    def process_frame(get_frame, t):
        frame = get_frame(t)
        frame_idx = int(t * fps)
        
        if color_grade:
            frame = apply_color_grade(frame, color_grade)
        
        if text_behind:
            frame = text_behind_person(frame, text_behind, frame_idx)
        
        if vignette:
            frame = apply_vignette(frame, intensity=0.35)
        
        if letterbox:
            frame = apply_letterbox(frame, ratio=2.39)
        
        return frame
    
    modified = video_clip.transform(process_frame)
    modified = modified.with_audio(video_clip.audio)
    
    if output_path:
        modified.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=8,
            logger="bar"
        )
        print(f"[COMPOSITING] ✅ Guardado en {output_path}")
    
    print(f"[COMPOSITING] ✅ Efectos aplicados")
    return modified
