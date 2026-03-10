"""
VideoForge — Overlays Module
B-Roll pop-ups, keyword-triggered images, lower thirds, and logo watermarks.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ---------- Animation Easings ---------- #

def bounce_ease_out(t):
    """Bounce easing for pop-in animations."""
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


def elastic_ease_out(t):
    """Elastic ease-out for springy pop-in."""
    if t == 0 or t == 1:
        return t
    return math.pow(2, -10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1


# ---------- Overlay Renderers ---------- #

def render_popup_overlay(frame_size, image_path, t, popup_start, popup_duration=1.5,
                          position="right", size_ratio=0.2):
    """
    Render a pop-up image overlay with bounce-in animation.
    
    Args:
        frame_size: (width, height) of video
        image_path: Path to overlay image (PNG with transparency)
        t: Current time
        popup_start: Time when popup should appear
        popup_duration: How long the popup is visible
        position: "right", "left", "top-right", "center"
        size_ratio: Size of overlay relative to frame width
    
    Returns:
        RGBA numpy array overlay
    """
    w, h = frame_size
    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    
    elapsed = t - popup_start
    if elapsed < 0 or elapsed > popup_duration:
        return overlay
    
    # Load and resize image
    try:
        img = Image.open(image_path).convert('RGBA')
    except Exception:
        return overlay
    
    target_size = int(w * size_ratio)
    img_ratio = img.height / img.width
    img = img.resize((target_size, int(target_size * img_ratio)), Image.LANCZOS)
    
    # Animation phases
    anim_in_duration = 0.3
    anim_out_duration = 0.3
    
    if elapsed < anim_in_duration:
        # Pop in with bounce
        progress = elapsed / anim_in_duration
        scale = bounce_ease_out(progress)
        alpha = min(1.0, progress * 2)
    elif elapsed > popup_duration - anim_out_duration:
        # Fade out
        progress = (elapsed - (popup_duration - anim_out_duration)) / anim_out_duration
        scale = 1.0
        alpha = 1.0 - progress
    else:
        # Fully visible, slight floating animation
        scale = 1.0
        alpha = 1.0
    
    # Scale the image
    scaled_w = max(1, int(img.width * scale))
    scaled_h = max(1, int(img.height * scale))
    scaled_img = img.resize((scaled_w, scaled_h), Image.LANCZOS)
    
    # Apply alpha
    img_array = np.array(scaled_img)
    img_array[:, :, 3] = (img_array[:, :, 3] * alpha).astype(np.uint8)
    
    # Position
    margin = int(w * 0.05)
    if position == "right":
        x = w - scaled_w - margin
        y = h // 2 - scaled_h // 2
    elif position == "left":
        x = margin
        y = h // 2 - scaled_h // 2
    elif position == "top-right":
        x = w - scaled_w - margin
        y = margin
    elif position == "center":
        x = w // 2 - scaled_w // 2
        y = h // 2 - scaled_h // 2
    else:
        x = w - scaled_w - margin
        y = h // 2 - scaled_h // 2
    
    # Floating animation (subtle vertical movement)
    if anim_in_duration < elapsed < popup_duration - anim_out_duration:
        float_offset = int(math.sin(elapsed * 3) * 5)
        y += float_offset
    
    # Clamp position
    x = max(0, min(x, w - scaled_w))
    y = max(0, min(y, h - scaled_h))
    
    # Paste into overlay
    overlay[y:y + scaled_h, x:x + scaled_w] = img_array
    
    return overlay


def render_lower_third(frame_size, text, t, start_time, duration=3.0,
                        bg_color=(30, 30, 30, 220), text_color=(255, 255, 255),
                        accent_color=(255, 215, 0)):
    """
    Render a professional lower third bar with animated text.
    
    Args:
        frame_size: (width, height)
        text: Text to display
        t: Current time
        start_time: When to show the lower third
        duration: Display duration
        bg_color: Background color (RGBA)
        text_color: Text color (RGB)
        accent_color: Accent line color (RGB)
    
    Returns:
        RGBA numpy array overlay
    """
    w, h = frame_size
    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    
    elapsed = t - start_time
    if elapsed < 0 or elapsed > duration:
        return overlay
    
    # Dimensions
    bar_height = int(h * 0.08)
    bar_y = int(h * 0.80)
    accent_height = 4
    padding = int(w * 0.03)
    
    # Animation
    anim_duration = 0.4
    if elapsed < anim_duration:
        progress = elastic_ease_out(elapsed / anim_duration)
        bar_width = int(w * 0.5 * progress)
        text_alpha = max(0, (progress - 0.5) * 2)
    elif elapsed > duration - anim_duration:
        progress = 1 - ((elapsed - (duration - anim_duration)) / anim_duration)
        bar_width = int(w * 0.5 * progress)
        text_alpha = progress
    else:
        bar_width = int(w * 0.5)
        text_alpha = 1.0
    
    # Draw background bar
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Main bar
    draw.rectangle(
        [padding, bar_y, padding + bar_width, bar_y + bar_height],
        fill=bg_color
    )
    
    # Accent line on top
    draw.rectangle(
        [padding, bar_y, padding + bar_width, bar_y + accent_height],
        fill=accent_color + (255,)
    )
    
    # Text
    font_size = int(bar_height * 0.5)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text_x = padding + int(w * 0.02)
    text_y = bar_y + (bar_height - font_size) // 2 + accent_height // 2
    
    text_rgba = text_color + (int(255 * text_alpha),)
    draw.text((text_x, text_y), text, font=font, fill=text_rgba)
    
    return np.array(img)


def render_watermark(frame_size, logo_path, opacity=0.3, position="bottom-right",
                      size_ratio=0.08):
    """
    Render a static logo watermark overlay.
    
    Args:
        frame_size: (width, height)
        logo_path: Path to logo image
        opacity: Watermark opacity (0-1)
        position: "bottom-right", "bottom-left", "top-right", "top-left"
        size_ratio: Size relative to frame width
    
    Returns:
        RGBA numpy array (static overlay, apply on every frame)
    """
    w, h = frame_size
    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    
    try:
        logo = Image.open(logo_path).convert('RGBA')
    except Exception:
        return overlay
    
    target_size = int(w * size_ratio)
    logo_ratio = logo.height / logo.width
    logo = logo.resize((target_size, int(target_size * logo_ratio)), Image.LANCZOS)
    
    # Apply opacity
    logo_array = np.array(logo)
    logo_array[:, :, 3] = (logo_array[:, :, 3] * opacity).astype(np.uint8)
    
    margin = int(w * 0.02)
    
    if position == "bottom-right":
        x = w - logo.width - margin
        y = h - logo.height - margin
    elif position == "bottom-left":
        x = margin
        y = h - logo.height - margin
    elif position == "top-right":
        x = w - logo.width - margin
        y = margin
    elif position == "top-left":
        x = margin
        y = margin
    else:
        x = w - logo.width - margin
        y = h - logo.height - margin
    
    overlay[y:y + logo.height, x:x + logo.width] = logo_array
    
    return overlay


def detect_keyword_timestamps(words, keywords):
    """
    Find timestamps where specific keywords are spoken.
    
    Args:
        words: List of word dicts from Whisper transcription
        keywords: Dict mapping keyword to overlay config
                  e.g. {"dinero": {"image": "money.png", "position": "right"}}
    
    Returns:
        List of (timestamp, keyword, config) tuples
    """
    triggers = []
    for word_info in words:
        word_lower = word_info["word"].lower().strip(".,!?¿¡\"'")
        for keyword, keyword_config in keywords.items():
            if keyword.lower() in word_lower:
                triggers.append((word_info["start"], keyword, keyword_config))
    
    return triggers


if __name__ == "__main__":
    print("Overlays module — Usa pipeline.py para aplicar overlays a tus vídeos.")
    print("Funciones disponibles: popup, lower_third, watermark, keyword_detection")
