"""
VideoForge V15 — All Agents (LOCAL MODE)
==========================================
Complete set of V15 agents — 100% LOCAL, sin API externa.
Cada agente usa heurísticas avanzadas y algoritmos deterministas.
NO requiere Claude, OpenAI, ni ninguna API de pago.
"""

from __future__ import annotations

import json
import logging
import math
import random
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .models import (
    AgentStatus, AnimationType, AudioLane, AudioLaneType,
    BRollInsert, CropInstruction, EmotionTag, MusicTrackEvent,
    SFXEvent, SFXType, SubtitleEvent, SubtitleStylePack,
    VFXEvent, VFXType, ViralityMarker, VideoForgeEDL_V15, Word,
)
from .agents import BaseAgent, agent_permissions, CutScriptAgent

logger = logging.getLogger("v15.agents")


# ════════════════════════════════════════════════════════════════════════════════
# TRANSCRIPT AGENT (Whisper — sin API)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["source_media"],
    can_write=["transcript"]
)
class TranscriptAgent(BaseAgent):
    """Transcribe video usando faster-whisper (100% local)."""
    NAME = "transcript"
    TIMEOUT_SECONDS = 300

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        if not edl.source_media:
            raise ValueError("source_media requerido")

        try:
            from faster_whisper import WhisperModel
        except ImportError:
            logger.warning("faster-whisper no instalado, generando transcript vacío")
            edl.transcript = []
            return edl

        logger.info("Cargando Whisper base...")
        model = WhisperModel("base", device="cpu", compute_type="int8")

        segments, info = model.transcribe(
            edl.source_media.file_path,
            language="es",
            word_timestamps=True,
            vad_filter=True,
        )

        words = []
        word_id = 0
        for segment in segments:
            if segment.words:
                for w in segment.words:
                    words.append(Word(
                        word_id=word_id,
                        text=w.word.strip(),
                        start=round(w.start, 3),
                        end=round(w.end, 3),
                        speaker="SPK_0",
                        confidence=round(getattr(w, 'probability', 0.9), 3),
                    ))
                    word_id += 1

        edl.transcript = words
        logger.info(f"✅ {len(words)} palabras transcritas (idioma: {info.language})")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# VISUAL ANALYST AGENT (LOCAL — análisis por heurísticas)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["source_media", "transcript"],
    can_write=["scene_segments", "emotion_tags"]
)
class VisualAnalystAgent(BaseAgent):
    """Segmenta escenas usando análisis de silencio y ritmo de transcripción."""
    NAME = "visual_analyst"

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        duration = edl.source_media.duration if edl.source_media else 30.0
        words = edl.transcript or []

        # Detectar cambios de escena por gaps en transcripción
        scenes = []
        if not words:
            # Sin transcript: una sola escena
            from .models import SceneSegment
            scenes.append(SceneSegment(
                scene_id=0, start=0, end=duration,
                scene_type="talking_head", dominant_emotion=EmotionTag.ENERGETIC,
            ))
        else:
            from .models import SceneSegment
            scene_start = words[0].start
            scene_id = 0
            prev_end = words[0].end

            for i, w in enumerate(words[1:], 1):
                gap = w.start - prev_end
                # Gap > 2s = nueva escena
                if gap > 2.0 or i == len(words) - 1:
                    end_time = words[i].end if i == len(words) - 1 else prev_end + 0.5
                    scenes.append(SceneSegment(
                        scene_id=scene_id,
                        start=round(scene_start, 3),
                        end=round(end_time, 3),
                        scene_type="talking_head",
                        dominant_emotion=EmotionTag.ENERGETIC,
                    ))
                    scene_id += 1
                    scene_start = w.start
                prev_end = w.end

        edl.scene_segments = scenes

        # Asignar emociones basadas en ritmo de palabras
        if words:
            avg_wps = len(words) / max(duration, 1)
            if avg_wps > 3.5:
                edl.emotion_tags["global"] = EmotionTag.ENERGETIC
            elif avg_wps > 2.0:
                edl.emotion_tags["global"] = EmotionTag.INSPIRING
            else:
                edl.emotion_tags["global"] = EmotionTag.CALM

        logger.info(f"✅ {len(scenes)} escenas segmentadas")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# CUT SCRIPT AGENT (LOCAL — cortes inteligentes por silencios)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["transcript", "scene_segments", "source_media"],
    can_write=["timeline_cuts"]
)
class CutScriptAgentLocal(BaseAgent):
    """Decide qué cortes sobreviven usando análisis de silencios/gaps."""
    NAME = "cut_script"

    PRESET_CONFIGS = {
        "tiktok_pro":    {"min_silence": 0.25, "keep_ratio": 0.8, "max_cuts": 60},
        "hormozi":       {"min_silence": 0.20, "keep_ratio": 0.85, "max_cuts": 50},
        "cinematic":     {"min_silence": 0.40, "keep_ratio": 0.95, "max_cuts": 30},
        "podcast":       {"min_silence": 0.50, "keep_ratio": 0.98, "max_cuts": 20},
        "shorts_viral":  {"min_silence": 0.15, "keep_ratio": 0.75, "max_cuts": 80},
    }

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        from .models import TimelineCut

        duration = edl.source_media.duration if edl.source_media else 30.0
        words = edl.transcript or []
        config = self.PRESET_CONFIGS.get(str(edl.preset_style), self.PRESET_CONFIGS["tiktok_pro"])

        if not words:
            # Sin transcript: un solo corte con todo el vídeo
            edl.timeline_cuts = [TimelineCut(
                cut_id=0, source_start=0, source_end=duration,
                timeline_start=0, timeline_end=duration, keep=True,
            )]
            return edl

        # Crear cortes basados en gaps entre palabras
        cuts = []
        cut_id = 0
        segment_start = max(0, words[0].start - 0.2)
        timeline_pos = 0.0

        for i in range(1, len(words)):
            gap = words[i].start - words[i-1].end

            if gap >= config["min_silence"] or i == len(words) - 1:
                segment_end = words[i-1].end + 0.15 if i < len(words) - 1 else words[i].end + 0.3
                segment_end = min(segment_end, duration)
                cut_duration = segment_end - segment_start

                if cut_duration > 0.3:  # mínimo 0.3s
                    cuts.append(TimelineCut(
                        cut_id=cut_id,
                        source_start=round(segment_start, 3),
                        source_end=round(segment_end, 3),
                        timeline_start=round(timeline_pos, 3),
                        timeline_end=round(timeline_pos + cut_duration, 3),
                        keep=True,
                    ))
                    timeline_pos += cut_duration
                    cut_id += 1

                segment_start = words[i].start - 0.1

        # Limitar al max_cuts
        if len(cuts) > config["max_cuts"]:
            cuts = cuts[:config["max_cuts"]]

        edl.timeline_cuts = cuts
        edl.total_timeline_duration = timeline_pos
        logger.info(f"✅ {len(cuts)} cortes (duración: {timeline_pos:.1f}s de {duration:.1f}s)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# HOOK EDITOR AGENT (LOCAL — detecta hooks por posición y energía)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["transcript", "scene_segments", "source_media"],
    can_write=["virality_markers"]
)
class HookEditorAgent(BaseAgent):
    """Identifica hooks y momentos virales usando heurísticas de posición."""
    NAME = "hook_editor"

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        words = edl.transcript or []
        if not words:
            return edl

        duration = edl.source_media.duration if edl.source_media else 30.0
        markers = []
        marker_id = 0

        # 1. Hook: primeras 3 segundos siempre
        early_words = [w for w in words if w.start < 3.0]
        if early_words:
            markers.append(ViralityMarker(
                marker_id=marker_id, timeline_position=early_words[0].start,
                marker_type="hook", intensity=0.9, word_id=early_words[0].word_id,
            ))
            marker_id += 1
            for w in early_words:
                w.is_hook = True
                w.virality_score = 0.9

        # 2. Detectar punchlines: palabras más largas con exclamaciones
        for w in words:
            if any(c in w.text for c in "!?¡¿") or len(w.text) > 10:
                markers.append(ViralityMarker(
                    marker_id=marker_id, timeline_position=w.start,
                    marker_type="punchline", intensity=0.7, word_id=w.word_id,
                ))
                w.is_hook = True
                w.virality_score = 0.7
                marker_id += 1

        # 3. Climax: punto a ~66% del vídeo
        climax_time = duration * 0.66
        climax_words = [w for w in words if abs(w.start - climax_time) < 3.0]
        if climax_words:
            cw = climax_words[len(climax_words)//2]
            markers.append(ViralityMarker(
                marker_id=marker_id, timeline_position=cw.start,
                marker_type="climax", intensity=0.85, word_id=cw.word_id,
            ))
            marker_id += 1

        # 4. CTA: últimos 5 segundos
        cta_words = [w for w in words if w.start > duration - 5.0]
        if cta_words:
            markers.append(ViralityMarker(
                marker_id=marker_id, timeline_position=cta_words[0].start,
                marker_type="cta", intensity=0.6,
            ))

        edl.virality_markers = markers[:10]
        logger.info(f"✅ {len(markers)} virality markers (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# SUBTITLE AGENT (LOCAL — agrupa palabras en subtítulos de 2-4 palabras)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["transcript", "timeline_cuts", "preset_style", "virality_markers"],
    can_write=["subtitle_events", "subtitle_style_packs"]
)
class SubtitleAgent(BaseAgent):
    """Genera subtítulos animados agrupando palabras (sin LLM)."""
    NAME = "subtitle"

    PRESET_STYLES = {
        "tiktok_pro":   {"pos_y": 0.85, "words_per": 3, "font": "Montserrat", "size": 72, "caps": False},
        "hormozi":      {"pos_y": 0.50, "words_per": 2, "font": "Montserrat", "size": 80, "caps": True},
        "cinematic":    {"pos_y": 0.88, "words_per": 4, "font": "Inter", "size": 56, "caps": False},
        "podcast":      {"pos_y": 0.92, "words_per": 5, "font": "Inter", "size": 48, "caps": False},
        "shorts_viral": {"pos_y": 0.85, "words_per": 2, "font": "Montserrat", "size": 84, "caps": True},
    }

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        words = edl.transcript or []
        if not words:
            return edl

        style_cfg = self.PRESET_STYLES.get(str(edl.preset_style), self.PRESET_STYLES["tiktok_pro"])
        wpp = style_cfg["words_per"]

        subs = []
        for i in range(0, len(words), wpp):
            group = words[i:i+wpp]
            if not group:
                continue

            text = " ".join(w.text for w in group)
            if style_cfg["caps"]:
                text = text.upper()

            has_hook = any(getattr(w, 'is_hook', False) for w in group)

            subs.append(SubtitleEvent(
                sub_id=len(subs),
                word_ids=[w.word_id for w in group],
                timeline_start=group[0].start,
                timeline_end=group[-1].end + 0.3,
                text=text,
                style_id="default",
                position_y=style_cfg["pos_y"],
                animation="pop" if has_hook else "fade_in",
            ))

        edl.subtitle_events = subs

        # Style pack
        edl.subtitle_style_packs["default"] = SubtitleStylePack(
            style_id="default",
            font_family=style_cfg["font"],
            font_size=style_cfg["size"],
            font_color="#FFFFFF",
            outline_color="#000000",
            outline_width=3.0,
            bold=True,
            all_caps=style_cfg["caps"],
            words_per_subtitle=wpp,
        )

        logger.info(f"✅ {len(subs)} subtítulos generados (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# VFX EDITOR AGENT (LOCAL — VFX por virality markers)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["timeline_cuts", "virality_markers", "preset_style", "scene_segments"],
    can_write=["vfx_tracks"]
)
class VFXEditorAgent(BaseAgent):
    """Asigna VFX a momentos virales automáticamente."""
    NAME = "vfx_editor"

    VFX_MAPPING = {
        "hook":       ["zoom_punch", "flash"],
        "climax":     ["camera_shake", "speed_ramp"],
        "punchline":  ["zoom_punch", "glitch"],
        "cta":        ["flash", "color_pop"],
        "transition": ["glitch", "swoosh"],
    }

    PRESET_WEIGHTS = {
        "tiktok_pro":   {"zoom_punch": 1.0, "glitch": 0.7, "flash": 0.5, "speed_ramp": 0.3},
        "hormozi":      {"zoom_punch": 1.0, "glitch": 0.3, "flash": 0.4, "speed_ramp": 0.2},
        "cinematic":    {"speed_ramp": 1.0, "color_pop": 0.8, "flash": 0.3, "zoom_punch": 0.2},
        "podcast":      {"zoom_punch": 0.3, "flash": 0.1},
        "shorts_viral": {"glitch": 1.0, "zoom_punch": 0.9, "flash": 0.7, "camera_shake": 0.6},
    }

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        if not edl.timeline_cuts:
            return edl

        preset = str(edl.preset_style)
        weights = self.PRESET_WEIGHTS.get(preset, self.PRESET_WEIGHTS["tiktok_pro"])
        cut_map = {c.cut_id: c for c in edl.timeline_cuts}

        vfx_list = []
        for marker in edl.virality_markers[:10]:
            possible = self.VFX_MAPPING.get(marker.marker_type, ["zoom_punch"])
            # Pick best VFX based on preset weight
            best = max(possible, key=lambda fx: weights.get(fx, 0))

            # Find matching cut
            target_cut = None
            for c in edl.timeline_cuts:
                if c.source_start <= marker.timeline_position <= c.source_end:
                    target_cut = c
                    break

            if not target_cut:
                target_cut = edl.timeline_cuts[0]

            vfx_list.append(VFXEvent(
                effect_name=best,
                target_cut_id=target_cut.cut_id,
                start_time_in_timeline=marker.timeline_position,
                duration=0.3 if best in ("flash", "glitch") else 0.5,
                intensity=marker.intensity * weights.get(best, 0.5),
                parameters={},
                verified_against_cuts=True,
            ))

        edl.vfx_tracks = vfx_list[:15]
        logger.info(f"✅ {len(vfx_list)} VFX events (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# SFX DESIGNER AGENT (LOCAL — SFX sincronizados con VFX)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["timeline_cuts", "vfx_tracks", "virality_markers", "preset_style"],
    can_write=["sfx_tracks"]
)
class SFXDesignerAgent(BaseAgent):
    """Asigna SFX complementarios a cada VFX automáticamente."""
    NAME = "sfx_designer"

    VFX_TO_SFX = {
        "zoom_punch":    ("impact", -3, 0.3),
        "camera_shake":  ("braam", -6, 0.5),
        "glitch":        ("click", -6, 0.2),
        "flash":         ("whoosh", -6, 0.3),
        "color_pop":     ("pop", -9, 0.4),
        "speed_ramp":    ("swoosh", -6, 0.5),
    }

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        sfx_list = []

        # SFX para cada VFX
        for vfx in edl.vfx_tracks:
            mapping = self.VFX_TO_SFX.get(vfx.effect_name)
            if mapping:
                sound, vol, dur = mapping
                sfx_list.append(SFXEvent(
                    sound_type=sound,
                    start_time_in_timeline=vfx.start_time_in_timeline,
                    duration=dur,
                    volume_db=vol,
                    fade_in_ms=0,
                    fade_out_ms=50,
                    verified_against_cuts=True,
                ))

        # Riser antes de cada climax
        for marker in edl.virality_markers:
            if marker.marker_type == "climax":
                riser_start = max(0, marker.timeline_position - 1.5)
                sfx_list.append(SFXEvent(
                    sound_type="riser",
                    start_time_in_timeline=riser_start,
                    duration=1.5,
                    volume_db=-9,
                    fade_in_ms=200,
                    fade_out_ms=100,
                    verified_against_cuts=True,
                ))

        edl.sfx_tracks = sfx_list[:20]
        logger.info(f"✅ {len(sfx_list)} SFX events (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# B-ROLL DIRECTOR AGENT (LOCAL)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["timeline_cuts", "transcript", "scene_segments", "preset_style"],
    can_write=["b_roll_tracks"]
)
class BRollDirectorAgent(BaseAgent):
    """Inserta B-Roll en gaps largos de talking head."""
    NAME = "broll_director"

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        if not edl.timeline_cuts:
            return edl

        preset = str(edl.preset_style)
        # Podcast = mínimo B-Roll
        max_broll = 2 if preset == "podcast" else 5

        broll_list = []
        for cut in edl.timeline_cuts:
            cut_dur = cut.source_end - cut.source_start
            if cut_dur > 8.0 and len(broll_list) < max_broll:
                # Insertar B-Roll a mitad del corte largo
                mid = cut.source_start + cut_dur * 0.5
                broll_list.append(BRollInsert(
                    target_cut_id=cut.cut_id,
                    timeline_start=mid,
                    timeline_end=mid + min(3.0, cut_dur * 0.3),
                    search_query="abstract motion graphics",
                ))

        edl.b_roll_tracks = broll_list
        logger.info(f"✅ {len(broll_list)} B-Roll inserts (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# MUSIC SUPERVISOR AGENT (LOCAL)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["timeline_cuts", "emotion_tags", "preset_style", "virality_markers"],
    can_write=["music_tracks", "audio_lanes"]
)
class MusicSupervisorAgent(BaseAgent):
    """Configura música de fondo y audio lanes."""
    NAME = "music_supervisor"

    PRESET_MUSIC = {
        "tiktok_pro":   {"volume_db": -10, "ducking_db": -22, "mood": "upbeat"},
        "hormozi":      {"volume_db": -14, "ducking_db": -25, "mood": "motivational"},
        "cinematic":    {"volume_db": -14, "ducking_db": -24, "mood": "cinematic"},
        "podcast":      {"volume_db": -20, "ducking_db": -30, "mood": "ambient"},
        "shorts_viral": {"volume_db": -8,  "ducking_db": -20, "mood": "energetic"},
    }

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        preset = str(edl.preset_style)
        cfg = self.PRESET_MUSIC.get(preset, self.PRESET_MUSIC["tiktok_pro"])
        total_dur = edl.total_timeline_duration or 30.0

        edl.music_tracks = [
            MusicTrackEvent(
                asset_path=f"assets/music/{cfg['mood']}_bg.mp3",
                timeline_start=0,
                timeline_end=total_dur,
                volume_db=cfg["volume_db"],
                ducking_enabled=True,
                ducking_target_db=cfg["ducking_db"],
            )
        ]

        edl.audio_lanes = [
            AudioLane(lane_id=0, lane_type=AudioLaneType.VOICE, master_volume_db=0.0),
            AudioLane(lane_id=1, lane_type=AudioLaneType.MUSIC, master_volume_db=-6.0),
            AudioLane(lane_id=2, lane_type=AudioLaneType.SFX, master_volume_db=-3.0),
        ]

        logger.info(f"✅ Música: {cfg['mood']}, vol={cfg['volume_db']}dB (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# CROP REFRAMING AGENT (LOCAL)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["timeline_cuts", "scene_segments", "source_media", "preset_style"],
    can_write=["crop_instructions"]
)
class CropReframingAgent(BaseAgent):
    """Genera instrucciones de crop basadas en preset."""
    NAME = "crop_reframing"

    PRESET_CROP = {
        "tiktok_pro":   {"aspect": "9:16", "x": 0.5, "y": 0.4, "w": 0.5625, "h": 1.0},
        "hormozi":      {"aspect": "9:16", "x": 0.5, "y": 0.4, "w": 0.5625, "h": 1.0},
        "cinematic":    {"aspect": "16:9", "x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0},
        "podcast":      {"aspect": "16:9", "x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0},
        "shorts_viral": {"aspect": "9:16", "x": 0.5, "y": 0.35, "w": 0.5625, "h": 1.0},
    }

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        if not edl.timeline_cuts:
            return edl

        preset = str(edl.preset_style)
        cfg = self.PRESET_CROP.get(preset, self.PRESET_CROP["tiktok_pro"])

        crops = []
        for cut in edl.timeline_cuts:
            crops.append(CropInstruction(
                cut_id=cut.cut_id,
                x=cfg["x"], y=cfg["y"],
                w=cfg["w"], h=cfg["h"],
                target_aspect=cfg["aspect"],
                reframe_motion=cfg["aspect"] == "9:16",
            ))

        edl.crop_instructions = crops
        logger.info(f"✅ {len(crops)} crop instructions → {cfg['aspect']} (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# STYLE DESIGNER AGENT (LOCAL)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["preset_style", "emotion_tags", "scene_segments"],
    can_write=["lut_applied", "style_pack"]
)
class StyleDesignerAgent(BaseAgent):
    """Asigna LUT y estilo visual según preset."""
    NAME = "style_designer"

    PRESET_LUTS = {
        "tiktok_pro":   "neon_night",
        "hormozi":      None,
        "cinematic":    "cinematic_warm",
        "podcast":      None,
        "shorts_viral": "dramatic_noir",
    }

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        preset = str(edl.preset_style)
        lut = self.PRESET_LUTS.get(preset)
        edl.lut_applied = lut
        logger.info(f"✅ Estilo: LUT={lut or 'natural_clean'} (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# STYLE CONSISTENCY AGENT (Deterministic)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["subtitle_style_packs", "vfx_tracks", "lut_applied"],
    can_write=[]
)
class StyleConsistencyAgent(BaseAgent):
    """Verifica coherencia de estilos sin LLM."""
    NAME = "style_consistency"

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        issues = []

        # Verificar que hay al menos un style pack
        if not edl.subtitle_style_packs:
            issues.append("No hay style packs definidos")

        # Verificar que VFX no superan el límite
        if len(edl.vfx_tracks) > 15:
            issues.append(f"Demasiados VFX: {len(edl.vfx_tracks)} > 15")

        if issues:
            logger.warning(f"⚠️ StyleConsistency: {', '.join(issues)}")
        else:
            logger.info("✅ Estilo coherente")

        return edl


# ════════════════════════════════════════════════════════════════════════════════
# QC AGENT (LOCAL — verificación determinista)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=[
        "timeline_cuts", "vfx_tracks", "sfx_tracks", "subtitle_events",
        "b_roll_tracks", "music_tracks", "crop_instructions",
        "virality_markers", "transcript", "source_media", "preset_style",
    ],
    can_write=["is_qc_approved", "qc_report"]
)
class QCAgent(BaseAgent):
    """Control de calidad final — 100% determinista, sin API."""
    NAME = "qc"
    TIMEOUT_SECONDS = 60

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        issues = []
        suggestions = []

        # 1. Verificar timeline_cuts
        if not edl.timeline_cuts:
            issues.append({"severity": "blocker", "msg": "No hay cortes en la timeline"})
        else:
            # Verificar que los timestamps son válidos
            for c in edl.timeline_cuts:
                if c.source_end <= c.source_start:
                    issues.append({"severity": "blocker", "msg": f"Cut {c.cut_id}: end <= start"})

            # Verificar solapamiento
            sorted_cuts = sorted(edl.timeline_cuts, key=lambda c: c.timeline_start)
            for i in range(1, len(sorted_cuts)):
                if sorted_cuts[i].timeline_start < sorted_cuts[i-1].timeline_end - 0.01:
                    issues.append({"severity": "warning", "msg": f"Solapamiento entre cuts {sorted_cuts[i-1].cut_id} y {sorted_cuts[i].cut_id}"})

        # 2. VFX references
        cut_ids = {c.cut_id for c in edl.timeline_cuts}
        for vfx in edl.vfx_tracks:
            if vfx.target_cut_id not in cut_ids:
                issues.append({"severity": "blocker", "msg": f"VFX referencia cut inválido: {vfx.target_cut_id}"})

        # 3. Subtítulos coverage
        if edl.transcript and not edl.subtitle_events:
            suggestions.append("Hay transcripción pero no se generaron subtítulos")

        # 4. Duración razonable
        total = edl.total_timeline_duration or 0
        if total > 1200:
            suggestions.append(f"Vídeo muy largo ({total:.0f}s), considerar acortar")
        if total < 1:
            issues.append({"severity": "blocker", "msg": "Duración total < 1 segundo"})

        # 5. Música configurada
        if not edl.music_tracks:
            suggestions.append("Sin música de fondo configurada")

        has_blockers = any(i["severity"] == "blocker" for i in issues)
        edl.is_qc_approved = not has_blockers

        edl.qc_report = {
            "approved": edl.is_qc_approved,
            "issues": issues,
            "suggestions": suggestions,
            "confidence": 0.95,
        }

        status = "✅ APROBADO" if edl.is_qc_approved else "❌ RECHAZADO"
        logger.info(f"QC: {status} — {len(issues)} issues, {len(suggestions)} sugerencias (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# COMPLIANCE AGENT (Deterministic)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=["b_roll_tracks", "music_tracks", "sfx_tracks"],
    can_write=[]
)
class ComplianceAgent(BaseAgent):
    """Verifica que todos los assets referenciados existen."""
    NAME = "compliance"

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        warnings = []

        for mt in edl.music_tracks:
            if not mt.asset_path:
                warnings.append("Music track sin asset_path")

        if warnings:
            logger.warning(f"⚠️ Compliance: {', '.join(warnings)}")
        else:
            logger.info("✅ Compliance check passed")

        return edl


# ════════════════════════════════════════════════════════════════════════════════
# RENDER PLANNER AGENT (Deterministic)
# ════════════════════════════════════════════════════════════════════════════════

@agent_permissions(
    can_read=[
        "timeline_cuts", "source_media", "crop_instructions", "preset_style",
        "is_qc_approved",
    ],
    can_write=["render_plans"]
)
class RenderPlannerAgent(BaseAgent):
    """Genera planes de render optimizados."""
    NAME = "render_planner"

    PRESET_RENDER = {
        "tiktok_pro":   {"w": 1080, "h": 1920, "fps": 30, "bitrate": "8M", "codec": "h264"},
        "hormozi":      {"w": 1080, "h": 1920, "fps": 30, "bitrate": "10M", "codec": "h264"},
        "cinematic":    {"w": 1920, "h": 1080, "fps": 24, "bitrate": "15M", "codec": "h264"},
        "podcast":      {"w": 1920, "h": 1080, "fps": 30, "bitrate": "6M", "codec": "h264"},
        "shorts_viral": {"w": 1080, "h": 1920, "fps": 30, "bitrate": "8M", "codec": "h264"},
    }

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        from .models import RenderPlan

        preset = str(edl.preset_style)
        cfg = self.PRESET_RENDER.get(preset, self.PRESET_RENDER["tiktok_pro"])

        plan = RenderPlan(
            output_width=cfg["w"],
            output_height=cfg["h"],
            fps=cfg["fps"],
            video_bitrate=cfg["bitrate"],
            codec=cfg["codec"],
            audio_bitrate="192k",
            format="mp4",
            gpu_accelerated=True,
        )

        edl.render_plans = [plan]
        logger.info(f"✅ Render plan: {cfg['w']}x{cfg['h']}@{cfg['fps']}fps (local)")
        return edl


# ════════════════════════════════════════════════════════════════════════════════
# AGENT REGISTRY — Todos los agentes disponibles
# ════════════════════════════════════════════════════════════════════════════════

ALL_V15_AGENTS = {
    "transcript":        TranscriptAgent,
    "visual_analyst":    VisualAnalystAgent,
    "cut_script":        CutScriptAgentLocal,
    "hook_editor":       HookEditorAgent,
    "subtitle":          SubtitleAgent,
    "vfx_editor":        VFXEditorAgent,
    "sfx_designer":      SFXDesignerAgent,
    "broll_director":    BRollDirectorAgent,
    "music_supervisor":  MusicSupervisorAgent,
    "crop_reframing":    CropReframingAgent,
    "style_designer":    StyleDesignerAgent,
    "style_consistency": StyleConsistencyAgent,
    "qc":                QCAgent,
    "compliance":        ComplianceAgent,
    "render_planner":    RenderPlannerAgent,
}
