"""
Google Maps Ghost Scraper — Sistema 180
Usa Ghost Mouse para navegar Google Maps como un humano y extraer:
- Nombre del negocio
- Teléfono
- Email (si aparece)
- Web
- Dirección
- Categoría

10x más rápido que el scraper HTTP porque Google NO bloquea un navegador real.

Uso:
  python gmaps_ghost_scraper.py "peluqueria" "Malaga"
  python gmaps_ghost_scraper.py "restaurante" "Torremolinos"  
  python gmaps_ghost_scraper.py auto   # Todos los nichos automáticos
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
from human_cursor import move_mouse, human_click, human_type, human_scroll

DB = os.path.join(os.path.dirname(__file__), "crm.db")
PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
GMAPS_PROFILE = os.path.join(PROFILES_DIR, "gmaps_scraper")
os.makedirs(GMAPS_PROFILE, exist_ok=True)

NICHOS = [
    "peluqueria", "barberia", "centro estetica",
    "restaurante", "cafeteria", "bar",
    "clinica dental", "dentista",
    "gimnasio", "crossfit", "yoga",
    "fisioterapeuta", "psicologo", "nutricionista",
    "veterinario", "clinica veterinaria",
    "inmobiliaria", "abogado", "asesoria fiscal",
    "taller mecanico", "autoescuela",
    "optica", "farmacia", "florista",
    "fotografo", "tienda ropa", "joyeria",
    "academia idiomas", "reformas",
]

CIUDADES = [
    "Malaga", "Torremolinos", "Benalmadena", "Fuengirola",
    "Marbella", "Mijas", "Nerja", "Estepona",
    "Velez-Malaga", "Rincon de la Victoria",
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
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS emails_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            subject TEXT,
            template TEXT,
            sent_at TEXT
        )
    """)
    conn.commit()
    conn.close()


async def human_delay(min_s=1, max_s=3):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def scrape_google_maps(page, nicho, ciudad, max_results=20):
    """Search Google Maps and extract business data."""
    query = "{} en {}".format(nicho, ciudad)
    url = "https://www.google.com/maps/search/{}".format(query.replace(" ", "+"))
    
    await page.goto(url, wait_until="domcontentloaded")
    await human_delay(3, 5)
    
    # Accept cookies if prompted
    try:
        accept = page.locator('button:has-text("Aceptar todo"), button:has-text("Accept all")')
        if await accept.count() > 0:
            abox = await accept.first.bounding_box()
            if abox:
                await human_click(page, abox["x"]+abox["width"]/2, abox["y"]+abox["height"]/2)
                await human_delay(2, 3)
    except:
        pass
    
    businesses = []
    seen_names = set()
    
    # Scroll through results panel
    results_panel = page.locator('div[role="feed"], div.m6QErb')
    
    for scroll_round in range(5):  # 5 rounds of scrolling
        # Get visible business cards
        cards = page.locator('div.Nv2PK, a.hfpxzc')
        count = await cards.count()
        
        for i in range(count):
            if len(businesses) >= max_results:
                break
            
            try:
                card = cards.nth(i)
                # Click on the business card
                box = await card.bounding_box()
                if not box or box["y"] < 0 or box["y"] > 800:
                    continue
                
                await human_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                await human_delay(2, 4)
                
                # Extract business info from detail panel
                biz = await extract_business_info(page)
                
                if biz and biz["nombre"] not in seen_names:
                    biz["nicho"] = nicho
                    biz["ciudad"] = ciudad
                    seen_names.add(biz["nombre"])
                    businesses.append(biz)
                    print("    [{}] {} | {} | {}".format(
                        len(businesses), biz["nombre"],
                        biz.get("telefono", "sin tel"),
                        biz.get("email", biz.get("web", "sin web"))
                    ))
                
                # Go back to results
                back_btn = page.locator('button[aria-label*="Atrás"], button[aria-label*="Back"]')
                if await back_btn.count() > 0:
                    bbox = await back_btn.first.bounding_box()
                    if bbox:
                        await human_click(page, bbox["x"]+bbox["width"]/2, bbox["y"]+bbox["height"]/2)
                        await human_delay(1, 2)
                
            except Exception as e:
                continue
        
        if len(businesses) >= max_results:
            break
        
        # Scroll down in results
        if await results_panel.count() > 0:
            rbox = await results_panel.first.bounding_box()
            if rbox:
                await page.mouse.move(rbox["x"] + rbox["width"]/2, rbox["y"] + rbox["height"]/2)
                await human_scroll(page, "down", 400)
                await human_delay(2, 3)
    
    return businesses


async def extract_business_info(page):
    """Extract business information from the detail panel."""
    biz = {"nombre": "", "telefono": "", "email": "", "web": "", "direccion": ""}
    
    try:
        # Name
        name_el = page.locator('h1.DUwDvf, h1.fontHeadlineLarge').first
        if await name_el.count() > 0:
            biz["nombre"] = (await name_el.text_content()).strip()
        
        if not biz["nombre"]:
            return None
        
        # Get all info items (phone, website, address)
        info_items = page.locator('button[data-item-id], a[data-item-id]')
        count = await info_items.count()
        
        for i in range(count):
            item = info_items.nth(i)
            data_id = await item.get_attribute("data-item-id") or ""
            aria = await item.get_attribute("aria-label") or ""
            text = await item.text_content() or ""
            
            # Phone
            if "phone" in data_id or "teléfono" in aria.lower() or "phone" in aria.lower():
                phone = re.sub(r'[^\d+]', '', text)
                if len(phone) >= 9:
                    biz["telefono"] = phone
            
            # Website  
            elif "authority" in data_id or "sitio" in aria.lower() or "website" in aria.lower():
                href = await item.get_attribute("href") or text
                if "http" in href or "www" in href or "." in text:
                    biz["web"] = href if "http" in href else text.strip()
            
            # Address
            elif "address" in data_id or "dirección" in aria.lower():
                biz["direccion"] = text.strip()
        
        # Try to find email in the page content  
        page_text = await page.content()
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', page_text)
        for email in emails:
            email = email.lower()
            if not any(skip in email for skip in ["google", "gstatic", "schema", "example", "w3"]):
                if len(email) > 5 and len(email) < 60:
                    biz["email"] = email
                    break
        
        # If no email found but has website, we can potentially scrape it later
        if not biz["email"] and biz["web"]:
            biz["email"] = ""  # Will try to get from website
        
    except Exception as e:
        pass
    
    return biz if biz["nombre"] else None


def save_businesses(businesses):
    """Save discovered businesses to CRM."""
    conn = sqlite3.connect(DB)
    new_count = 0
    
    for biz in businesses:
        # Use email if available, otherwise create from phone/name
        email = biz.get("email", "")
        if not email and biz.get("telefono"):
            # Placeholder for phone-only leads
            email = "tel_{}@phone.lead".format(biz["telefono"])
        elif not email and biz.get("web"):
            email = "web_{}@web.lead".format(
                biz["web"].replace("https://", "").replace("http://", "").replace("/", "_")[:30]
            )
        
        if not email:
            continue
        
        try:
            conn.execute("""
                INSERT OR IGNORE INTO leads 
                (email, nombre, nicho, ciudad, telefono, web, source, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'gmaps_ghost', 'nuevo', ?)
            """, (
                email, biz["nombre"], biz.get("nicho", ""),
                biz.get("ciudad", ""), biz.get("telefono", ""),
                biz.get("web", ""), datetime.now().isoformat()
            ))
            new_count += 1
        except:
            pass
    
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    conn.close()
    return new_count, total


async def main():
    init_db()
    
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        nichos = NICHOS
        ciudades = CIUDADES[:5]  # First 5 cities
    else:
        nichos = [sys.argv[1]] if len(sys.argv) > 1 else ["peluqueria"]
        ciudades = [sys.argv[2]] if len(sys.argv) > 2 else ["Malaga"]
    
    print("=" * 60)
    print("  GOOGLE MAPS GHOST SCRAPER")
    print("  {} nichos × {} ciudades".format(len(nichos), len(ciudades)))
    print("=" * 60)
    
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=GMAPS_PROFILE,
        channel="msedge",
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--window-position=50,30",
            "--window-size=1300,900",
        ],
        viewport={"width": 1280, "height": 850},
        locale="es-ES",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        ignore_https_errors=True,
    )
    
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
    
    total_found = 0
    
    try:
        for ciudad in ciudades:
            for nicho in nichos:
                print("\n  >>> {} en {} ...".format(nicho, ciudad))
                businesses = await scrape_google_maps(page, nicho, ciudad, max_results=10)
                
                if businesses:
                    new, total = save_businesses(businesses)
                    total_found += len(businesses)
                    print("  → {} negocios (total DB: {})".format(len(businesses), total))
                
                await human_delay(5, 10)
        
        print("\n" + "=" * 60)
        print("  RESULTADO FINAL")
        conn = sqlite3.connect(DB)
        total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        nuevos = conn.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE email NOT IN (SELECT email FROM emails_sent)
        """).fetchone()[0]
        conn.close()
        print("  Encontrados hoy: {}".format(total_found))
        print("  Total en DB: {}".format(total))
        print("  Nuevos sin contactar: {}".format(nuevos))
        print("=" * 60)
        
        print("\n  Pulsa Enter para cerrar...")
        input()
    
    finally:
        await ctx.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
