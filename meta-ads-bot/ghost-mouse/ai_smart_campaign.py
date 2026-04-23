import os
import sys
import time
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Cargar variables (.env)
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

# Configuracion Base de Datos y SMTP
DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER = "Jose Maria Moreno"

# Cargar Cerebro Digital (Gemini 2.5 Flash)
try:
    from google import genai
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_KEY:
        client = genai.Client(api_key=GEMINI_KEY)
        cerebro_activo = True
    else:
        cerebro_activo = False
except ImportError:
    cerebro_activo = False
    client = None

# Objetivo
OBJETIVO_LEADS = 10000


def get_lead_count():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Try both column names (email vs mail) for compatibility
        try:
            cursor.execute("SELECT count(*) FROM leads WHERE email IS NOT NULL AND email != ''")
        except:
            cursor.execute("SELECT count(*) FROM leads WHERE mail IS NOT NULL AND mail != ''")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0

def get_all_leads():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT rowid as id, nombre as name, nicho as category, ciudad as city, email as mail FROM leads WHERE email IS NOT NULL AND email != '' AND emailed=0 LIMIT 500")
        except:
            cursor.execute("SELECT id, name, category, city, mail FROM leads WHERE mail IS NOT NULL AND mail != '' AND emailed=0 LIMIT 500")
        leads = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return leads
    except Exception:
        return []

def mark_as_sent(lead_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE leads SET emailed = 1 WHERE rowid = ?", (lead_id,))
        conn.commit()
        conn.close()
    except:
        pass


def digital_brain_rewrite(lead):
    if not cerebro_activo:
        return "Tus clientes se van a otro", "Hola.\n\nMejoramos webs. Hablemos.\n\nJose Maria"

    prompt = f"""
    Eres Jose Maria Moreno de 'Sistema 180', un experto copywriter con el estilo exacto de Luis Monge Malo.
    Vas a mandar un Cold Email a un negocio local.

    Perfil del negocio que mi scraper acaba de analizar:
    Nombre: {lead.get('name', 'Negocio')}
    Nicho: {lead.get('category', 'local')}
    Ciudad: {lead.get('city', 'Malaga')}

    ESTRUCTURA OBLIGATORIA (Seduccion, Fascinacion, Cero Agresividad):
    1. ASUNTO: Muy corto, casual, en minusculas, generando curiosidad brutal. NADA de ventas en el asunto.
    2. HOOK: Empieza con una metafora o anecdota curiosa que viviste hace poco relacionada con su industria.
    3. DOLOR: Menciona sutilmente que los buscaste en Google Maps y no los encontraste bien posicionados.
    4. CALCULO DE PERDIDA: Ponle una metrica realista: "10 reservas perdidas al dia x 30 dias...".
    5. MORALEJA: Una leccion anti-intuitiva de negocio.
    6. CTA CERO PRESION: Ecosistemas digitales (Sistema 180) por 497 EUR. Si les duele regalar dinero que contesten. Si no, tan amigos.

    REGLA STRICTA: Devuelve la salida en un formato estricto:
    ASUNTO: [El asunto aqui]
    CUERPO: [El cuerpo del email aqui]
    NO PONGAS NADA MAS QUE ESO. Ni saludos de la IA ni meta-texto.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text

        # Parse output
        lines = text.strip().split('\n')
        subject = lines[0].replace("ASUNTO:", "").strip()
        body = "\n".join(lines[1:]).replace("CUERPO:", "").strip()
        return subject, body
    except Exception as e:
        print(f"  [ERROR] Cerebro fallo: {e}")
        return "Tus clientes se van", "Tus clientes se van. Respondeme si quieres cambiarlo. Jose Maria"


def send_email(to_address, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{SENDER} <{SMTP_EMAIL}>"
        msg["To"] = to_address
        msg["Subject"] = subject
        msg["Reply-To"] = SMTP_EMAIL
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"  [SMTP ERROR] {to_address}: {e}")
        return False

# ===============================================
# CICLO PRINCIPAL
# ===============================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  SISTEMA 180: CEREBRO DIGITAL AUTO-ADAPTATIVO (ESPECIAL 10K)")
    print("="*70)

    force_start = "--force" in sys.argv

    if not force_start:
        print(f"\n  FASE 1: Analisis Activo. Los scrapers estan recopilando datos en 2do plano.")
        print(f"  Objetivo de masa critica: {OBJETIVO_LEADS} perfiles.")
        while True:
            current_count = get_lead_count()
            porcentaje = (current_count / OBJETIVO_LEADS) * 100
            sys.stdout.write(f"\r  [SCAN] Progreso: {current_count} / {OBJETIVO_LEADS} correos ({porcentaje:.2f}%)")
            sys.stdout.flush()

            if current_count >= OBJETIVO_LEADS:
                print("\n\n  MASA CRITICA ALCANZADA. 10.000 correos analizados.")
                break
            time.sleep(5)

    # FASE 2: DESPERTAR EL CEREBRO Y ENVIAR
    print("\n  FASE 2: DESPERTANDO CEREBRO DIGITAL (GEMINI)...")
    if not cerebro_activo:
        print("  ALERTA: GEMINI_API_KEY no detectada. Saliendo.")
        sys.exit(1)

    print("  El Cerebro ha tomado el control. Leyendo matriz de leads y autoadaptando copy...")
    leads = get_all_leads()
    print(f"  Emails en cola: {len(leads)}")

    sent_count = 0
    for i, lead in enumerate(leads):
        print("-"*60)
        print(f"  [{i+1}/{len(leads)}] Analizando '{lead.get('name', '?')}' ({lead.get('category', '?')} en {lead.get('city', '?')})")
        print("  Reescribiendo mensaje con IA...")

        subj, body = digital_brain_rewrite(lead)

        print(f"  ASUNTO: {subj}")
        print("  Enviando...")

        success = send_email(lead.get('mail', ''), subj, body)
        if success:
            print("  [OK] ENVIADO")
            mark_as_sent(lead['id'])
            sent_count += 1
        else:
            print("  [FAIL] Error SMTP")

        time.sleep(2)

    print("\n" + "="*70)
    print(f"  RESULTADO FINAL: {sent_count} emails enviados")
    print("="*70)
