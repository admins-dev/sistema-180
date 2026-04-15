#!/bin/bash
# Setup script para Meta Ads Bot

echo "🔧 Sistema 180 — Meta Ads Bot Setup"
echo "═══════════════════════════════════"

# Detectar gestor de paquetes
if command -v apt-get &> /dev/null; then
    echo "📦 Instalando python3-pip y python3-venv..."
    sudo apt-get update -qq
    sudo apt-get install -y python3-pip python3-venv >/dev/null 2>&1
elif command -v brew &> /dev/null; then
    echo "📦 Instalando python3 con Homebrew..."
    brew install python3 >/dev/null 2>&1
else
    echo "❌ No se pudo detectar gestor de paquetes"
    exit 1
fi

# Crear y activar virtualenv
echo "📂 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias Python..."
pip install -q -r requirements.txt

echo "✅ Setup completado!"
echo ""
echo "Para iniciar el bot y servidor:"
echo "  source venv/bin/activate"
echo "  ./start.sh"
