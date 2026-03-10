import sys
sys.path.insert(0, '.')

print("Testing all module imports after bug fixes...")
print("=" * 50)

errors = []

try:
    from editor.silence_cutter import cut_silences, _get_gpu_write_params
    print("  ✓ silence_cutter OK")
except Exception as e:
    errors.append(f"silence_cutter: {e}")
    print(f"  ✗ silence_cutter FAIL: {e}")

try:
    from editor.subtitles import add_subtitles, _detect_whisper_device
    print("  ✓ subtitles OK")
except Exception as e:
    errors.append(f"subtitles: {e}")
    print(f"  ✗ subtitles FAIL: {e}")

try:
    from editor.retention_engine import apply_retention_effects, analyze_energy
    print("  ✓ retention_engine OK")
except Exception as e:
    errors.append(f"retention_engine: {e}")
    print(f"  ✗ retention_engine FAIL: {e}")

try:
    from editor.vfx_engine import apply_vfx, apply_camera_shake
    print("  ✓ vfx_engine OK")
except Exception as e:
    errors.append(f"vfx_engine: {e}")
    print(f"  ✗ vfx_engine FAIL: {e}")

try:
    from editor.sound_design import apply_sound_design
    print("  ✓ sound_design OK")
except Exception as e:
    errors.append(f"sound_design: {e}")
    print(f"  ✗ sound_design FAIL: {e}")

try:
    from editor.compositing import apply_compositing
    print("  ✓ compositing OK")
except Exception as e:
    errors.append(f"compositing: {e}")
    print(f"  ✗ compositing FAIL: {e}")

try:
    from editor.beat_engine import apply_beat_sync, get_nearest_beat
    print("  ✓ beat_engine OK")
except Exception as e:
    errors.append(f"beat_engine: {e}")
    print(f"  ✗ beat_engine FAIL: {e}")

try:
    from editor.audio_engine import process_audio
    print("  ✓ audio_engine OK")
except Exception as e:
    errors.append(f"audio_engine: {e}")
    print(f"  ✗ audio_engine FAIL: {e}")

try:
    from editor.broll_engine import apply_broll
    print("  ✓ broll_engine OK")
except Exception as e:
    errors.append(f"broll_engine: {e}")
    print(f"  ✗ broll_engine FAIL: {e}")

try:
    from editor.smart_zoom import apply_smart_zoom
    print("  ✓ smart_zoom OK")
except Exception as e:
    errors.append(f"smart_zoom: {e}")
    print(f"  ✗ smart_zoom FAIL: {e}")

try:
    from editor.smart_reframe import smart_reframe
    print("  ✓ smart_reframe OK")
except Exception as e:
    errors.append(f"smart_reframe: {e}")
    print(f"  ✗ smart_reframe FAIL: {e}")

try:
    from editor.overlays import render_popup_overlay
    print("  ✓ overlays OK")
except Exception as e:
    errors.append(f"overlays: {e}")
    print(f"  ✗ overlays FAIL: {e}")

try:
    from editor.transitions import get_transition_function
    print("  ✓ transitions OK")
except Exception as e:
    errors.append(f"transitions: {e}")
    print(f"  ✗ transitions FAIL: {e}")

print("=" * 50)
if errors:
    print(f"FAILED: {len(errors)} errors")
    for e in errors:
        print(f"  - {e}")
else:
    print("ALL 13 MODULES IMPORT OK")
