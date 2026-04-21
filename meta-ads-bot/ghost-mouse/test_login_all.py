"""
Ghost Mouse - Test ALL 5 setter accounts login.
Prueba las 5 cuentas en secuencia con sus proxies.
Resultado: PASS/FAIL por cada cuenta.
"""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
import time, os, json

SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SHOTS, exist_ok=True)

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "login_results.json")

def test_account(pw, acc, index):
    username = acc["username"]
    print(f"\n{'='*50}")
    print(f"[{index+1}/5] Testing @{username}")
    print(f"Proxy: {acc['proxy']['server']}")
    print(f"{'='*50}")
    
    result = {
        "username": username,
        "fullname": acc.get("fullname", ""),
        "proxy": acc["proxy"]["server"],
        "status": "UNKNOWN",
        "error": None
    }
    
    try:
        br = pw.chromium.launch(
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
        time.sleep(4)

        for txt in ["Rechazar cookies opcionales", "Permitir todas las cookies",
                     "Decline optional cookies", "Allow all cookies"]:
            try:
                page.click(f'button:has-text("{txt}")', timeout=2000)
                break
            except:
                continue
        time.sleep(2)

        user_field = page.locator('input[name="email"], input[name="username"]').first
        pass_field = page.locator('input[name="pass"], input[name="password"]').first

        user_field.click()
        time.sleep(0.2)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        for c in acc["username"]:
            page.keyboard.type(c, delay=40)
        time.sleep(0.3)

        pass_field.click()
        time.sleep(0.2)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        for c in acc["password"]:
            page.keyboard.type(c, delay=40)
        time.sleep(0.5)

        page.keyboard.press("Enter")
        time.sleep(12)

        shot_path = os.path.join(SHOTS, f"login_{username}.png")
        page.screenshot(path=shot_path)

        notif = page.locator('text="Activar notificaciones"')
        home = page.locator('svg[aria-label="Inicio"], svg[aria-label="Home"]')
        error_pwd = page.locator('text="incorrecta"')
        error_unusual = page.locator('text="sospechosa"')
        challenge = page.locator('text="Confirma"')

        if error_pwd.count() > 0:
            result["status"] = "FAIL_PASSWORD"
            result["error"] = "Password incorrecta"
            print(f"  [FAIL] Password incorrecta")
        elif error_unusual.count() > 0:
            result["status"] = "FAIL_SUSPICIOUS"
            result["error"] = "Actividad sospechosa detectada"
            print(f"  [WARN] BLOQUEADO: Actividad sospechosa")
        elif challenge.count() > 0:
            result["status"] = "CHALLENGE"
            result["error"] = "Requiere verificacion"
            print(f"  [WARN] CHALLENGE: Necesita verificacion")
        elif notif.count() > 0 or home.count() > 0:
            result["status"] = "PASS"
            print(f"  [OK] Login correcto!")
        else:
            body = page.inner_text("body")[:200]
            result["status"] = "UNKNOWN"
            result["error"] = body
            print(f"  [?] DESCONOCIDO: {body[:100]}")

        br.close()

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        print(f"  [ERROR] {e}")

    return result


def main():
    print("[LOCK] GHOST MOUSE - TEST LOGIN 5 CUENTAS")
    print("=" * 60)

    results = []

    with sync_playwright() as pw:
        for i, acc in enumerate(ACCOUNTS):
            res = test_account(pw, acc, i)
            results.append(res)
            time.sleep(3)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("[REPORT] RESUMEN DE LOGIN")
    print("=" * 60)

    passed = 0
    for r in results:
        icon = "[OK]" if r["status"] == "PASS" else "[FAIL]" if "FAIL" in r["status"] else "[WARN]"
        print(f"  {icon} @{r['username']}: {r['status']}")
        if r["status"] == "PASS":
            passed += 1

    print(f"\n  {passed}/5 cuentas operativas")
    print(f"  Resultados guardados en: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
