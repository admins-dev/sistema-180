"""
DISPARO MASIVO DIA 1 — Plan Guerra 9 Días
Envía email DIA 0 (controversia máxima) a TODOS los leads nuevos.
"""
import sqlite3
import smtplib
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER = "Jose Maria Moreno"
PHONE = "+34 615 606 285"
DB = os.path.join(os.path.dirname(__file__), "crm.db")


def html_wrap(body_text):
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Georgia,serif; max-width:600px; margin:0 auto; 
             padding:20px; color:#222; line-height:1.8; font-size:15px;">
{}
<div style="margin-top:30px; padding-top:20px; border-top:1px solid #ddd; 
            color:#888; font-size:12px;">
    José María Moreno | Sistema 180 | {}
    <br>Responde OPT-OUT si prefieres no recibir más.
</div>
</body></html>""".format(body_text.replace("\n", "<br>"), PHONE)


def email_dia0(nombre, nicho, ciudad):
    """DÍA 0: Controversia máxima — obliga a abrir."""
    if nombre and len(nombre) > 2:
        subject = "¿Sabéis lo que dicen de {} en Google?".format(nombre)
    elif nicho:
        subject = "Un problema con vuestra {} en Google".format(nicho)
    else:
        subject = "Un problema con vuestro negocio en Google"
    
    n = nombre if nombre else "vuestro negocio"
    ni = nicho if nicho else "negocio"
    ci = ciudad if ciudad else "Málaga"
    
    body = """He hecho algo que no os va a gustar.

He buscado "{} en {}" en Google. Como haría cualquier cliente vuestro.

No aparecéis. Ni en la primera página. Ni en la segunda.

¿Sabéis quién sí aparece? Vuestra competencia. Los que sí tienen web optimizada. Esos se llevan a VUESTROS clientes. Cada día. Sin hacer nada especial. Solo por estar ahí.

Y vosotros no estáis.

No os escribo para venderos nada. Os escribo porque me parece una pena que un negocio que funciona pierda clientes por algo tan estúpido como no aparecer en Google.

Puedo cambiarlo. 497 EUR. 5 días. Web con botón de WhatsApp + Google Maps optimizado. Sin mensualidades.

Si queréis cambiarlo, respondedme o escribidme al {} (WhatsApp).

Si no, tirad este email y seguid perdiendo clientes sin saberlo.

José María Moreno
Sistema 180""".format(ni, ci, PHONE)
    
    return subject, html_wrap(body)


def send_email(to, subject, html):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = "{} <{}>".format(SENDER, SMTP_EMAIL)
        msg["To"] = to
        msg["Subject"] = subject
        msg["Reply-To"] = SMTP_EMAIL
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        return True
    except Exception as e:
        print("  [ERROR] {}: {}".format(to, e))
        return False


def fire():
    print("=" * 60)
    print("  DISPARO MASIVO DIA 1 — {}".format(datetime.now().strftime("%H:%M")))
    print("=" * 60)
    
    conn = sqlite3.connect(DB)
    
    # Get all unsent leads (excluding placeholders and already sent)
    leads = conn.execute("""
        SELECT email, nombre, nicho, ciudad FROM leads
        WHERE email NOT IN (SELECT email FROM emails_sent)
        AND email NOT LIKE '%placeholder%'
        AND email NOT LIKE '%google%'
        AND email NOT LIKE '%example%'
        AND LENGTH(email) > 5
    """).fetchall()
    
    print("  {} leads para disparo\n".format(len(leads)))
    
    sent = 0
    errors = 0
    
    for email, nombre, nicho, ciudad in leads:
        subject, html = email_dia0(nombre, nicho, ciudad)
        
        if send_email(email, subject, html):
            sent += 1
            print("  [{}] {} -> {}".format(sent, email, subject[:50]))
            
            # Log in CRM
            conn.execute("""
                INSERT INTO emails_sent (email, subject, template, sent_at)
                VALUES (?, ?, 'b7mg_dia0', ?)
            """, (email, subject, datetime.now().isoformat()))
            conn.commit()
        else:
            errors += 1
        
        # Delay between emails (avoid Gmail throttle)
        delay = 3 + (sent % 5 == 0) * 5  # Extra pause every 5 emails
        time.sleep(delay)
    
    print("\n" + "=" * 60)
    print("  RESULTADO DISPARO")
    print("  Enviados: {}".format(sent))
    print("  Errores: {}".format(errors))
    print("  Total contactados: {}".format(
        conn.execute("SELECT COUNT(DISTINCT email) FROM emails_sent").fetchone()[0]))
    print("=" * 60)
    
    conn.close()
    return sent


if __name__ == "__main__":
    fire()
