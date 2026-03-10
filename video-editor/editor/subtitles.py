"""
VideoForge — Auto Subtitles Module
Transcribes video with Whisper and renders animated Hormozi-style subtitles.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Try to import faster_whisper; if unavailable, provide fallback info
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


# ---------- Configuration ---------- #

DEFAULT_CONFIG = {
    "font_size": 80,
    "font_path": None,  # Will use bundled or system fallback
    "text_color": (255, 255, 255),         # White
    "highlight_color": (255, 215, 0),      # Gold
    "outline_color": (0, 0, 0),            # Black outline
    "outline_width": 4,
    "shadow_color": (0, 0, 0, 128),
    "shadow_offset": (4, 4),
    "position": "center",                  # "center", "bottom", "top"
    "max_words_per_line": 4,
    "highlight_scale": 1.2,                # Scale factor for active word
    "whisper_model": "base",               # "tiny", "base", "small", "medium", "large-v3"
    "language": "es",                      # Auto-detect if None
}


# ---------- Transcription ---------- #

def _detect_whisper_device():
    """BUG-12 FIX: Auto-detect best device for Whisper."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda", "float16"
    except ImportError:
        pass
    return "cpu", "int8"


def transcribe_video(video_path, model_size="base", language="es"):
    """
    Transcribe a video file using faster-whisper with word-level timestamps.
    
    Args:
        video_path: Path to video file
        model_size: Whisper model size (tiny/base/small/medium/large-v3)
        language: Language code (None for auto-detection)
    
    Returns:
        List of dicts: [{"word": str, "start": float, "end": float}, ...]
    """
    if not WHISPER_AVAILABLE:
        raise ImportError(
            "faster-whisper no está instalado. Ejecuta: pip install faster-whisper"
        )
    
    device, compute_type = _detect_whisper_device()
    print(f"[Subtitles] Cargando modelo Whisper '{model_size}' en {device} ({compute_type})...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    
    print(f"[Subtitles] Transcribiendo: {video_path}")
    segments, info = model.transcribe(
        video_path,
        language=language,
        word_timestamps=True,
        vad_filter=True,
    )
    
    words = []
    for segment in segments:
        if segment.words:
            for word_info in segment.words:
                words.append({
                    "word": word_info.word.strip(),
                    "start": word_info.start,
                    "end": word_info.end,
                })
    
    print(f"[Subtitles] ✅ Transcritas {len(words)} palabras (idioma detectado: {info.language})")
    return words


# ---------- Subtitle Groups ---------- #

def group_words_into_lines(words, max_words=4):
    """
    Group transcribed words into display lines of max_words each.
    
    Returns:
        List of groups, each group is a list of word dicts
    """
    groups = []
    current_group = []
    
    for word in words:
        current_group.append(word)
        if len(current_group) >= max_words:
            groups.append(current_group)
            current_group = []
    
    if current_group:
        groups.append(current_group)
    
    return groups


# ---------- Rendering ---------- #

def get_font(font_path=None, font_size=80):
    """Load font with fallback chain."""
    if font_path and os.path.exists(font_path):
        return ImageFont.truetype(font_path, font_size)
    
    # Try common system fonts
    font_candidates = [
        "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold
        "C:/Windows/Fonts/segoeui.ttf",       # Segoe UI
        "C:/Windows/Fonts/calibrib.ttf",      # Calibri Bold
        "C:/Windows/Fonts/impact.ttf",        # Impact
    ]
    
    for candidate in font_candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, font_size)
    
    # Last resort
    return ImageFont.load_default()


def render_subtitle_frame(frame_size, words_group, current_time, config=None):
    """
    Render a subtitle frame overlay with Hormozi-style animated text.
    """
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    width, height = frame_size
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = config.get("font_size", 80)
    font = get_font(config.get("font_path"), font_size)
    highlight_font = get_font(config.get("font_path"), int(font_size * config.get("highlight_scale", 1.2)))
    
    text_color = config.get("text_color", (255, 255, 255))
    highlight_color = config.get("highlight_color", (255, 215, 0))
    outline_color = config.get("outline_color", (0, 0, 0))
    outline_width = config.get("outline_width", 4)
    
    if not words_group:
        return np.array(img)
    
    # Determine which word is currently active
    active_index = -1
    for i, word_info in enumerate(words_group):
        if word_info["start"] <= current_time <= word_info["end"]:
            active_index = i
            break
    
    # If between words, highlight the last spoken word
    if active_index == -1:
        for i, word_info in enumerate(words_group):
            if current_time >= word_info["start"]:
                active_index = i
    
    # Calculate total text width for centering
    total_width = 0
    word_widths = []
    space_width = draw.textlength(" ", font=font)
    
    for i, word_info in enumerate(words_group):
        use_font = highlight_font if i == active_index else font
        w = draw.textlength(word_info["word"], font=use_font)
        word_widths.append(w)
        total_width += w
        if i < len(words_group) - 1:
            total_width += space_width
    
    # Position calculation
    position = config.get("position", "center")
    x_start = (width - total_width) / 2
    
    if position == "center":
        y_pos = height * 0.5 - font_size / 2
    elif position == "bottom":
        y_pos = height * 0.82
    elif position == "top":
        y_pos = height * 0.1
    else:
        y_pos = height * 0.5 - font_size / 2
    
    # Draw each word
    x_cursor = x_start
    for i, word_info in enumerate(words_group):
        is_active = (i == active_index)
        use_font = highlight_font if is_active else font
        color = highlight_color if is_active else text_color
        word_text = word_info["word"]
        
        # Bounce animation for active word
        y_offset = 0
        if is_active:
            progress = 0
            word_duration = word_info["end"] - word_info["start"]
            if word_duration > 0:
                progress = (current_time - word_info["start"]) / word_duration
            # Bounce: sin curve for pop effect
            y_offset = -abs(math.sin(progress * math.pi)) * 8
        
        draw_y = y_pos + y_offset
        
        # Draw outline (stroke)
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx * dx + dy * dy <= outline_width * outline_width:
                    draw.text(
                        (x_cursor + dx, draw_y + dy),
                        word_text,
                        font=use_font,
                        fill=outline_color + (255,)
                    )
        
        # Draw main text
        draw.text(
            (x_cursor, draw_y),
            word_text,
            font=use_font,
            fill=color + (255,)
        )
        
        x_cursor += word_widths[i] + space_width
    
    return np.array(img)


def create_subtitle_clip(video_clip, words, config=None):
    """
    Create a VideoClip with animated subtitles overlaid on the original video.
    """
    from moviepy import VideoClip, CompositeVideoClip
    
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    max_words = config.get("max_words_per_line", 4)
    groups = group_words_into_lines(words, max_words)
    
    frame_size = (video_clip.w, video_clip.h)
    
    def make_frame(t):
        """Generate subtitle overlay frame at time t."""
        # Find which group should be displayed at time t
        current_group = None
        for group in groups:
            group_start = group[0]["start"]
            group_end = group[-1]["end"]
            if group_start <= t <= group_end + 0.3:  # Small buffer after last word
                current_group = group
                break
        
        if current_group is None:
            # No subtitle at this time
            return np.zeros((frame_size[1], frame_size[0], 4), dtype=np.uint8)
        
        return render_subtitle_frame(frame_size, current_group, t, config)
    
    subtitle_clip = VideoClip(
        make_frame,
        duration=video_clip.duration,
    ).with_fps(video_clip.fps)
    
    # Composite: original video + subtitle overlay
    final = CompositeVideoClip([video_clip, subtitle_clip])
    
    return final


def add_subtitles(input_path, output_path=None, config=None):
    """
    Full pipeline: transcribe video and add animated subtitles.
    BUG-02 FIX: Uses the same video clip for both transcription and rendering,
    so timestamps always match the actual video.
    """
    from moviepy import VideoFileClip
    
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    if output_path is None:
        base = input_path.rsplit('.', 1)[0]
        output_path = f"{base}_subtitled.mp4"
    
    # Step 1: Transcribe — uses the input_path directly (same file)
    words = transcribe_video(
        input_path,
        model_size=config.get("whisper_model", "base"),
        language=config.get("language", "es")
    )
    
    if not words:
        print("[Subtitles] ⚠ No se detectaron palabras en el vídeo.")
        return {"word_count": 0, "duration": 0, "output_path": output_path}
    
    # Step 2: Create subtitled video — uses same input_path
    print(f"[Subtitles] Generando subtítulos animados ({len(words)} palabras)...")
    video = VideoFileClip(input_path)
    subtitled = create_subtitle_clip(video, words, config)
    
    # Step 3: Export
    print(f"[Subtitles] Exportando: {output_path}")
    try:
        from editor.gpu_engine import get_gpu_info, get_moviepy_write_params
        gpu_info = get_gpu_info()
        write_params = get_moviepy_write_params(gpu_info)
    except Exception:
        write_params = {"codec": "libx264", "audio_codec": "aac", "preset": "ultrafast", "threads": 8}
    
    subtitled.write_videofile(output_path, **write_params, logger="bar")
    
    stats = {
        "word_count": len(words),
        "duration": round(video.duration, 2),
        "output_path": output_path,
        "transcript_text": " ".join(w["word"] for w in words),
    }
    
    print(f"[Subtitles] ✅ Subtítulos añadidos — {stats['word_count']} palabras")
    
    video.close()
    subtitled.close()
    
    return stats


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python subtitles.py <video.mp4> [idioma]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "es"
    
    result = add_subtitles(input_file, config={"language": lang})
    print(f"\nResultado: {result}")
