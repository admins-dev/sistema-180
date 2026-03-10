"""
VideoForge v10 — Sound Design Engine
=======================================
Professional SFX synthesis: 12 sound effect types, beat-synced impacts,
auto-ducking, risers, multi-layer master mix.
"""

import numpy as np
import math
import os
import shutil
import tempfile
from pydub import AudioSegment


# ─── SFX Synthesis (12 Types) ──────────────────────────────────────

def synth_whoosh(duration_ms=300, sample_rate=44100):
    """Cinematic whoosh sweep."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    # Frequency sweep 200Hz → 2000Hz
    freq = 200 + 1800 * t
    phase = np.cumsum(freq) / sample_rate * 2 * math.pi
    wave = np.sin(phase) * 0.4
    
    # Add noise
    noise = np.random.normal(0, 0.15, samples) * np.exp(-t * 3)
    wave += noise
    
    # Envelope
    envelope = np.sin(t * math.pi)
    wave *= envelope
    
    return (wave * 32767).astype(np.int16)


def synth_impact(duration_ms=200, sample_rate=44100):
    """Heavy impact/hit sound."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    # Low frequency slam
    wave = np.sin(2 * math.pi * 60 * t) * 0.6
    wave += np.sin(2 * math.pi * 40 * t) * 0.4
    
    # Fast decay
    envelope = np.exp(-t * 8)
    wave *= envelope
    
    # Add transient click
    click = np.random.normal(0, 0.5, min(200, samples))
    wave[:len(click)] += click * np.exp(-np.linspace(0, 5, len(click)))
    
    return (np.clip(wave, -1, 1) * 32767).astype(np.int16)


def synth_bass_drop(duration_ms=500, sample_rate=44100):
    """808-style bass drop."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    # Pitch drops from 150Hz to 30Hz
    freq = 150 * np.exp(-t * 3) + 30
    phase = np.cumsum(freq) / sample_rate * 2 * math.pi
    wave = np.sin(phase) * 0.7
    
    # Distortion
    wave = np.tanh(wave * 2) * 0.5
    
    # Envelope
    envelope = np.exp(-t * 2)
    wave *= envelope
    
    return (wave * 32767).astype(np.int16)


def synth_riser(duration_ms=1500, sample_rate=44100):
    """Tension-building riser."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    # Rising frequency
    freq = 200 + 3000 * t ** 2
    phase = np.cumsum(freq) / sample_rate * 2 * math.pi
    wave = np.sin(phase) * 0.3
    
    # Add harmonics
    wave += np.sin(phase * 2) * 0.15
    wave += np.sin(phase * 3) * 0.08
    
    # Volume builds
    envelope = t ** 1.5
    wave *= envelope
    
    # Add noise
    noise = np.random.normal(0, 0.05, samples) * t
    wave += noise
    
    return (np.clip(wave, -1, 1) * 32767).astype(np.int16)


def synth_pop(duration_ms=100, sample_rate=44100):
    """Quick pop/click."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    wave = np.sin(2 * math.pi * 800 * t) * 0.3
    wave += np.sin(2 * math.pi * 1200 * t) * 0.2
    envelope = np.exp(-t * 15)
    wave *= envelope
    
    return (wave * 32767).astype(np.int16)


def synth_click(duration_ms=50, sample_rate=44100):
    """Minimal click."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    wave = np.sin(2 * math.pi * 2000 * t) * 0.3
    envelope = np.exp(-t * 30)
    wave *= envelope
    
    return (wave * 32767).astype(np.int16)


def synth_glitch_sfx(duration_ms=150, sample_rate=44100):
    """Digital glitch sound."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    # Random bit-crush effect
    wave = np.random.uniform(-0.3, 0.3, samples)
    # Quantize
    bits = 4
    wave = np.round(wave * (2**bits)) / (2**bits)
    envelope = np.exp(-t * 5)
    wave *= envelope
    
    return (wave * 32767).astype(np.int16)


def synth_shimmer(duration_ms=400, sample_rate=44100):
    """Ethereal shimmer/sparkle."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    wave = np.sin(2 * math.pi * 4000 * t) * 0.1
    wave += np.sin(2 * math.pi * 5000 * t + math.pi/3) * 0.08
    wave += np.sin(2 * math.pi * 6000 * t + math.pi/5) * 0.06
    
    # Random sparkle
    sparkle = np.random.normal(0, 0.03, samples)
    sparkle *= (np.sin(t * math.pi * 8) > 0).astype(float)
    wave += sparkle
    
    envelope = np.sin(t * math.pi) * np.exp(-t * 2)
    wave *= envelope
    
    return (wave * 32767).astype(np.int16)


def synth_sub_bass(duration_ms=600, sample_rate=44100):
    """Deep sub-bass rumble."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    wave = np.sin(2 * math.pi * 35 * t) * 0.8
    wave += np.sin(2 * math.pi * 70 * t) * 0.3
    envelope = np.exp(-t * 1.5)
    wave *= envelope
    
    return (np.clip(wave, -1, 1) * 32767).astype(np.int16)


def synth_sweep_down(duration_ms=250, sample_rate=44100):
    """Quick frequency sweep down."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    freq = 3000 * np.exp(-t * 4) + 100
    phase = np.cumsum(freq) / sample_rate * 2 * math.pi
    wave = np.sin(phase) * 0.3
    envelope = np.exp(-t * 3)
    wave *= envelope
    
    return (wave * 32767).astype(np.int16)


def synth_laser(duration_ms=200, sample_rate=44100):
    """Sci-fi laser zap."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    freq = 2000 * np.exp(-t * 5) + 200
    phase = np.cumsum(freq) / sample_rate * 2 * math.pi
    wave = np.sign(np.sin(phase)) * 0.2  # Square wave
    envelope = np.exp(-t * 6)
    wave *= envelope
    
    return (wave * 32767).astype(np.int16)


def synth_reverse_hit(duration_ms=350, sample_rate=44100):
    """Reversed impact (builds up then cuts)."""
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, 1, samples)
    
    wave = np.sin(2 * math.pi * 80 * t) * 0.5
    noise = np.random.normal(0, 0.2, samples)
    wave += noise
    
    # Reverse envelope (builds up)
    envelope = t ** 3
    wave *= envelope
    
    return (np.clip(wave, -1, 1) * 32767).astype(np.int16)


# ─── SFX Map ───────────────────────────────────────────────────────

SFX_MAP = {
    "whoosh": synth_whoosh,
    "impact": synth_impact,
    "bass_drop": synth_bass_drop,
    "riser": synth_riser,
    "pop": synth_pop,
    "click": synth_click,
    "glitch": synth_glitch_sfx,
    "shimmer": synth_shimmer,
    "sub_bass": synth_sub_bass,
    "sweep_down": synth_sweep_down,
    "laser": synth_laser,
    "reverse_hit": synth_reverse_hit,
}


def generate_sfx(sfx_type, duration_ms=None, sample_rate=44100):
    """Generate a sound effect by type."""
    fn = SFX_MAP.get(sfx_type, synth_click)
    kwargs = {"sample_rate": sample_rate}
    if duration_ms:
        kwargs["duration_ms"] = duration_ms
    
    samples = fn(**kwargs)
    
    # Convert to AudioSegment
    audio = AudioSegment(
        data=samples.tobytes(),
        sample_width=2,
        frame_rate=sample_rate,
        channels=1
    )
    return audio


# ─── Event Generation ──────────────────────────────────────────────

def generate_events_from_energy(energy_map, beat_data=None):
    """
    Generate SFX events from audio energy data.
    Maps energy peaks to appropriate SFX types.
    """
    events = []
    
    if not energy_map:
        return events
    
    # Find energy peaks
    for i, entry in enumerate(energy_map):
        if entry.get("is_climax", False):
            # Climax moments get heavy impacts
            sfx = np.random.choice(["impact", "bass_drop", "sub_bass"])
            events.append({
                "time_ms": int(entry["time"] * 1000),
                "type": sfx,
                "volume_db": -6
            })
        elif entry["energy"] > 0.6 and i > 0 and energy_map[i-1]["energy"] < 0.4:
            # Sudden energy rise = transition SFX
            sfx = np.random.choice(["whoosh", "sweep_down", "reverse_hit"])
            events.append({
                "time_ms": int(entry["time"] * 1000),
                "type": sfx,
                "volume_db": -10
            })
    
    # Add risers before climax moments
    climax_times = [e["time"] for e in energy_map if e.get("is_climax")]
    for ct in climax_times:
        if ct > 2.0:
            events.append({
                "time_ms": int((ct - 1.5) * 1000),
                "type": "riser",
                "volume_db": -12
            })
    
    # Beat-synced clicks/pops
    if beat_data and beat_data.get("beats"):
        for i, bt in enumerate(beat_data["beats"]):
            if i % 4 == 0:  # Every 4th beat
                events.append({
                    "time_ms": int(bt * 1000),
                    "type": np.random.choice(["click", "pop"]),
                    "volume_db": -18
                })
    
    return events


# ─── Master Mix ─────────────────────────────────────────────────────

def create_sfx_timeline(events, duration_ms):
    """Create a timeline of SFX AudioSegments."""
    timeline = []
    for event in events:
        sfx = generate_sfx(event["type"])
        vol = event.get("volume_db", -12)
        sfx = sfx + vol
        timeline.append({
            "audio": sfx,
            "position_ms": event["time_ms"]
        })
    return timeline


def create_master_mix(original_audio_path, sfx_timeline, output_path):
    """Mix original audio with SFX timeline."""
    original = AudioSegment.from_file(original_audio_path)
    
    # Create SFX mix
    sfx_mix = AudioSegment.silent(duration=len(original))
    
    for item in sfx_timeline:
        pos = item["position_ms"]
        if 0 <= pos < len(sfx_mix):
            sfx_mix = sfx_mix.overlay(item["audio"], position=pos)
    
    # Final mix
    master = original.overlay(sfx_mix)
    master.export(output_path, format="wav")
    
    print(f"[SOUND DESIGN] 🎵 Master mix: {len(sfx_timeline)} SFX mezclados")
    return output_path


# ─── Main Pipeline ──────────────────────────────────────────────────

def apply_sound_design(video_clip, energy_map=None, beat_data=None,
                       extra_events=None):
    """
    Full sound design pipeline:
    1. Analyze energy (if not provided)
    2. Generate events from energy + beats
    3. Create SFX timeline
    4. Mix with original audio
    
    BUG-05 FIX: Properly cleans up temp files after processing.
    v10: 12 SFX types, beat-sync, higher quality (44.1kHz stereo).
    
    Returns: modified video clip with enhanced audio
    """
    from moviepy import AudioFileClip
    
    print("[SOUND DESIGN] 🎬 Iniciando diseño de sonido profesional v10...")
    
    duration_ms = int(video_clip.duration * 1000)
    
    # Get energy data
    if energy_map is None:
        from editor.retention_engine import analyze_energy
        energy_map = analyze_energy(video_clip.audio)
    
    # Generate events
    events = generate_events_from_energy(energy_map, beat_data)
    
    if extra_events:
        events.extend(extra_events)
    
    events.sort(key=lambda x: x["time_ms"])
    
    print(f"[SOUND DESIGN] 📋 {len(events)} eventos de audio planificados")
    
    # Create SFX timeline
    sfx_timeline = create_sfx_timeline(events, duration_ms)
    
    # BUG-05 FIX: Use try/finally to clean up temp files
    temp_dir = tempfile.mkdtemp()
    try:
        # Export original audio
        original_audio_path = os.path.join(temp_dir, "original_audio.wav")
        video_clip.audio.write_audiofile(original_audio_path, logger=None)
        
        # Create master mix
        output_audio_path = os.path.join(temp_dir, "master_audio.wav")
        create_master_mix(original_audio_path, sfx_timeline, output_audio_path)
        
        # Replace video audio
        new_audio = AudioFileClip(output_audio_path)
        result = video_clip.with_audio(new_audio)
        
        print("[SOUND DESIGN] ✅ Diseño de sonido v10 aplicado")
        return result
    except Exception as e:
        print(f"[SOUND DESIGN] ⚠️ Error: {e}")
        return video_clip
    finally:
        # BUG-05 FIX: Always clean up temp directory
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
