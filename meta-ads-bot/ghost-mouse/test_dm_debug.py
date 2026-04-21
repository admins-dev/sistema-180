"""Debug: ver exactamente el flujo DM para 1 cuenta."""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
import time, os

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
acc = ACCOUNTS[2]  # Ana (nunca ha enviado DM)

with sync_playwright() as p:
    name = acc["username"]
    proxy = acc["proxy"]
    print(f"Abriendo @{name}...")

    ctx = p.chromium.launch_persistent_context(
        user_data_dir=os.path.join(PROFILES_DIR, name),
        channel="msedge", headless=False,
        proxy={"server": proxy["server"], "username": proxy["username"], "password": proxy["password"]},
        args=["--disable-blink-features=AutomationControlled", "--window-size=900,700"],
        viewport={"width": 880, "height": 650}, locale="es-ES",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        ignore_https_errors=True,
    )

    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
    page.goto("https://www.instagram.com/direct/inbox/", wait_until="domcontentloaded")
    time.sleep(3)

    try:
        page.click('text="Ahora no"', timeout=2000)
    except:
        pass

    page.screenshot(path=os.path.join(SHOTS, "debug_1_inbox.png"))
    print("1. Inbox cargado")

    # Clic compose
    compose = page.locator('svg[aria-label="Nuevo mensaje"], svg[aria-label="New message"]')
    print(f"   compose icons: {compose.count()}")
    
    # Listar TODOS los svg aria-labels
    all_svgs = page.locator('svg[aria-label]').all()
    for s in all_svgs:
        try:
            label = s.get_attribute("aria-label")
            print(f"   SVG: {label}")
        except:
            pass

    if compose.count() > 0:
        compose.first.click()
    else:
        # Intentar "Enviar mensaje"
        page.click('text="Enviar mensaje"', timeout=3000)
    time.sleep(2)

    page.screenshot(path=os.path.join(SHOTS, "debug_2_compose.png"))
    print("2. Compose abierto")

    # Buscar input
    inputs = page.locator('input').all()
    for inp in inputs:
        try:
            ph = inp.get_attribute("placeholder") or ""
            tp = inp.get_attribute("type") or ""
            nm = inp.get_attribute("name") or ""
            print(f"   INPUT: placeholder='{ph}' type='{tp}' name='{nm}'")
        except:
            pass

    # Escribir en busqueda
    search = page.locator('input[placeholder*="Busca"], input[type="text"]').first
    search.click()
    search.fill("josemariamoren0")
    time.sleep(3)

    page.screenshot(path=os.path.join(SHOTS, "debug_3_results.png"))
    print("3. Resultados de busqueda")

    # Ver todos los elementos clickeables en el dialog
    dialog = page.locator('div[role="dialog"]')
    if dialog.count() > 0:
        # Listar botones y divs clickeables
        buttons = dialog.locator('div[role="button"], button, label').all()
        for b in buttons:
            try:
                txt = b.inner_text()[:60]
                print(f"   BUTTON: '{txt}'")
            except:
                pass

    print("\nPulsa Enter para cerrar.")
    input()
    ctx.close()
