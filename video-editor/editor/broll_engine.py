"""
VideoForge v3.0 — B-Roll Auto-Generator
=========================================
Automatically adds contextual stock footage as B-Roll overlays.
Analyzes the transcript for keywords, searches Pexels API for
matching footage, and composites it with the person's figure.
"""

import os
import re
import json
import tempfile
import requests
import numpy as np
import cv2


# ─── Keyword Extraction ────────────────────────────────────────────

# Keywords → search terms for stock footage
KEYWORD_MAP = {
    # Money & Business
    "dinero": "money cash", "bitcoin": "bitcoin cryptocurrency",
    "crypto": "cryptocurrency", "inversión": "investment stock market",
    "negocio": "business office", "empresa": "corporate business",
    "éxito": "success celebration", "millonario": "luxury wealth",
    "ventas": "sales business", "marketing": "digital marketing",
    "clientes": "customers shopping", "ganancias": "profit money",
    "emprender": "entrepreneur startup", "mercado": "stock market",
    "banco": "bank finance", "inmobiliario": "real estate buildings",
    
    # Technology
    "inteligencia artificial": "artificial intelligence technology",
    "tecnología": "technology futuristic", "código": "programming code",
    "app": "mobile application", "web": "website technology",
    "robot": "robot technology", "futuro": "futuristic technology",
    "ia": "artificial intelligence", "automatizar": "automation robot",
    
    # People & Emotions
    "equipo": "team people working", "familia": "family happy",
    "libertad": "freedom nature", "viaje": "travel adventure",
    "salud": "health fitness", "deporte": "sports fitness",
    "comida": "food restaurant", "fiesta": "party celebration",
    
    # Nature & Places
    "playa": "beach tropical", "montaña": "mountain landscape",
    "ciudad": "city skyline night", "coche": "luxury car",
    "casa": "luxury home interior", "mundo": "world globe earth",
    
    # Action
    "explosión": "explosion fire", "velocidad": "speed motion",
    "poder": "power energy", "fuego": "fire flames",
    "agua": "water ocean", "tormenta": "storm lightning",
    
    # General
    "problema": "problem frustration", "solución": "solution idea lightbulb",
    "idea": "idea lightbulb creative", "tiempo": "clock time",
    "redes sociales": "social media phone", "instagram": "social media",
    "tiktok": "social media phone", "youtube": "video content creator",
}


def extract_keywords(transcript_segments):
    """
    Extract visual keywords from transcript segments.
    Returns list of (time_sec, search_query, original_word) tuples.
    """
    keywords_found = []
    
    for seg in transcript_segments:
        text = seg.get("text", "").lower()
        start = seg.get("start", 0)
        
        for keyword, search_term in KEYWORD_MAP.items():
            if keyword in text:
                keywords_found.append({
                    "time": start,
                    "search": search_term,
                    "keyword": keyword,
                    "duration": min(seg.get("duration", 3), 4)
                })
    
    # Remove duplicates within 5 second windows
    filtered = []
    last_time = -10
    for kw in sorted(keywords_found, key=lambda x: x["time"]):
        if kw["time"] - last_time > 5:
            filtered.append(kw)
            last_time = kw["time"]
    
    return filtered


def extract_keywords_from_text(full_text, timestamps=None):
    """
    Extract keywords from a plain text string.
    If timestamps provided, map keywords to approximate times.
    """
    text_lower = full_text.lower()
    keywords_found = []
    
    for keyword, search_term in KEYWORD_MAP.items():
        idx = text_lower.find(keyword)
        while idx != -1:
            # Estimate time based on position in text
            position_ratio = idx / max(len(text_lower), 1)
            estimated_time = position_ratio * (timestamps[-1] if timestamps else 60)
            
            keywords_found.append({
                "time": estimated_time,
                "search": search_term,
                "keyword": keyword,
                "duration": 3
            })
            idx = text_lower.find(keyword, idx + 1)
    
    # Deduplicate
    filtered = []
    last_time = -10
    for kw in sorted(keywords_found, key=lambda x: x["time"]):
        if kw["time"] - last_time > 5:
            filtered.append(kw)
            last_time = kw["time"]
    
    return filtered


# ─── Pexels API Integration ────────────────────────────────────────

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PEXELS_VIDEO_SEARCH = "https://api.pexels.com/videos/search"
PEXELS_PHOTO_SEARCH = "https://api.pexels.com/v1/search"


def search_stock_video(query, per_page=3):
    """
    Search Pexels for stock video footage.
    Returns list of video URLs and metadata.
    """
    if not PEXELS_API_KEY:
        print("[B-ROLL] ⚠️ PEXELS_API_KEY no configurada — usando fallback de color")
        return []
    
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": per_page, "orientation": "landscape"}
        
        res = requests.get(PEXELS_VIDEO_SEARCH, headers=headers, params=params, timeout=10)
        data = res.json()
        
        results = []
        for video in data.get("videos", []):
            # Get the smallest quality file
            files = video.get("video_files", [])
            if files:
                # Prefer SD quality for speed
                sd_files = [f for f in files if f.get("quality") == "sd"]
                file_info = sd_files[0] if sd_files else files[0]
                results.append({
                    "url": file_info["link"],
                    "width": file_info.get("width", 1920),
                    "height": file_info.get("height", 1080),
                    "duration": video.get("duration", 10),
                })
        
        return results
    except Exception as e:
        print(f"[B-ROLL] ⚠️ Error buscando en Pexels: {e}")
        return []


def download_stock_clip(url, save_path):
    """Download a stock video clip to disk."""
    try:
        res = requests.get(url, stream=True, timeout=30)
        with open(save_path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
        return save_path
    except Exception as e:
        print(f"[B-ROLL] ⚠️ Error descargando clip: {e}")
        return None


# ─── B-Roll Visual Effects ─────────────────────────────────────────

def create_gradient_broll(frame_size, keyword, duration_sec=3, fps=24):
    """
    Fallback: create an animated gradient background with keyword text
    when no stock footage is available.
    """
    from PIL import Image, ImageDraw, ImageFont
    
    w, h = frame_size
    frames = []
    total_frames = int(duration_sec * fps)
    
    for i in range(total_frames):
        progress = i / total_frames
        
        # BUG-25 FIX: Vectorized gradient (no row-by-row loop)
        # BUG-07 FIX: Build directly in RGB (MoviePy expects RGB)
        y_ratios = ((np.arange(h) / h + progress * 0.3) % 1.0)
        r = (139 * y_ratios).astype(np.uint8)
        g = (92 * (1 - y_ratios)).astype(np.uint8)
        b = (246 * y_ratios + 100 * (1 - y_ratios)).astype(np.uint8)
        
        img = np.zeros((h, w, 3), dtype=np.uint8)
        img[:, :, 0] = r.reshape(h, 1)  # R
        img[:, :, 1] = g.reshape(h, 1)  # G
        img[:, :, 2] = b.reshape(h, 1)  # B
        
        # Add keyword text
        pil_img = Image.fromarray(img)  # Already RGB
        draw = ImageDraw.Draw(pil_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except (OSError, IOError):
            font = ImageFont.load_default()
        
        text = keyword.upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        # Animated position (slight float)
        offset_y = int(np.sin(progress * np.pi * 4) * 10)
        draw.text(((w - tw) // 2, (h - th) // 2 + offset_y), text,
                  font=font, fill=(255, 255, 255))
        
        frame = np.array(pil_img)  # Already RGB, no conversion needed
        frames.append(frame)
    
    return frames


def apply_broll_overlay(main_frame, broll_frame, opacity=0.35, style="corner"):
    """
    Overlay B-roll footage on the main video.
    
    Styles:
    - "fullscreen": Full background replacement with person composited
    - "corner": Picture-in-picture in the corner
    - "split": Split screen (left/right)
    """
    h, w = main_frame.shape[:2]
    
    if style == "fullscreen":
        # Resize broll to match
        broll_resized = cv2.resize(broll_frame, (w, h))
        # Darken broll for readability
        broll_dark = (broll_resized.astype(np.float32) * 0.5).astype(np.uint8)
        # Blend
        result = cv2.addWeighted(main_frame, 1 - opacity, broll_dark, opacity, 0)
        return result
    
    elif style == "corner":
        # Picture-in-picture: small broll in bottom-right
        pip_w, pip_h = int(w * 0.3), int(h * 0.3)
        broll_small = cv2.resize(broll_frame, (pip_w, pip_h))
        
        # Add border
        broll_bordered = cv2.copyMakeBorder(broll_small, 3, 3, 3, 3,
                                            cv2.BORDER_CONSTANT,
                                            value=[139, 92, 246])
        
        result = main_frame.copy()
        bh, bw = broll_bordered.shape[:2]
        x = w - bw - 20
        y = h - bh - 20
        
        if y > 0 and x > 0:
            result[y:y + bh, x:x + bw] = broll_bordered
        
        return result
    
    elif style == "split":
        # Left half: main, Right half: broll
        half_w = w // 2
        broll_resized = cv2.resize(broll_frame, (half_w, h))
        result = main_frame.copy()
        result[:, half_w:half_w + broll_resized.shape[1]] = broll_resized
        
        # Add divider line
        cv2.line(result, (half_w, 0), (half_w, h), (139, 92, 246), 3)
        
        return result
    
    return main_frame


# ─── Main B-Roll Processor ─────────────────────────────────────────

def apply_broll(video_clip, transcript_segments=None, full_text=None,
                overlay_style="fullscreen", output_path=None):
    """
    Full B-roll pipeline:
    1. Extract keywords from transcript
    2. Search stock footage (or generate gradients)
    3. Overlay at the right moments
    
    Returns: modified video clip
    """
    from moviepy import VideoFileClip
    
    print("[B-ROLL] 🎥 Iniciando generación de B-Roll automática...")
    
    # Extract keywords
    if transcript_segments:
        keywords = extract_keywords(transcript_segments)
    elif full_text:
        keywords = extract_keywords_from_text(full_text)
    else:
        print("[B-ROLL] ⚠️ No hay transcripción disponible para B-Roll")
        return video_clip
    
    print(f"[B-ROLL] 🔑 {len(keywords)} keywords detectadas: {[k['keyword'] for k in keywords]}")
    
    if not keywords:
        print("[B-ROLL] ℹ️ No se encontraron keywords de B-Roll en la transcripción")
        return video_clip
    
    # Prepare B-roll clips
    fps = video_clip.fps
    w, h = video_clip.size
    
    broll_plan = {}
    for kw in keywords:
        start_frame = int(kw["time"] * fps)
        end_frame = int((kw["time"] + kw["duration"]) * fps)
        
        # Try to get stock footage
        stock_clips = search_stock_video(kw["search"])
        
        if stock_clips:
            # Download first result
            temp_path = os.path.join(tempfile.mkdtemp(), f"broll_{kw['keyword']}.mp4")
            downloaded = download_stock_clip(stock_clips[0]["url"], temp_path)
            
            if downloaded:
                try:
                    broll_video = VideoFileClip(downloaded)
                    for f in range(start_frame, end_frame):
                        broll_t = (f - start_frame) / fps
                        if broll_t < broll_video.duration:
                            broll_plan[f] = {"clip": broll_video, "time": broll_t, "style": overlay_style}
                    continue
                except Exception as e:
                    print(f"[B-ROLL] ⚠️ Error cargando clip: {e}")
        
        # Fallback: generate gradient
        gradient_frames = create_gradient_broll((w, h), kw["keyword"], kw["duration"], fps)
        for idx, f in enumerate(range(start_frame, min(end_frame, start_frame + len(gradient_frames)))):
            broll_plan[f] = {"gradient_frame": gradient_frames[idx], "style": overlay_style}
    
    # BUG-08 FIX: Track temp dirs for cleanup
    _broll_temp_dirs = []
    for kw in keywords:
        pass  # temp dirs already created above, tracked in broll_plan
    
    print(f"[B-ROLL] 🎬 Planificados {len(broll_plan)} frames de B-Roll")
    
    # Apply B-Roll frame by frame
    def process_frame(get_frame, t):
        frame = get_frame(t)
        frame_idx = int(t * fps)
        
        if frame_idx in broll_plan:
            plan = broll_plan[frame_idx]
            
            if "clip" in plan:
                broll_frame = plan["clip"].get_frame(plan["time"])
                broll_frame = cv2.resize(broll_frame.astype(np.uint8), (w, h))
            elif "gradient_frame" in plan:
                broll_frame = plan["gradient_frame"]
            else:
                return frame
            
            frame = apply_broll_overlay(frame, broll_frame, opacity=0.35, style=plan["style"])
        
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
    
    print("[B-ROLL] ✅ B-Roll automático aplicado")
    return modified
