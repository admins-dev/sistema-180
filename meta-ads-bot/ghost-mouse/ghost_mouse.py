"""
Ghost Mouse — Motor Principal.
Abre todas las cuentas con perfiles persistentes,
busca leads, y envia DMs automaticamente.

Uso:
  python ghost_mouse.py                     # Solo abrir cuentas
  python ghost_mouse.py buscar peluquerias  # Buscar leads
  python ghost_mouse.py enviar              # Enviar DMs pendientes
  python ghost_mouse.py auto                # Buscar + Enviar todo
"""
from playwright.sync_api import sync_playwright
from config import ACCOUNTS, MAX_DMS_PER_ACCOUNT_PER_DAY
from dm_sender import send_dm
from brain import generate_dm
from lead_finder import search_and_find_instagram
from crm import (
    init_db, import_leads_from_json, get_leads_to_contact,
    update_lead_status, log_message, get_dms_sent_today,
    get_pipeline_stats, was_already_contacted
)
import time, os, sys, random

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(PROFILES_DIR, exist_ok=True)
os.makedirs(SHOTS, exist_ok=True)

# Ciudades Costa del Sol + Espana
CIUDADES_COSTA_SOL = [
    "Malaga", "Marbella", "Fuengirola", "Torremolinos", "Benalmadena",
    "Estepona", "Nerja", "Rincon de la Victoria", "Velez-Malaga",
]
CIUDADES_ESPANA = [
    "Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza",
    "Bilbao", "Alicante", "Cordoba", "Granada", "Murcia",
]
NICHOS_LOCALES = [
    # Servicios con cita/agenda
    "peluquerias", "clinicas dentales", "clinicas esteticas", "centros de fisioterapia",
    "gimnasios", "centros de yoga", "centros de pilates",
    # Hosteleria
    "restaurantes", "cafeterias", "bares de copas",
    # Servicios profesionales
    "inmobiliarias", "asesoria fiscal", "despacho abogados", "seguros",
    # Comercio
    "tiendas de ropa", "opticas", "floristerias", "joyerias",
    # Salud y bienestar
    "psicologos", "nutricionistas", "veterinarios",
    # Servicios tecnicos
    "talleres mecanicos", "reformas",
    # Educacion
    "academias de idiomas", "autoescuelas",
]

NICHOS_PREMIUM = [
    # Mentores e infoproductores
    "mentor de negocios", "coach de vida", "coach empresarial",
    "formador online", "infoproductor", "consultor de marketing",
    "mentor de ventas", "coach financiero", "experto en ecommerce",
    "formador de desarrollo personal", "mentor inmobiliario",
]


def open_account(pw, acc, index):
    """Abrir cuenta con perfil persistente."""
    name = acc["username"]
    profile_dir = os.path.join(PROFILES_DIR, name)

    ctx = pw.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        channel="msedge",
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            f"--window-position={320 * index},30",
            f"--window-size=640,500",
        ],
        viewport={"width": 620, "height": 450},
        locale="es-ES",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        ignore_https_errors=True,
    )

    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
    page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
    time.sleep(3)

    # Check login
    home = page.locator('svg[aria-label="Inicio"], svg[aria-label="Home"]')
    sug = page.locator('text="Sugerencias para ti"')
    notif = page.locator('text="Activar notificaciones"')

    if home.count() > 0 or sug.count() > 0 or notif.count() > 0:
        try:
            page.click('text="Ahora no"', timeout=2000)
        except:
            pass
        print(f"  [{name}] LOGUEADO")
        return ctx, page, True

    # Necesita login
    for txt in ["Rechazar cookies opcionales", "Permitir todas las cookies"]:
        try:
            page.click(f'button:has-text("{txt}")', timeout=2000)
            break
        except:
            continue
    time.sleep(2)

    user_f = page.locator('input[name="email"], input[name="username"]').first
    pass_f = page.locator('input[name="pass"], input[name="password"]').first

    user_f.click()
    time.sleep(0.2)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    for c in acc["username"]:
        page.keyboard.type(c, delay=30)
    time.sleep(0.3)
    pass_f.click()
    time.sleep(0.2)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    for c in acc["password"]:
        page.keyboard.type(c, delay=30)
    time.sleep(0.5)
    page.keyboard.press("Enter")
    time.sleep(10)

    error = page.locator('text="incorrecta"')
    if error.count() > 0:
        print(f"  [{name}] PASSWORD INCORRECTA")
        return ctx, page, False

    try:
        page.click('text="Ahora no"', timeout=3000)
    except:
        pass
    print(f"  [{name}] LOGIN OK")
    return ctx, page, True


def distribute_leads(leads, accounts):
    """Distribuir leads entre cuentas (round-robin)."""
    assignments = {acc["username"]: [] for acc in accounts}
    active_accounts = [acc["username"] for acc in accounts]

    for i, lead in enumerate(leads):
        acc_name = active_accounts[i % len(active_accounts)]
        if len(assignments[acc_name]) < MAX_DMS_PER_ACCOUNT_PER_DAY:
            assignments[acc_name].append(lead)

    return assignments


# =============================================
#  MAIN
# =============================================
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "abrir"

    print("=" * 55)
    print("  GHOST MOUSE — SISTEMA DE PROSPECCION AUTOMATICA")
    print("=" * 55)

    with sync_playwright() as p:
        # 1 - Abrir todas las cuentas
        print("\n[FASE 1] Abriendo cuentas...")
        contexts = []
        pages_map = {}

        for i, acc in enumerate(ACCOUNTS):
            ctx, page, ok = open_account(p, acc, i)
            contexts.append(ctx)
            if ok:
                pages_map[acc["username"]] = {"page": page, "account": acc}

        print(f"\n  {len(pages_map)}/{len(ACCOUNTS)} cuentas activas")

        if mode == "abrir":
            print("\nCuentas abiertas. Pulsa Enter para cerrar.")
            input()

        elif mode == "buscar":
            # 2 - Buscar leads usando una ventana del navegador
            nicho = sys.argv[2] if len(sys.argv) > 2 else "peluquerias"
            ciudad = sys.argv[3] if len(sys.argv) > 3 else "Malaga"
            # Usar la primera cuenta disponible para buscar
            first_page = list(pages_map.values())[0]["page"] if pages_map else None
            if first_page:
                search_and_find_instagram(first_page, nicho, ciudad)
            else:
                print("No hay cuentas activas para buscar")
            print("\nBusqueda completa. Pulsa Enter para cerrar.")
            input()

        elif mode == "enviar":
            # 3 - Enviar DMs con CRM + Brain
            import_leads_from_json()  # Sync JSON → CRM
            leads = get_leads_to_contact(limit=100)
            if not leads:
                print("\nNo hay leads pendientes. Busca primero.")
            else:
                print(f"\n[FASE 2] {len(leads)} leads en CRM pendientes")
                active = list(pages_map.keys())
                sent_total = 0

                for lead in leads:
                    # Elegir cuenta con menos DMs hoy
                    acc_name = min(active, key=lambda a: get_dms_sent_today(a))
                    if get_dms_sent_today(acc_name) >= MAX_DMS_PER_ACCOUNT_PER_DAY:
                        print("  Todas las cuentas al limite diario")
                        break

                    page = pages_map[acc_name]["page"]
                    msg = generate_dm(lead)

                    print(f"\n  @{acc_name} -> @{lead['instagram']}")
                    print(f"  MSG: {msg[:80]}...")

                    ok, status = send_dm(page, lead["instagram"], msg)
                    if ok:
                        log_message(lead["id"], acc_name, msg)
                        sent_total += 1
                    else:
                        update_lead_status(lead["id"], "rejected")

                    pause = random.randint(30, 90)
                    print(f"  Pausa {pause}s...")
                    time.sleep(pause)

                print(f"\n  TOTAL ENVIADOS: {sent_total}")

            # Stats
            stats = get_pipeline_stats()
            print(f"\n  CRM: {stats}")
            print("\nPulsa Enter para cerrar.")
            input()

        elif mode == "auto":
            # 4 - Buscar en Costa del Sol + enviar
            first_page = list(pages_map.values())[0]["page"] if pages_map else None
            if first_page:
                for ciudad in CIUDADES_COSTA_SOL[:3]:  # 3 ciudades
                    for nicho in NICHOS[:2]:  # 2 nichos
                        print(f"\n>>> {nicho} en {ciudad}...")
                        search_and_find_instagram(first_page, nicho, ciudad)
                        time.sleep(2)

                import_leads_from_json()
                # Enviar
                leads = get_leads_to_contact(limit=50)
                active = list(pages_map.keys())
                for lead in leads:
                    acc_name = min(active, key=lambda a: get_dms_sent_today(a))
                    if get_dms_sent_today(acc_name) >= MAX_DMS_PER_ACCOUNT_PER_DAY:
                        break
                    page = pages_map[acc_name]["page"]
                    msg = generate_dm(lead)
                    ok, _ = send_dm(page, lead["instagram"], msg)
                    if ok:
                        log_message(lead["id"], acc_name, msg)
                    time.sleep(random.randint(30, 90))

            stats = get_pipeline_stats()
            print(f"\n  CRM: {stats}")
            print("\nPulsa Enter para cerrar.")
            input()

        # Cerrar
        for ctx in contexts:
            try:
                ctx.close()
            except:
                pass
