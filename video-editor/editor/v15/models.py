"""
VideoForge V15 — Pydantic V2 State Models
==========================================
Estado Maestro EDL + todos los modelos de datos.
Motor LLM: Claude Sonnet 4.6 via Anthropic API
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import (
    BaseModel, Field, field_validator, model_validator,
    computed_field, ConfigDict
)


# ════════════════════════════════════════════════════════════════════════════════
# ENUMS
# ════════════════════════════════════════════════════════════════════════════════

class PresetStyle(str, Enum):
    TIKTOK_PRO   = "tiktok_pro"
    HORMOZI      = "hormozi"
    CINEMATIC    = "cinematic"
    PODCAST      = "podcast"
    SHORTS_VIRAL = "shorts_viral"

class AnimationType(str, Enum):
    NONE = "none"; POP = "pop"; BOUNCE = "bounce"
    SHAKE = "shake"; FADE = "fade"; SLIDE = "slide"

class VFXType(str, Enum):
    ZOOM_PUNCH = "zoom_punch"; CAMERA_SHAKE = "camera_shake"
    GLITCH = "glitch"; FLASH = "flash"; COLOR_POP = "color_pop"
    FREEZE_FRAME = "freeze_frame"; SPEED_RAMP = "speed_ramp"

class SFXType(str, Enum):
    WHOOSH = "whoosh"; IMPACT = "impact"; RISER = "riser"
    POP = "pop"; CLICK = "click"; BRAAM = "braam"; SWOOSH = "swoosh"

class AgentStatus(str, Enum):
    PENDING = "pending"; RUNNING = "running"; COMPLETED = "completed"
    FAILED = "failed"; SKIPPED = "skipped"; RETRYING = "retrying"

class ValidationSeverity(str, Enum):
    INFO = "info"; WARNING = "warning"; ERROR = "error"; FATAL = "fatal"

class ApprovalState(str, Enum):
    PENDING = "pending"; APPROVED = "approved"
    REJECTED = "rejected"; BYPASSED = "bypassed"

class EmotionTag(str, Enum):
    ENERGETIC = "energetic"; CALM = "calm"; FUNNY = "funny"
    DRAMATIC = "dramatic"; INSPIRING = "inspiring"
    TENSE = "tense"; NEUTRAL = "neutral"

class AudioLaneType(str, Enum):
    VOICE = "voice"; MUSIC = "music"; SFX = "sfx"; AMBIENT = "ambient"


# ════════════════════════════════════════════════════════════════════════════════
# MODELOS DE INFRAESTRUCTURA
# ════════════════════════════════════════════════════════════════════════════════

class AgentLogEntry(BaseModel):
    model_config = ConfigDict(frozen=True)
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: AgentStatus
    message: str
    confidence_score: float = Field(ge=0.0, le=1.0, default=1.0)
    duration_ms: Optional[int] = None
    retry_count: int = Field(ge=0, default=0)
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None

class ValidationEntry(BaseModel):
    model_config = ConfigDict(frozen=True)
    error_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    severity: ValidationSeverity
    agent_source: str
    field_path: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    auto_fixed: bool = False

class RollbackCheckpoint(BaseModel):
    checkpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    phase: str
    state_json: str
    agents_completed: List[str] = []
    description: str = ""

class WriteLock(BaseModel):
    field_path: str
    locked_by: str
    locked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


# ════════════════════════════════════════════════════════════════════════════════
# MODELOS DE CONTENIDO
# ════════════════════════════════════════════════════════════════════════════════

class Word(BaseModel):
    word_id: int
    text: str
    start: float = Field(ge=0.0)
    end: float = Field(ge=0.0)
    speaker: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    is_hook: bool = False
    is_filler: bool = False
    color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    animation: AnimationType = AnimationType.NONE
    virality_score: float = Field(ge=0.0, le=1.0, default=0.0)

    @field_validator("end")
    @classmethod
    def end_after_start(cls, v, info):
        if "start" in info.data and v <= info.data["start"]:
            raise ValueError(f"end ({v}) must be > start ({info.data['start']})")
        return v

class SceneSegment(BaseModel):
    segment_id: int
    start: float = Field(ge=0.0)
    end: float = Field(ge=0.0)
    scene_type: Literal["talking_head", "b_roll", "transition", "title", "unknown"]
    emotion: EmotionTag = EmotionTag.NEUTRAL
    energy_level: float = Field(ge=0.0, le=1.0, default=0.5)
    motion_intensity: float = Field(ge=0.0, le=1.0, default=0.0)

class VideoCut(BaseModel):
    cut_id: int
    source_start: float = Field(ge=0.0)
    source_end: float = Field(ge=0.0)
    timeline_start: float = Field(ge=0.0)
    timeline_end: float = Field(ge=0.0)
    visual_context: Optional[str] = None
    scene_segment_id: Optional[int] = None
    emotion: EmotionTag = EmotionTag.NEUTRAL
    keep_audio: bool = True
    speed_factor: float = Field(ge=0.1, le=10.0, default=1.0)

    @model_validator(mode="after")
    def validate_durations(self):
        src = self.source_end - self.source_start
        tl = self.timeline_end - self.timeline_start
        expected = src / self.speed_factor
        if abs(tl - expected) > 0.05:
            raise ValueError(
                f"cut {self.cut_id}: timeline_dur={tl:.3f}s != "
                f"source_dur/speed={expected:.3f}s"
            )
        return self

class BRollInsert(BaseModel):
    broll_id: int = Field(default_factory=lambda: int(uuid.uuid4().int % 100000))
    target_cut_id: int
    timeline_start: float = Field(ge=0.0)
    timeline_end: float = Field(ge=0.0)
    search_query: str
    asset_url: Optional[str] = None
    asset_local_path: Optional[str] = None
    asset_verified: bool = False
    blend_mode: Literal["normal", "screen", "multiply", "overlay"] = "normal"
    opacity: float = Field(ge=0.0, le=1.0, default=1.0)

class VFXEvent(BaseModel):
    vfx_id: int = Field(default_factory=lambda: int(uuid.uuid4().int % 100000))
    effect_name: VFXType
    target_cut_id: Optional[int] = None
    start_time_in_timeline: float = Field(ge=0.0)
    duration: float = Field(gt=0.0)
    intensity: float = Field(ge=0.0, le=1.0)
    parameters: Dict[str, Any] = {}
    verified_against_cuts: bool = False

class SFXEvent(BaseModel):
    sfx_id: int = Field(default_factory=lambda: int(uuid.uuid4().int % 100000))
    sound_type: SFXType
    start_time_in_timeline: float = Field(ge=0.0)
    duration: float = Field(gt=0.0, default=0.5)
    volume_db: float = Field(ge=-60.0, le=6.0, default=0.0)
    fade_in_ms: int = Field(ge=0, default=0)
    fade_out_ms: int = Field(ge=0, default=0)
    asset_path: Optional[str] = None
    verified_against_cuts: bool = False

class MusicTrackEvent(BaseModel):
    track_id: int = Field(default_factory=lambda: int(uuid.uuid4().int % 100000))
    asset_path: str
    timeline_start: float = Field(ge=0.0)
    timeline_end: float = Field(ge=0.0)
    volume_db: float = Field(ge=-60.0, le=0.0, default=-12.0)
    ducking_enabled: bool = True
    ducking_target_db: float = Field(ge=-60.0, le=0.0, default=-25.0)
    ducking_attack_ms: int = Field(ge=0, default=200)
    ducking_release_ms: int = Field(ge=0, default=500)
    loop: bool = False
    copyright_cleared: bool = False

class AudioLane(BaseModel):
    lane_id: int
    lane_type: AudioLaneType
    events: List[int] = []
    master_volume_db: float = Field(ge=-60.0, le=6.0, default=0.0)

class SubtitleEvent(BaseModel):
    sub_id: int
    word_ids: List[int]
    timeline_start: float = Field(ge=0.0)
    timeline_end: float = Field(ge=0.0)
    text: str
    style_id: str
    position_x: float = Field(ge=0.0, le=1.0, default=0.5)
    position_y: float = Field(ge=0.0, le=1.0, default=0.85)
    animation: AnimationType = AnimationType.POP

class SubtitleStylePack(BaseModel):
    style_id: str
    font_family: str = "Montserrat"
    font_size: int = Field(ge=8, le=200, default=72)
    font_color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    outline_color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    outline_width: float = Field(ge=0.0, le=10.0, default=3.0)
    bold: bool = True
    all_caps: bool = False
    max_chars_per_line: int = Field(ge=5, le=50, default=20)
    words_per_subtitle: int = Field(ge=1, le=5, default=3)

class CropInstruction(BaseModel):
    cut_id: int
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    w: float = Field(ge=0.0, le=1.0)
    h: float = Field(ge=0.0, le=1.0)
    target_aspect: Literal["9:16", "1:1", "4:5", "16:9"] = "9:16"
    reframe_motion: bool = False

class ViralityMarker(BaseModel):
    marker_id: int
    timeline_position: float = Field(ge=0.0)
    marker_type: Literal["hook", "climax", "punchline", "cta", "transition_peak"]
    intensity: float = Field(ge=0.0, le=1.0)
    word_id: Optional[int] = None

class SourceMediaMetadata(BaseModel):
    file_path: str
    duration: float = Field(gt=0.0)
    fps: float = Field(gt=0.0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    codec_video: str
    codec_audio: str
    sample_rate: int
    channels: int
    file_size_bytes: int
    md5_hash: str
    has_multiple_speakers: bool = False

class RenderPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    output_path: str
    output_format: Literal["mp4", "mov", "webm"] = "mp4"
    output_width: int = Field(gt=0)
    output_height: int = Field(gt=0)
    output_fps: float = Field(gt=0.0)
    output_codec: str = "libx264"
    output_audio_codec: str = "aac"
    crf: int = Field(ge=0, le=51, default=18)
    preset: Literal["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"] = "fast"
    use_gpu: bool = False
    gpu_encoder: Optional[Literal["h264_nvenc", "hevc_nvenc", "h264_videotoolbox"]] = None
    render_passes: int = Field(ge=1, le=3, default=1)
    estimated_duration_s: float = 0.0
    approved_by_qc: bool = False


# ════════════════════════════════════════════════════════════════════════════════
# ESTADO MAESTRO V15 EDL
# ════════════════════════════════════════════════════════════════════════════════

class VideoForgeEDL_V15(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )

    # Identidad
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    schema_version: Literal["V15.0"] = "V15.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    preset_style: PresetStyle

    # Source
    source_media: Optional[SourceMediaMetadata] = None

    # Agentes
    agents_status: Dict[str, AgentStatus] = {}
    agents_log: List[AgentLogEntry] = []
    active_locks: List[WriteLock] = []

    # Contenido
    transcript: List[Word] = []
    scene_segments: List[SceneSegment] = []
    timeline_cuts: List[VideoCut] = []
    b_roll_tracks: List[BRollInsert] = []
    vfx_tracks: List[VFXEvent] = []
    sfx_tracks: List[SFXEvent] = []
    music_tracks: List[MusicTrackEvent] = []
    audio_lanes: List[AudioLane] = []
    subtitle_events: List[SubtitleEvent] = []
    subtitle_style_packs: Dict[str, SubtitleStylePack] = {}
    crop_instructions: List[CropInstruction] = []
    virality_markers: List[ViralityMarker] = []

    # Metadatos
    lut_applied: Optional[str] = None
    style_pack: Optional[SubtitleStylePack] = None
    speaker_diarization_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    emotion_tags: Dict[str, EmotionTag] = {}

    # QC
    is_qc_approved: bool = False
    qc_report: Dict[str, Any] = {}
    compliance_flags: List[str] = []
    validation_errors: List[ValidationEntry] = []
    warnings: List[str] = []

    # Render
    render_plan: Optional[RenderPlan] = None
    ffmpeg_commands: List[str] = []
    total_timeline_duration: float = Field(ge=0.0, default=0.0)

    # Trazabilidad
    rollback_checkpoints: List[RollbackCheckpoint] = []
    decision_history: List[Dict[str, Any]] = []
    pipeline_metrics: Dict[str, Any] = {}
    retry_counters: Dict[str, int] = {}
    approval_states: Dict[str, ApprovalState] = {}
    integrity_hash: Optional[str] = None

    # ── Validadores cruzados ──

    @model_validator(mode="after")
    def no_timeline_overlap(self):
        cuts = sorted(self.timeline_cuts, key=lambda c: c.timeline_start)
        for i in range(len(cuts) - 1):
            if cuts[i].timeline_end > cuts[i + 1].timeline_start + 0.001:
                raise ValueError(
                    f"Overlap: cut {cuts[i].cut_id} ends {cuts[i].timeline_end:.3f}s "
                    f"but cut {cuts[i + 1].cut_id} starts {cuts[i + 1].timeline_start:.3f}s"
                )
        return self

    @model_validator(mode="after")
    def vfx_refs_exist(self):
        ids = {c.cut_id for c in self.timeline_cuts}
        for v in self.vfx_tracks:
            if v.target_cut_id is not None and v.target_cut_id not in ids:
                raise ValueError(f"VFX {v.vfx_id} refs missing cut {v.target_cut_id}")
        return self

    @model_validator(mode="after")
    def broll_refs_exist(self):
        ids = {c.cut_id for c in self.timeline_cuts}
        for b in self.b_roll_tracks:
            if b.target_cut_id not in ids:
                raise ValueError(f"B-Roll {b.broll_id} refs missing cut {b.target_cut_id}")
        return self

    @computed_field
    @property
    def computed_duration(self) -> float:
        return max((c.timeline_end for c in self.timeline_cuts), default=0.0)

    def compute_integrity_hash(self) -> str:
        data = self.model_dump_json(exclude={"integrity_hash", "updated_at"})
        return hashlib.sha256(data.encode()).hexdigest()

    def create_checkpoint(self, phase: str, desc: str = "") -> RollbackCheckpoint:
        cp = RollbackCheckpoint(
            phase=phase,
            state_json=self.model_dump_json(),
            agents_completed=[n for n, s in self.agents_status.items()
                              if s == AgentStatus.COMPLETED],
            description=desc,
        )
        self.rollback_checkpoints.append(cp)
        return cp

    def acquire_lock(self, field: str, agent: str) -> bool:
        now = datetime.utcnow()
        self.active_locks = [l for l in self.active_locks
                             if not (l.expires_at and l.expires_at < now)]
        if any(l.field_path == field for l in self.active_locks):
            return False
        self.active_locks.append(WriteLock(
            field_path=field, locked_by=agent,
            expires_at=now + timedelta(minutes=5)
        ))
        return True

    def release_lock(self, field: str, agent: str):
        self.active_locks = [
            l for l in self.active_locks
            if not (l.field_path == field and l.locked_by == agent)
        ]
