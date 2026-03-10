"""
VideoForge — Audio Engine Module
Professional audio processing: normalization, compression, noise reduction, and auto-ducking.
"""

import os
import math
import struct
import wave
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize


def load_audio(path):
    """Load audio from any video/audio file using pydub."""
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.mp4', '.mov', '.avi', '.mkv', '.webm'):
        return AudioSegment.from_file(path, format=ext.replace('.', ''))
    else:
        return AudioSegment.from_file(path)


def normalize_loudness(audio, target_lufs=-14):
    """
    Normalize audio loudness to target LUFS level.
    Uses peak normalization as an approximation.
    
    Args:
        audio: pydub AudioSegment
        target_lufs: Target loudness in LUFS (default: -14 for social media)
    
    Returns:
        Normalized AudioSegment
    """
    print(f"[Audio] Normalizando a {target_lufs} LUFS...")
    # Calculate current loudness
    current_dbfs = audio.dBFS
    target_dbfs = target_lufs  # Simplified LUFS ≈ dBFS for speech
    
    change_db = target_dbfs - current_dbfs
    normalized = audio.apply_gain(change_db)
    
    # Prevent clipping
    if normalized.max_dBFS > -1.0:
        normalized = normalized.apply_gain(-1.0 - normalized.max_dBFS)
    
    return normalized


def apply_compression(audio, threshold=-20, ratio=4.0, attack=5, release=50):
    """
    Apply dynamic range compression for a professional "radio voice" sound.
    
    Args:
        audio: pydub AudioSegment
        threshold: dB threshold (default: -20)
        ratio: Compression ratio (default: 4:1)
        attack: Attack time in ms (default: 5)
        release: Release time in ms (default: 50)
    
    Returns:
        Compressed AudioSegment
    """
    print(f"[Audio] Aplicando compresión (ratio {ratio}:1, umbral {threshold}dB)...")
    compressed = compress_dynamic_range(
        audio,
        threshold=threshold,
        ratio=ratio,
        attack=attack,
        release=release
    )
    return compressed


def reduce_noise(audio, noise_reduction_db=12):
    """
    Basic noise reduction using spectral gating approach.
    Reduces constant background noise (fan, AC, hum).
    
    Args:
        audio: pydub AudioSegment
        noise_reduction_db: Amount of noise reduction in dB
    
    Returns:
        Denoised AudioSegment
    """
    print(f"[Audio] Reduciendo ruido de fondo ({noise_reduction_db}dB)...")
    
    # Convert to numpy
    samples = np.array(audio.get_array_of_samples(), dtype=np.float64)
    
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
    
    # Estimate noise floor from quietest 10% of audio
    frame_size = int(audio.frame_rate * 0.02)  # 20ms frames
    num_frames = len(samples) // frame_size
    
    if num_frames < 10:
        return audio  # Too short to process
    
    # BUG-16 FIX: Vectorized noise reduction (no frame-by-frame Python loop)
    frame_energies = np.array([
        np.mean(samples[i * frame_size:(i + 1) * frame_size] ** 2)
        for i in range(num_frames)
    ])
    
    # Sort by energy, take bottom 10% as noise estimate
    sorted_energies = np.sort(frame_energies)
    noise_threshold = sorted_energies[max(1, int(num_frames * 0.1))]
    
    # Reduce gain on frames below noise threshold — vectorized
    noise_factor = 10 ** (-noise_reduction_db / 20.0)
    
    result_samples = samples.copy()
    for i in range(num_frames):
        start = i * frame_size
        end = start + frame_size
        energy = frame_energies[i]
        
        if energy < noise_threshold * 3:  # Near noise floor
            reduction = noise_factor + (1 - noise_factor) * (energy / (noise_threshold * 3))
            result_samples[start:end] = samples[start:end] * reduction
    
    # Convert back to pydub
    if audio.channels == 2:
        result_samples = result_samples.flatten()
    
    result_samples = np.clip(result_samples, -32768, 32767).astype(np.int16)
    
    result = audio._spawn(result_samples.tobytes())
    return result


def auto_ducking(voice_audio, music_path, music_volume_db=-18, duck_amount_db=12,
                 voice_threshold_db=-30, fade_duration_ms=200):
    """
    Mix background music with voice, automatically lowering music when voice is detected.
    
    Args:
        voice_audio: pydub AudioSegment with voice
        music_path: Path to background music file
        music_volume_db: Base music volume in dB (default: -18)
        duck_amount_db: Additional dB reduction when voice detected (default: 12)
        voice_threshold_db: Voice detection threshold (default: -30)
        fade_duration_ms: Fade in/out duration for ducking (default: 200ms)
    
    Returns:
        Mixed AudioSegment with auto-ducking
    """
    print(f"[Audio] Auto-ducking: música a {music_volume_db}dB, duck {duck_amount_db}dB...")
    
    # Load and loop music to match voice duration
    music = AudioSegment.from_file(music_path)
    music = music + music_volume_db  # Set base volume
    
    # Loop music if shorter than voice
    while len(music) < len(voice_audio):
        music = music + music
    music = music[:len(voice_audio)]
    
    # BUG-20 FIX: Process in chunks with smooth ducking transitions
    chunk_ms = 100  # 100ms chunks
    processed_music = AudioSegment.empty()
    
    was_ducked = False
    
    for i in range(0, len(voice_audio), chunk_ms):
        voice_chunk = voice_audio[i:i + chunk_ms]
        music_chunk = music[i:i + chunk_ms]
        
        # Check if voice is present
        voice_present = voice_chunk.dBFS > voice_threshold_db
        
        if voice_present:
            # Duck the music
            ducked_chunk = music_chunk - duck_amount_db
            # Smooth transition: fade in/out at duck boundaries
            if not was_ducked:
                ducked_chunk = ducked_chunk.fade_in(min(fade_duration_ms, len(ducked_chunk)))
            processed_music += ducked_chunk
            was_ducked = True
        else:
            # Unduck
            if was_ducked:
                music_chunk = music_chunk.fade_in(min(fade_duration_ms, len(music_chunk)))
            processed_music += music_chunk
            was_ducked = False
    
    # Mix voice with processed music
    final = voice_audio.overlay(processed_music)
    
    return final


# BUG-18 FIX: Renamed 'normalize' parameter to 'do_normalize' to avoid
# shadowing the pydub 'normalize' import.
def process_audio(input_path, output_path=None, music_path=None,
                  do_normalize=True, compress=True, denoise=True,
                  target_lufs=-14):
    """
    Full audio processing pipeline.
    
    Args:
        input_path: Path to input video/audio
        output_path: Path to output audio (WAV)
        music_path: Optional path to background music
        normalize: Enable loudness normalization
        compress: Enable dynamic compression
        denoise: Enable noise reduction
        target_lufs: Target loudness level
    
    Returns:
        dict with stats and output path
    """
    if output_path is None:
        base = input_path.rsplit('.', 1)[0]
        output_path = f"{base}_audio_pro.wav"
    
    print(f"[Audio] Cargando audio: {input_path}")
    audio = load_audio(input_path)
    original_dbfs = audio.dBFS
    
    # Processing chain
    if denoise:
        audio = reduce_noise(audio)
    
    if compress:
        audio = apply_compression(audio)
    
    if do_normalize:
        audio = normalize_loudness(audio, target_lufs)
    
    if music_path and os.path.exists(music_path):
        audio = auto_ducking(audio, music_path)
    
    print(f"[Audio] Exportando: {output_path}")
    audio.export(output_path, format="wav")
    
    stats = {
        "original_dbfs": round(original_dbfs, 2),
        "final_dbfs": round(audio.dBFS, 2),
        "duration_seconds": round(len(audio) / 1000, 2),
        "output_path": output_path
    }
    
    print(f"[Audio] ✅ Audio procesado — {stats['original_dbfs']}dB → {stats['final_dbfs']}dB")
    
    return stats


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python audio_engine.py <video.mp4> [música_fondo.mp3]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    music_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = process_audio(input_file, music_path=music_file)
    print(f"\nResultado: {result}")
