"""
VideoForge V15 — Orchestrator
===============================
asyncio FSM que coordina los agentes en fases con locks, retries y rollback.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field as dc_field
from typing import Dict, List, Optional, Tuple

from .models import (
    AgentStatus, ValidationEntry, ValidationSeverity,
    VideoForgeEDL_V15,
)
from .agents import BaseAgent
from .validators import run_all_validators

logger = logging.getLogger("v15.orchestrator")


class PipelineAbortError(Exception):
    """Error fatal que detiene la pipeline."""
    pass


@dataclass
class AgentNode:
    """Nodo del grafo de ejecución."""
    name: str
    agent: BaseAgent
    depends_on: List[str] = dc_field(default_factory=list)
    writes_fields: List[str] = dc_field(default_factory=list)


class ExecutiveOfficeOrchestrator:
    """
    Orquestador central de la Oficina Ejecutiva de Editores V15.

    Fases:
    - INTAKE: Transcripción (sin LLM)
    - ANALYSIS: Diarización + Análisis Visual (paralelo)
    - EDITORIAL: CutScript + HookEditor (secuencial)
    - ENRICHMENT: 6 agentes creativos en paralelo
    - STYLING: Diseño + Consistencia
    - VALIDATION: Timeline + QC + Compliance
    - RENDER_PREP: Render Plan + FFmpeg Build
    """

    PHASES: List[Tuple[str, List[str], bool]] = [
        ("INTAKE",      ["transcript"],                              False),
        ("ANALYSIS",    ["diarization", "visual_analyst"],           True),
        ("EDITORIAL",   ["cut_script", "hook_editor"],               False),
        ("ENRICHMENT",  ["subtitle", "broll_director", "vfx_editor",
                         "sfx_designer", "music_supervisor",
                         "crop_reframing"],                          True),
        ("STYLING",     ["style_designer", "style_consistency"],     False),
        ("VALIDATION",  ["timeline_validator", "qc", "compliance"],  False),
        ("RENDER_PREP", ["render_planner", "ffmpeg_builder"],        False),
    ]

    def __init__(self, registry: Dict[str, AgentNode]):
        self.registry = registry
        self.state: Optional[VideoForgeEDL_V15] = None
        self._lock = asyncio.Lock()

    async def run(self, initial: VideoForgeEDL_V15) -> VideoForgeEDL_V15:
        """Ejecuta la pipeline completa."""
        self.state = initial
        logger.info(f"🎬 Proyecto {self.state.project_id} — inicio pipeline V15")

        for phase, agents, parallel in self.PHASES:
            logger.info(f"━━━ FASE: {phase} ━━━")
            self.state.create_checkpoint(phase, f"Pre-{phase}")

            try:
                if parallel:
                    await self._parallel(phase, agents)
                else:
                    await self._sequential(phase, agents)
                self._validate_integrity(phase)
            except PipelineAbortError as e:
                logger.critical(f"❌ ABORT en {phase}: {e}")
                self._rollback()
                raise

        logger.info(f"✅ Pipeline V15 completada — {self.state.project_name}")
        return self.state

    async def _sequential(self, phase: str, names: List[str]):
        """Ejecuta agentes secuencialmente."""
        for name in names:
            if name in self.registry:
                await self._exec_with_retry(name)
            else:
                logger.warning(f"Agente '{name}' no registrado, saltando")

    async def _parallel(self, phase: str, names: List[str]):
        """Ejecuta agentes en paralelo (3-5 max por recomendación Anthropic)."""
        tasks = [
            self._exec_with_retry(n) for n in names if n in self.registry
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                logger.error(f"Agente paralelo falló: {r}")

    async def _exec_with_retry(self, name: str):
        """Ejecuta un agente con reintentos automáticos."""
        node = self.registry[name]
        retries = 0

        # Verificar dependencias
        for dep in node.depends_on:
            if self.state.agents_status.get(dep) != AgentStatus.COMPLETED:
                raise PipelineAbortError(f"{name} necesita {dep} completado")

        self.state.agents_status[name] = AgentStatus.RUNNING

        while retries <= node.agent.MAX_RETRIES:
            try:
                # Adquirir locks
                async with self._lock:
                    for f in node.writes_fields:
                        if not self.state.acquire_lock(f, name):
                            raise RuntimeError(f"Lock bloqueado en {f}")

                # Ejecutar con timeout
                result = await asyncio.wait_for(
                    node.agent.run(self.state),
                    timeout=node.agent.TIMEOUT_SECONDS
                )

                # Guardar resultado
                async with self._lock:
                    self.state = result
                    self.state.agents_status[name] = AgentStatus.COMPLETED
                    for f in node.writes_fields:
                        self.state.release_lock(f, name)

                logger.info(f"  ✅ {name}")
                return

            except Exception as e:
                retries += 1
                self.state.retry_counters[name] = retries
                logger.warning(f"  ⚠️ {name} intento {retries}: {e}")

                # Liberar locks
                async with self._lock:
                    for f in node.writes_fields:
                        self.state.release_lock(f, name)

                if retries > node.agent.MAX_RETRIES:
                    self.state.agents_status[name] = AgentStatus.FAILED
                    self.state.validation_errors.append(ValidationEntry(
                        severity=ValidationSeverity.ERROR,
                        agent_source=name, field_path="*",
                        message=str(e)
                    ))
                    logger.error(f"  ❌ {name} fallido tras {retries} intentos")
                    return

                await asyncio.sleep(min(2 ** retries, 30))

    def _validate_integrity(self, phase: str):
        """Verifica que el estado sigue siendo válido tras una fase."""
        try:
            VideoForgeEDL_V15.model_validate(self.state.model_dump())
        except Exception as e:
            raise PipelineAbortError(f"Integridad rota tras {phase}: {e}")

    def _rollback(self):
        """Restaura al último checkpoint válido."""
        if not self.state.rollback_checkpoints:
            logger.error("No hay checkpoints para rollback")
            return
        cp = self.state.rollback_checkpoints[-1]
        logger.warning(f"🔄 Rollback a fase {cp.phase}")
        self.state = VideoForgeEDL_V15.model_validate_json(cp.state_json)
