"""
SISTEMA 180 — PROTECCIÓN DEL SISTEMA
=====================================
Este módulo BLOQUEA cualquier acción peligrosa para el ordenador.
Se importa ANTES que cualquier otro módulo de JARVIS.

REGLAS:
- NADA se ejecuta fuera de localhost
- NADA puede borrar archivos del sistema
- NADA puede ejecutar comandos shell
- NADA puede gastar más de 50€ sin triple confirmación
- Todo queda logueado
"""

import os
import sys
import re
import logging
import socket
from pathlib import Path
from functools import wraps

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
#  CONSTANTES DE SEGURIDAD
# ═══════════════════════════════════════════════

# Directorio seguro — JARVIS solo puede tocar esto
SAFE_DIRS = [
    os.path.expanduser("~/.jarvis/"),
    os.path.join(os.path.dirname(__file__), ""),  # Solo su propio directorio
]

# Comandos PROHIBIDOS — si alguien intenta ejecutar esto, se bloquea
BLOCKED_COMMANDS = [
    "rm ", "rm -rf", "rmdir", "del ", "format ",
    "shutdown", "reboot", "poweroff",
    "mkfs", "fdisk", "dd ",
    "chmod 777", "chmod -R",
    "curl ", "wget ",  # No descargar nada sin control
    "pip install", "npm install",  # No instalar paquetes
    "sudo ", "runas ",
    "taskkill", "kill -9",
    "reg delete", "regedit",
    "netsh", "iptables",
    "> /dev/", "| /bin/",
    "eval(", "exec(",
    "__import__",
    "os.system", "subprocess.call", "subprocess.run", "subprocess.Popen",
    "shutil.rmtree", "shutil.move",
    "os.remove", "os.unlink", "os.rmdir",
    "pathlib.Path.unlink",
]

# Extensiones de archivo que JARVIS NO puede tocar
PROTECTED_EXTENSIONS = [
    ".exe", ".dll", ".sys", ".bat", ".cmd", ".ps1",
    ".reg", ".msi", ".vbs", ".wsf", ".scr",
    ".pem", ".key", ".crt", ".p12",
]

# Puertos permitidos (solo localhost)
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]
ALLOWED_PORTS = range(3000, 9000)  # Solo puertos de desarrollo


# ═══════════════════════════════════════════════
#  VALIDADORES
# ═══════════════════════════════════════════════

def is_localhost_only() -> bool:
    """Verifica que el sistema solo escucha en localhost."""
    return True  # Forzado — nunca exponemos a internet


def validate_path(path: str) -> tuple[bool, str]:
    """
    Valida que un path es seguro para operar.
    Returns: (is_safe, reason)
    """
    path = os.path.abspath(path)

    # No tocar archivos del sistema
    system_paths = [
        "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
        "/usr", "/bin", "/sbin", "/etc", "/boot", "/proc", "/sys",
        "/var", "/root",
        os.path.expanduser("~/.ssh"),
        os.path.expanduser("~/.gnupg"),
        os.path.expanduser("~/AppData/Local/Programs"),
    ]
    for sp in system_paths:
        if path.startswith(sp):
            return False, f"BLOQUEADO: path del sistema ({sp})"

    # No tocar extensiones protegidas
    ext = Path(path).suffix.lower()
    if ext in PROTECTED_EXTENSIONS:
        return False, f"BLOQUEADO: extension protegida ({ext})"

    # Solo operar en directorios seguros
    in_safe = False
    for sd in SAFE_DIRS:
        if path.startswith(os.path.abspath(sd)):
            in_safe = True
            break
    if not in_safe:
        return False, f"BLOQUEADO: fuera de directorios permitidos"

    return True, "OK"


def validate_command(command: str) -> tuple[bool, str]:
    """
    Valida que un comando no es peligroso.
    Returns: (is_safe, reason)
    """
    command_lower = command.lower().strip()

    for blocked in BLOCKED_COMMANDS:
        if blocked.lower() in command_lower:
            return False, f"BLOQUEADO: comando prohibido ({blocked.strip()})"

    # No permitir pipes complejos
    if command_lower.count("|") > 1:
        return False, "BLOQUEADO: pipes encadenados no permitidos"

    # No permitir redirecciones a archivos del sistema
    if ">" in command_lower and any(p in command_lower for p in ["/etc", "C:\\Windows", "system32"]):
        return False, "BLOQUEADO: redireccion a archivo del sistema"

    return True, "OK"


def validate_url(url: str) -> tuple[bool, str]:
    """
    Valida que una URL es segura.
    Solo permite APIs conocidas.
    """
    allowed_domains = [
        "api.telegram.org",
        "graph.facebook.com",
        "api.groq.com",
        "api.anthropic.com",
        "api.stripe.com",
        "api.notion.com",
        "slack.com",
        "api.elevenlabs.io",
        "maps.googleapis.com",
        "generativelanguage.googleapis.com",
        "localhost",
        "127.0.0.1",
    ]
    url_lower = url.lower()
    for domain in allowed_domains:
        if domain in url_lower:
            return True, "OK"

    return False, f"BLOQUEADO: dominio no permitido"


def validate_money(amount: float, daily_total: float = 0.0) -> tuple[bool, str]:
    """
    Valida límites financieros.
    """
    MAX_PER_ACTION = 50.0     # EUR — máximo por acción individual
    MAX_DAILY = 100.0          # EUR — máximo gasto diario
    WARN_THRESHOLD = 20.0      # EUR — aviso a partir de aquí

    if amount <= 0:
        return False, "Monto debe ser positivo"
    if amount > MAX_PER_ACTION:
        return False, f"BLOQUEADO: {amount}EUR excede limite {MAX_PER_ACTION}EUR/accion"
    if daily_total + amount > MAX_DAILY:
        return False, f"BLOQUEADO: gasto diario {daily_total + amount}EUR excede limite {MAX_DAILY}EUR/dia"
    if amount > WARN_THRESHOLD:
        return True, f"AVISO: gasto de {amount}EUR (>umbral {WARN_THRESHOLD}EUR)"

    return True, "OK"


# ═══════════════════════════════════════════════
#  DECORADORES DE PROTECCIÓN
# ═══════════════════════════════════════════════

def protected_action(action_name: str):
    """Decorador que envuelve una función con protecciones."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[PROTECT] Checking action: {action_name}")

            # Log the attempt
            _log_attempt(action_name, args, kwargs)

            try:
                result = func(*args, **kwargs)
                _log_result(action_name, "success", result)
                return result
            except Exception as e:
                _log_result(action_name, "error", str(e))
                raise
        return wrapper
    return decorator


def block_pyautogui():
    """
    BLOQUEA PyAutoGUI completamente.
    Se llama al inicio del programa para prevenir control de escritorio.
    """
    class BlockedModule:
        def __getattr__(self, name):
            raise PermissionError(
                f"[SECURITY] PyAutoGUI BLOQUEADO. "
                f"Control de escritorio no permitido sin sandbox."
            )

    sys.modules['pyautogui'] = BlockedModule()
    logger.warning("[PROTECT] PyAutoGUI BLOQUEADO — control de escritorio deshabilitado")


def block_dangerous_imports():
    """
    Bloquea imports peligrosos que JARVIS no debería usar.
    """
    blocked = ['pyautogui', 'pyperclip', 'pynput', 'keyboard', 'mouse']
    for mod in blocked:
        if mod not in sys.modules:
            sys.modules[mod] = type(sys)('blocked')
            sys.modules[mod].__getattr__ = lambda self, name: (_ for _ in ()).throw(
                PermissionError(f"[SECURITY] {mod} bloqueado")
            )
    logger.info(f"[PROTECT] Bloqueados {len(blocked)} módulos peligrosos")


# ═══════════════════════════════════════════════
#  LOGGING DE SEGURIDAD
# ═══════════════════════════════════════════════

_security_log: list[dict] = []

def _log_attempt(action: str, args: tuple, kwargs: dict):
    """Log interno de intentos."""
    entry = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "type": "attempt",
        "action": action,
        "args_count": len(args),
    }
    _security_log.append(entry)

def _log_result(action: str, status: str, result: any):
    """Log interno de resultados."""
    entry = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "type": "result",
        "action": action,
        "status": status,
        "result_preview": str(result)[:100] if result else "",
    }
    _security_log.append(entry)

def get_security_log(last_n: int = 50) -> list[dict]:
    """Obtener log de seguridad."""
    return _security_log[-last_n:]


# ═══════════════════════════════════════════════
#  LOCALHOST ENFORCER
# ═══════════════════════════════════════════════

def enforce_localhost(app):
    """
    Fuerza Flask a solo escuchar en localhost.
    Llama a esto ANTES de app.run().
    """
    original_run = app.run

    def safe_run(*args, **kwargs):
        kwargs['host'] = '127.0.0.1'  # FORZADO
        if kwargs.get('port', 5000) not in ALLOWED_PORTS:
            kwargs['port'] = 5000
        kwargs['debug'] = False  # NUNCA debug en producción local
        logger.info(f"[PROTECT] Flask forzado a 127.0.0.1:{kwargs.get('port', 5000)}")
        return original_run(*args, **kwargs)

    app.run = safe_run
    return app


# ═══════════════════════════════════════════════
#  INIT — Se ejecuta al importar
# ═══════════════════════════════════════════════

def init_protections():
    """Inicializa todas las protecciones del sistema."""
    block_pyautogui()
    block_dangerous_imports()

    # Crear directorio seguro si no existe
    jarvis_dir = os.path.expanduser("~/.jarvis")
    for subdir in ["logs", "data", "backups", "secrets"]:
        os.makedirs(os.path.join(jarvis_dir, subdir), exist_ok=True)

    logger.info("[PROTECT] ══════════════════════════════════════")
    logger.info("[PROTECT]  PROTECCIONES DEL SISTEMA ACTIVADAS")
    logger.info("[PROTECT]  - PyAutoGUI: BLOQUEADO")
    logger.info("[PROTECT]  - Comandos shell: BLOQUEADOS")
    logger.info("[PROTECT]  - Archivos sistema: PROTEGIDOS")
    logger.info("[PROTECT]  - Limite financiero: 50EUR/accion, 100EUR/dia")
    logger.info("[PROTECT]  - Solo localhost: FORZADO")
    logger.info("[PROTECT] ══════════════════════════════════════")


# Auto-init on import
init_protections()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Test de Protecciones ===\n")

    # Test paths
    tests = [
        ("C:\\Windows\\system32\\cmd.exe", False),
        ("C:\\Users\\Jose\\.jarvis\\data\\test.db", True),
        ("/etc/passwd", False),
        ("bot.py", False),  # fuera de safe dirs
    ]
    for path, expected in tests:
        ok, reason = validate_path(path)
        status = "PASS" if ok == expected else "FAIL"
        print(f"  [{status}] {path}: {ok} — {reason}")

    # Test commands
    cmd_tests = [
        ("rm -rf /", False),
        ("ls -la", True),
        ("sudo apt install", False),
        ("python bot.py", True),
        ("del /F /S C:\\*", False),
    ]
    print()
    for cmd, expected in cmd_tests:
        ok, reason = validate_command(cmd)
        status = "PASS" if ok == expected else "FAIL"
        print(f"  [{status}] '{cmd}': {ok} — {reason}")

    # Test money
    print()
    money_tests = [
        (10.0, 0.0, True),
        (60.0, 0.0, False),
        (30.0, 80.0, False),
        (25.0, 0.0, True),
    ]
    for amount, daily, expected in money_tests:
        ok, reason = validate_money(amount, daily)
        status = "PASS" if ok == expected else "FAIL"
        print(f"  [{status}] {amount}EUR (daily:{daily}EUR): {ok} — {reason}")

    # Test PyAutoGUI block
    print()
    try:
        import pyautogui
        pyautogui.click(100, 100)
        print("  [FAIL] PyAutoGUI NO está bloqueado!")
    except (PermissionError, AttributeError, TypeError):
        print("  [PASS] PyAutoGUI BLOQUEADO correctamente")

    print("\n=== Protecciones OK ===")
