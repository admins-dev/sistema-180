"""
Ghost Mouse - Actualizar TODOS los perfiles de setters en paralelo.
Usa Playwright con proxies dedicados para cada cuenta.
Login + Bio + Avatar para las 5 cuentas simultaneamente.
"""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
from setter_profiles import SETTER_PROFILES, get_bio_text
import time, os, threading, json

SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
AVATARS = os.path.join(os.path.dirname(__file__), "setter_avatars")
os.makedirs(SHOTS, exist_ok=True)

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "profile_update_results.json")

# Mapeo cuenta -> perfil setter
ACCOUNT_PROFILE_MAP = {
    "lauramtz.95": "lauramtz.95",
    "carlosruiz.88": "carlosruiz.88",
    "anabelenn.90": "anabelenn.90",
    "pablofdezz86": "pablofdezz86",
    "martadiaz.24": "martadiaz.24",
}

# Mapeo cuenta -> avatar file
ACCOUNT_AVATAR_MAP = {
    "lauramtz.95": "laura_martinez.png",
    "carlosruiz.88": "carlos_ruiz.png",
    "anabelenn.90": "ana_torres.png",
    "pablofdezz86": "pablo_fernandez.png",
    "martadiaz.24": "marta_diaz.png",
}


def update_single_profile(acc, index):
    """Actualiza un perfil completo: login + bio + avatar."""
    username = acc["username"]
    profile = SETTER_PROFILES.get(username)
    if not profile:
        print(f"  [{username}] No hay perfil de setter configurado")
        return {"username": username, "status": "NO_PROFILE"}
    
    bio_text = get_bio_text(username)
    avatar_file = os.path.join(AVATARS, ACCOUNT_AVATAR_MAP.get(username, ""))
    
    print(f"\n[{index+1}/5] Actualizando @{username} ({profile['fullname']})")
    print(f"  Proxy: {acc['proxy']['server']}")
    print(f"  Bio: {bio_text[:50]}...")
    
    result = {
        "username": username,
        "fullname": profile["fullname"],
        "login": "PENDING",
        "bio_updated": False,
        "avatar_updated": False,
        "error": None
    }
    
    try:
        with sync_playwright() as pw:
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
            
            # === LOGIN ===
            print(f"  [{username}] Haciendo login...")
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            time.sleep(4)
            
            # Cookies
            for txt in ["Rechazar cookies opcionales", "Permitir todas las cookies",
                         "Decline optional cookies", "Allow all cookies"]:
                try:
                    page.click(f'button:has-text("{txt}")', timeout=2000)
                    break
                except:
                    continue
            time.sleep(2)
            
            # Escribir credenciales
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
            
            # Verificar login
            notif = page.locator('text="Activar notificaciones"')
            home = page.locator('svg[aria-label="Inicio"], svg[aria-label="Home"]')
            error_pwd = page.locator('text="incorrecta"')
            
            if error_pwd.count() > 0:
                result["login"] = "FAIL"
                result["error"] = "Password incorrecta"
                print(f"  [{username}] [FAIL] Password incorrecta")
                br.close()
                return result
            
            if notif.count() > 0:
                page.click('text="Ahora no"', timeout=3000)
                time.sleep(1)
            
            if notif.count() > 0 or home.count() > 0:
                result["login"] = "OK"
                print(f"  [{username}] [OK] Login correcto")
            else:
                result["login"] = "UNKNOWN"
                page.screenshot(path=os.path.join(SHOTS, f"login_{username}.png"))
                print(f"  [{username}] [?] Estado desconocido - screenshot guardado")
                br.close()
                return result
            
            # === EDITAR PERFIL ===
            print(f"  [{username}] Navegando a editar perfil...")
            page.goto("https://www.instagram.com/accounts/edit/", wait_until="domcontentloaded")
            time.sleep(5)
            
            # Actualizar bio
            try:
                bio_field = page.locator('textarea[id="pepBio"], textarea[name="bio"], textarea').first
                bio_field.click()
                time.sleep(0.3)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                time.sleep(0.2)
                
                # Escribir bio linea por linea
                for line in bio_text.split("\n"):
                    page.keyboard.type(line, delay=20)
                    page.keyboard.press("Enter")
                time.sleep(0.5)
                
                # Buscar boton guardar
                for btn_text in ["Enviar", "Submit", "Guardar", "Save"]:
                    try:
                        page.click(f'button:has-text("{btn_text}")', timeout=2000)
                        result["bio_updated"] = True
                        print(f"  [{username}] [OK] Bio actualizada")
                        break
                    except:
                        continue
                
                if not result["bio_updated"]:
                    # Intentar con el boton de submit del form
                    try:
                        page.locator('form button[type="submit"]').click()
                        result["bio_updated"] = True
                        print(f"  [{username}] [OK] Bio actualizada (form submit)")
                    except:
                        print(f"  [{username}] [WARN] No encontre boton guardar")
                
                time.sleep(3)
            except Exception as e:
                print(f"  [{username}] [ERROR] Bio: {e}")
                result["error"] = str(e)
            
            # Screenshot final
            page.screenshot(path=os.path.join(SHOTS, f"profile_{username}.png"))
            
            # === AVATAR (si existe) ===
            if os.path.exists(avatar_file):
                try:
                    page.goto("https://www.instagram.com/accounts/edit/", wait_until="domcontentloaded")
                    time.sleep(3)
                    
                    # Buscar el boton de cambiar foto
                    change_photo = page.locator('text="Cambiar foto de perfil", text="Change profile photo"').first
                    if change_photo.count() > 0:
                        change_photo.click()
                        time.sleep(2)
                        
                        # Subir archivo
                        upload = page.locator('text="Subir foto", text="Upload Photo"').first
                        if upload.count() > 0:
                            with page.expect_file_chooser() as fc:
                                upload.click()
                            file_chooser = fc.value
                            file_chooser.set_files(avatar_file)
                            time.sleep(5)
                            result["avatar_updated"] = True
                            print(f"  [{username}] [OK] Avatar actualizado")
                except Exception as e:
                    print(f"  [{username}] [WARN] Avatar no actualizado: {e}")
            
            br.close()
    
    except Exception as e:
        result["error"] = str(e)
        print(f"  [{username}] [ERROR] {e}")
    
    return result


def update_all_profiles_sequential():
    """Actualiza todos los perfiles en secuencia (mas seguro)."""
    print("=" * 60)
    print("  GHOST MOUSE - ACTUALIZAR 5 PERFILES")
    print("  Login + Bio + Avatar para cada setter")
    print("=" * 60)
    
    results = []
    for i, acc in enumerate(ACCOUNTS):
        res = update_single_profile(acc, i)
        results.append(res)
        time.sleep(5)  # Pausa entre cuentas
    
    # Guardar resultados
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN DE ACTUALIZACION")
    print("=" * 60)
    
    for r in results:
        login_icon = "[OK]" if r["login"] == "OK" else "[FAIL]"
        bio_icon = "[OK]" if r["bio_updated"] else "[--]"
        avatar_icon = "[OK]" if r["avatar_updated"] else "[--]"
        print(f"  {login_icon} @{r['username']}: Login={r['login']} Bio={bio_icon} Avatar={avatar_icon}")
    
    ok = len([r for r in results if r["login"] == "OK"])
    print(f"\n  {ok}/5 perfiles actualizados")
    return results


if __name__ == "__main__":
    update_all_profiles_sequential()
