"""
VideoForge V15 — Validadores por Capas
========================================
Validadores deterministas (sin LLM) que verifican invariantes del EDL.
"""

from __future__ import annotations

from typing import List, Tuple

from .models import (
    ValidationEntry, ValidationSeverity, VideoForgeEDL_V15,
)


class ValidationResult:
    def __init__(self):
        self.errors: List[ValidationEntry] = []
        self.is_valid = True

    def add(self, sev: ValidationSeverity, agent: str, field: str, msg: str):
        self.errors.append(ValidationEntry(
            severity=sev, agent_source=agent, field_path=field, message=msg
        ))
        if sev in (ValidationSeverity.ERROR, ValidationSeverity.FATAL):
            self.is_valid = False


class TimelineValidator:
    """Verifica invariantes de la timeline."""

    @staticmethod
    def validate_no_gaps(edl: VideoForgeEDL_V15) -> ValidationResult:
        r = ValidationResult()
        cuts = sorted(edl.timeline_cuts, key=lambda c: c.timeline_start)
        for i in range(len(cuts) - 1):
            gap = cuts[i + 1].timeline_start - cuts[i].timeline_end
            if gap > 0.1:
                r.add(
                    ValidationSeverity.WARNING, "timeline_validator",
                    f"cuts[{i}]",
                    f"Gap {gap:.3f}s entre cuts {cuts[i].cut_id} y {cuts[i + 1].cut_id}"
                )
        return r

    @staticmethod
    def validate_vfx_bounds(edl: VideoForgeEDL_V15) -> ValidationResult:
        r = ValidationResult()
        for vfx in edl.vfx_tracks:
            if vfx.target_cut_id is None:
                continue
            cut = next(
                (c for c in edl.timeline_cuts if c.cut_id == vfx.target_cut_id), None
            )
            if cut is None:
                r.add(
                    ValidationSeverity.FATAL, "vfx_validator",
                    f"vfx[{vfx.vfx_id}]",
                    f"VFX '{vfx.effect_name}' refs cut eliminado {vfx.target_cut_id}"
                )
                continue
            end = vfx.start_time_in_timeline + vfx.duration
            if vfx.start_time_in_timeline < cut.timeline_start or end > cut.timeline_end + 0.001:
                r.add(
                    ValidationSeverity.ERROR, "vfx_validator",
                    f"vfx[{vfx.vfx_id}]",
                    f"VFX fuera de bounds del cut {cut.cut_id}"
                )
        return r

    @staticmethod
    def validate_sfx_bounds(edl: VideoForgeEDL_V15) -> ValidationResult:
        r = ValidationResult()
        dur = edl.computed_duration
        for sfx in edl.sfx_tracks:
            if sfx.start_time_in_timeline + sfx.duration > dur + 0.1:
                r.add(
                    ValidationSeverity.ERROR, "sfx_validator",
                    f"sfx[{sfx.sfx_id}]",
                    f"SFX '{sfx.sound_type}' excede timeline ({dur:.3f}s)"
                )
        return r

    @staticmethod
    def validate_subtitle_refs(edl: VideoForgeEDL_V15) -> ValidationResult:
        r = ValidationResult()
        wids = {w.word_id for w in edl.transcript}
        for sub in edl.subtitle_events:
            missing = [w for w in sub.word_ids if w not in wids]
            if missing:
                r.add(
                    ValidationSeverity.ERROR, "sub_validator",
                    f"sub[{sub.sub_id}]",
                    f"word_ids inexistentes: {missing}"
                )
        return r


class PreRenderValidator:
    """Validación final antes de render."""

    @staticmethod
    def validate_assets(edl: VideoForgeEDL_V15) -> ValidationResult:
        r = ValidationResult()
        for br in edl.b_roll_tracks:
            if not br.asset_verified:
                r.add(
                    ValidationSeverity.ERROR, "asset_validator",
                    f"broll[{br.broll_id}]",
                    f"Asset no verificado: '{br.search_query}'"
                )
        for m in edl.music_tracks:
            if not m.copyright_cleared:
                r.add(
                    ValidationSeverity.WARNING, "compliance",
                    f"music[{m.track_id}]",
                    f"Copyright no limpio: '{m.asset_path}'"
                )
        return r

    @staticmethod
    def validate_render_plan(edl: VideoForgeEDL_V15) -> ValidationResult:
        r = ValidationResult()
        if not edl.render_plan:
            r.add(ValidationSeverity.FATAL, "pre_render", "render_plan", "Falta render_plan")
        elif not edl.render_plan.approved_by_qc:
            r.add(ValidationSeverity.FATAL, "pre_render", "render_plan.approved", "QC no aprobó")
        return r

    @staticmethod
    def validate_no_fatals(edl: VideoForgeEDL_V15) -> ValidationResult:
        r = ValidationResult()
        for e in edl.validation_errors:
            if e.severity == ValidationSeverity.FATAL:
                r.add(
                    ValidationSeverity.FATAL, "pre_render", e.field_path,
                    f"FATAL sin resolver: {e.message}"
                )
        return r


def run_all_validators(edl: VideoForgeEDL_V15) -> Tuple[bool, List[ValidationEntry]]:
    """Ejecuta todos los validadores y retorna (is_valid, errors)."""
    results = [
        TimelineValidator.validate_no_gaps(edl),
        TimelineValidator.validate_vfx_bounds(edl),
        TimelineValidator.validate_sfx_bounds(edl),
        TimelineValidator.validate_subtitle_refs(edl),
        PreRenderValidator.validate_assets(edl),
        PreRenderValidator.validate_render_plan(edl),
        PreRenderValidator.validate_no_fatals(edl),
    ]

    all_errors = []
    ok = True
    for r in results:
        all_errors.extend(r.errors)
        if not r.is_valid:
            ok = False

    return ok, all_errors
