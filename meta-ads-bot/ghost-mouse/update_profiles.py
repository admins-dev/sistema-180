"""
Ghost Mouse — Actualizar perfiles de Instagram (nombre, bio).
Abre cada cuenta y actualiza el perfil.
"""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS
import time, os

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")

# Datos de perfil para cada cuenta
PROFILE_DATA = {
    "lauramtz.95": {
        "name": "Laura Martínez",
        "bio": "Consultora de marketing digital\nAyudo a negocios locales a llenar agenda 📈\nMálaga",
        "nicho": "local",
    },
    "carlosruiz.88": {
        "name": "Carlos Ruiz",
        "bio": "Estratega digital\nEscalo marcas personales de mentores y formadores 🚀\nMadrid · Remote",
        "nicho": "premium",
    },
    "anabelenn.90": {
        "name": "Ana Belén García",
        "bio": "Social Media Manager\nEspecialista en hostelería y restauración 🍽️\nCosta del Sol",
        "nicho": "local",
    },
    "pablofdezz86": {
        "name": "Pablo Fernández",
        "bio": "Growth marketing\nAyudo a infoproductores a escalar con estrategia digital 📊\nEspaña",
        "nicho": "premium",
    },
    "martadiaz.24": {
        "name": "Marta Díaz",
        "bio": "Captación de clientes para negocios locales\n+50 negocios ayudados 💡\nAndalucía",
        "nicho": "local",
    },
}


def update_profile(page, username, data):
    """Actualizar nombre y bio de un perfil de Instagram."""
    print(f"\n  Actualizando @{username}...")

    # Ir a editar perfil
    page.goto("https://www.instagram.com/accounts/edit/", wait_until="domcontentloaded")
    time.sleep(3)

    # Cerrar popups
    for txt in ["Ahora no", "Not Now"]:
        try: page.click(f'text="{txt}"', timeout=1000)
        except: pass

    page.screenshot(path=os.path.join(SHOTS, f"profile_edit_{username}.png"))

    # Intentar via settings
    page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded")
    time.sleep(2)

    # Clic en "Editar perfil"
    try:
        page.click('text="Editar perfil"', timeout=3000)
    except:
        try:
            page.click('text="Edit profile"', timeout=3000)
        except:
            try:
                page.click('a[href="/accounts/edit/"]', timeout=2000)
            except:
                print(f"    No se pudo abrir editar perfil")
                page.screenshot(path=os.path.join(SHOTS, f"profile_noedit_{username}.png"))
                return False

    time.sleep(3)
    page.screenshot(path=os.path.join(SHOTS, f"profile_editing_{username}.png"))
    print(f"    Perfil de edición abierto")
    return True


if __name__ == "__main__":
    print("=" * 55)
    print("  GHOST MOUSE — OPTIMIZAR PERFILES")
    print("=" * 55)

    with sync_playwright() as p:
        for i, acc in enumerate(ACCOUNTS):
            name = acc["username"]
            if name not in PROFILE_DATA:
                continue

            profile_dir = os.path.join(PROFILES_DIR, name)
            proxy = acc["proxy"]

            ctx = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                channel="msedge", headless=False,
                proxy={"server": proxy["server"], "username": proxy["username"], "password": proxy["password"]},
                args=["--disable-blink-features=AutomationControlled",
                       f"--window-position={320 * i},30", "--window-size=700,550"],
                viewport={"width": 680, "height": 500}, locale="es-ES",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                ignore_https_errors=True,
            )

            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')

            update_profile(page, name, PROFILE_DATA[name])
            ctx.close()

    print("\nPerfiles actualizados!")
