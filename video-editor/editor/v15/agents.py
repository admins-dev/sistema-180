"""
VideoForge V15 — Agent Base + CutScript Agent
===============================================
Base agent with permissions, validation, confidence scoring.
CutScriptAgent as the reference implementation.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Type, frozenset

from pydantic import BaseModel, Field

from .models import (
    AgentLogEntry, AgentStatus, EmotionTag, ValidationEntry,
    ValidationSeverity, VideoCut, VideoForgeEDL_V15,
)
from .llm_client import ClaudeSonnetClient

logger = logging.getLogger("v15.agents")


# ════════════════════════════════════════════════════════════════════════════════
# DECORATOR DE PERMISOS
# ════════════════════════════════════════════════════════════════════════════════

def agent_permissions(can_read: List[str], can_write: List[str]):
    """Decorator que define qué campos del EDL puede leer/escribir un agente."""
    def decorator(cls):
        cls._can_read = frozenset(can_read)
        cls._can_write = frozenset(can_write)
        return cls
    return decorator


class AgentPermissionViolation(Exception):
    """Se lanza si un agente modifica campos fuera de su permiso."""
    pass


# ════════════════════════════════════════════════════════════════════════════════
# BASE AGENT
# ════════════════════════════════════════════════════════════════════════════════

class BaseAgent(ABC):
    """
    Clase base para todos los agentes V15.
    - Extrae contexto según permisos de lectura
    - Verifica que solo escribe en campos autorizados
    - Registra logs con timing y confidence
    """
    NAME: str = "base_agent"
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 120
    MIN_CONFIDENCE: float = 0.6

    def __init__(self, llm: ClaudeSonnetClient):
        self.llm = llm

    @classmethod
    def get_write_fields(cls) -> frozenset:
        return getattr(cls, "_can_write", frozenset())

    @classmethod
    def get_read_fields(cls) -> frozenset:
        return getattr(cls, "_can_read", frozenset())

    def _extract_context(self, edl: VideoForgeEDL_V15) -> Dict[str, Any]:
        """Extrae solo los campos que el agente tiene permiso de leer."""
        ctx = {}
        for field in self.get_read_fields():
            val = getattr(edl, field, None)
            if val is not None:
                if isinstance(val, list) and len(val) > 200:
                    ctx[field] = val[:200]  # Truncar contexto largo
                else:
                    ctx[field] = val
        return ctx

    async def run(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        """Ejecuta el agente con verificación de permisos y logging."""
        start = datetime.utcnow()

        # Snapshot de campos NO-escribibles para verificar al final
        exempt_fields = {
            "agents_status", "agents_log", "active_locks",
            "updated_at", "retry_counters", "rollback_checkpoints",
            "decision_history", "validation_errors", "warnings",
            "pipeline_metrics", "approval_states"
        }
        snapshot_before = {
            f: getattr(edl, f) for f in edl.model_fields
            if f not in self.get_write_fields() and f not in exempt_fields
        }

        # Ejecutar lógica del agente
        result = await self.execute(edl)

        # Verificar que solo tocó sus campos
        for f, old_val in snapshot_before.items():
            new_val = getattr(result, f)
            if new_val != old_val:
                raise AgentPermissionViolation(
                    f"Agent {self.NAME} modified forbidden field '{f}'"
                )

        # Log de éxito
        ms = int((datetime.utcnow() - start).total_seconds() * 1000)
        result.agents_log.append(AgentLogEntry(
            agent_name=self.NAME,
            status=AgentStatus.COMPLETED,
            message="OK",
            duration_ms=ms,
            output_hash=result.compute_integrity_hash()
        ))
        logger.info(f"Agent {self.NAME} completed in {ms}ms")
        return result

    @abstractmethod
    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        """Implementación específica del agente."""
        ...


# ════════════════════════════════════════════════════════════════════════════════
# CUT SCRIPT AGENT (REFERENCIA)
# ════════════════════════════════════════════════════════════════════════════════

class CutScriptOutput(BaseModel):
    """Schema que Claude Sonnet devuelve como structured output."""
    cuts: List[Dict[str, Any]]
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)


@agent_permissions(
    can_read=["transcript", "scene_segments", "source_media", "preset_style"],
    can_write=["timeline_cuts", "total_timeline_duration"]
)
class CutScriptAgent(BaseAgent):
    """
    Agente CutScript — decide qué fragmentos del vídeo original sobreviven.
    Usa Extended Thinking para razonamiento profundo sobre cortes.
    """
    NAME = "cut_script"
    TIMEOUT_SECONDS = 180
    MIN_SEGMENT_DURATION = 1.5
    MAX_TOTAL_DURATION = 90.0

    SYSTEM_PROMPT = """Eres el agente CutScript de la Oficina Ejecutiva de Editores.
Tu ÚNICA responsabilidad: decidir qué fragmentos del vídeo original sobreviven.

REGLAS ABSOLUTAS:
1. Solo produces el campo `cuts`. Nada más.
2. NUNCA inventes timestamps que no existan en la transcripción.
3. source_start y source_end DEBEN estar dentro de [0, {source_duration}].
4. Duración total de cuts <= {max_duration}s.
5. timeline_start y timeline_end ponlos en 0.0; el sistema los recalcula.
6. Si no estás seguro de un corte, OMÍTELO. Mejor corto que roto.

CRITERIOS DE SELECCIÓN (prioridad):
1. Fragmentos con is_hook=True
2. Fragmentos con virality_score > 0.7
3. Speaker principal sin pausas largas
4. Alta energía emocional

FORMATO: Devuelve el schema CutScriptOutput exacto."""

    async def execute(self, edl: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        ctx = self._extract_context(edl)
        src_dur = edl.source_media.duration if edl.source_media else 999.0

        system = self.SYSTEM_PROMPT.format(
            source_duration=src_dur,
            max_duration=self.MAX_TOTAL_DURATION
        )
        user_msg = json.dumps({
            "transcript_sample": [
                w.model_dump() for w in ctx.get("transcript", [])[:150]
            ],
            "scene_segments": [
                s.model_dump() for s in ctx.get("scene_segments", [])
            ],
            "preset_style": ctx.get("preset_style", "tiktok_pro"),
            "source_duration": src_dur,
        }, ensure_ascii=False)

        raw = await self.llm.structured_output(
            system_prompt=system,
            user_prompt=user_msg,
            output_schema=CutScriptOutput,
            temperature=0.1,
        )

        if raw.confidence < self.MIN_CONFIDENCE:
            raise ValueError(
                f"CutScript confidence {raw.confidence:.2f} < threshold {self.MIN_CONFIDENCE}"
            )

        # Validar y recalcular cortes
        validated = self._validate_cuts(raw.cuts, edl)
        edl.timeline_cuts = validated
        edl.total_timeline_duration = max(
            (c.timeline_end for c in validated), default=0.0
        )
        edl.decision_history.append({
            "agent": self.NAME,
            "reasoning": raw.reasoning,
            "confidence": raw.confidence,
            "cuts_proposed": len(raw.cuts),
            "cuts_accepted": len(validated),
        })
        return edl

    def _validate_cuts(
        self, raw_cuts: List[Dict], edl: VideoForgeEDL_V15
    ) -> List[VideoCut]:
        """Valida cortes contra metadatos reales — NUNCA confía en timestamps del LLM."""
        src_dur = edl.source_media.duration if edl.source_media else float("inf")
        valid = []
        cursor = 0.0

        for i, rc in enumerate(raw_cuts):
            try:
                ss = float(rc.get("source_start", 0))
                se = float(rc.get("source_end", 0))
            except (TypeError, ValueError):
                continue

            # Rechazar si fuera de rango
            if se > src_dur + 0.1 or ss < 0 or se <= ss:
                logger.warning(f"Cut {i} descartado: fuera de rango [{ss}, {se}]")
                continue

            dur = se - ss
            if dur < self.MIN_SEGMENT_DURATION:
                continue

            speed = float(rc.get("speed_factor", 1.0))
            speed = max(0.1, min(speed, 10.0))
            tl_dur = dur / speed

            cut = VideoCut(
                cut_id=i + 1,
                source_start=ss, source_end=se,
                timeline_start=cursor,
                timeline_end=cursor + tl_dur,
                speed_factor=speed,
                visual_context=rc.get("visual_context"),
                emotion=rc.get("emotion", "neutral"),
            )
            cursor += tl_dur
            if cursor > self.MAX_TOTAL_DURATION:
                break
            valid.append(cut)

        logger.info(f"CutScript: {len(valid)}/{len(raw_cuts)} cortes validados")
        return valid
