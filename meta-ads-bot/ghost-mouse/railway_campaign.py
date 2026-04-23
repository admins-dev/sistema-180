"""
Sistema 180 — Railway Campaign Engine (Headless / Cloud)
Versión para Railway: NO usa navegador. Usa APIs directas + Gemini.

Este script corre en Railway 24/7 y hace:
1. Scraping de emails vía HTTP (Páginas Amarillas, InfoIsInfo, Cylex) — SIN NAVEGADOR
2. Generación de emails con Gemini (Auto-Adaptativo, Monge Malo style)
3. Envío masivo SMTP con throttling inteligente
4. Log de todo a la DB SQLite (crm.db)
"""
import os
import sys
import time
import sqlite3
import smtplib
import re
import json
import threading
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(env_path)

DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Gemini AI Brain
try:
    from google import genai
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    ai = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
except ImportError:
    ai = None

NICHOS = [
    "peluqueria", "barberia", "centro estetica",
    "restaurante", "cafeteria", "bar",
    "clinica dental", "dentista",
    "gimnasio", "crossfit", "yoga",
    "fisioterapeuta", "psicologo", "nutricionista",
    "veterinario", "inmobiliaria", "abogado",
    "taller mecanico", "autoescuela", "optica",
    "fotografo", "tienda ropa", "academia idiomas",
    "reformas", "florista",
]

CIUDADES = [
    "Malaga", "Torremolinos", "Benalmadena", "Fuengirola",
    "Marbella", "Mijas", "Nerja", "Estepona",
    "Velez-Malaga", "Rincon de la Victoria",
    "Sevilla", "Granada", "Cordoba", "Cadiz", "Almeria",
    "Jaen", "Huelva", "Madrid", "Barcelona", "Valencia",
    "Zaragoza", "Bilbao", "Alicante", "Murcia",
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
            emailed INTEGER DEFAULT 0
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


# ===================================================================
# FASE 1: HTTP SCRAPING (sin navegador — funciona en Railway)
# ===================================================================
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def scrape_paginasamarillas(nicho, ciudad, max_pages=3):
    """Scrape Páginas Amarillas vía HTTP."""
    leads = []
    for page in range(1, max_pages + 1):
        try:
            url = f"https://www.paginasamarillas.es/search/{nicho}/all-ma/{ciudad}/all-is/{ciudad}/all-ba/all-pu/all-nc/{page}"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            
            # Extract emails from page
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', resp.text)
            # Extract phone numbers
            phones = re.findall(r'(?:\+34\s?)?(?:6|7|9)\d{2}\s?\d{3}\s?\d{3}', resp.text)
            # Extract business names from title tags
            names = re.findall(r'<span class="nombre"[^>]*>(.*?)</span>', resp.text)
            if not names:
                names = re.findall(r'<h2[^>]*>(.*?)</h2>', resp.text)
            
            for i, email in enumerate(emails):
                email = email.lower().strip()
                if any(skip in email for skip in ["google", "paginas", "schema", "example"]):
                    continue
                lead = {
                    "email": email,
                    "nombre": names[i].strip() if i < len(names) else f"Negocio {nicho}",
                    "telefono": phones[i] if i < len(phones) else "",
                    "nicho": nicho,
                    "ciudad": ciudad,
                }
                leads.append(lead)
            time.sleep(0.5)
        except Exception as e:
            continue
    return leads


def scrape_infoisinfo(nicho, ciudad):
    """Scrape InfoIsInfo vía HTTP."""
    leads = []
    try:
        slug_nicho = nicho.replace(" ", "-")
        slug_ciudad = ciudad.lower().replace(" ", "-")
        url = f"https://www.infoisinfo.es/busqueda/{slug_nicho}/{slug_ciudad}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', resp.text)
            phones = re.findall(r'(?:\+34\s?)?(?:6|7|9)\d{2}\s?\d{3}\s?\d{3}', resp.text)
            for i, email in enumerate(emails):
                email = email.lower().strip()
                if any(skip in email for skip in ["infoisinfo", "google", "schema"]):
                    continue
                leads.append({
                    "email": email,
                    "nombre": f"{nicho.title()} en {ciudad}",
                    "telefono": phones[i] if i < len(phones) else "",
                    "nicho": nicho,
                    "ciudad": ciudad,
                })
    except:
        pass
    return leads


def scrape_all_directories(nichos, ciudades):
    """Run all HTTP scrapers across all nicho/city combos."""
    all_leads = []
    total_combos = len(nichos) * len(ciudades)
    done = 0
    for ciudad in ciudades:
        for nicho in nichos:
            done += 1
            sys.stdout.write(f"\r  [{done}/{total_combos}] {nicho} / {ciudad}...")
            sys.stdout.flush()
            
            leads_pa = scrape_paginasamarillas(nicho, ciudad)
            leads_ii = scrape_infoisinfo(nicho, ciudad)
            all_leads.extend(leads_pa)
            all_leads.extend(leads_ii)
            time.sleep(0.3)
    
    print(f"\n  HTTP Scraping completado: {len(all_leads)} leads brutos")
    return all_leads


def save_leads_to_db(leads):
    conn = sqlite3.connect(DB_PATH)
    new = 0
    for lead in leads:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO leads (email, nombre, nicho, ciudad, telefono, source, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'railway_http', 'nuevo', ?)
            """, (lead["email"], lead["nombre"], lead["nicho"], lead["ciudad"],
                  lead.get("telefono", ""), datetime.now().isoformat()))
            new += 1
        except:
            pass
    conn.commit()
    total = conn.execute("SELECT count(*) FROM leads").fetchone()[0]
    conn.close()
    return new, total


# ===================================================================
# FASE 2: GEMINI AI EMAIL WRITER (Monge Malo Auto-Adapt)
# ===================================================================

def ai_write_email(lead):
    """Gemini auto-adapts an email for this specific lead."""
    if not ai:
        return fallback_email(lead)
    
    dolor = ""
    if not lead.get("web"):
        dolor += "NO tiene página web. "
    if not lead.get("telefono"):
        dolor += "NO tiene teléfono visible. "
    
    prompt = f"""
    Eres Jose Maria Moreno de 'Sistema 180'. Copywriter estilo Luis Monge Malo.
    Escribe un Cold Email para este negocio local.
    
    Negocio: {lead['nombre']}
    Nicho: {lead['nicho']}
    Ciudad: {lead['ciudad']}
    Datos faltantes: {dolor if dolor else 'Tiene web y teléfono pero no tiene embudo digital.'}
    
    ESTRUCTURA:
    1. ASUNTO: Corto, casual, curiosidad. Nada de ventas.
    2. HOOK: Anécdota o metáfora curiosa sobre su industria en {lead['ciudad']}.
    3. DOLOR: Has buscado en Google y no aparecen. Están perdiendo 10 clientes/día.
    4. CÁLCULO: 10 reservas/día x 30 días = miles de € regalados a la competencia.
    5. MORALEJA: Lección anti-intuitiva de negocio.
    6. CTA: Ecosistema digital por 497€. Cero presión. Respondedme o tan amigos.
    
    Formato estricto:
    ASUNTO: [asunto]
    CUERPO: [cuerpo]
    """
    try:
        res = ai.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        text = res.text.strip()
        lines = text.split('\n', 1)
        subject = lines[0].replace("ASUNTO:", "").strip()
        body = lines[1].replace("CUERPO:", "").strip() if len(lines) > 1 else text
        return subject, body
    except:
        return fallback_email(lead)


def fallback_email(lead):
    subject = f"¿Por qué {lead['nicho']} se está llevando a vuestros clientes?"
    body = f"""Hola.

El otro día busqué "{lead['nicho']} en {lead['ciudad']}" en Google como si fuera un cliente normal.
Vuestros competidores aparecían. Vosotros, invisibles.

Eso significa que cada día perdéis unos 10 clientes potenciales que terminan reservando en otro sitio.
Multiplica lo que os deja un cliente x 10 al día x 30 días... Son miles de euros que la competencia se lleva.

No porque sean mejores. Porque aparecen primero.

Monto ecosistemas digitales que cortan esta hemorragia. 497€. 5 días. Sin mensualidades.

Si queréis recuperar esos clientes, respondedme. Si no, tan amigos.

Jose Maria Moreno
Sistema 180"""
    return subject, body


# ===================================================================
# FASE 3: SMTP ENGINE
# ===================================================================

def send_email(to, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = f"Jose Maria Moreno <{SMTP_EMAIL}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg["Reply-To"] = SMTP_EMAIL
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"  [SMTP ERROR] {to}: {e}")
        return False


def log_sent(email, subject):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO emails_sent (email, subject, template, sent_at) VALUES (?, ?, 'ai_mongemalo', ?)",
                 (email, subject, datetime.now().isoformat()))
    conn.execute("UPDATE leads SET emailed = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()


# ===================================================================
# MAIN LOOP
# ===================================================================

def run():
    init_db()
    
    print("\n" + "=" * 70)
    print("  🚀 SISTEMA 180 — RAILWAY CAMPAIGN ENGINE v3.0")
    print("  📡 Modo: Headless HTTP + Gemini AI + SMTP")
    print("=" * 70)
    
    # PHASE 1: Scrape
    print("\n📡 FASE 1: Scraping HTTP masivo (sin navegador)...")
    leads = scrape_all_directories(NICHOS, CIUDADES)
    new, total = save_leads_to_db(leads)
    print(f"  ✅ {new} nuevos guardados. Total en DB: {total}")
    
    # PHASE 2: Send AI emails
    print(f"\n🧠 FASE 2: Generando + enviando emails con Gemini AI...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    unsent = [dict(r) for r in conn.execute(
        "SELECT * FROM leads WHERE emailed = 0 AND email NOT LIKE '%@phone.lead' AND email NOT LIKE '%@web.lead' LIMIT 500"
    ).fetchall()]
    conn.close()
    
    print(f"  📋 {len(unsent)} leads en cola")
    
    sent_count = 0
    for i, lead in enumerate(unsent):
        print(f"\n  [{i+1}/{len(unsent)}] 🔍 {lead['nombre']} ({lead['nicho']} / {lead['ciudad']})")
        
        subject, body = ai_write_email(lead)
        print(f"  ✍️  Asunto: {subject[:60]}...")
        
        if send_email(lead["email"], subject, body):
            log_sent(lead["email"], subject)
            sent_count += 1
            print(f"  ✅ ENVIADO a {lead['email']}")
        else:
            print(f"  ❌ Falló {lead['email']}")
        
        # Gmail limit: ~100/hr. Throttle at 2s between sends.
        time.sleep(2)
    
    print("\n" + "=" * 70)
    print(f"  📊 RESULTADO: {sent_count} emails enviados de {len(unsent)} en cola")
    print("=" * 70)


if __name__ == "__main__":
    run()
