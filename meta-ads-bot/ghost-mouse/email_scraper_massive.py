"""
Sistema 180 - TURBO Email Scraper v4.0
100x mas rapido: sin navegador, 20 hilos, scrapea directorios de empresas.
Fuentes: PaginasAmarillas.es, Cylex.es, InfoIsInfo.es + webs propias.
"""
import requests
import re
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus

OUTPUT = os.path.join(os.path.dirname(__file__), "emails_leads_massive.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9"})

NICHOS_PA = {
    "peluquerias": "peluquerias",
    "restaurantes": "restaurantes",
    "clinicas-dentales": "clinicas-dentales",
    "gimnasios": "gimnasios",
    "abogados": "abogados",
    "tiendas-de-ropa": "tiendas-de-ropa",
    "clinicas-de-estetica": "clinicas-esteticas",
    "fisioterapeutas": "fisioterapeutas",
    "veterinarios": "veterinarios",
    "inmobiliarias": "inmobiliarias",
    "talleres-mecanicos": "talleres-mecanicos",
    "barberias": "barberias",
    "opticas": "opticas",
    "nutricionistas": "nutricionistas",
    "psicologos": "psicologos",
    "academias-de-idiomas": "academias-de-idiomas",
    "autoescuelas": "autoescuelas",
    "cafeterias": "cafeterias",
    "panaderias": "panaderias",
    "floristerias": "floristerias",
}

CIUDADES = [
    "malaga", "marbella", "fuengirola", "torremolinos", "benalmadena",
    "estepona", "nerja", "velez-malaga", "ronda", "antequera",
    "sevilla", "granada", "cordoba", "cadiz", "almeria",
    "madrid", "barcelona", "valencia", "alicante", "murcia",
    "zaragoza", "bilbao", "salamanca", "valladolid", "palma-de-mallorca",
]


def extract_emails(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found = re.findall(pattern, text)
    bad = ["example", "test.", "sentry", "w3.org", "schema.org", "wix",
           "googleapis", "noreply", "no-reply", "wordpress", "jquery",
           "cloudflare", "bootstrap", "fontawesome", "gravatar",
           "gstatic", "facebook", "twitter", "instagram", "linkedin"]
    return list(set([e.lower() for e in found if not any(b in e.lower() for b in bad)]))


def extract_phones(text):
    patterns = [
        r'(?:\+34|0034)?\s*[6789]\d{2}[\s.-]?\d{3}[\s.-]?\d{3}',
        r'[6789]\d{2}\s?\d{3}\s?\d{3}',
    ]
    phones = []
    for p in patterns:
        phones.extend(re.findall(p, text))
    return list(set([re.sub(r'\s+', '', ph) for ph in phones]))


# ===================================================================
# FUENTE 1: PAGINAS AMARILLAS
# ===================================================================
def scrape_paginas_amarillas(nicho_slug, ciudad, page_num=1):
    """Scrapea paginasamarillas.es — tiene nombre, tel, web, direccion."""
    url = "https://www.paginasamarillas.es/search/{}/{}/all-ma/{}/d/".format(
        nicho_slug, ciudad, page_num)
    leads = []
    try:
        r = SESSION.get(url, timeout=10)
        if r.status_code != 200:
            return leads

        text = r.text
        # Extraer bloques de resultados
        blocks = re.findall(r'<div class="listado-item.*?</div>\s*</div>\s*</div>', text, re.DOTALL)
        if not blocks:
            blocks = [text]

        # Nombres
        names = re.findall(r'<span class="nombre"[^>]*>(.*?)</span>', text)
        # Telefonos
        tels = re.findall(r'data-track-click="phone"[^>]*>([^<]+)', text)
        # Webs
        webs = re.findall(r'href="(https?://(?!www\.paginasamarillas)[^"]+)"[^>]*class="[^"]*web', text)
        # Direcciones
        addrs = re.findall(r'<span class="direccion"[^>]*>(.*?)</span>', text, re.DOTALL)

        for i in range(max(len(names), len(tels))):
            name = names[i].strip() if i < len(names) else ""
            tel = tels[i].strip() if i < len(tels) else ""
            web = webs[i].strip() if i < len(webs) else ""
            addr = re.sub(r'<[^>]+>', '', addrs[i]).strip() if i < len(addrs) else ""

            if name:
                leads.append({
                    "nombre": name,
                    "telefono": tel,
                    "website": web,
                    "address": addr,
                    "nicho": nicho_slug,
                    "ciudad": ciudad,
                    "fuente": "paginas_amarillas",
                })
    except Exception as e:
        pass
    return leads


# ===================================================================
# FUENTE 2: CYLEX
# ===================================================================
def scrape_cylex(nicho, ciudad):
    """Scrapea cylex.es — tiene emails directos."""
    url = "https://www.cylex.es/search/{}-{}.html".format(
        nicho.replace(" ", "-"), ciudad)
    leads = []
    try:
        r = SESSION.get(url, timeout=10)
        if r.status_code != 200:
            return leads

        text = r.text
        names = re.findall(r'class="company_name"[^>]*>.*?<a[^>]*>([^<]+)', text, re.DOTALL)
        emails_page = extract_emails(text)
        phones_page = extract_phones(text)

        for i, name in enumerate(names):
            leads.append({
                "nombre": name.strip(),
                "email": emails_page[i] if i < len(emails_page) else "",
                "telefono": phones_page[i] if i < len(phones_page) else "",
                "nicho": nicho,
                "ciudad": ciudad,
                "fuente": "cylex",
            })
    except:
        pass
    return leads


# ===================================================================
# FUENTE 3: INFOISINFO
# ===================================================================
def scrape_infoisinfo(nicho, ciudad):
    """Scrapea infoisinfo.es — datos de contacto de negocios."""
    url = "https://www.infoisinfo.es/buscar/{}/{}".format(
        nicho.replace(" ", "-"), ciudad)
    leads = []
    try:
        r = SESSION.get(url, timeout=10)
        if r.status_code != 200:
            return leads

        text = r.text
        names = re.findall(r'itemprop="name"[^>]*>([^<]+)', text)
        tels = re.findall(r'itemprop="telephone"[^>]*>([^<]+)', text)
        emails_page = extract_emails(text)
        webs = re.findall(r'itemprop="url"[^>]*href="(https?://(?!www\.infoisinfo)[^"]+)', text)

        for i, name in enumerate(names[:30]):
            leads.append({
                "nombre": name.strip(),
                "email": emails_page[i] if i < len(emails_page) else "",
                "telefono": tels[i].strip() if i < len(tels) else "",
                "website": webs[i] if i < len(webs) else "",
                "nicho": nicho,
                "ciudad": ciudad,
                "fuente": "infoisinfo",
            })
    except:
        pass
    return leads


# ===================================================================
# ENRIQUECIMIENTO: Visitar webs para extraer email
# ===================================================================
def enrich_lead_email(lead):
    """Visita la web del negocio para extraer email (rapido, sin navegador)."""
    web = lead.get("website", "")
    if not web or lead.get("email"):
        return lead

    try:
        r = SESSION.get(web, timeout=6, allow_redirects=True, verify=False)
        emails = extract_emails(r.text[:12000])

        # Intentar /contacto
        if not emails:
            for suffix in ["/contacto", "/contact"]:
                try:
                    r2 = SESSION.get(web.rstrip("/") + suffix, timeout=4, verify=False)
                    emails = extract_emails(r2.text[:8000])
                    if emails:
                        break
                except:
                    pass

        if emails:
            lead["email"] = emails[0]
    except:
        pass
    return lead


# ===================================================================
# MAIN TURBO
# ===================================================================
def run_turbo(nichos=None, ciudades=None):
    """Scraping masivo con 20 hilos paralelos."""
    nichos = nichos or list(NICHOS_PA.keys())[:10]
    ciudades = ciudades or CIUDADES[:8]

    print("=" * 60)
    print("  TURBO SCRAPER v4.0 — SIN NAVEGADOR")
    print("  Nichos: {} | Ciudades: {} | Fuentes: 3".format(len(nichos), len(ciudades)))
    print("  Hilos: 20 paralelos")
    print("=" * 60)

    all_leads = []
    seen = set()

    # FASE 1: Scrape directorios (rapido, sin hilos aun)
    total = len(nichos) * len(ciudades)
    done = 0
    for ciudad in ciudades:
        for nicho in nichos:
            done += 1
            slug = NICHOS_PA.get(nicho, nicho)

            # Paginas Amarillas (3 paginas)
            for pg in range(1, 4):
                pa = scrape_paginas_amarillas(slug, ciudad, pg)
                for l in pa:
                    key = l.get("nombre", "") + l.get("telefono", "")
                    if key and key not in seen:
                        seen.add(key)
                        all_leads.append(l)

            # Cylex
            cx = scrape_cylex(nicho, ciudad)
            for l in cx:
                key = l.get("nombre", "") + l.get("email", "")
                if key and key not in seen:
                    seen.add(key)
                    all_leads.append(l)

            # InfoIsInfo
            ii = scrape_infoisinfo(nicho, ciudad)
            for l in ii:
                key = l.get("nombre", "") + l.get("email", "")
                if key and key not in seen:
                    seen.add(key)
                    all_leads.append(l)

            with_email = len([l for l in all_leads if l.get("email")])
            print("  [{}/{}] {} / {} -> {} leads ({} con email)".format(
                done, total, nicho, ciudad, len(all_leads), with_email))

    print("\n  FASE 1 completada: {} leads brutos".format(len(all_leads)))

    # FASE 2: Enriquecer con emails (20 hilos paralelos)
    without_email = [l for l in all_leads if not l.get("email") and l.get("website")]
    print("  FASE 2: Enriqueciendo {} leads con web pero sin email...".format(len(without_email)))

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(enrich_lead_email, l): l for l in without_email}
        enriched = 0
        for f in as_completed(futures):
            result = f.result()
            if result and result.get("email"):
                enriched += 1
                if enriched % 10 == 0:
                    print("    +{} emails encontrados...".format(enriched))

    # Guardar todo
    save_leads(all_leads)

    # Importar al CRM
    email_leads = [l for l in all_leads if l.get("email")]
    try:
        from email_crm import add_leads_bulk
        add_leads_bulk(email_leads)
    except:
        pass

    # Resumen
    total_email = len(email_leads)
    total_phone = len([l for l in all_leads if l.get("telefono")])
    total_web = len([l for l in all_leads if l.get("website")])

    print("\n" + "=" * 60)
    print("  RESULTADO FINAL")
    print("  Negocios: {}".format(len(all_leads)))
    print("  Con EMAIL: {}".format(total_email))
    print("  Con TELEFONO: {}".format(total_phone))
    print("  Con WEB: {}".format(total_web))
    print("=" * 60)

    return all_leads


def save_leads(leads):
    # Merge con existentes
    existing = []
    if os.path.exists(OUTPUT):
        try:
            existing = json.load(open(OUTPUT, "r", encoding="utf-8"))
        except:
            pass

    seen_emails = set(l.get("email", "") for l in existing if l.get("email"))
    new = [l for l in leads if l.get("email") and l["email"] not in seen_emails]
    combined = existing + new

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print("  Guardados: {} leads ({} nuevos)".format(len(combined), len(new)))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        run_turbo(list(NICHOS_PA.keys()), CIUDADES)
    else:
        run_turbo(
            nichos=["peluquerias", "restaurantes", "clinicas-dentales", "gimnasios", "abogados",
                    "barberias", "inmobiliarias", "veterinarios"],
            ciudades=["malaga", "marbella", "fuengirola", "sevilla", "granada"]
        )
