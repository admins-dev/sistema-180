"""Ghost Mouse — Test solo Carlos con Edge + Proxy. Confirmacion."""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
import time, os

SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SHOTS, exist_ok=True)

acc = ACCOUNTS[1]  # carlosruiz.88 - el que funciono antes
print(f"TEST: @{acc['username']} / {acc['password']}")
print(f"Proxy: {acc['proxy']['server']}")

with sync_playwright() as p:
    br = p.chromium.launch(
        headless=False,
        channel="msedge",
        proxy={
            "server": acc["proxy"]["server"],
            "username": acc["proxy"]["username"],
            "password": acc["proxy"]["password"],
        },
        args=["--disable-blink-features=AutomationControlled"]
    )
    ctx = br.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        viewport={"width": 1280, "height": 900},
        locale="es-ES",
        ignore_https_errors=True,
    )
    page = ctx.new_page()
    page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')

    page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    time.sleep(5)

    for txt in ["Rechazar cookies opcionales", "Permitir todas las cookies"]:
        try:
            page.click(f'button:has-text("{txt}")', timeout=3000)
            break
        except:
            continue
    time.sleep(3)

    # Login
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

    print(f"Escrito: {user_field.input_value()} / {pass_field.input_value()}")
    page.keyboard.press("Enter")
    time.sleep(15)

    page.screenshot(path=os.path.join(SHOTS, "confirm_carlos.png"))

    # Deteccion REAL - buscar el popup de notificaciones o iconos del feed
    notif = page.locator('text="Activar notificaciones"')
    home = page.locator('svg[aria-label="Inicio"], svg[aria-label="Home"]')
    error = page.locator('text="incorrecta"')
    
    if error.count() > 0:
        print(">>> FALLO: Password incorrecta")
        print(">>> Instagram bloqueo temporalmente por muchos intentos")
    elif notif.count() > 0 or home.count() > 0:
        print(">>> EXITO: Dentro de Instagram!")
    else:
        body = page.inner_text("body")[:300]
        print(f">>> OTRO: {body}")

    print("\nPulsa Enter para cerrar.")
    input()
    br.close()
