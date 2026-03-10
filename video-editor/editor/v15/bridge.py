"""
VideoForge V15 — Bridge (V10 ↔ V15)
======================================
Convierte decisiones del EDL V15 a acciones de procesamiento V10,
y resultados V10 al formato EDL V15.
"""

from __future__ import annotations

import logging
import os
import shutil
from typing import Dict, List, Optional, Any

from .models import VideoForgeEDL_V15

logger = logging.getLogger("v15.bridge")


class V15toV10Bridge:
    """
    Traduce el EDL V15 (decisiones de IA) a parámetros para los módulos V10
    (procesamiento real de vídeo con MoviePy/FFmpeg).
    """

    def __init__(self, edl: VideoForgeEDL_V15):
        self.edl = edl

    def get_silence_cutter_params(self) -> Dict[str, Any]:
        """Genera parámetros para silence_cutter.py"""
        return {
            "silence_threshold_db": -35,
            "min_silence_duration": 0.4,
            "padding_ms": 80,
        }

    def get_smart_zoom_params(self) -> Dict[str, Any]:
        """Genera parámetros para smart_zoom.py basados en VFX tracks."""
        zoom_vfx = [v for v in self.edl.vfx_tracks if v.effect_name == "zoom_punch"]
        if zoom_vfx:
            return {
                "mode": "punch_in",
                "start_scale": 1.0,
                "end_scale": 1.0 + max(v.intensity for v in zoom_vfx) * 0.2,
            }
        return {"mode": "ken_burns", "start_scale": 1.0, "end_scale": 1.08}

    def get_subtitle_params(self) -> Dict[str, Any]:
        """Genera config para subtitles.py desde el style pack V15."""
        style = self.edl.subtitle_style_packs.get("default")
        if not style:
            return {
                "font_size": 72,
                "text_color": (255, 255, 255),
                "highlight_color": (255, 215, 0),
                "position": "center",
                "max_words_per_line": 3,
            }

        # Parse hex color
        def hex_to_rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        pos = "center"
        if style.font_size and any(
            s.position_y > 0.7 for s in self.edl.subtitle_events
        ):
            pos = "bottom"

        return {
            "font_size": style.font_size,
            "text_color": hex_to_rgb(style.font_color),
            "highlight_color": (255, 215, 0),
            "outline_color": hex_to_rgb(style.outline_color),
            "outline_width": int(style.outline_width),
            "position": pos,
            "max_words_per_line": style.words_per_subtitle,
            "whisper_model": "base",
            "language": "es",
        }

    def get_compositing_params(self) -> Dict[str, Any]:
        """Genera parámetros para compositing.py."""
        lut_to_grade = {
            "cinematic_warm": "warm",
            "cinematic_cold": "cold",
            "dramatic_noir": "noir",
            "vintage_film": "vintage",
            "neon_night": "neon",
        }
        grade = lut_to_grade.get(self.edl.lut_applied or "", "cinematic")

        return {
            "color_grade": grade,
            "vignette": True,
            "letterbox": str(self.edl.preset_style) == "cinematic",
        }

    def get_retention_params(self) -> Dict[str, Any]:
        """Genera parámetros para retention_engine.py basados en energy map."""
        vfx_types_map = {
            "zoom_punch": "zoom_punch",
            "camera_shake": "camera_shake",
            "glitch": "glitch",
            "flash": "flash",
            "color_pop": "high_contrast",
        }
        effects = []
        for v in self.edl.vfx_tracks:
            mapped = vfx_types_map.get(str(v.effect_name))
            if mapped:
                effects.append({
                    "type": mapped,
                    "time": v.start_time_in_timeline,
                    "duration": v.duration,
                    "intensity": v.intensity,
                })
        return {
            "effects": effects,
            "max_effects_per_minute": 8,
        }

    def get_sound_design_params(self) -> Dict[str, Any]:
        """Genera parámetros para sound_design.py."""
        sfx_map = {}
        for s in self.edl.sfx_tracks:
            sfx_map.setdefault(str(s.sound_type), []).append({
                "time": s.start_time_in_timeline,
                "duration": s.duration,
                "volume_db": s.volume_db,
            })
        return {"sfx_events": sfx_map}

    def get_audio_engine_params(self) -> Dict[str, Any]:
        """Genera parámetros para audio_engine.py."""
        music = self.edl.music_tracks[0] if self.edl.music_tracks else None
        return {
            "normalize": True,
            "compress": True,
            "noise_reduce": True,
            "music_ducking": music is not None,
            "music_volume_db": music.volume_db if music else -15,
        }

    def get_reframe_params(self) -> Dict[str, Any]:
        """Genera parámetros para smart_reframe.py."""
        crop = self.edl.crop_instructions[0] if self.edl.crop_instructions else None
        if crop and crop.target_aspect == "9:16":
            return {"target_ratio": (9, 16), "sample_rate": 5}
        elif crop and crop.target_aspect == "1:1":
            return {"target_ratio": (1, 1), "sample_rate": 5}
        return {"target_ratio": (16, 9), "sample_rate": 5}

    def get_vfx_engine_params(self) -> Dict[str, Any]:
        """Genera parámetros para vfx_engine.py."""
        return {
            "film_grain": True,
            "light_leaks": str(self.edl.preset_style) == "cinematic",
            "chromatic_aberration": any(
                v.effect_name == "glitch" for v in self.edl.vfx_tracks
            ),
        }

    def get_full_v10_config(self) -> Dict[str, Any]:
        """Retorna la configuración completa para todos los módulos V10."""
        return {
            "silence_cutter": self.get_silence_cutter_params(),
            "smart_zoom": self.get_smart_zoom_params(),
            "subtitles": self.get_subtitle_params(),
            "compositing": self.get_compositing_params(),
            "retention": self.get_retention_params(),
            "sound_design": self.get_sound_design_params(),
            "audio_engine": self.get_audio_engine_params(),
            "reframe": self.get_reframe_params(),
            "vfx_engine": self.get_vfx_engine_params(),
        }


def execute_v10_with_v15_decisions(
    input_path: str,
    output_path: str,
    edl: VideoForgeEDL_V15,
) -> Dict[str, Any]:
    """
    Ejecuta el motor V10 usando las decisiones del EDL V15.
    
    El brain (V15) ya decidió qué cortes, VFX, SFX, subs, etc.
    Ahora el motor (V10) ejecuta el procesamiento real.
    """
    bridge = V15toV10Bridge(edl)
    config = bridge.get_full_v10_config()

    logger.info(f"🔗 Bridge: ejecutando V10 con decisiones V15")
    logger.info(f"   Input: {input_path}")
    logger.info(f"   Output: {output_path}")

    # Importar pipeline V10
    try:
        from editor.pipeline import run_pipeline, PRESETS
    except ImportError:
        logger.error("No se pudo importar editor.pipeline")
        raise

    # Mapear preset V15 a V10
    preset_map = {
        "tiktok_pro": "tiktok_pro",
        "hormozi": "hormozi",
        "cinematic": "cinematic_pro",
        "podcast": "podcast_pro",
        "shorts_viral": "viral_max",
    }
    v10_preset = preset_map.get(str(edl.preset_style), "youtube_pro")

    # Ejecutar V10
    result = run_pipeline(
        input_path=input_path,
        output_path=output_path,
        preset=v10_preset,
    )

    logger.info(f"✅ Bridge: V10 completado")
    return {
        "v10_result": result,
        "v15_config": config,
        "output_path": output_path,
    }
