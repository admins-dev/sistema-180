"""
VideoForge V15 — Pipeline Runner (LOCAL MODE)
===============================================
Entry point — 100% local, NO requiere API externa.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Dict, Optional

from .models import PresetStyle, VideoForgeEDL_V15
from .orchestrator import AgentNode, ExecutiveOfficeOrchestrator
from .media_analyzer import analyze_media
from .all_agents import ALL_V15_AGENTS

logger = logging.getLogger("v15.pipeline")


def create_agent_registry() -> Dict[str, AgentNode]:
    """Crea el registro completo de agentes (todos locales, sin LLM)."""

    registry = {}
    for name, agent_class in ALL_V15_AGENTS.items():
        # Todos los agentes son locales — no necesitan LLM
        agent = agent_class(llm=None)

        # Definir dependencias
        depends = []
        writes = list(agent_class.get_write_fields()) if hasattr(agent_class, '_can_write') else []

        if name == "visual_analyst":
            depends = ["transcript"]
        elif name == "cut_script":
            depends = ["transcript"]
        elif name == "hook_editor":
            depends = ["transcript"]
        elif name in ("subtitle", "vfx_editor", "sfx_designer",
                       "broll_director", "music_supervisor", "crop_reframing"):
            depends = ["cut_script"]
        elif name == "style_designer":
            depends = ["cut_script"]
        elif name == "style_consistency":
            depends = ["subtitle", "vfx_editor", "style_designer"]
        elif name == "qc":
            depends = ["style_consistency"]
        elif name == "compliance":
            depends = ["music_supervisor", "broll_director"]
        elif name == "render_planner":
            depends = ["qc"]

        registry[name] = AgentNode(
            name=name,
            agent=agent,
            depends_on=depends,
            writes_fields=writes,
        )

    return registry


async def run_v15_pipeline(
    input_path: str,
    preset: str = "tiktok_pro",
    api_key: Optional[str] = None,  # Ignorado — 100% local
    project_name: Optional[str] = None,
    progress_callback=None,
) -> Dict:
    """
    Ejecuta la pipeline V15 completa — 100% LOCAL.

    Args:
        input_path: Ruta al vídeo de entrada
        preset: Estilo de preset (tiktok_pro, hormozi, cinematic, podcast, shorts_viral)
        api_key: IGNORADO — V15 es 100% local
        project_name: Nombre del proyecto
        progress_callback: Callable(phase, progress_pct, message)

    Returns:
        Dict con resultado: output_path, stats, edl
    """
    start_time = time.time()

    # Preset
    try:
        preset_style = PresetStyle(preset)
    except ValueError:
        preset_style = PresetStyle.TIKTOK_PRO
        logger.warning(f"Preset '{preset}' no válido, usando tiktok_pro")

    # Proyecto
    if not project_name:
        project_name = os.path.splitext(os.path.basename(input_path))[0]

    logger.info(f"🎬 V15 Pipeline LOCAL — '{project_name}' — preset: {preset_style.value}")

    # 1. Analizar media
    if progress_callback:
        progress_callback("INTAKE", 5, "Analizando vídeo...")
    media = analyze_media(input_path)

    # 2. Crear EDL inicial
    edl = VideoForgeEDL_V15(
        project_name=project_name,
        preset_style=preset_style,
        source_media=media,
    )

    # 3. Crear registro de agentes (LOCAL — sin LLM)
    registry = create_agent_registry()

    # 4. Ejecutar orquestador
    orchestrator = ExecutiveOfficeOrchestrator(registry)

    # Progress wrapper
    phase_progress = {
        "INTAKE": 10, "ANALYSIS": 25, "EDITORIAL": 40,
        "ENRICHMENT": 60, "STYLING": 75, "VALIDATION": 85,
        "RENDER_PREP": 95,
    }

    # Run
    try:
        result_edl = await orchestrator.run(edl)
    except Exception as e:
        logger.error(f"❌ Pipeline falló: {e}")
        raise

    elapsed = time.time() - start_time

    # 5. Resultado
    result = {
        "success": result_edl.is_qc_approved,
        "project_id": result_edl.project_id,
        "preset": preset_style.value,
        "stats": {
            "source_duration": media.duration,
            "timeline_duration": result_edl.total_timeline_duration,
            "cuts_count": len(result_edl.timeline_cuts),
            "vfx_count": len(result_edl.vfx_tracks),
            "sfx_count": len(result_edl.sfx_tracks),
            "subtitle_count": len(result_edl.subtitle_events),
            "broll_count": len(result_edl.b_roll_tracks),
            "music_count": len(result_edl.music_tracks),
            "qc_approved": result_edl.is_qc_approved,
            "warnings_count": len(result_edl.warnings),
            "elapsed_seconds": round(elapsed, 1),
        },
        "qc_report": result_edl.qc_report,
        "edl_json": result_edl.model_dump_json(indent=2),
    }

    if progress_callback:
        progress_callback("DONE", 100, "¡Pipeline V15 completada!")

    logger.info(
        f"✅ V15 LOCAL completada en {elapsed:.1f}s — "
        f"{len(result_edl.timeline_cuts)} cuts, "
        f"QC={'✅' if result_edl.is_qc_approved else '❌'}"
    )

    return result


def run_v15_sync(
    input_path: str,
    preset: str = "tiktok_pro",
    project_name: Optional[str] = None,
) -> Dict:
    """Wrapper síncrono para run_v15_pipeline."""
    return asyncio.run(
        run_v15_pipeline(input_path, preset, project_name=project_name)
    )
