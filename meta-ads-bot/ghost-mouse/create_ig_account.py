"""
Instagram signup v6 — Sigue el flujo REAL paso a paso:
1. Numero de telefono -> Siguiente
2. Codigo SMS
3. Nombre + Username + Password
4. Fecha nacimiento
"""
from playwright.sync_api import sync_playwright
import cloudscraper
import json
import time
import os

SMSPOOL_KEY = "jCQH7hDydYjVxO8449OKru8HOsR22eJ1"
FULLNAME = "Laura Martinez"
USERNAME = "laura.mtz.180"
PASSWORD = "Gh0stM0use2026!"

sms_api = cloudscraper.create_scraper()
DIR = os.path.dirname(__file__)
SHOTS = os.path.join(DIR, "screenshots")
os.makedirs(SHOTS, exist_ok=True)


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, f"{name}.png"))
    print(f"    [📸 {name}]")


def buy():
    r = sms_api.post("https://api.smspool.net/purchase/sms", data={
        "key": SMSPOOL_KEY, "country": "ES", "service": "457", "pricing_option": "0"})
    d = json.loads(r.text)
    return (d["phonenumber"], d["orderid"]) if d.get("success") else (None, None)


def wait_code(oid):
    for i in range(50):
        time.sleep(4)
        r = sms_api.get("https://api.smspool.net/sms/check",
                        params={"key": SMSPOOL_KEY, "orderid": oid})
        d = json.loads(r.text)
        if d.get("status") == 3:
            code = "".join(c for c in str(d.get("sms", "")) if c.isdigit())
            return code[-6:] if len(code) >= 6 else code
        if d.get("status") == 6:
            return None
        if i % 5 == 0:
            print(f"    ⏳ {i*4}s...")
    return None


with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=[
        "--disable-blink-features=AutomationControlled", "--no-first-run"])
    ctx = br.new_context(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        viewport={"width": 390, "height": 844}, locale="es-ES",
        is_mobile=True, has_touch=True)
    page = ctx.new_page()
    page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')

    # === PASO 0: Comprar numero ===
    print("[0] Comprando numero...")
    phone, oid = buy()
    if not phone:
        print("ERROR comprando numero"); br.close(); exit(1)
    full = f"+34{phone}"
    print(f"    📱 {full} (Order: {oid})")

    # === PASO 1: Abrir y cerrar cookies ===
    print("[1] Abriendo Instagram...")
    page.goto("https://www.instagram.com/accounts/emailsignup/")
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    # Cerrar cookies
    try:
        page.click('button:has-text("Rechazar cookies opcionales")', timeout=5000)
        print("    🍪 Cookies rechazadas")
    except:
        try:
            page.click('button:has-text("Permitir todas las cookies")', timeout=3000)
            print("    🍪 Cookies aceptadas")
        except:
            print("    🍪 Sin popup")
    time.sleep(3)
    shot(page, "s1_ready")

    # === PASO 2: Introducir numero de telefono ===
    print("[2] Introduciendo telefono...")
    # El input tiene aria-label "Número de móvil" o placeholder
    try:
        phone_input = page.locator('input[aria-label*="móvil"], input[aria-label*="Número"], input[name="phoneNumber"], input[type="tel"]').first
        phone_input.click()
        time.sleep(0.5)
        phone_input.fill("")
        time.sleep(0.3)
        # Escribir con keyboard para que React lo registre
        phone_input.type(full, delay=80)
        print(f"    ✅ {full}")
    except Exception as e:
        print(f"    ❌ {e}")
        # Intentar con generico
        try:
            page.locator("input").first.click()
            time.sleep(0.3)
            page.keyboard.type(full, delay=80)
            print(f"    ✅ (keyboard) {full}")
        except Exception as e2:
            print(f"    ❌❌ {e2}")
    time.sleep(1)
    shot(page, "s2_phone_filled")

    # Click "Siguiente"
    print("    Clicking Siguiente...")
    try:
        page.click('button:has-text("Siguiente")', timeout=5000)
        print("    ✅ Siguiente")
    except:
        try:
            page.click("button >> nth=0", timeout=3000)
            print("    ✅ Button[0]")
        except Exception as e:
            print(f"    ❌ {e}")
    time.sleep(5)
    shot(page, "s3_after_siguiente")

    # === PASO 3: Esperar y meter codigo SMS ===
    print("[3] Esperando SMS...")
    code = wait_code(oid)
    if not code:
        print("    ❌ SMS no llego")
        shot(page, "s4_no_sms")
        print(f"\n  FALLO - SMS no recibido para {full}")
        br.close()
        exit(1)

    print(f"    ✅ CODIGO: {code}")

    # Meter codigo
    try:
        code_input = page.locator('input[name*="code"], input[name*="Code"], input[aria-label*="ódigo"], input[aria-label*="code"]').first
        code_input.fill("")
        code_input.type(code, delay=80)
    except:
        # Primer input visible
        page.locator("input:visible").first.click()
        page.keyboard.type(code, delay=80)
    print(f"    Codigo ingresado")
    time.sleep(1)
    shot(page, "s4_code_entered")

    # Click confirmar/siguiente
    for txt in ["Siguiente", "Confirmar", "Confirm", "Next"]:
        try:
            page.click(f'button:has-text("{txt}")', timeout=2000)
            print(f"    ✅ {txt}")
            break
        except:
            continue
    time.sleep(5)
    shot(page, "s5_code_confirmed")

    # === PASO 4: Nombre, username, password ===
    print("[4] Datos de la cuenta...")
    # Ahora Instagram deberia pedir nombre/user/pass
    inputs = page.locator("input:visible").all()
    print(f"    {len(inputs)} inputs visibles")

    for inp in inputs:
        name = inp.get_attribute("name") or ""
        label = inp.get_attribute("aria-label") or ""
        lbl = (name + label).lower()
        if "name" in lbl or "nombre" in lbl:
            inp.fill("")
            inp.type(FULLNAME, delay=50)
            print(f"    Nombre: {FULLNAME}")
        elif "user" in lbl or "usuario" in lbl:
            inp.fill("")
            inp.type(USERNAME, delay=50)
            print(f"    Username: @{USERNAME}")
        elif "pass" in lbl or "contraseña" in lbl:
            inp.fill("")
            inp.type(PASSWORD, delay=50)
            print(f"    Password: {PASSWORD}")
    time.sleep(1)
    shot(page, "s6_profile_filled")

    # Click siguiente/registrarse
    for txt in ["Siguiente", "Registrarte", "Sign up", "Next"]:
        try:
            page.click(f'button:has-text("{txt}")', timeout=2000)
            print(f"    ✅ {txt}")
            break
        except:
            continue
    time.sleep(5)
    shot(page, "s7_after_profile")

    # === PASO 5: Fecha nacimiento ===
    print("[5] Fecha nacimiento...")
    selects = page.locator("select").all()
    if len(selects) >= 3:
        selects[0].select_option("3")
        selects[1].select_option("15")
        selects[2].select_option("1995")
        time.sleep(1)
        for txt in ["Siguiente", "Next"]:
            try:
                page.click(f'button:has-text("{txt}")', timeout=2000)
                break
            except:
                continue
        print("    ✅ Fecha enviada")
    else:
        print(f"    Sin fecha ({len(selects)} selects)")
    time.sleep(5)
    shot(page, "s8_final")

    # === RESULTADO ===
    url = page.url
    print(f"\n{'='*50}")
    print(f"  URL FINAL: {url}")
    if "challenge" not in url and "/accounts/" not in url:
        print(f"  ✅ PARECE QUE LA CUENTA SE CREO!")
    print(f"  Username: @{USERNAME}")
    print(f"  Password: {PASSWORD}")
    print(f"  Phone:    {full}")
    print(f"{'='*50}")
    br.close()
    print("FIN")
