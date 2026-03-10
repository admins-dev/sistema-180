"""
VideoForge v3.0 — GPU Acceleration Engine
===========================================
Detects and utilizes NVIDIA GPU (NVENC/CUDA) for hardware-accelerated
video encoding. Falls back to CPU with multi-threading if no GPU found.
"""

import subprocess
import os
import shutil
import json


# ─── GPU Detection ──────────────────────────────────────────────────

def detect_gpu():
    """
    Detect available GPU encoders via FFmpeg.
    Returns dict with GPU capabilities.
    """
    gpu_info = {
        "has_nvidia": False,
        "has_nvenc": False,
        "has_cuda": False,
        "has_amd": False,
        "has_intel_qsv": False,
        "encoder": "libx264",  # Default CPU encoder
        "decoder": "",
        "hwaccel": "",
        "extra_flags": [],
    }
    
    try:
        # Check FFmpeg for available encoders
        result = subprocess.run(
            ["ffmpeg", "-encoders"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr
        
        # NVIDIA NVENC
        if "h264_nvenc" in output:
            gpu_info["has_nvidia"] = True
            gpu_info["has_nvenc"] = True
            gpu_info["encoder"] = "h264_nvenc"
            gpu_info["extra_flags"] = [
                "-rc", "vbr",
                "-cq", "23",
                "-b:v", "0",
            ]
            print("[GPU] 🟢 NVIDIA NVENC detectado — aceleración GPU activada")
        
        # Check CUDA
        if "cuda" in output or "h264_cuvid" in output:
            gpu_info["has_cuda"] = True
            gpu_info["hwaccel"] = "cuda"
            gpu_info["decoder"] = "h264_cuvid"
            print("[GPU] 🟢 CUDA disponible para decodificación acelerada")
        
        # AMD AMF
        if "h264_amf" in output:
            gpu_info["has_amd"] = True
            if not gpu_info["has_nvenc"]:
                gpu_info["encoder"] = "h264_amf"
                print("[GPU] 🟢 AMD AMF detectado — aceleración GPU activada")
        
        # Intel QuickSync
        if "h264_qsv" in output:
            gpu_info["has_intel_qsv"] = True
            if not gpu_info["has_nvenc"] and not gpu_info["has_amd"]:
                gpu_info["encoder"] = "h264_qsv"
                gpu_info["hwaccel"] = "qsv"
                print("[GPU] 🟢 Intel QuickSync detectado — aceleración GPU activada")
        
        if not any([gpu_info["has_nvenc"], gpu_info["has_amd"], gpu_info["has_intel_qsv"]]):
            print("[GPU] ⚪ No se detectó GPU compatible — usando CPU (ultrafast)")
    
    except Exception as e:
        print(f"[GPU] ⚠️ Error detectando GPU: {e}")
    
    return gpu_info


# ─── Hardware-Accelerated Encoding ──────────────────────────────────

def gpu_encode(input_path, output_path, gpu_info=None, 
               crf=23, preset="fast", audio_codec="aac"):
    """
    Encode a video file using hardware GPU acceleration if available.
    Falls back to CPU with ultrafast preset.
    """
    if gpu_info is None:
        gpu_info = detect_gpu()
    
    encoder = gpu_info["encoder"]
    
    # Build FFmpeg command
    cmd = ["ffmpeg", "-y"]
    
    # Hardware acceleration for decoding
    if gpu_info["hwaccel"]:
        cmd.extend(["-hwaccel", gpu_info["hwaccel"]])
    if gpu_info["decoder"]:
        cmd.extend(["-c:v", gpu_info["decoder"]])
    
    cmd.extend(["-i", input_path])
    
    # Video encoding
    cmd.extend(["-c:v", encoder])
    
    if encoder == "h264_nvenc":
        # NVENC specific options
        cmd.extend([
            "-preset", "p4",       # Balance speed/quality
            "-tune", "hq",
            "-rc", "vbr",
            "-cq", str(crf),
            "-b:v", "0",
            "-maxrate", "10M",
            "-bufsize", "10M",
        ])
    elif encoder == "h264_amf":
        cmd.extend([
            "-quality", "balanced",
            "-rc", "vbr_peak",
        ])
    elif encoder == "h264_qsv":
        cmd.extend([
            "-preset", "medium",
            "-global_quality", str(crf),
        ])
    else:
        # CPU fallback
        cmd.extend([
            "-preset", "ultrafast",
            "-crf", str(crf),
        ])
    
    # Audio
    cmd.extend(["-c:a", audio_codec])
    
    # Threading
    cmd.extend(["-threads", str(os.cpu_count() or 8)])
    
    # Output
    cmd.append(output_path)
    
    print(f"[GPU] 🚀 Codificando con {encoder}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print(f"[GPU] ✅ Codificación completada: {output_path}")
            return True
        else:
            print(f"[GPU] ⚠️ Error GPU, intentando con CPU...")
            return _fallback_cpu_encode(input_path, output_path, crf, audio_codec)
    except Exception as e:
        print(f"[GPU] ⚠️ Excepción: {e}, intentando CPU...")
        return _fallback_cpu_encode(input_path, output_path, crf, audio_codec)


def _fallback_cpu_encode(input_path, output_path, crf, audio_codec):
    """CPU fallback encoding."""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", str(crf),
        "-c:a", audio_codec,
        "-threads", str(os.cpu_count() or 8),
        output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.returncode == 0
    except Exception:
        return False


# ─── Parallel Frame Processing ──────────────────────────────────────

def get_optimal_thread_count():
    """Get the optimal number of threads based on system resources."""
    cpu_count = os.cpu_count() or 4
    # Use 75% of available cores for processing, leave some for system
    return max(4, int(cpu_count * 0.75))


def get_moviepy_write_params(gpu_info=None):
    """
    Get optimized write_videofile parameters based on GPU availability.
    Returns a dict suitable for moviepy's write_videofile(**params).
    """
    if gpu_info is None:
        gpu_info = detect_gpu()
    
    params = {
        "codec": gpu_info["encoder"],
        "audio_codec": "aac",
        "threads": get_optimal_thread_count(),
        "logger": "bar",
    }
    
    if gpu_info["encoder"] == "h264_nvenc":
        params["ffmpeg_params"] = [
            "-preset", "p4",
            "-tune", "hq",
            "-rc", "vbr",
            "-cq", "23",
            "-b:v", "0",
        ]
    elif gpu_info["encoder"] in ("h264_amf", "h264_qsv"):
        params["ffmpeg_params"] = ["-quality", "balanced"]
    else:
        params["preset"] = "ultrafast"
    
    return params


# ─── Smart Encoding Decision ───────────────────────────────────────

def smart_encode(video_clip, output_path, gpu_info=None):
    """
    Intelligently encode a MoviePy clip using the best available method.
    Uses GPU if available, falls back to optimized CPU encoding.
    """
    if gpu_info is None:
        gpu_info = detect_gpu()
    
    params = get_moviepy_write_params(gpu_info)
    
    speed_label = "GPU" if gpu_info["encoder"] != "libx264" else "CPU"
    print(f"[GPU] 🚀 Smart encoding ({speed_label}) → {output_path}")
    
    video_clip.write_videofile(output_path, **params)
    
    print(f"[GPU] ✅ Encoding completado")
    return output_path


# ─── Init: Auto-detect on import ────────────────────────────────────

_gpu_info_cache = None

def get_gpu_info():
    """Get cached GPU info (detected once)."""
    global _gpu_info_cache
    if _gpu_info_cache is None:
        _gpu_info_cache = detect_gpu()
    return _gpu_info_cache
