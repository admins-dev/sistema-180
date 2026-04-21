"""
Sistema 180 — Email Marketing Automatizado v1.0
Busca emails de negocios locales y envia emails frios de venta.
Canal paralelo a Instagram DMs — funciona sin riesgo de bloqueo.
"""
import requests
import json
import re
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import GEMINI_KEY

# =========================================================
# CONFIGURACION
# =========================================================

# Email desde el que envias (configurar con tu email real)
SMTP_CONFIG = {
    "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "email": os.getenv("SMTP_EMAIL", ""),  # Tu email
    "password": os.getenv("SMTP_PASSWORD", ""),  # App password de Gmail
    "nombre": "Jose Maria Moreno",
    "firma": "Sistema 180 | Marketing para negocios locales",
}

EMAILS_FILE = os.path.join(os.path.dirname(__file__), "emails_leads.json")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={GEMINI_KEY}"

# =========================================================
# BUSCADOR DE EMAILS
# =========================================================

def extract_emails_from_text(text):
    """Extrae emails validos de un bloque de texto."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    # Filtrar emails genericos/invalidos
    blacklist = ["example.com", "test.com", "email.com", "correo.com", 
                 "noreply", "no-reply", "info@info", "sentry"]
    return [e for e in emails if not any(b in e.lower() for b in blacklist)]


def find_emails_google(page, query, city, max_results=20):
    """Busca emails de negocios via Google Search."""
    search_query = f'"{query}" "{city}" email "@" contacto'
    print(f"\n[BUSCANDO EMAILS] '{query}' en {city}...")
    
    page.goto(f"https://www.google.com/search?q={search_query}&num=20", 
              wait_until="domcontentloaded")
    time.sleep(3)
    
    # Aceptar cookies
    try:
        page.click('button:has-text("Aceptar todo")', timeout=2000)
        time.sleep(1)
    except:
        pass
    
    text = page.inner_text("body")
    emails = extract_emails_from_text(text)
    
    # Buscar tambien en los links de resultados
    links = page.locator('a[href*="://"]').all()
    visited = set()
    
    for link in links[:10]:
        try:
            href = link.get_attribute("href") or ""
            if "google" in href or href in visited:
                continue
            visited.add(href)
            
            page.goto(href, wait_until="domcontentloaded", timeout=5000)
            time.sleep(1)
            body = page.inner_text("body")[:5000]
            found = extract_emails_from_text(body)
            emails.extend(found)
        except:
            continue
    
    unique_emails = list(set(emails))
    print(f"  Encontrados: {len(unique_emails)} emails unicos")
    return unique_emails


def find_emails_maps(page, query, city, max_businesses=15):
    """Busca negocios en Maps y luego sus emails en sus webs."""
    print(f"\n[MAPS -> EMAILS] '{query}' en {city}...")
    
    page.goto(f"https://www.google.com/maps/search/{query}+en+{city}", 
              wait_until="domcontentloaded")
    time.sleep(5)
    
    try:
        page.click('button:has-text("Aceptar todo")', timeout=2000)
        time.sleep(1)
    except:
        pass
    
    # Scroll para cargar resultados
    sidebar = page.locator('[role="feed"]')
    if sidebar.count() > 0:
        for _ in range(3):
            sidebar.first.evaluate('el => el.scrollTop = el.scrollHeight')
            time.sleep(2)
    
    items = page.locator('a[href*="/maps/place/"]').all()
    leads = []
    
    for item in items[:max_businesses]:
        try:
            name = item.get_attribute("aria-label") or ""
            if not name:
                continue
            
            # Click en el negocio para ver detalles
            item.click()
            time.sleep(2)
            
            # Buscar email y web en el panel
            panel_text = page.inner_text("body")[:3000]
            emails = extract_emails_from_text(panel_text)
            
            # Buscar link de web
            web_link = page.locator('a[data-value="Sitio web"], a[aria-label*="sitio web"]').first
            website = None
            try:
                website = web_link.get_attribute("href")
            except:
                pass
            
            if website and not emails:
                # Ir a la web del negocio a buscar email
                try:
                    page.goto(website, wait_until="domcontentloaded", timeout=5000)
                    time.sleep(1)
                    web_text = page.inner_text("body")[:5000]
                    emails = extract_emails_from_text(web_text)
                    page.go_back()
                    time.sleep(1)
                except:
                    pass
            
            if emails:
                leads.append({
                    "nombre": name,
                    "email": emails[0],
                    "website": website,
                    "query": query,
                    "city": city,
                    "enviado": False,
                })
                print(f"  [OK] {name} -> {emails[0]}")
            else:
                print(f"  [--] {name} -> sin email")
                
        except:
            continue
    
    print(f"\n  Total con email: {len(leads)}")
    return leads


# =========================================================
# TEMPLATES DE EMAIL FRIO
# =========================================================

EMAIL_TEMPLATE_1 = """Asunto: {nombre_negocio} - una idea para llenar vuestra agenda

Hola,

Acabo de ver {nombre_negocio} online y la verdad es que se nota la calidad de vuestro trabajo.

Os escribo porque trabajo ayudando a negocios de {nicho} en {ciudad} a conseguir mas clientes a traves de internet, y creo que tengo una idea que os puede funcionar muy bien.

En 2 palabras: os monto una web profesional con formulario de contacto + WhatsApp + Google Maps optimizado para que cuando alguien busque "{nicho} en {ciudad}", os encuentre a vosotros.

El 76% de los clientes buscan en Google antes de ir a un negocio local. Si no apareceis, esos clientes se van a la competencia.

Si os interesa, os hago un diagnostico GRATIS de vuestra presencia online en 15 min. Sin compromiso.

Respondedme aqui o llamadme al [TU TELEFONO].

Un saludo,
Jose Maria Moreno
Sistema 180 | Marketing para negocios locales
"""

EMAIL_TEMPLATE_2 = """Asunto: He buscado "{nicho} en {ciudad}" y no os encuentro

Hola,

Os escribo porque he buscado "{nicho} en {ciudad}" en Google y no apareceis en los primeros resultados.

Eso significa que cada dia hay clientes que os estan buscando y se van a vuestro competidor.

Trabajo con negocios de {nicho} en {ciudad} y les ayudo a aparecer en Google + tener una web profesional para que esos clientes os elijan a vosotros.

Desde 497 EUR. Entrega en 5 dias. Sin mensualidades.

Si os interesa, respondedme y os cuento en 2 minutos.

Un saludo,
Jose Maria Moreno
Sistema 180
"""

EMAIL_FOLLOWUP = """Asunto: Re: {nombre_negocio} - seguimiento

Hola de nuevo,

Os escribi hace unos dias sobre vuestra presencia online y queria saber si lo llegasteis a ver.

Solo quiero ofreceros un diagnostico GRATIS de 15 min para ver como podeis conseguir mas clientes desde internet.

Sin compromiso, sin coste. Si no os cuadra, sin problema.

Respondedme aqui y os propongo un dia.

Un saludo,
Jose Maria Moreno
"""


def generate_personalized_email(lead):
    """Genera email personalizado con IA."""
    prompt = f"""Escribe un email frio B2B en espanol de Espana para vender servicios de creacion de paginas web a un negocio local.

DATOS DEL NEGOCIO:
Nombre: {lead.get('nombre', 'tu negocio')}
Tipo: {lead.get('query', 'negocio local')}
Ciudad: {lead.get('city', 'Malaga')}
Web actual: {lead.get('website', 'No tiene')}

REGLAS:
- Maximo 8 lineas
- Tono cercano pero profesional
- Tutea/vosotros
- NO adjuntes archivos
- Menciona algo especifico del negocio
- Ofrece diagnostico GRATIS de 15 min
- Precio desde 497 EUR
- Firma: Jose Maria Moreno - Sistema 180

Escribe SOLO el email completo con asunto. Formato:
Asunto: [asunto]

[cuerpo del email]"""

    try:
        r = requests.post(GEMINI_URL, json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 512}
        }, timeout=60)
        data = r.json()
        parts = data["candidates"][0]["content"]["parts"]
        texts = [p["text"] for p in parts if "text" in p and not p.get("thought")]
        return texts[-1].strip() if texts else None
    except:
        return None


# =========================================================
# ENVIO DE EMAILS
# =========================================================

def send_email(to_email, subject, body, dry_run=True):
    """Envia un email. dry_run=True para probar sin enviar."""
    if dry_run:
        print(f"\n  [DRY RUN] Para: {to_email}")
        print(f"  Asunto: {subject}")
        print(f"  Cuerpo: {body[:100]}...")
        return True
    
    if not SMTP_CONFIG["email"] or not SMTP_CONFIG["password"]:
        print("  [ERROR] Configura SMTP_EMAIL y SMTP_PASSWORD en .env")
        return False
    
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{SMTP_CONFIG['nombre']} <{SMTP_CONFIG['email']}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["email"], SMTP_CONFIG["password"])
            server.send_message(msg)
        
        print(f"  [ENVIADO] {to_email}")
        return True
    except Exception as e:
        print(f"  [ERROR] {to_email}: {e}")
        return False


def send_campaign(leads, template_num=1, dry_run=True):
    """Envia campana de emails a lista de leads."""
    print(f"\n{'='*60}")
    print(f"  EMAIL CAMPAIGN {'(DRY RUN)' if dry_run else '(REAL)'}")
    print(f"  Leads: {len(leads)} | Template: {template_num}")
    print(f"{'='*60}")
    
    template = EMAIL_TEMPLATE_1 if template_num == 1 else EMAIL_TEMPLATE_2
    sent = 0
    
    for lead in leads:
        if lead.get("enviado"):
            continue
        
        email_body = template.format(
            nombre_negocio=lead.get("nombre", "tu negocio"),
            nicho=lead.get("query", "tu sector"),
            ciudad=lead.get("city", "tu ciudad"),
        )
        
        # Extraer asunto
        lines = email_body.strip().split("\n")
        subject = lines[0].replace("Asunto: ", "")
        body = "\n".join(lines[2:])
        
        success = send_email(lead["email"], subject, body, dry_run=dry_run)
        if success:
            lead["enviado"] = True
            sent += 1
        
        time.sleep(2)  # Pausa entre emails
    
    # Guardar estado
    save_email_leads(leads)
    print(f"\n  Enviados: {sent}/{len(leads)}")
    return sent


def save_email_leads(leads):
    """Guardar leads con estado de envio."""
    existing = load_email_leads()
    existing_emails = {l["email"] for l in existing}
    new = [l for l in leads if l["email"] not in existing_emails]
    all_leads = existing + new
    
    with open(EMAILS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_leads, f, ensure_ascii=False, indent=2)
    return all_leads


def load_email_leads():
    if os.path.exists(EMAILS_FILE):
        with open(EMAILS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  SISTEMA 180 - EMAIL MARKETING AUTOMATIZADO v1.0")
    print("  Canal paralelo a Instagram DMs")
    print("=" * 60)
    
    # Demo: mostrar templates
    print("\n--- TEMPLATE 1 ---")
    print(EMAIL_TEMPLATE_1.format(
        nombre_negocio="Clinica Dental Smile",
        nicho="clinicas dentales",
        ciudad="Malaga"
    )[:300])
    
    print("\n--- TEMPLATE 2 ---")
    print(EMAIL_TEMPLATE_2.format(
        nicho="peluquerias",
        ciudad="Malaga"
    )[:300])
    
    print("\n--- CONFIGURACION SMTP ---")
    if SMTP_CONFIG["email"]:
        print(f"  Email configurado: {SMTP_CONFIG['email']}")
    else:
        print("  [!] Falta configurar SMTP_EMAIL en variables de entorno")
        print("  Pasos para Gmail:")
        print("  1. Ve a myaccount.google.com/apppasswords")
        print("  2. Genera una 'App password' para 'Mail'")
        print("  3. Configura SMTP_EMAIL=tu@gmail.com")
        print("  4. Configura SMTP_PASSWORD=la_app_password")
    
    print("\n--- MODO DE USO ---")
    print("  1. Buscar emails: find_emails_google(page, 'peluquerias', 'Malaga')")
    print("  2. Enviar prueba: send_campaign(leads, dry_run=True)")  
    print("  3. Enviar real: send_campaign(leads, dry_run=False)")
