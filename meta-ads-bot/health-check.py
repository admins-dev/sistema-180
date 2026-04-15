#!/usr/bin/env python3
"""
Health Check para Sistema 180 Meta Ads Bot
Verifica estado de todos los componentes
"""

import os
import sys
import json
from pathlib import Path

def check_environment():
    """Verifica variables de entorno críticas"""
    # Cargar .env manualmente
    env_file = Path('.env')
    env_vars = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env_vars[key] = val

    required = [
        'TELEGRAM_BOT_TOKEN',
        'META_ACCESS_TOKEN',
        'META_AD_ACCOUNT_ID',
        'ANTHROPIC_API_KEY'
    ]

    missing = [var for var in required if var not in env_vars]

    return {
        'status': 'ok' if not missing else 'error',
        'missing': missing,
        'loaded': len(required) - len(missing)
    }

def check_files():
    """Verifica que todos los archivos requeridos existan"""
    required_files = [
        'bot.py',
        'server.py',
        'meta_client.py',
        'nlp.py',
        'sync.py',
        'requirements.txt',
        '.env'
    ]

    missing = []
    for f in required_files:
        if not Path(f).exists():
            missing.append(f)

    return {
        'status': 'ok' if not missing else 'error',
        'missing': missing,
        'present': len(required_files) - len(missing)
    }

def check_python_modules():
    """Verifica módulos Python requeridos"""
    modules = [
        'telegram',
        'flask',
        'requests',
        'dotenv',
        'flask_cors'
    ]

    missing = []
    for module in modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    return {
        'status': 'ok' if not missing else 'error',
        'missing': missing,
        'available': len(modules) - len(missing)
    }

def check_dashboard_integration():
    """Verifica integración en dashboard.js"""
    dashboard_path = '../src/pages/dashboard.js'
    if not Path(dashboard_path).exists():
        return {'status': 'error', 'message': 'dashboard.js no encontrado'}

    with open(dashboard_path) as f:
        content = f.read()

    checks = {
        'import_meta_ads_section': 'import { renderMetaAdsSection }' in content,
        'container_div': 'id="meta-ads-container"' in content,
        'render_call': 'renderMetaAdsSection' in content
    }

    return {
        'status': 'ok' if all(checks.values()) else 'error',
        'checks': checks
    }

def main():
    print("🔍 Sistema 180 — Health Check")
    print("═" * 50)

    results = {
        'environment': check_environment(),
        'files': check_files(),
        'python_modules': check_python_modules(),
        'dashboard_integration': check_dashboard_integration()
    }

    # Resumen
    print("\n📊 RESUMEN DE ESTADO:\n")

    all_ok = True
    for component, result in results.items():
        status = result.get('status', 'unknown')
        emoji = '✅' if status == 'ok' else '❌'
        print(f"{emoji} {component}: {status.upper()}")

        if status != 'ok':
            all_ok = False
            if 'missing' in result and result['missing']:
                print(f"   Missing: {', '.join(result['missing'])}")
            if 'message' in result:
                print(f"   {result['message']}")
            if 'checks' in result:
                for check, passed in result['checks'].items():
                    check_emoji = '✓' if passed else '✗'
                    print(f"   {check_emoji} {check}")

    print("\n" + "═" * 50)

    if all_ok:
        print("✅ SISTEMA LISTO PARA INICIAR")
        print("\nPróximos pasos:")
        print("1. Ejecutar: ./start.sh")
        print("2. Abrir dashboard en browser")
        print("3. Click en 'Sync' en sección Meta Ads Bot")
        return 0
    else:
        print("❌ SE ENCONTRARON PROBLEMAS")
        print("\nPara instalar dependencias:")
        print("./install.sh")
        return 1

if __name__ == '__main__':
    sys.exit(main())
