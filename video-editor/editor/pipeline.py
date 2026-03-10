"""
VideoForge v10 — Pipeline Orchestrator
=========================================
Master pipeline with 12 professional presets. Integrates all v10 engines:
silence cutter, subtitles, smart zoom, smart reframe, audio processing,
retention engine, compositing, sound design, VFX engine, beat sync, transitions.
"""

import os
import sys
import time
import shutil

from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips

# v1 core modules
from editor.silence_cutter import cut_silences
from editor.subtitles import add_subtitles
from editor.smart_zoom import apply_smart_zoom
from editor.smart_reframe import smart_reframe
from editor.audio_engine import process_audio

# v3 modules (rewritten for v10)
from editor.retention_engine import analyze_energy, apply_retention_effects, enhance_climax_moments
from editor.compositing import apply_compositing
from editor.sound_design import apply_sound_design

# v10 new modules
from editor.vfx_engine import apply_vfx
from editor.beat_engine import detect_beats, apply_beat_sync
from editor.gpu_engine import detect_gpu, get_moviepy_write_params


# ─── 12 Professional Presets ───────────────────────────────────────

PRESETS = {
    # ── GOD MODE PRESETS ──
    "viral_max": {
        "description": "� VIRAL MAX — Todo al máximo: 12+ efectos, beat sync, retención brutal",
        "steps": [
            "silence_cut", "subtitles", "smart_zoom", "audio_pro",
            "retention", "beat_sync", "vfx", "sound_design", "compositing"
        ],
        "config": {
            "silence_threshold_db": -30,
            "min_silence_duration": 0.25,
            "padding_ms": 60,
            "zoom_mode": "punch_in",
            "zoom_scale": 1.2,
            "retention_gap": 2.0,
            "retention_threshold": 0.3,
            "color_grade": "cinematic",
            "vignette": True,
            "vfx_effects": {
                "film_grain": {"intensity": 0.05},
                "light_leak": {"intensity": 0.2, "position": "right"},
                "chromatic_aberration": {"intensity": 2},
                "glow": {"threshold": 210, "intensity": 0.25},
                "camera_shake": {"intensity": 3},
            },
            "beat_effects": ["zoom", "flash"],
        }
    },
    
    "cinematic_pro": {
        "description": "🎬 CINEMATIC PRO — Color grade cine, grain, letterbox, SFX épico",
        "steps": [
            "silence_cut", "subtitles", "audio_pro",
            "vfx", "compositing", "sound_design"
        ],
        "config": {
            "silence_threshold_db": -35,
            "min_silence_duration": 0.5,
            "color_grade": "cinematic",
            "vignette": True,
            "letterbox": True,
            "vfx_effects": {
                "film_grain": {"intensity": 0.08, "size": 2},
                "light_leak": {"intensity": 0.15, "position": "center"},
                "glow": {"threshold": 200, "intensity": 0.2},
                "particles": {"count": 15},
            },
        }
    },
    
    "aggressive_v10": {
        "description": "⚡ AGGRESSIVE v10 — Cortes 0.05s, glitch, bass drops, RGB split",
        "steps": [
            "silence_cut", "subtitles", "smart_zoom", "audio_pro",
            "retention", "beat_sync", "vfx", "sound_design", "compositing"
        ],
        "config": {
            "silence_threshold_db": -28,
            "min_silence_duration": 0.15,
            "padding_ms": 40,
            "zoom_mode": "punch_in",
            "zoom_scale": 1.25,
            "retention_gap": 1.5,
            "retention_threshold": 0.25,
            "color_grade": "dramatic",
            "vignette": True,
            "vfx_effects": {
                "film_grain": {"intensity": 0.04},
                "chromatic_aberration": {"intensity": 4},
                "camera_shake": {"intensity": 5},
            },
            "beat_effects": ["shake", "rgb_split", "flash"],
        }
    },
    
    "hormozi": {
        "description": "💰 HORMOZI — Estilo Alex Hormozi: zooms, subtítulos grandes, ritmo",
        "steps": [
            "silence_cut", "subtitles", "smart_zoom", "audio_pro",
            "retention", "compositing"
        ],
        "config": {
            "silence_threshold_db": -30,
            "min_silence_duration": 0.3,
            "padding_ms": 60,
            "zoom_mode": "punch_in",
            "zoom_scale": 1.2,
            "subtitle_font_size": 100,
            "subtitle_max_words": 3,
            "subtitle_highlight_color": [0, 255, 0],
            "retention_gap": 2.5,
            "color_grade": "warm",
            "vignette": True,
        }
    },
    
    "mrbeast": {
        "description": "🧲 MRBEAST — Colorido, rápido, SFX pesados, máxima energía",
        "steps": [
            "silence_cut", "subtitles", "smart_zoom", "audio_pro",
            "retention", "beat_sync", "vfx", "sound_design", "compositing"
        ],
        "config": {
            "silence_threshold_db": -28,
            "min_silence_duration": 0.2,
            "padding_ms": 50,
            "zoom_mode": "punch_in",
            "zoom_scale": 1.18,
            "subtitle_font_size": 90,
            "subtitle_highlight_color": [255, 255, 0],
            "retention_gap": 2.0,
            "color_grade": "neon",
            "vignette": True,
            "vfx_effects": {
                "film_grain": {"intensity": 0.03},
                "glow": {"threshold": 190, "intensity": 0.3},
            },
            "beat_effects": ["zoom", "flash"],
        }
    },
    
    "music_video": {
        "description": "� MUSIC VIDEO — Beat-sync total, VFX reactivos al ritmo",
        "steps": [
            "silence_cut", "audio_pro",
            "beat_sync", "vfx", "compositing"
        ],
        "config": {
            "silence_threshold_db": -40,
            "min_silence_duration": 0.8,
            "color_grade": "neon",
            "vignette": True,
            "vfx_effects": {
                "film_grain": {"intensity": 0.04},
                "light_leak": {"intensity": 0.3, "position": "right"},
                "chromatic_aberration": {"intensity": 3},
                "glow": {"threshold": 180, "intensity": 0.35},
                "particles": {"count": 30},
            },
            "beat_effects": ["zoom", "flash", "rgb_split"],
        }
    },
    
    # ── PLATFORM PRESETS ──
    "reel_pro": {
        "description": "� REEL PRO — Instagram vertical, subtítulos, retención, VFX",
        "steps": [
            "silence_cut", "reframe_916", "subtitles", "smart_zoom",
            "audio_pro", "retention", "vfx", "sound_design", "compositing"
        ],
        "config": {
            "silence_threshold_db": -30,
            "min_silence_duration": 0.25,
            "padding_ms": 60,
            "target_ratio": [9, 16],
            "zoom_mode": "punch_in",
            "zoom_scale": 1.15,
            "retention_gap": 2.5,
            "color_grade": "warm",
            "vignette": True,
            "vfx_effects": {
                "film_grain": {"intensity": 0.04},
                "glow": {"threshold": 210, "intensity": 0.2},
            },
        }
    },
    
    "tiktok_pro": {
        "description": "� TIKTOK PRO — Vertical, beat-sync, retención, SFX",
        "steps": [
            "silence_cut", "reframe_916", "subtitles", "smart_zoom",
            "audio_pro", "retention", "beat_sync", "sound_design", "compositing"
        ],
        "config": {
            "silence_threshold_db": -28,
            "min_silence_duration": 0.2,
            "padding_ms": 50,
            "target_ratio": [9, 16],
            "zoom_mode": "punch_in",
            "zoom_scale": 1.2,
            "retention_gap": 2.0,
            "color_grade": "neon",
            "vignette": True,
            "beat_effects": ["zoom", "flash"],
        }
    },
    
    "youtube_pro": {
        "description": "▶️ YOUTUBE PRO — 16:9, color cine, SFX pro, subtítulos",
        "steps": [
            "silence_cut", "subtitles", "smart_zoom", "audio_pro",
            "retention", "vfx", "sound_design", "compositing"
        ],
        "config": {
            "silence_threshold_db": -33,
            "min_silence_duration": 0.4,
            "padding_ms": 70,
            "zoom_mode": "punch_in",
            "zoom_scale": 1.12,
            "retention_gap": 3.0,
            "color_grade": "cinematic",
            "vignette": True,
            "vfx_effects": {
                "film_grain": {"intensity": 0.05},
                "light_leak": {"intensity": 0.12},
            },
        }
    },
    
    "ad_killer": {
        "description": "📢 AD KILLER — Anuncio con retención máxima, B-Roll, CTA",
        "steps": [
            "silence_cut", "subtitles", "smart_zoom", "audio_pro",
            "retention", "broll", "vfx", "sound_design", "compositing"
        ],
        "config": {
            "silence_threshold_db": -28,
            "min_silence_duration": 0.15,
            "padding_ms": 40,
            "zoom_mode": "punch_in",
            "zoom_scale": 1.2,
            "retention_gap": 1.5,
            "retention_threshold": 0.25,
            "color_grade": "warm",
            "vignette": True,
            "vfx_effects": {
                "film_grain": {"intensity": 0.03},
                "glow": {"threshold": 200, "intensity": 0.2},
            },
        }
    },
    
    "podcast_pro": {
        "description": "🎙️ PODCAST PRO — Audio premium, subtítulos, zoom suave",
        "steps": [
            "silence_cut", "subtitles", "smart_zoom", "audio_pro",
            "compositing"
        ],
        "config": {
            "silence_threshold_db": -38,
            "min_silence_duration": 0.6,
            "padding_ms": 100,
            "zoom_mode": "ken_burns",
            "zoom_scale": 1.08,
            "color_grade": "warm",
            "vignette": True,
        }
    },
    
    "speed_only": {
        "description": "⚡ SPEED ONLY — Solo corte de silencios + GPU (ultra rápido)",
        "steps": ["silence_cut"],
        "config": {
            "silence_threshold_db": -33,
            "min_silence_duration": 0.4,
            "padding_ms": 80,
        }
    },
}


# ─── Pipeline Orchestrator ─────────────────────────────────────────

def run_pipeline(input_path, output_path, preset="youtube_pro", 
                 music_path=None, custom_config=None, progress_callback=None):
    """
    VideoForge Pro — Master Pipeline
    
    Processes a video through the selected preset's step chain.
    Each step is fault-tolerant (continues on error).
    All encoding uses GPU acceleration when available.
    progress_callback(pct, msg) — optional function to report progress.
    """
    def report(pct, msg):
        if progress_callback:
            try:
                progress_callback(pct, msg)
            except:
                pass
        print(f"   [{pct}%] {msg}")
    
    start_time = time.time()
    
    if preset not in PRESETS:
        print(f"⚠️ Preset '{preset}' no encontrado. Usando 'youtube_pro'")
        preset = "youtube_pro"
    
    preset_data = PRESETS[preset]
    active_steps = preset_data["steps"]
    active_config = {**preset_data.get("config", {})}
    if custom_config:
        active_config.update(custom_config)
    
    # Detect GPU
    gpu_info = detect_gpu()
    gpu_label = gpu_info["encoder"] if gpu_info["encoder"] != "libx264" else "CPU"
    
    total_steps = len(active_steps)
    report(10, f"🎬 Preset '{preset}' — {total_steps} pasos")
    
    print("=" * 60)
    print(f"🎬 VideoForge Pro — Preset '{preset}'")
    print(f"   {preset_data.get('description', '')}")
    print(f"   🖥  Motor: {gpu_label} | Threads: {os.cpu_count()}")
    print(f"   📥 Input:  {input_path}")
    print(f"   📤 Output: {output_path}")
    print(f"   🔧 Steps:  {' → '.join(active_steps)}")
    print("=" * 60)
    
    # Directories
    temp_dir = os.path.join(os.path.dirname(output_path) or '.', ".videoforge_temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    current_video_path = input_path
    step_results = {}
    energy_map = None
    beat_data = None
    
    try:
        step_num = 0
        
        # ── STEP: Silence Cut ──
        if "silence_cut" in active_steps:
            step_num += 1
            report(15, "✂️ Cortando silencios...")
            print(f"\n📌 [{step_num}] ✂️ Cortando silencios...")
            try:
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_jumpcut.mp4")
                result = cut_silences(
                    current_video_path, temp_out,
                    silence_threshold_db=active_config.get("silence_threshold_db", -35),
                    min_silence_duration=active_config.get("min_silence_duration", 0.4),
                    padding_ms=active_config.get("padding_ms", 80)
                )
                step_results["silence_cut"] = result
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Silence cut falló (continuando): {e}")
        
        # ── STEP: Reframe 9:16 ──
        if "reframe_916" in active_steps:
            step_num += 1
            report(22, "📐 Reframe a vertical 9:16...")
            print(f"\n📌 [{step_num}] 📐 Reframe a vertical 9:16...")
            try:
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_reframed.mp4")
                result = smart_reframe(
                    current_video_path, temp_out,
                    target_ratio=tuple(active_config.get("target_ratio", [9, 16]))
                )
                step_results["reframe"] = result
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Reframe falló (continuando): {e}")
        
        # ── STEP: Audio Processing ──
        if "audio_pro" in active_steps:
            step_num += 1
            report(30, "🎧 Audio profesional...")
            print(f"\n📌 [{step_num}] 🎧 Audio profesional...")
            try:
                temp_audio = os.path.join(temp_dir, f"{step_num:02d}_audio.wav")
                result = process_audio(
                    current_video_path, temp_audio,
                    music_path=music_path,
                    target_lufs=active_config.get("target_lufs", -14)
                )
                step_results["audio"] = result
                
                video = VideoFileClip(current_video_path)
                new_audio = AudioFileClip(temp_audio)
                if new_audio.duration > video.duration:
                    new_audio = new_audio.subclipped(0, video.duration)
                video_with_audio = video.with_audio(new_audio)
                
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_audio_done.mp4")
                write_params = get_moviepy_write_params(gpu_info)
                video_with_audio.write_videofile(temp_out, **write_params)
                video.close()
                new_audio.close()
                video_with_audio.close()
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Audio pro falló (continuando): {e}")
        
        # ── STEP: Smart Zoom ──
        if "smart_zoom" in active_steps:
            step_num += 1
            report(38, "🔍 Zoom inteligente...")
            print(f"\n📌 [{step_num}] 🔍 Zoom inteligente...")
            try:
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_zoomed.mp4")
                result = apply_smart_zoom(
                    current_video_path, temp_out,
                    mode=active_config.get("zoom_mode", "punch_in"),
                    end_scale=active_config.get("zoom_scale", 1.15)
                )
                step_results["zoom"] = result
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Smart zoom falló (continuando): {e}")
        
        # ── STEP: Subtitles ──
        if "subtitles" in active_steps:
            step_num += 1
            report(45, "📝 Subtítulos animados...")
            print(f"\n📌 [{step_num}] 📝 Subtítulos animados...")
            try:
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_subtitled.mp4")
                subtitle_config = {
                    "style": active_config.get("subtitle_style", "hormozi"),
                    "position": active_config.get("subtitle_position", "center"),
                    "max_words_per_line": active_config.get("subtitle_max_words", 4),
                    "whisper_model": active_config.get("whisper_model", "base"),
                    "language": active_config.get("language", "es"),
                }
                highlight_color = active_config.get("subtitle_highlight_color")
                if highlight_color:
                    subtitle_config["highlight_color"] = tuple(highlight_color)
                
                result = add_subtitles(current_video_path, temp_out, config=subtitle_config)
                step_results["subtitles"] = result
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Subtítulos falló (continuando): {e}")
        
        # ── v10 STEP: Analyze Energy & Beats (shared data) ──
        needs_energy = any(s in active_steps for s in ["retention", "vfx", "sound_design"])
        needs_beats = "beat_sync" in active_steps
        
        if needs_energy or needs_beats:
            step_num += 1
            report(52, "📊 Analizando energía y ritmo...")
            print(f"\n📌 [{step_num}] 📊 Analizando audio (energía + ritmo)...")
            try:
                video = VideoFileClip(current_video_path)
                if video.audio:
                    if needs_energy:
                        energy_map = analyze_energy(video.audio)
                        print(f"   ✅ Energy map: {len(energy_map)} puntos analizados")
                    if needs_beats:
                        beat_data = detect_beats(video.audio)
                        print(f"   ✅ Beat map: {beat_data.get('bpm', 0)} BPM, {len(beat_data.get('beats', []))} beats")
                video.close()
            except Exception as e:
                print(f"   ⚠️ Análisis de audio falló (continuando): {e}")
        
        # ── v10 STEP: Retention Engine ──
        if "retention" in active_steps:
            step_num += 1
            report(58, "🧠 Motor de retención Pro (16 efectos)...")
            print(f"\n📌 [{step_num}] 🧠 Motor de retención Pro (16 efectos)...")
            try:
                video = VideoFileClip(current_video_path)
                # BUG-03 FIX: Pass pre-computed energy_map to avoid double analysis
                video = apply_retention_effects(
                    video,
                    max_gap_sec=active_config.get("retention_gap", 3.0),
                    low_threshold=active_config.get("retention_threshold", 0.35),
                    energy_map=energy_map
                )
                video = enhance_climax_moments(video, energy_map or [])
                
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_retention.mp4")
                write_params = get_moviepy_write_params(gpu_info)
                video.write_videofile(temp_out, **write_params)
                video.close()
                step_results["retention"] = {"effects_applied": True, "version": "v10"}
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Retention engine falló (continuando): {e}")
                try: video.close()
                except: pass
        
        # ── v10 STEP: Beat Sync ──
        if "beat_sync" in active_steps:
            step_num += 1
            report(65, "🎵 Beat-sync engine...")
            print(f"\n📌 [{step_num}] 🎵 Beat-sync engine...")
            try:
                video = VideoFileClip(current_video_path)
                beat_effects = active_config.get("beat_effects", ["zoom", "flash"])
                video = apply_beat_sync(video, beat_data=beat_data, effects=beat_effects)
                
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_beatsync.mp4")
                write_params = get_moviepy_write_params(gpu_info)
                video.write_videofile(temp_out, **write_params)
                video.close()
                step_results["beat_sync"] = {
                    "bpm": beat_data.get("bpm", 0) if beat_data else 0,
                    "effects": beat_effects
                }
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Beat-sync falló (continuando): {e}")
                try: video.close()
                except: pass
        
        # ── v10 STEP: VFX Engine ──
        if "vfx" in active_steps:
            step_num += 1
            report(72, "✨ VFX Engine (After Effects)...")
            print(f"\n📌 [{step_num}] ✨ VFX Engine (After Effects)...")
            try:
                video = VideoFileClip(current_video_path)
                vfx_effects = active_config.get("vfx_effects", {
                    "film_grain": {"intensity": 0.05},
                    "glow": {"threshold": 210, "intensity": 0.2},
                })
                video = apply_vfx(video, effects=vfx_effects, energy_map=energy_map)
                
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_vfx.mp4")
                write_params = get_moviepy_write_params(gpu_info)
                video.write_videofile(temp_out, **write_params)
                video.close()
                step_results["vfx"] = {"effects": list(vfx_effects.keys())}
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ VFX engine falló (continuando): {e}")
                try: video.close()
                except: pass
        
        # ── v10 STEP: Sound Design ──
        if "sound_design" in active_steps:
            step_num += 1
            report(78, "🎧 Sound Design Pro (12 SFX)...")
            print(f"\n📌 [{step_num}] 🎧 Sound Design Pro (12 SFX)...")
            try:
                video = VideoFileClip(current_video_path)
                video = apply_sound_design(video, energy_map=energy_map, beat_data=beat_data)
                
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_sfx.mp4")
                write_params = get_moviepy_write_params(gpu_info)
                video.write_videofile(temp_out, **write_params)
                video.close()
                step_results["sound_design"] = {"sfx_applied": True, "version": "v10"}
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Sound design falló (continuando): {e}")
                try: video.close()
                except: pass
        
        # ── v10 STEP: B-Roll ──
        if "broll" in active_steps:
            step_num += 1
            report(83, "🎥 B-Roll automático...")
            print(f"\n📌 [{step_num}] 🎥 B-Roll automático...")
            try:
                from editor.broll_engine import apply_broll
                video = VideoFileClip(current_video_path)
                transcript = step_results.get("subtitles", {}).get("transcript_text", "")
                video = apply_broll(video, full_text=transcript, overlay_style="fullscreen")
                
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_broll.mp4")
                write_params = get_moviepy_write_params(gpu_info)
                video.write_videofile(temp_out, **write_params)
                video.close()
                step_results["broll"] = {"broll_applied": True}
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ B-Roll falló (continuando): {e}")
                try: video.close()
                except: pass
        
        # ── v10 STEP: Compositing ──
        if "compositing" in active_steps:
            step_num += 1
            report(88, "🎨 Compositing Pro (color + vignette)...")
            print(f"\n📌 [{step_num}] 🎨 Compositing Pro (color + vignette)...")
            try:
                video = VideoFileClip(current_video_path)
                color_grade = active_config.get("color_grade", "cinematic")
                vignette = active_config.get("vignette", True)
                letterbox = active_config.get("letterbox", False)
                text_behind = active_config.get("text_behind_person", None)
                
                video = apply_compositing(
                    video,
                    text_behind=text_behind,
                    color_grade=color_grade,
                    vignette=vignette,
                    letterbox=letterbox,
                )
                
                temp_out = os.path.join(temp_dir, f"{step_num:02d}_composited.mp4")
                write_params = get_moviepy_write_params(gpu_info)
                video.write_videofile(temp_out, **write_params)
                video.close()
                step_results["compositing"] = {
                    "color_grade": color_grade, 
                    "vignette": vignette,
                    "letterbox": letterbox
                }
                current_video_path = temp_out
            except Exception as e:
                print(f"   ⚠️ Compositing falló (continuando): {e}")
                try: video.close()
                except: pass
        
        # ── FINAL: Copy to output ──
        report(95, "💾 Guardando resultado final...")
        print(f"\n📌 Paso final: Guardando resultado...")
        shutil.copy2(current_video_path, output_path)
    
    finally:
        print("\n🧹 Limpiando archivos temporales...")
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
    
    elapsed = round(time.time() - start_time, 1)
    
    # Count v10 effects
    v10_modules = ["retention", "beat_sync", "vfx", "sound_design", "compositing"]
    num_v10 = sum(1 for s in v10_modules if s in step_results)
    
    print("\n" + "=" * 60)
    print(f"✅ VideoForge Pro — ¡COMPLETADO!")
    print(f"   ⏱  Tiempo: {elapsed}s")
    print(f"   🎬 Preset: {preset}")
    print(f"   🖥  Motor: {gpu_label}")
    print(f"   📊 Pasos completados: {len(step_results)}/{len(active_steps)}")
    print(f"   🔧 Módulos Pro: {num_v10}")
    print(f"   📤 Output: {output_path}")
    print("=" * 60)
    
    return {
        "preset": preset,
        "time_seconds": elapsed,
        "gpu": gpu_label,
        "steps": step_results,
        "v10_modules_used": num_v10,
        "output_path": output_path,
    }
