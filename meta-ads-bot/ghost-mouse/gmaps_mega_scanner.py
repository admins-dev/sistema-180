# -*- coding: utf-8 -*-
"""
SISTEMA 180 — GHOST MOUSE MEGA SCANNER v5.0
============================================
Escanea TODA la Costa del Sol. Abre pestanas como un LOCO.
Para cada negocio:
  1. Click en Google Maps -> Lee nombre, estrellas, resenas, telefono, web, direccion
  2. Si tiene WEB -> Abre nueva pestana -> Escanea la web ENTERA (emails, duenos, redes sociales)
  3. Gemini AI analiza dolores y genera dossier personalizado
  4. Guarda TODO en crm.db + archivos JSON de dossier

Uso:
  python gmaps_mega_scanner.py
"""
import asyncio
import os
import sys
import re
import random
import sqlite3
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DB = os.path.join(os.path.dirname(__file__), "crm.db")
DOSSIER_DIR = os.path.join(os.path.dirname(__file__), "dossiers")
os.makedirs(DOSSIER_DIR, exist_ok=True)

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
GMAPS_PROFILE = os.path.join(PROFILES_DIR, "gmaps_mega")
os.makedirs(GMAPS_PROFILE, exist_ok=True)

# Gemini AI Brain
try:
    from google import genai
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    ai = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
except:
    ai = None

# ==========================================================
# TODOS LOS NICHOS x TODA LA COSTA DEL SOL
# ==========================================================
NICHOS = [
    "peluqueria", "barberia", "centro de estetica", "salon de belleza",
    "restaurante", "cafeteria", "bar", "pizzeria", "comida rapida",
    "clinica dental", "dentista", "ortodoncista",
    "gimnasio", "crossfit", "yoga", "pilates",
    "fisioterapeuta", "psicologo", "nutricionista", "podologa",
    "veterinario", "clinica veterinaria",
    "inmobiliaria", "agencia inmobiliaria",
    "abogado", "abogado divorcios", "asesoria fiscal", "gestoria",
    "taller mecanico", "taller coches", "autoescuela",
    "optica", "farmacia", "florista", "floristeria",
    "fotografo", "estudio fotografico",
    "tienda ropa", "boutique", "joyeria", "relojeria",
    "academia idiomas", "academia ingles",
    "reformas", "empresa reformas", "interiorismo",
    "cerrajero", "electricista", "fontanero", "pintor",
    "hotel", "hostal", "apartamentos turisticos",
    "agencia de viajes", "wedding planner",
    "clinica estetica", "cirugia estetica",
    "lavanderia", "tintoreria",
    "guarderia", "escuela infantil",
    "centro de formacion", "clases particulares",
]

CIUDADES_COSTA_DEL_SOL = [
    "Malaga", "Torremolinos", "Benalmadena", "Fuengirola",
    "Mijas", "Marbella", "San Pedro de Alcantara", "Estepona",
    "Manilva", "Casares", "Nerja", "Rincon de la Victoria",
    "Velez-Malaga", "Torre del Mar", "Alhaurin de la Torre",
    "Alhaurin el Grande", "Coin", "Cartama", "Antequera",
    "Ronda", "Torremolinos", "Benalmadena Costa",
]


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            email TEXT PRIMARY KEY,
            nombre TEXT,
            nicho TEXT,
            ciudad TEXT,
            telefono TEXT,
            instagram TEXT,
            web TEXT,
            source TEXT,
            status TEXT DEFAULT 'nuevo',
            created_at TEXT,
            emailed INTEGER DEFAULT 0,
            estrellas REAL,
            num_resenas INTEGER,
            direccion TEXT,
            dueno TEXT,
            dolores TEXT,
            dossier_path TEXT
        )
    """)
    conn.commit()
    conn.close()


# ==========================================================
# VELOCIDAD x1000 — DELAYS MINIMOS
# ==========================================================
async def turbo_delay():
    """Delay casi nulo para velocidad maxima."""
    await asyncio.sleep(random.uniform(0.05, 0.15))


async def mini_delay():
    """Delay minimo para cargas de pagina."""
    await asyncio.sleep(random.uniform(0.2, 0.5))


# ==========================================================
# EXTRACTOR PROFUNDO DE GOOGLE MAPS
# ==========================================================
async def extract_deep_info(page):
    """Extrae ABSOLUTAMENTE TODO de la ficha de Google Maps."""
    biz = {
        "nombre": "", "telefono": "", "email": "", "web": "",
        "direccion": "", "estrellas": 0, "num_resenas": 0,
        "horario": "", "categoria": "", "dueno": "",
        "fotos_count": 0, "redes_sociales": [],
    }

    try:
        # NOMBRE
        name_el = page.locator('h1.DUwDvf, h1.fontHeadlineLarge').first
        if await name_el.count() > 0:
            biz["nombre"] = (await name_el.text_content()).strip()
        if not biz["nombre"]:
            return None

        # ESTRELLAS Y RESENAS
        try:
            rating_el = page.locator('div.F7nice span[aria-hidden="true"]').first
            if await rating_el.count() > 0:
                txt = await rating_el.text_content()
                biz["estrellas"] = float(txt.replace(",", "."))
        except:
            pass

        try:
            reviews_el = page.locator('div.F7nice span[aria-label*="reseñ"], div.F7nice span[aria-label*="review"]').first
            if await reviews_el.count() > 0:
                rtxt = await reviews_el.get_attribute("aria-label") or ""
                nums = re.findall(r'[\d.]+', rtxt.replace(".", "").replace(",", ""))
                if nums:
                    biz["num_resenas"] = int(nums[0])
        except:
            pass

        # CATEGORIA
        try:
            cat_el = page.locator('button[jsaction*="category"]').first
            if await cat_el.count() > 0:
                biz["categoria"] = (await cat_el.text_content()).strip()
        except:
            pass

        # DATOS DE CONTACTO (telefono, web, direccion)
        info_items = page.locator('button[data-item-id], a[data-item-id]')
        count = await info_items.count()

        for i in range(count):
            item = info_items.nth(i)
            data_id = await item.get_attribute("data-item-id") or ""
            aria = await item.get_attribute("aria-label") or ""
            text = await item.text_content() or ""

            if "phone" in data_id or "telefono" in aria.lower():
                phone = re.sub(r'[^\d+]', '', text)
                if len(phone) >= 9:
                    biz["telefono"] = phone
            elif "authority" in data_id or "sitio" in aria.lower() or "website" in aria.lower():
                href = await item.get_attribute("href") or text
                if "http" in str(href) or "www" in str(href) or "." in text:
                    biz["web"] = href if "http" in str(href) else text.strip()
            elif "address" in data_id or "direccion" in aria.lower():
                biz["direccion"] = text.strip()

        # BUSCAR EMAILS EN EL HTML DE MAPS
        page_html = await page.content()
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', page_html)
        for email in emails:
            email = email.lower()
            if not any(skip in email for skip in ["google", "gstatic", "schema", "example", "w3", "googleapis"]):
                if 5 < len(email) < 60:
                    biz["email"] = email
                    break

    except Exception as e:
        pass

    return biz if biz["nombre"] else None


# ==========================================================
# ESCANEAR WEB DEL NEGOCIO (NUEVA PESTANA)
# ==========================================================
async def scan_business_website(context, web_url, biz):
    """Abre la WEB del negocio en nueva pestana y extrae TODA la info."""
    extra = {"emails": [], "phones": [], "social": [], "owner_hints": []}

    if not web_url or "google" in web_url:
        return extra

    # Limpiar URL
    if not web_url.startswith("http"):
        web_url = "https://" + web_url

    try:
        new_tab = await context.new_page()
        print(f"      [TAB+] Abriendo web: {web_url[:60]}...")

        await new_tab.goto(web_url, wait_until="domcontentloaded", timeout=8000)
        await mini_delay()

        html = await new_tab.content()
        text = await new_tab.evaluate("document.body ? document.body.innerText : ''")

        # EMAILS en la web
        found_emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', html)
        for e in found_emails:
            e = e.lower()
            if not any(skip in e for skip in ["google", "facebook", "twitter", "schema", "example", "wix", "wordpress", "sentry"]):
                if 5 < len(e) < 60 and e not in extra["emails"]:
                    extra["emails"].append(e)

        # TELEFONOS en la web
        found_phones = re.findall(r'(?:\+34\s?)?(?:6|7|8|9)\d{2}[\s.-]?\d{3}[\s.-]?\d{3}', text)
        for p in found_phones:
            clean = re.sub(r'[\s.-]', '', p)
            if len(clean) >= 9 and clean not in extra["phones"]:
                extra["phones"].append(clean)

        # REDES SOCIALES
        social_patterns = [
            (r'(?:instagram\.com|instagr\.am)/[\w.]+', "instagram"),
            (r'(?:facebook\.com|fb\.com)/[\w.]+', "facebook"),
            (r'(?:twitter\.com|x\.com)/[\w]+', "twitter"),
            (r'(?:tiktok\.com)/@[\w.]+', "tiktok"),
            (r'(?:linkedin\.com)/(?:in|company)/[\w-]+', "linkedin"),
            (r'(?:youtube\.com)/(?:c/|channel/|@)[\w-]+', "youtube"),
        ]
        for pattern, platform in social_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for m in matches:
                link = f"https://{m}" if not m.startswith("http") else m
                extra["social"].append({"platform": platform, "url": link})

        # NOMBRES DE DUENOS (heuristico)
        owner_patterns = [
            r'(?:fundad[oa]|CEO|director|propietari[oa]|gerente)\s*[:\-]?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:Sobre\s+(?:mi|nosotros)).*?([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ]
        for pat in owner_patterns:
            matches = re.findall(pat, text)
            for m in matches:
                if len(m) > 4 and m not in extra["owner_hints"]:
                    extra["owner_hints"].append(m)

        print(f"      [TAB-] Cerrada. Emails:{len(extra['emails'])} Tels:{len(extra['phones'])} Social:{len(extra['social'])} Duenos:{len(extra['owner_hints'])}")
        await new_tab.close()

    except Exception as e:
        print(f"      [TAB!] Error en web: {str(e)[:50]}")
        try:
            await new_tab.close()
        except:
            pass

    return extra


# ==========================================================
# GEMINI AI — ANALISIS DE DOLORES (BELTRAN BRIONES LOGIC)
# ==========================================================
def ai_analyze_pain(biz, web_data):
    """Gemini analiza el dossier completo y genera los dolores del negocio."""
    if not ai:
        return "Sin IA disponible"

    prompt = f"""
    Eres Beltran Briones, el mejor analista de negocios locales de Espana.
    Analiza este negocio y dame un INFORME DE DOLORES ultra-preciso en 5 lineas:

    NEGOCIO: {biz['nombre']}
    CATEGORIA: {biz.get('categoria', biz.get('nicho', '?'))}
    CIUDAD: {biz.get('ciudad', '?')}
    ESTRELLAS: {biz.get('estrellas', '?')} / 5
    RESENAS: {biz.get('num_resenas', '?')}
    TELEFONO: {biz.get('telefono', 'NO TIENE')}
    WEB: {biz.get('web', 'NO TIENE')}
    EMAIL: {biz.get('email', 'NO TIENE')}
    REDES SOCIALES: {len(web_data.get('social', []))} perfiles
    DUENO DETECTADO: {', '.join(web_data.get('owner_hints', ['No detectado']))}

    Reglas:
    - Si NO tiene web: dolor CRITICO (pierde 10+ clientes/dia)
    - Si tiene web pero no email visible: dolor ALTO (no captura leads)
    - Si tiene pocas resenas (<20): dolor MEDIO (poca prueba social)
    - Si tiene pocas estrellas (<4): dolor ALTO (reputacion)
    - Si no tiene redes sociales: dolor MEDIO
    - Calcula cuanto dinero pierde al mes EN EUROS con estos dolores

    Responde SOLO con el analisis. Nada mas. Sin saludos ni meta-texto.
    """
    try:
        res = ai.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return res.text.strip()
    except Exception as e:
        return f"Error IA: {e}"


# ==========================================================
# GUARDAR DOSSIER COMPLETO
# ==========================================================
def save_dossier(biz, web_data, dolores):
    """Guarda un archivo JSON completo con toda la inteligencia del negocio."""
    safe_name = re.sub(r'[^\w\s-]', '', biz["nombre"])[:40].strip().replace(" ", "_")
    filename = f"{safe_name}_{biz.get('ciudad', 'unknown')}.json"
    filepath = os.path.join(DOSSIER_DIR, filename)

    dossier = {
        "negocio": biz,
        "web_scan": web_data,
        "analisis_dolores": dolores,
        "generado_en": datetime.now().isoformat(),
        "sistema": "Sistema 180 — MegaScanner v5.0"
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(dossier, f, ensure_ascii=False, indent=2)

    return filepath


def save_to_crm(biz, web_data, dolores, dossier_path):
    """Guarda el lead completo en la base de datos CRM."""
    conn = sqlite3.connect(DB)

    email = biz.get("email", "")
    if not email and web_data.get("emails"):
        email = web_data["emails"][0]
    if not email and biz.get("telefono"):
        email = f"tel_{biz['telefono']}@phone.lead"
    if not email:
        email = f"noemail_{re.sub(r'[^a-z0-9]', '', biz['nombre'].lower()[:20])}@scan.lead"

    dueno = ", ".join(web_data.get("owner_hints", []))

    try:
        conn.execute("""
            INSERT OR REPLACE INTO leads
            (email, nombre, nicho, ciudad, telefono, web, source, status, created_at,
             emailed, estrellas, num_resenas, direccion, dueno, dolores, dossier_path)
            VALUES (?, ?, ?, ?, ?, ?, 'mega_scanner_v5', 'nuevo', ?, 0, ?, ?, ?, ?, ?, ?)
        """, (
            email, biz["nombre"], biz.get("nicho", biz.get("categoria", "")),
            biz.get("ciudad", ""), biz.get("telefono", ""),
            biz.get("web", ""), datetime.now().isoformat(),
            biz.get("estrellas", 0), biz.get("num_resenas", 0),
            biz.get("direccion", ""), dueno, dolores, dossier_path
        ))
        conn.commit()
    except Exception as e:
        print(f"      [DB ERROR] {e}")

    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    conn.close()
    return total


# ==========================================================
# MOTOR PRINCIPAL — MEGA SCAN
# ==========================================================
async def mega_scan(page, context, nicho, ciudad, max_results=30):
    """Escanea un nicho+ciudad a velocidad MAXIMA con pestanas multiples."""
    query = f"{nicho} en {ciudad}"
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

    await page.goto(url, wait_until="domcontentloaded")
    await mini_delay()

    # Aceptar cookies
    try:
        accept = page.locator('button:has-text("Aceptar todo"), button:has-text("Accept all")')
        if await accept.count() > 0:
            await accept.first.click()
            await turbo_delay()
    except:
        pass

    businesses = []
    seen = set()
    results_panel = page.locator('div[role="feed"], div.m6QErb')

    for scroll_round in range(8):
        cards = page.locator('div.Nv2PK, a.hfpxzc')
        count = await cards.count()

        for i in range(count):
            if len(businesses) >= max_results:
                break

            try:
                card = cards.nth(i)
                box = await card.bounding_box()
                if not box or box["y"] < 0 or box["y"] > 900:
                    continue

                await card.click()
                await asyncio.sleep(0.3)

                # EXTRAER INFO PROFUNDA
                biz = await extract_deep_info(page)
                if not biz or biz["nombre"] in seen:
                    continue

                biz["nicho"] = nicho
                biz["ciudad"] = ciudad
                seen.add(biz["nombre"])

                print(f"    [{len(businesses)+1}] {biz['nombre']} | {biz.get('estrellas', '?')} estrellas | {biz.get('num_resenas', '?')} resenas | Tel:{biz.get('telefono', 'NO')} | Web:{bool(biz.get('web'))}")

                # SI TIENE WEB -> ABRIR NUEVA PESTANA Y ESCANEAR
                web_data = {"emails": [], "phones": [], "social": [], "owner_hints": []}
                if biz.get("web"):
                    web_data = await scan_business_website(context, biz["web"], biz)
                    if web_data["emails"] and not biz["email"]:
                        biz["email"] = web_data["emails"][0]

                # GEMINI AI ANALIZA DOLORES
                dolores = ai_analyze_pain(biz, web_data)
                print(f"      [IA] Dolores: {dolores[:80]}...")

                # GUARDAR DOSSIER
                dossier_path = save_dossier(biz, web_data, dolores)
                total_db = save_to_crm(biz, web_data, dolores, dossier_path)
                businesses.append(biz)
                print(f"      [DB] Guardado. Total en CRM: {total_db}")

                # VOLVER A RESULTADOS
                back = page.locator('button[aria-label*="Atras"], button[aria-label*="Back"]')
                if await back.count() > 0:
                    await back.first.click()
                    await turbo_delay()

            except Exception as e:
                continue

        if len(businesses) >= max_results:
            break

        # SCROLL PARA CARGAR MAS
        if await results_panel.count() > 0:
            rbox = await results_panel.first.bounding_box()
            if rbox:
                await page.mouse.move(rbox["x"] + rbox["width"]/2, rbox["y"] + rbox["height"]/2)
                await page.mouse.wheel(0, 600)
                await asyncio.sleep(0.3)

    return businesses


# ==========================================================
# MAIN
# ==========================================================
async def main():
    init_db()

    print("\n" + "=" * 70)
    print("  SISTEMA 180 — GHOST MOUSE MEGA SCANNER v5.0")
    print(f"  {len(NICHOS)} NICHOS x {len(CIUDADES_COSTA_DEL_SOL)} CIUDADES = {len(NICHOS)*len(CIUDADES_COSTA_DEL_SOL)} COMBINACIONES")
    print("  Velocidad: x1000 | IA: Gemini + Beltran Briones Logic")
    print("  Modo: ESCANEO TOTAL COSTA DEL SOL")
    print("=" * 70)

    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=GMAPS_PROFILE,
        channel="msedge",
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--window-position=20,20",
            "--window-size=1400,900",
        ],
        viewport={"width": 1380, "height": 860},
        locale="es-ES",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        ignore_https_errors=True,
    )

    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')

    total_scanned = 0
    start_time = time.time()

    try:
        for ciudad in CIUDADES_COSTA_DEL_SOL:
            for nicho in NICHOS:
                elapsed = time.time() - start_time
                rate = total_scanned / max(elapsed/60, 1)
                print(f"\n{'='*70}")
                print(f"  >>> {nicho.upper()} en {ciudad.upper()} | Total: {total_scanned} | Vel: {rate:.0f}/min")
                print(f"{'='*70}")

                businesses = await mega_scan(page, ctx, nicho, ciudad, max_results=20)
                total_scanned += len(businesses)

                await turbo_delay()

        # REPORTE FINAL
        conn = sqlite3.connect(DB)
        total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        con_email = conn.execute("SELECT COUNT(*) FROM leads WHERE email NOT LIKE '%@%.lead'").fetchone()[0]
        con_web = conn.execute("SELECT COUNT(*) FROM leads WHERE web IS NOT NULL AND web != ''").fetchone()[0]
        con_tel = conn.execute("SELECT COUNT(*) FROM leads WHERE telefono IS NOT NULL AND telefono != ''").fetchone()[0]
        conn.close()

        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        print("  RESULTADO FINAL — MEGA SCANNER v5.0")
        print(f"  Tiempo total: {elapsed/60:.1f} minutos")
        print(f"  Negocios escaneados hoy: {total_scanned}")
        print(f"  Total en CRM: {total}")
        print(f"  Con EMAIL real: {con_email}")
        print(f"  Con WEB: {con_web}")
        print(f"  Con TELEFONO: {con_tel}")
        print(f"  Dossiers generados: {len(os.listdir(DOSSIER_DIR))}")
        print("=" * 70)

        print("\n  Pulsa Enter para cerrar...")
        input()

    finally:
        await ctx.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
