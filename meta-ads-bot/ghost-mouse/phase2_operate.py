"""
Ghost Mouse — Abrir TODAS las sesiones guardadas con proxy.
Rapido. Mantiene pestanas abiertas.
"""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
import time, os, json

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")

# Filtrar solo cuentas con sesion guardada
ready = []
for acc in ACCOUNTS:
    sf = os.path.join(SESSIONS_DIR, f"{acc['username']}.json")
    if os.path.exists(sf):
        acc["session_file"] = sf
        ready.append(acc)
    else:
        print(f"  SKIP @{acc['username']} (sin sesion)")

print(f"\n{len(ready)} cuentas listas. Abriendo...\n")

with sync_playwright() as p:
    browsers = []
    pages = []

    for i, acc in enumerate(ready):
        name = acc["username"]
        print(f"[{i+1}] @{name} con proxy {acc['proxy']['server'].split('//')[1].split(':')[0]}")

        br = p.chromium.launch(
            headless=False,
            channel="msedge",
            proxy={
                "server": acc["proxy"]["server"],
                "username": acc["proxy"]["username"],
                "password": acc["proxy"]["password"],
            },
            args=[
                "--disable-blink-features=AutomationControlled",
                f"--window-position={320 * i},30",
                f"--window-size=640,500",
            ]
        )

        # Cargar sesion guardada
        ctx = br.new_context(
            storage_state=acc["session_file"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            viewport={"width": 620, "height": 450},
            locale="es-ES",
            ignore_https_errors=True,
        )
        page = ctx.new_page()
        page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')

        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(3)

        # Verificar que esta logueado
        home = page.locator('svg[aria-label="Inicio"], svg[aria-label="Home"]')
        sugerencias = page.locator('text="Sugerencias para ti"')
        notif = page.locator('text="Activar notificaciones"')

        if home.count() > 0 or sugerencias.count() > 0 or notif.count() > 0:
            print(f"    >>> DENTRO!")
            # Cerrar popup notificaciones
            try:
                page.click('text="Ahora no"', timeout=2000)
            except:
                pass
        else:
            login_form = page.locator('text="Iniciar sesión"')
            if login_form.count() > 0:
                print(f"    >>> Sesion expirada, necesita re-login")
            else:
                print(f"    >>> Estado desconocido")

        browsers.append(br)
        pages.append(page)

    print(f"\n{'='*50}")
    print(f"  {len(browsers)} ventanas abiertas con proxy")
    print(f"  Manteniendolas abiertas...")
    print(f"{'='*50}")
    print(f"\nPulsa Enter para cerrar todas.")
    input()

    for br in browsers:
        try:
            br.close()
        except:
            pass
