"""
Ghost Mouse — Lead Finder v2.
Busca negocios con Instagram usando Perplexity + scraping directo.
No necesita Google Maps API.
"""
import requests
import json
import os
import re
import time

LEADS_FILE = os.path.join(os.path.dirname(__file__), "leads.json")


def search_google_maps_browser(page, query, city):
    """Buscar negocios directamente en Google Maps via navegador."""
    print(f"\n[BUSCANDO] '{query}' en {city} via Google Maps...")
    
    search_term = f"{query} en {city}"
    page.goto(f"https://www.google.com/maps/search/{search_term}", wait_until="domcontentloaded")
    time.sleep(5)
    
    # Aceptar cookies de Google
    try:
        page.click('button:has-text("Aceptar todo")', timeout=3000)
        time.sleep(2)
    except:
        pass
    
    # Scroll para cargar mas resultados
    sidebar = page.locator('[role="feed"]')
    if sidebar.count() > 0:
        for _ in range(5):
            sidebar.first.evaluate('el => el.scrollTop = el.scrollHeight')
            time.sleep(2)
    
    # Extraer negocios
    items = page.locator('a[href*="/maps/place/"]').all()
    businesses = []
    seen = set()
    
    for item in items:
        try:
            name = item.get_attribute("aria-label") or ""
            href = item.get_attribute("href") or ""
            if name and name not in seen:
                seen.add(name)
                businesses.append({
                    "name": name,
                    "maps_url": href,
                    "query": query,
                    "location": city,
                    "instagram": None,
                    "website": None,
                    "dm_sent": False,
                    "dm_account": None,
                    "dm_date": None,
                })
        except:
            continue
    
    print(f"  {len(businesses)} negocios encontrados")
    return businesses


def find_instagram_via_google(page, business_name, city):
    """Buscar Instagram de un negocio via Google Search."""
    query = f'"{business_name}" {city} instagram.com'
    page.goto(f"https://www.google.com/search?q={query}", wait_until="domcontentloaded")
    time.sleep(2)
    
    # Buscar links de instagram en resultados
    links = page.locator('a[href*="instagram.com/"]').all()
    for link in links:
        href = link.get_attribute("href") or ""
        match = re.search(r'instagram\.com/([a-zA-Z0-9_.]+)', href)
        if match:
            username = match.group(1)
            if username not in ["explore", "accounts", "p", "reel", "stories", "direct", ""]:
                return username
    return None


def search_and_find_instagram(page, query, city, max_businesses=20):
    """Pipeline completo: buscar negocios + encontrar su Instagram."""
    # 1. Buscar negocios en Google Maps
    businesses = search_google_maps_browser(page, query, city)
    
    # 2. Buscar Instagram de cada uno
    print(f"\n[BUSCANDO INSTAGRAM] para {len(businesses[:max_businesses])} negocios...")
    found = 0
    
    for i, biz in enumerate(businesses[:max_businesses]):
        ig = find_instagram_via_google(page, biz["name"], city)
        if ig:
            biz["instagram"] = ig
            found += 1
            print(f"  [{i+1}] {biz['name']} -> @{ig}")
        else:
            print(f"  [{i+1}] {biz['name']} -> (sin IG)")
        
        time.sleep(1)  # No spamear Google
    
    print(f"\n  {found}/{len(businesses[:max_businesses])} con Instagram")
    
    # 3. Guardar
    save_leads(businesses)
    return businesses


def save_leads(leads):
    """Guardar leads a disco."""
    existing = load_leads()
    existing_names = {l["name"] for l in existing}
    new_leads = [l for l in leads if l["name"] not in existing_names]
    all_leads = existing + new_leads
    
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_leads, f, ensure_ascii=False, indent=2)
    
    print(f"  {len(new_leads)} nuevos ({len(all_leads)} total)")
    return all_leads


def load_leads():
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_unsent_leads():
    leads = load_leads()
    return [l for l in leads if not l.get("dm_sent") and l.get("instagram")]
