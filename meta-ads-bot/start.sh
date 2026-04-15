#!/bin/bash
# Start script para Meta Ads Bot + Flask Server

echo "🚀 Iniciando Sistema 180 Meta Ads Bot..."
echo "════════════════════════════════════════"

# Verificar que estamos en el directorio correcto
cd "$(dirname "$0")"

# Activar virtualenv si existe
if [ -d "venv" ]; then
    echo "📌 Activando entorno virtual..."
    source venv/bin/activate
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo "❌ Error: .env no encontrado"
    exit 1
fi

echo "✅ Entorno listo"
echo ""
echo "Iniciando servicios en paralelo:"
echo "  • Telegram Bot (bot.py)"
echo "  • Flask Server (server.py en :5000)"
echo ""

# Captura SIGTERM y SIGINT para matar procesos hijos
trap 'kill $(jobs -p)' EXIT

# Inicia ambos servicios en paralelo
python3 bot.py &
BOT_PID=$!

python3 server.py &
SERVER_PID=$!

echo "🤖 Bot PID: $BOT_PID"
echo "🌐 Server PID: $SERVER_PID"
echo ""
echo "Para detener: Presiona Ctrl+C"
echo ""

# Espera a que terminen
wait
