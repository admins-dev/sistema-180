"""Test rapido: 1 cuenta -> DM a @josemariamoren0"""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
from dm_sender import send_dm
import time, os

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
acc = ACCOUNTS[1]  # Carlos

with sync_playwright() as p:
    name = acc["username"]
    proxy = acc["proxy"]
    print(f"Abriendo @{name} con proxy...")

    ctx = p.chromium.launch_persistent_context(
        user_data_dir=os.path.join(PROFILES_DIR, name),
        channel="msedge",
        headless=False,
        proxy={"server": proxy["server"], "username": proxy["username"], "password": proxy["password"]},
        args=["--disable-blink-features=AutomationControlled", "--window-size=900,700"],
        viewport={"width": 880, "height": 650},
        locale="es-ES",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        ignore_https_errors=True,
    )

    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
    page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
    time.sleep(4)

    try:
        page.click('text="Ahora no"', timeout=2000)
    except:
        pass

    print("Enviando DM...")
    ok, status = send_dm(page, "josemariamoren0", "Test Ghost Mouse! Esto es un mensaje automatico de prueba.")
    print(f"Resultado: {ok} - {status}")

    print("\nPulsa Enter para cerrar.")
    input()
    ctx.close()
