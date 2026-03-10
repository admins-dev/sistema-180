#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🎬 VideoForge v1.0 — Editor de Vídeo Profesional con IA    ║
║                                                               ║
║   Automatiza la edición de vídeo como un profesional.         ║
║   Subtítulos Hormozi, jumpcuts, zoom, audio pro y más.        ║
║                                                               ║
║   Sistema 180 — By Jose                                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Uso:
    python main.py <video.mp4> --preset reel --output editado.mp4
    python main.py <video.mp4> --preset youtube
    python main.py <video.mp4> --preset ad --music fondo.mp3
    python main.py --presets                    (ver presets disponibles)
    python main.py <video.mp4> --only subtitles (solo subtítulos)
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from editor.pipeline import run_pipeline, list_presets, PRESETS


def main():
    parser = argparse.ArgumentParser(
        description="🎬 VideoForge — Editor de Vídeo Profesional con IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py video.mp4 --preset reel
  python main.py video.mp4 --preset youtube --output final.mp4
  python main.py video.mp4 --preset ad --music musica.mp3
  python main.py video.mp4 --only subtitles
  python main.py video.mp4 --only silence_cut
  python main.py --presets
        """
    )
    
    parser.add_argument("input", nargs="?", help="Vídeo de entrada (mp4, mov, avi, mkv)")
    parser.add_argument("--preset", "-p", default="youtube",
                        choices=list(PRESETS.keys()),
                        help="Preset de edición (default: youtube)")
    parser.add_argument("--output", "-o", help="Ruta del vídeo de salida")
    parser.add_argument("--music", "-m", help="Ruta a música de fondo (mp3/wav)")
    
    # Individual module flags
    parser.add_argument("--only", nargs="+",
                        choices=["silence_cut", "subtitles", "smart_zoom", 
                                 "audio_pro", "reframe_916"],
                        help="Ejecutar solo estos pasos específicos")
    
    # Override config
    parser.add_argument("--language", "-l", default="es",
                        help="Idioma para subtítulos (default: es)")
    parser.add_argument("--whisper-model", default="base",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Modelo Whisper (default: base)")
    parser.add_argument("--silence-threshold", type=float,
                        help="Umbral de silencio en dB (default: -35)")
    parser.add_argument("--subtitle-position", choices=["center", "bottom", "top"],
                        help="Posición de subtítulos")
    parser.add_argument("--zoom-scale", type=float,
                        help="Factor de zoom (default: 1.15)")
    
    # Utility commands
    parser.add_argument("--presets", action="store_true",
                        help="Listar presets disponibles")
    
    args = parser.parse_args()
    
    # List presets
    if args.presets:
        list_presets()
        return
    
    # Validate input
    if not args.input:
        parser.print_help()
        print("\n❌ Error: Debes especificar un vídeo de entrada.")
        sys.exit(1)
    
    if not os.path.exists(args.input):
        print(f"❌ Error: No se encuentra el archivo: {args.input}")
        sys.exit(1)
    
    # Build config overrides
    config_overrides = {
        "language": args.language,
        "whisper_model": args.whisper_model,
    }
    
    if args.silence_threshold is not None:
        config_overrides["silence_threshold_db"] = args.silence_threshold
    if args.subtitle_position:
        config_overrides["subtitle_position"] = args.subtitle_position
    if args.zoom_scale is not None:
        config_overrides["zoom_scale"] = args.zoom_scale
    
    # Run pipeline
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                 🎬 VideoForge v1.0                           ║
║            Editor de Vídeo Profesional con IA                ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        result = run_pipeline(
            input_path=args.input,
            output_path=args.output,
            preset=args.preset,
            steps=args.only,
            config=config_overrides,
            music_path=args.music
        )
        
        print(f"\n✅ ¡Vídeo editado correctamente!")
        print(f"📁 Resultado: {result['output_path']}")
        print(f"⏱  Tiempo: {result['elapsed_seconds']}s")
        
    except KeyboardInterrupt:
        print("\n\n⛔ Edición cancelada por el usuario.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
