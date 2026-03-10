"""
VideoForge V15 — FFmpeg Builder
================================
Genera filter graphs y comandos FFmpeg desde el EDL V15.
"""

from __future__ import annotations

import json
import logging
import subprocess
from typing import List, Tuple

from .models import VideoForgeEDL_V15

logger = logging.getLogger("v15.ffmpeg")


class FilterGraphBuilder:
    """Construye filtergraphs de FFmpeg desde el EDL."""

    def __init__(self, edl: VideoForgeEDL_V15):
        self.edl = edl
        self.chains: List[str] = []
        self.extra_inputs: List[str] = []
        self._idx = 0

    def _label(self, prefix="v"):
        l = f"{prefix}{self._idx}"
        self._idx += 1
        return l

    def build_cuts(self) -> Tuple[str, str]:
        """Genera trim+concat para todos los cortes."""
        cuts = sorted(self.edl.timeline_cuts, key=lambda c: c.timeline_start)
        src = 0
        vlabels, alabels = [], []

        for cut in cuts:
            vl, al = self._label("v"), self._label("a")
            if cut.speed_factor == 1.0:
                self.chains.append(
                    f"[{src}:v]trim={cut.source_start}:{cut.source_end},"
                    f"setpts=PTS-STARTPTS[{vl}]"
                )
                self.chains.append(
                    f"[{src}:a]atrim={cut.source_start}:{cut.source_end},"
                    f"asetpts=PTS-STARTPTS[{al}]"
                )
            else:
                pts = 1.0 / cut.speed_factor
                atempo = max(0.5, min(cut.speed_factor, 2.0))
                self.chains.append(
                    f"[{src}:v]trim={cut.source_start}:{cut.source_end},"
                    f"setpts={pts:.4f}*PTS-STARTPTS[{vl}]"
                )
                self.chains.append(
                    f"[{src}:a]atrim={cut.source_start}:{cut.source_end},"
                    f"asetpts=PTS-STARTPTS,atempo={atempo:.4f}[{al}]"
                )
            vlabels.append(vl)
            alabels.append(al)

        n = len(cuts)
        vout, aout = self._label("vc"), self._label("ac")
        vin = "".join(f"[{l}]" for l in vlabels)
        ain = "".join(f"[{l}]" for l in alabels)
        self.chains.append(f"{vin}concat=n={n}:v=1:a=0[{vout}]")
        self.chains.append(f"{ain}concat=n={n}:v=0:a=1[{aout}]")
        return vout, aout

    def apply_crop(self, label: str) -> str:
        """Aplica crop/reframe según CropInstructions."""
        out = self._label("crop")
        if self.edl.crop_instructions:
            c = self.edl.crop_instructions[0]
            self.chains.append(
                f"[{label}]crop=iw*{c.w:.4f}:ih*{c.h:.4f}:"
                f"iw*{c.x:.4f}:ih*{c.y:.4f},scale=1080:1920[{out}]"
            )
        else:
            self.chains.append(
                f"[{label}]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
                f"scale=1080:1920[{out}]"
            )
        return out

    def apply_lut(self, label: str) -> str:
        """Aplica LUT de color grading."""
        if not self.edl.lut_applied:
            return label
        out = self._label("lut")
        self.chains.append(f"[{label}]lut3d='{self.edl.lut_applied}'[{out}]")
        return out

    def mix_audio(self, voice: str) -> str:
        """Mezcla pista de voz con música de fondo."""
        if not self.edl.music_tracks:
            return voice
        m = self.edl.music_tracks[0]
        midx = len(self.extra_inputs) + 1
        self.extra_inputs.append(m.asset_path)
        ml = self._label("mus")
        self.chains.append(f"[{midx}:a]volume={m.volume_db}dB[{ml}]")
        out = self._label("amx")
        self.chains.append(
            f"[{voice}][{ml}]amix=inputs=2:duration=first:"
            f"dropout_transition=2[{out}]"
        )
        return out

    def build(self) -> Tuple[str, str, str]:
        """Construye el filtergraph completo. Returns (filtergraph, video_label, audio_label)."""
        v, a = self.build_cuts()
        v = self.apply_crop(v)
        v = self.apply_lut(v)
        a = self.mix_audio(a)
        return ";".join(self.chains), v, a


class FFmpegCommandBuilder:
    """Genera el comando FFmpeg final desde el EDL."""

    def __init__(self, edl: VideoForgeEDL_V15):
        self.edl = edl

    def build(self) -> List[str]:
        """Genera el comando FFmpeg principal."""
        if not self.edl.render_plan:
            raise ValueError("render_plan requerido para generar comando FFmpeg")

        plan = self.edl.render_plan
        g = FilterGraphBuilder(self.edl)
        fc, vout, aout = g.build()

        # Inputs
        inputs = ["-i", self.edl.source_media.file_path]
        for extra in g.extra_inputs:
            inputs += ["-i", extra]

        # Codec
        if plan.use_gpu and plan.gpu_encoder:
            codec = ["-c:v", plan.gpu_encoder, "-preset", "p4", "-cq", str(plan.crf)]
        else:
            codec = [
                "-c:v", plan.output_codec, "-preset", plan.preset,
                "-crf", str(plan.crf)
            ]

        return (
            ["ffmpeg", "-y"] + inputs
            + ["-filter_complex", fc]
            + ["-map", f"[{vout}]", "-map", f"[{aout}]"]
            + codec
            + ["-c:a", plan.output_audio_codec, "-b:a", "192k"]
            + ["-movflags", "+faststart"]
            + [plan.output_path]
        )

    def build_subtitle_pass(self, video_in: str, ass: str, out: str) -> List[str]:
        """Genera segundo pase para subtítulos ASS."""
        return [
            "ffmpeg", "-y", "-i", video_in,
            "-vf", f"ass={ass}",
            "-c:v", "libx264", "-crf", "18",
            "-c:a", "copy", out
        ]


class FFmpegExecutor:
    """Ejecuta comandos FFmpeg y valida output."""

    @staticmethod
    def run(cmd: List[str], timeout: int = 3600) -> Tuple[bool, str]:
        """Ejecuta un comando FFmpeg con timeout."""
        logger.info(f"FFmpeg: {' '.join(cmd[:10])}...")
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if r.returncode == 0:
                logger.info("FFmpeg: ✅ OK")
                return True, "OK"
            else:
                logger.error(f"FFmpeg: ❌ {r.stderr[:500]}")
                return False, r.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"FFmpeg: ❌ Timeout {timeout}s")
            return False, f"Timeout {timeout}s"

    @staticmethod
    def validate_output(path: str, expected_dur: float, tol: float = 0.5) -> Tuple[bool, str]:
        """Valida que el output tenga duración correcta via ffprobe."""
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
                capture_output=True, text=True
            )
            if r.returncode != 0:
                return False, r.stderr
            dur = float(json.loads(r.stdout)["format"]["duration"])
            if abs(dur - expected_dur) > tol:
                return False, f"Duración {dur:.1f}s vs esperada {expected_dur:.1f}s"
            return True, "OK"
        except Exception as e:
            return False, str(e)
