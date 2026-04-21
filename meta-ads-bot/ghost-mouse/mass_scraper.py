"""
Sistema 180 — Scraper Masivo de Negocios Locales v2.0
Objetivo: 500+ leads con emails de Malaga y alrededores.
"""
import json
import os
import time
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), "crm.db")

# 20+ nichos para maximizar volumen
NICHOS = [
    # Ya scrapeados (skip duplicados)
    "peluqueria", "restaurante", "gimnasio", "clinica dental", "abogado",
    # NUEVOS nichos con alto volumen
    "veterinario", "inmobiliaria", "taller mecanico", "fontanero",
    "electricista", "fisioterapeuta", "psicologo", "optica",
    "farmacia", "florista", "carpintero", "fotografo",
    "academia idiomas", "autoescuela", "clinica estetica",
    "podologia", "dentista", "nutricionista", "pilates",
    "yoga", "crossfit", "cerrajero", "mudanzas",
    "jardineria", "limpieza", "reformas", "pintores",
    "asesoria fiscal", "gestor administrativo", "notaria",
    "clinica veterinaria", "residencia canina", "tienda mascotas",
    "joyeria", "relojeria", "zapateria", "panaderia",
    "pasteleria", "heladeria", "cafeteria", "bar de copas",
    "discoteca", "karaoke", "escape room", "spa",
    "centro de belleza", "barberia", "tatuaje", "piercing",
]

CIUDADES = [
    "Malaga", "Torremolinos", "Benalmadena", "Fuengirola",
    "Marbella", "Mijas", "Nerja", "Velez-Malaga",
    "Rincon de la Victoria", "Estepona", "Alhaurin de la Torre",
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


def search_google_business(query, city, num=20):
    """Busca negocios en Google y extrae emails de las páginas."""
    results = []
    search_queries = [
        "{} {} email contacto",
        "{} {} gmail.com",
        "{} {} correo electronico",
        "{} {} @gmail @hotmail @yahoo",
    ]
    
    for sq in search_queries:
        full_query = sq.format(query, city)
        url = "https://www.google.com/search?q={}&num={}".format(
            urllib.parse.quote(full_query), num)
        
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            
            # Extraer emails con regex simple
            import re
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', html)
            for email in emails:
                email = email.lower().strip()
                # Filtrar basura
                if any(skip in email for skip in [
                    "google", "gstatic", "schema", "example", "sentry",
                    "w3.org", "googleapis", "android", "apple", "microsoft",
                    "mozilla", "webkit", "github", "npm"
                ]):
                    continue
                if email.endswith(('.png', '.jpg', '.js', '.css', '.svg')):
                    continue
                if len(email) < 8 or len(email) > 60:
                    continue
                    
                results.append({
                    "email": email,
                    "nombre": "",
                    "nicho": query,
                    "ciudad": city,
                    "source": "google_scrape",
                })
        except Exception as e:
            pass
        
        time.sleep(1)  # Rate limit
    
    return results


def scrape_paginas_amarillas(nicho, ciudad):
    """Busca en Paginas Amarillas España."""
    results = []
    url = "https://www.paginasamarillas.es/search/{}/all-ma/{}/all-is/{}/all-ba/all-pu/all-nc/1".format(
        urllib.parse.quote(nicho),
        urllib.parse.quote(ciudad),
        urllib.parse.quote(ciudad),
    )
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        
        import re
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', html)
        for email in emails:
            email = email.lower().strip()
            if any(skip in email for skip in ["paginasamarillas", "google", "example"]):
                continue
            if len(email) > 60 or len(email) < 8:
                continue
            results.append({
                "email": email,
                "nombre": "",
                "nicho": nicho,
                "ciudad": ciudad,
                "source": "paginas_amarillas",
            })
    except:
        pass
    
    return results


def save_leads(leads):
    """Guarda leads en el CRM, evitando duplicados."""
    conn = sqlite3.connect(DB)
    new_count = 0
    for lead in leads:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO leads (email, nombre, nicho, ciudad, source, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'nuevo', ?)
            """, (
                lead["email"],
                lead.get("nombre", ""),
                lead["nicho"],
                lead["ciudad"],
                lead.get("source", "scrape"),
                datetime.now().isoformat(),
            ))
            new_count += 1
        except:
            pass
    conn.commit()
    
    # Count total
    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    conn.close()
    return new_count, total


def run_mass_scrape():
    """Scrape masivo: todos los nichos x todas las ciudades."""
    init_db()
    
    total_found = 0
    total_new = 0
    
    print("=" * 60)
    print("  SCRAPER MASIVO — {} nichos x {} ciudades".format(len(NICHOS), len(CIUDADES)))
    print("  Objetivo: 500+ leads")
    print("=" * 60)
    
    for ciudad in CIUDADES:
        for nicho in NICHOS:
            leads = search_google_business(nicho, ciudad, num=10)
            leads += scrape_paginas_amarillas(nicho, ciudad)
            
            if leads:
                # Dedup dentro de este lote
                seen = set()
                unique = []
                for l in leads:
                    if l["email"] not in seen:
                        seen.add(l["email"])
                        unique.append(l)
                
                new, total = save_leads(unique)
                total_found += len(unique)
                
                if unique:
                    print("  [{}] {} {} -> {} emails (total DB: {})".format(
                        ciudad[:3].upper(), nicho, ciudad, len(unique), total))
            
            time.sleep(0.5)
    
    # Report final
    conn = sqlite3.connect(DB)
    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    nuevos = conn.execute("SELECT COUNT(*) FROM leads WHERE status='nuevo'").fetchone()[0]
    conn.close()
    
    print("\n" + "=" * 60)
    print("  RESULTADO FINAL")
    print("  Total en DB: {} leads".format(total))
    print("  Nuevos (sin contactar): {}".format(nuevos))
    print("  Encontrados hoy: {}".format(total_found))
    print("=" * 60)


def get_unsent_leads(limit=50):
    """Obtener leads sin contactar para campaña."""
    conn = sqlite3.connect(DB)
    rows = conn.execute("""
        SELECT email, nombre, nicho, ciudad FROM leads 
        WHERE status = 'nuevo'
        AND email NOT IN (SELECT email FROM emails_sent)
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [{"email": r[0], "nombre": r[1] or r[0].split("@")[0], "nicho": r[2], "ciudad": r[3]} for r in rows]


if __name__ == "__main__":
    run_mass_scrape()
