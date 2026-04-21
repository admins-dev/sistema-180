"""
Sistema 180 - Lanzar Campana de Email Real
Envia emails a todos los leads pendientes del CRM.
Registra cada envio en la base de datos.
"""
import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar .env del proyecto
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

from email_crm import get_unsent_leads, log_email_sent, print_dashboard
from email_marketing import EMAIL_TEMPLATE_1, EMAIL_TEMPLATE_2

# SMTP Config
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = "Jose Maria Moreno"
PHONE = "+34 615 606 285"


def send_real_email(to_email, subject, body):
    """Envia un email real via Gmail SMTP."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("  [!] SMTP no configurado")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = "{} <{}>".format(SENDER_NAME, SMTP_EMAIL)
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print("  [ERROR] {}: {}".format(to_email, e))
        return False


def run_campaign(max_emails=20, template=1, dry_run=True):
    """Envia campana a leads pendientes."""
    leads = get_unsent_leads(limit=max_emails)

    mode = "DRY RUN" if dry_run else "REAL"
    print("=" * 60)
    print("  CAMPANA EMAIL {} — {} leads".format(mode, len(leads)))
    print("  Template: {} | SMTP: {}".format(template, SMTP_EMAIL))
    print("=" * 60)

    if not leads:
        print("  No hay leads pendientes!")
        return 0

    sent = 0
    for lead in leads:
        nombre = lead.get("nombre", "tu negocio")
        email = lead.get("email", "")
        nicho = lead.get("nicho", "tu sector")
        ciudad = lead.get("ciudad", "tu ciudad")

        if not email:
            continue

        # Generar email
        if template == 1:
            email_text = EMAIL_TEMPLATE_1.format(
                nombre_negocio=nombre, nicho=nicho, ciudad=ciudad)
        else:
            email_text = EMAIL_TEMPLATE_2.format(nicho=nicho, ciudad=ciudad)

        # Extraer asunto y cuerpo
        lines = email_text.strip().split("\n")
        subject = lines[0].replace("Asunto: ", "")
        body = "\n".join(lines[2:]).replace("[TU TELEFONO]", PHONE)

        if dry_run:
            print("\n  [DRY] {} -> {}".format(email, subject))
        else:
            success = send_real_email(email, subject, body)
            if success:
                log_email_sent(email, subject, "template_{}".format(template))
                sent += 1
                print("  [OK] {} -> {}".format(email, subject))
            else:
                print("  [FAIL] {}".format(email))

            # Pausa entre emails (evitar spam filter)
            time.sleep(3)

    print("\n  Enviados: {}/{}".format(sent if not dry_run else len(leads), len(leads)))

    if not dry_run:
        print("\n  DASHBOARD ACTUALIZADO:")
        print_dashboard()

    return sent


if __name__ == "__main__":
    dry = "--real" not in sys.argv
    max_e = 42

    for arg in sys.argv:
        if arg.startswith("--max="):
            max_e = int(arg.split("=")[1])

    run_campaign(max_emails=max_e, template=1, dry_run=dry)
