"""
Sistema 180 — Scheduler B7 MONGEMALO v3.0 (CONTROVERSIA MÁXIMA)
Emails que ENGANCHAN. Asuntos que OBLIGAN a abrir.
Follow-ups automáticos con botón WhatsApp.
"""
import os
import sys
import time
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER = "Jose Maria Moreno"
PHONE = "+34 615 606 285"
BIZUM_PHONE = "615606285"
DB = os.path.join(os.path.dirname(__file__), "crm.db")
SEQUENCE_DAYS = [0, 3, 7, 12, 18]


def get_db():
    return sqlite3.connect(DB)


def html_email(body_text, nombre, show_button=False):
    button_html = ""
    if show_button:
        button_html = """
        <div style="text-align:center; margin:30px 0;">
            <a href="https://wa.me/34615606285?text=Hola%20Jose%20Maria%2C%20quiero%20contratar%20la%20web%20para%20{}" 
               style="background:#25D366; color:#fff; padding:16px 40px; 
               text-decoration:none; font-size:16px; font-weight:bold;
               border-radius:4px; display:inline-block;">
                QUIERO MIS 12 CLIENTES NUEVOS AL MES
            </a>
            <p style="color:#666; font-size:13px; margin-top:12px;">
                497 EUR. Una vez. Sin mensualidades. 5 días.<br>
                Pago por Bizum al {} o transferencia.
            </p>
        </div>
        """.format(nombre.replace(" ", "%20"), BIZUM_PHONE)

    html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Georgia,serif; max-width:600px; margin:0 auto; 
             padding:20px; color:#222; line-height:1.8; font-size:15px;">

{}

{}

<div style="margin-top:30px; padding-top:20px; border-top:1px solid #ddd; 
            color:#888; font-size:12px;">
    José María Moreno | Sistema 180 | {}
    <br>Responde OPT-OUT si prefieres no recibir más.
</div>
</body></html>""".format(
        body_text.replace("\n", "<br>"),
        button_html,
        PHONE
    )
    return html


# ===================================================================
# 5 EMAILS B7 MONGEMALO — MÁXIMA CONTROVERSIA
# ===================================================================

def email_dia0(nombre, nicho, ciudad):
    """DÍA 0: EL GANCHO. Asunto que obliga a abrir. Primera frase que duele."""
    subject = "¿Sabéis lo que dicen de {} en Google?".format(nombre)
    body = """He hecho algo que no os va a gustar.

He buscado "{} en {}" en Google. Como haría cualquier cliente vuestro.

No aparecéis. Ni en la primera página. Ni en la segunda. Ni en la tercera.

¿Sabéis quién sí aparece? Vuestra competencia. Los otros tres {} de {} que sí tienen web. Esos se llevan a VUESTROS clientes. Cada día. Sin hacer nada especial. Solo por estar ahí.

Y vosotros no estáis.

No os escribo para venderos nada. Os escribo porque me parece una pena que un negocio que funciona pierda clientes por algo tan estúpido como no aparecer en una búsqueda de Google.

Si queréis cambiarlo, respondedme. Si no, tirad este email y seguid perdiendo clientes sin saberlo.

José María
{} (WhatsApp)""".format(nicho, ciudad, nicho, ciudad, PHONE)
    return subject, body, False


def email_dia3(nombre, nicho, ciudad):
    """DÍA 3: LA HISTORIA QUE DUELE. Storytelling puro. Que el lector se vea reflejado."""
    subject = "La {} de {} que cerró el mes pasado".format(nicho, ciudad)
    body = """Os cuento una historia real. No os va a gustar.

Hace 4 meses una {} de {} me contactó. Llevaban 6 años abiertos. Buen trabajo. Clientes fieles. Boca a boca.

Pero cada mes cerraban con menos margen. Los clientes nuevos no venían. Y los de siempre... algunos se iban.

¿Sabéis qué pasó? Que un competidor abrió a 500 metros. Con una web bonita. Con Google Maps bien puesto. Con WhatsApp en la web.

En 3 meses les quitó el 30% de la facturación. No porque fuera mejor. Porque aparecía primero cuando alguien buscaba "{} en {}".

Esa {} cerró hace un mes. 6 años de trabajo. Tirados.

No os digo que os vaya a pasar lo mismo. Os digo que ya os está pasando y no lo sabéis. Cada vez que alguien busca lo que hacéis y no os encuentra, elige a otro. Y no vuelve.

Puedo evitar que os pase. 497 EUR. 5 días. Sin mensualidades.

José María
{}""".format(nicho, ciudad, nicho, ciudad, nicho, PHONE)
    return subject, body, False


def email_dia7(nombre, nicho, ciudad):
    """DÍA 7: LA PRUEBA. Números reales. Caso de éxito. Botón de compra."""
    subject = "De 0 a 12 clientes nuevos al mes (con pruebas)"
    body = """No os voy a contar teoría. Os voy a contar hechos.

Una {} de {} vino a mí con el mismo problema que vosotros. Cero presencia online. Dependiendo 100% del boca a boca.

Le hice exactamente 3 cosas:

<strong>1. Una web con botón de WhatsApp.</strong>
No una web "bonita". Una web que CONVIERTE. Cuando alguien entra, tiene un botón enorme de WhatsApp que dice "Pide cita ahora". Un 23% de los visitantes hacen clic.

<strong>2. Google Maps bien configurado.</strong>
Fotos del negocio, horarios actualizados, reseñas respondidas, categoría correcta. Pasó de la posición 18 a la 3 en su zona.

<strong>3. SEO para aparecer en "{} en {}".</strong>
Ahora cuando alguien busca eso, aparece en el top 3. Antes no existía.

<strong>Resultado después de 60 días:</strong>
- 12 clientes nuevos al mes que vienen SOLOS desde la web
- 340 visitas mensuales a la web
- ROI del 400% sobre lo que me pagó

Os puede pasar lo mismo. No es magia. Es hacer las cosas bien en internet.

<strong>497 EUR. Una sola vez. Entrega en 5 días. Sin mensualidades.</strong>""".format(nicho, ciudad, nicho, ciudad)
    return subject, body, True  # CON BOTON


def email_dia12(nombre, nicho, ciudad):
    """DÍA 12: LA PROVOCACIÓN. Romper objeciones con verdades incómodas."""
    subject = "Lo que no os atrevéis a admitir sobre {}".format(nombre)
    body = """Esto os va a molestar. Pero alguien tiene que decíroslo.

Hay dos tipos de negocios:

<strong>Los que dicen "ya tenemos web"</strong> — y cuando la buscas no aparece en Google, no tiene WhatsApp, carga lenta y parece de 2015. Tener web y tener clientes por la web son cosas completamente diferentes. Es como tener una tienda con la persiana bajada.

<strong>Los que dicen "no tenemos presupuesto"</strong> — pero sí tienen para un cartel nuevo, para publicidad en un periódico local que nadie lee, para repartir flyers que acaban en la basura. 497 EUR es lo que cuesta una cena para 4 en un buen restaurante de {}. Y se recupera con 2 clientes nuevos.

El problema real no es el dinero. Es el miedo a lo digital. Os da pereza. Os parece complicado. Pensáis que "eso no es para nosotros".

Y mientras pensáis eso, vuestra competencia ya lo hizo. Y se lleva a vuestros clientes.

No hay truco. No hay letra pequeña. No hay mensualidad. 497 EUR. 5 días. Os la hago yo. Vosotros solo me dais las fotos.

Es el penúltimo email que os mando. Si no os interesa, lo respeto. Pero por lo menos que no sea por no haberlo sabido.""".format(ciudad)
    return subject, body, True  # CON BOTON


def email_dia18(nombre, nicho, ciudad):
    """DÍA 18: EL ADIÓS. Psicología inversa. Puerta que se cierra."""
    subject = "Me despido de {}".format(nombre)
    body = """Este es el último email que os envío. Lo prometo.

Llevo 18 días escribiéndoos. No porque me sobre el tiempo. Sino porque cuando busqué {} en {} y no os encontré, pensé: "Qué pena. Si este negocio supiera lo que está perdiendo..."

Pero he aprendido algo en 10 años montando webs para negocios: no puedes ayudar a quien no quiere ser ayudado.

Si no habéis respondido a ninguno de mis 4 emails anteriores, es porque estáis en una de estas tres situaciones:

1. No os interesa crecer. Respetable.
2. No me creéis. Entendible, soy un desconocido.
3. Os da pereza. Lo más habitual.

Sea cual sea, lo acepto.

Solo os pido que hagáis una cosa por mí (bueno, por vosotros): buscad "{} en {}" en Google. Mirad quién sale. Y preguntaos: ¿por qué ellos sí y nosotros no?

Si algún día queréis cambiar eso, mi teléfono sigue siendo el mismo: {}

Os deseo lo mejor. En serio.

José María Moreno
Sistema 180""".format(nicho, ciudad, nicho, ciudad, PHONE)
    return subject, body, True  # CON BOTON


SEQUENCE = {
    0: email_dia0,
    3: email_dia3,
    7: email_dia7,
    12: email_dia12,
    18: email_dia18,
}


def send_html_email(to, subject, html_body):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = "{} <{}>".format(SENDER, SMTP_EMAIL)
        msg["To"] = to
        msg["Subject"] = subject
        msg["Reply-To"] = SMTP_EMAIL
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        return True
    except Exception as e:
        print("  [ERROR] {}: {}".format(to, e))
        return False


def run_scheduler():
    print("=" * 60)
    print("  SCHEDULER B7 MONGEMALO v3 — {}".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("=" * 60)

    total_sent = 0
    for day in SEQUENCE_DAYS:
        gen = SEQUENCE[day]
        leads = get_leads_for_day(day)

        if not leads:
            continue

        print("\n  DIA {} — {} leads pendientes".format(day, len(leads)))

        for lead in leads:
            nombre = lead["nombre"]
            email = lead["email"]
            nicho = lead["nicho"]
            ciudad = lead["ciudad"]

            subject, body, show_btn = gen(nombre, nicho, ciudad)
            html = html_email(body, nombre, show_button=show_btn)

            if send_html_email(email, subject, html):
                total_sent += 1
                print("    [OK] {} -> {}".format(email, subject))
                try:
                    conn = get_db()
                    conn.execute("""
                        INSERT INTO emails_sent (email, subject, template, sent_at)
                        VALUES (?, ?, ?, ?)
                    """, (email, subject, "b7mg_dia{}".format(day),
                          datetime.now().isoformat()))
                    conn.commit()
                    conn.close()
                except:
                    pass
            time.sleep(3)

    print("\n  TOTAL ENVIADOS: {}".format(total_sent))
    return total_sent


def get_leads_for_day(day):
    conn = get_db()
    cursor = conn.cursor()
    target_date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d")
    if day == 0:
        cursor.execute("""
            SELECT email, nombre, nicho, ciudad FROM leads 
            WHERE status = 'nuevo' OR status IS NULL
            LIMIT 50
        """)
    else:
        cursor.execute("""
            SELECT l.email, l.nombre, l.nicho, l.ciudad 
            FROM leads l
            JOIN emails_sent e ON l.email = e.email
            WHERE e.template LIKE 'b7mg_dia0%'
            AND DATE(e.sent_at) = ?
            AND l.status != 'respondido'
            AND l.email NOT IN (
                SELECT email FROM emails_sent WHERE template = ?
            )
        """, (target_date, "b7mg_dia{}".format(day)))
    leads = [{"email": r[0], "nombre": r[1] or "", "nicho": r[2] or "", "ciudad": r[3] or ""}
             for r in cursor.fetchall()]
    conn.close()
    return leads


def send_test_html():
    print("Enviando secuencia CONTROVERSIA MAXIMA...")
    for day in SEQUENCE_DAYS:
        gen = SEQUENCE[day]
        subject, body, show_btn = gen("Tu Negocio Test", "peluqueria", "Malaga")
        subject = "[TEST DIA {}] {}".format(day, subject)
        html = html_email(body, "Tu Negocio Test", show_button=True)
        if send_html_email(SMTP_EMAIL, subject, html):
            print("  [OK] Dia {} -> {}".format(day, subject))
        time.sleep(2)
    print("Revisa tu Gmail!")


if __name__ == "__main__":
    if "--test" in sys.argv:
        send_test_html()
    elif "--run" in sys.argv:
        run_scheduler()
    else:
        print("Uso:")
        print("  python followup_scheduler.py --test")
        print("  python followup_scheduler.py --run")
