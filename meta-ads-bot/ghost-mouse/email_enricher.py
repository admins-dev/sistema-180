"""
Sistema 180 - TURBO Scraper v5.0
Estrategia que FUNCIONA: busca webs de negocios via Google, luego
20 hilos paralelos extraen emails de esas webs.
Sin navegador excepto para la busqueda inicial.
"""
import requests
import re
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT = os.path.join(os.path.dirname(__file__), "emails_leads_massive.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

requests.packages.urllib3.disable_warnings()

QUERIES = [
    # Malaga
    "peluqueria malaga", "restaurante malaga", "clinica dental malaga",
    "gimnasio malaga", "abogado malaga", "barberia malaga",
    "fisioterapia malaga", "veterinario malaga", "inmobiliaria malaga",
    "optica malaga", "clinica estetica malaga", "nutricionista malaga",
    # Marbella
    "peluqueria marbella", "restaurante marbella", "clinica dental marbella",
    "gimnasio marbella", "abogado marbella",
    # Fuengirola
    "peluqueria fuengirola", "restaurante fuengirola",
    # Sevilla
    "peluqueria sevilla", "restaurante sevilla", "clinica dental sevilla",
    "gimnasio sevilla", "abogado sevilla",
    # Granada
    "peluqueria granada", "restaurante granada", "abogado granada",
    # Cordoba
    "peluqueria cordoba", "restaurante cordoba",
]


def extract_emails(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found = re.findall(pattern, text)
    bad = ["example", "test.", "sentry", "w3.org", "schema.org", "wix",
           "googleapis", "noreply", "no-reply", "wordpress", "jquery",
           "cloudflare", "bootstrap", "fontawesome", "gravatar",
           "gstatic", "facebook", "twitter", "instagram", "google",
           "apple.com", "microsoft", "mozilla", "github"]
    return list(set([e.lower() for e in found if not any(b in e.lower() for b in bad)]))


def scrape_single_website(url):
    """Visita una web y extrae emails. Rapido, sin navegador."""
    if not url:
        return []
    try:
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        r = s.get(url, timeout=6, allow_redirects=True, verify=False)
        emails = extract_emails(r.text[:15000])

        # Intentar pagina de contacto si no hay emails
        if not emails:
            base = url.rstrip("/")
            for suffix in ["/contacto", "/contact", "/contacta", "/about", "/sobre-nosotros"]:
                try:
                    r2 = s.get(base + suffix, timeout=4, verify=False)
                    if r2.status_code == 200:
                        emails = extract_emails(r2.text[:8000])
                        if emails:
                            break
                except:
                    pass
        return emails
    except:
        return []


def scrape_url_for_lead(args):
    """Worker thread: visita URL y extrae email."""
    url, name, nicho, ciudad = args
    emails = scrape_single_website(url)
    if emails:
        return {
            "nombre": name,
            "email": emails[0],
            "website": url,
            "nicho": nicho,
            "ciudad": ciudad,
            "fuente": "web_scrape",
            "enviado": False,
        }
    return None


def collect_urls_from_existing():
    """Recolecta URLs de negocios que ya tenemos pero sin email."""
    existing = []
    if os.path.exists(OUTPUT):
        try:
            existing = json.load(open(OUTPUT, "r", encoding="utf-8"))
        except:
            pass

    urls = []
    for l in existing:
        if l.get("website") and not l.get("email"):
            urls.append((l["website"], l.get("nombre", ""), l.get("nicho", ""), l.get("ciudad", "")))
    return urls, existing


def main():
    print("=" * 60)
    print("  TURBO SCRAPER v5.0 — ENRIQUECIMIENTO PARALELO")
    print("  20 hilos, visita webs de negocios para extraer emails")
    print("=" * 60)

    urls_to_scrape, existing = collect_urls_from_existing()
    print("\n  Negocios con web pero sin email: {}".format(len(urls_to_scrape)))

    if not urls_to_scrape:
        print("  No hay webs para enriquecer. Cargando del Maps scraper anterior...")
        # Reimportar resultados del Maps scraper
        try:
            existing = json.load(open(OUTPUT, "r", encoding="utf-8"))
            urls_to_scrape = [(l["website"], l.get("nombre", ""), l.get("nicho", ""), l.get("ciudad", ""))
                              for l in existing if l.get("website") and not l.get("email")]
        except:
            urls_to_scrape = []

    if not urls_to_scrape:
        print("  Sin URLs. Ejecuta primero el scraper de Google Maps.")
        return

    # Scrape en paralelo con 20 hilos
    print("  Lanzando 20 hilos paralelos...")
    new_leads = []

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [pool.submit(scrape_url_for_lead, args) for args in urls_to_scrape]
        done = 0
        for f in as_completed(futures):
            done += 1
            result = f.result()
            if result:
                new_leads.append(result)
                print("    [{}] {} -> {}".format(len(new_leads), result["nombre"][:30], result["email"]))
            if done % 20 == 0:
                print("    ... {}/{} procesados".format(done, len(urls_to_scrape)))

    # Enriquecer los existentes
    email_map = {l["website"]: l["email"] for l in new_leads if l.get("website")}
    for lead in existing:
        if lead.get("website") in email_map and not lead.get("email"):
            lead["email"] = email_map[lead["website"]]

    # Guardar
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    # CRM
    try:
        from email_crm import add_leads_bulk
        add_leads_bulk([l for l in existing if l.get("email")])
    except:
        pass

    total_email = len([l for l in existing if l.get("email")])
    print("\n" + "=" * 60)
    print("  RESULTADO: {} emails nuevos | {} total con email".format(len(new_leads), total_email))
    print("=" * 60)


if __name__ == "__main__":
    main()
