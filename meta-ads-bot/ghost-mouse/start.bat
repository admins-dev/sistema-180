@echo off
REM ══════════════════════════════════════════════
REM  SISTEMA 180 — Ghost Mouse Launcher (Windows)
REM ══════════════════════════════════════════════

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   SISTEMA 180 — RATON FANTASMA v1.0             ║
echo  ║   Ghost Mouse Instagram Prospector + Dashboard   ║
echo  ╚══════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM ── Paso 1: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instala Python 3.11+
    pause
    exit /b
)

REM ── Paso 2: Crear entorno virtual si no existe
if not exist "venv" (
    echo [SETUP] Creando entorno virtual...
    python -m venv venv
)

REM ── Paso 3: Activar entorno
call venv\Scripts\activate.bat

REM ── Paso 4: Instalar dependencias
echo [SETUP] Instalando dependencias...
pip install -r requirements.txt --quiet

REM ── Paso 5: Instalar Playwright browsers
echo [SETUP] Instalando navegador Chromium para Playwright...
playwright install chromium

REM ── Paso 6: Crear carpetas de datos
if not exist "data" mkdir data
if not exist "data\sessions" mkdir data\sessions

echo.
echo ===================================================
echo  TODO LISTO. Lanzando Ghost Mouse...
echo.
echo  Dashboard:  http://localhost:3180
echo  WebSocket:  ws://localhost:8765
echo ===================================================
echo.

REM ── Paso 7: Lanzar el servidor (bot + dashboard)
python server.py

pause
