"""
TEST: Enviar DM a @josemariamoren0 desde las 5 cuentas con proxy ISP.
"""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
from dm_sender import send_dm
import time, os

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
TARGET = "josemariamoren0"

MESSAGES = [
    "Hola Jose! Soy Laura, probando Ghost Mouse 👻",
    "Ey Jose! Carlos aqui, test del sistema DM!",
    "Buenas Jose! Ana probando el motor automatico",
    "Que tal Jose! Pablo testeando Ghost Mouse",
    "Hola Jose! Marta, verificando el envio de DMs!",
]

print("=" * 55)
print("  TEST DM -> @josemariamoren0 (5 cuentas + proxy)")
print("=" * 55)

with sync_playwright() as p:
    contexts = []
    results = {}

    for i, acc in enumerate(ACCOUNTS):
        name = acc["username"]
        profile_dir = os.path.join(PROFILES_DIR, name)
        proxy = acc["proxy"]

        print(f"\n[{i+1}] @{name} (proxy: {proxy['server'].split('//')[1].split(':')[0]})")

        ctx = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            channel="msedge",
            headless=False,
            proxy={
                "server": proxy["server"],
                "username": proxy["username"],
                "password": proxy["password"],
            },
            args=[
                "--disable-blink-features=AutomationControlled",
                f"--window-position={320 * i},30",
                f"--window-size=640,500",
            ],
            viewport={"width": 620, "height": 450},
            locale="es-ES",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            ignore_https_errors=True,
        )

        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')

        # Verificar login
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(4)

        home = page.locator('svg[aria-label="Inicio"], svg[aria-label="Home"]')
        sug = page.locator('text="Sugerencias para ti"')
        notif = page.locator('text="Activar notificaciones"')

        if home.count() > 0 or sug.count() > 0 or notif.count() > 0:
            try:
                page.click('text="Ahora no"', timeout=2000)
            except:
                pass
            print(f"  LOGUEADO con proxy!")

            # Enviar DM
            msg = MESSAGES[i]
            print(f"  Enviando: {msg}")
            ok, status = send_dm(page, TARGET, msg)
            results[name] = "ENVIADO" if ok else f"FALLO ({status})"
            print(f"  -> {results[name]}")
        else:
            print(f"  SESION EXPIRADA con proxy")
            results[name] = "SESION_EXPIRADA"

        contexts.append(ctx)

    # Resumen
    print(f"\n{'='*55}")
    print(f"  RESULTADOS")
    print(f"{'='*55}")
    for name, status in results.items():
        icon = "OK" if "ENVIADO" in status else "XX"
        print(f"  [{icon}] @{name} -> {status}")
    print(f"{'='*55}")

    print(f"\nVentanas abiertas. Pulsa Enter para cerrar.")
    input()

    for ctx in contexts:
        try:
            ctx.close()
        except:
            pass
