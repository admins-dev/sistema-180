"""
Ghost Mouse — FASE 1: Login sin proxy + guardar sesiones.
Abre cada cuenta en Edge real, logea, guarda las cookies a disco.
Solo se ejecuta UNA VEZ por cuenta.
"""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
import time, os, json

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(SHOTS, exist_ok=True)

def login_and_save(pw, acc):
    name = acc["username"]
    session_file = os.path.join(SESSIONS_DIR, f"{name}.json")

    # Si ya tiene sesion guardada, saltar
    if os.path.exists(session_file):
        print(f"  [{name}] Sesion ya existe, saltando")
        return True

    print(f"  [{name}] Abriendo Edge...")
    br = pw.chromium.launch(
        headless=False,
        channel="msedge",
        args=["--disable-blink-features=AutomationControlled"]
    )
    ctx = br.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        viewport={"width": 1280, "height": 900},
        locale="es-ES",
    )
    page = ctx.new_page()
    page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')

    # Instagram
    page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    time.sleep(5)

    # Cookies
    for txt in ["Rechazar cookies opcionales", "Permitir todas las cookies"]:
        try:
            page.click(f'button:has-text("{txt}")', timeout=3000)
            break
        except:
            continue
    time.sleep(3)

    # Login char by char
    user_field = page.locator('input[name="email"], input[name="username"]').first
    pass_field = page.locator('input[name="pass"], input[name="password"]').first

    user_field.click()
    time.sleep(0.3)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    for c in acc["username"]:
        page.keyboard.type(c, delay=50)
    time.sleep(0.5)

    pass_field.click()
    time.sleep(0.3)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    for c in acc["password"]:
        page.keyboard.type(c, delay=50)
    time.sleep(1)

    page.keyboard.press("Enter")
    print(f"  [{name}] Login enviado, esperando...")
    time.sleep(15)

    # Verificar login real
    notif = page.locator('text="Activar notificaciones"')
    home = page.locator('svg[aria-label="Inicio"], svg[aria-label="Home"]')
    error = page.locator('text="incorrecta"')
    sugerencias = page.locator('text="Sugerencias para ti"')

    if error.count() > 0:
        print(f"  [{name}] FALLO: Password incorrecta")
        page.screenshot(path=os.path.join(SHOTS, f"login_fail_{name}.png"))
        br.close()
        return False

    if notif.count() > 0 or home.count() > 0 or sugerencias.count() > 0:
        # Cerrar popup notificaciones
        try:
            page.click('text="Ahora no"', timeout=3000)
        except:
            pass
        time.sleep(2)

        # Guardar sesion (cookies + storage)
        storage = ctx.storage_state()
        with open(session_file, "w") as f:
            json.dump(storage, f)

        page.screenshot(path=os.path.join(SHOTS, f"login_ok_{name}.png"))
        print(f"  [{name}] OK! Sesion guardada en {session_file}")
        br.close()
        return True
    else:
        url = page.url
        if "/challenge" in url or "auth_platform" in url:
            print(f"  [{name}] CHALLENGE - verificacion requerida")
        else:
            print(f"  [{name}] DESCONOCIDO: {page.inner_text('body')[:100]}")
        page.screenshot(path=os.path.join(SHOTS, f"login_other_{name}.png"))
        br.close()
        return False


# Main
print("=" * 50)
print("  FASE 1: LOGIN Y GUARDAR SESIONES")
print("=" * 50)

with sync_playwright() as p:
    ok = 0
    for acc in ACCOUNTS:
        print(f"\n@{acc['username']}:")
        if login_and_save(p, acc):
            ok += 1
        time.sleep(3)  # Pausa entre cuentas

    print(f"\n{'=' * 50}")
    print(f"  {ok}/{len(ACCOUNTS)} sesiones guardadas")
    print(f"{'=' * 50}")
