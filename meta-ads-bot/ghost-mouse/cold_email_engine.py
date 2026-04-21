"""
Sistema 180 — Cold Email Engine B7 + MONGEMALO v2.0

ESTILO MONGEMALO (5 patrones):
1. CONCISION BRUTAL: más feo, más simple, más telegráfico. Cuanto menos escribes, más te leen.
2. DESCRIBIR, NO ADJETIVAR: no digas "terrorífico", describe la escena y que el lector sienta.
3. IMPACTO EMOCIONAL INMEDIATO: primera frase que duele o que provoca.
4. VELOCIDAD: vender tiene que ver con ir rápido. Sin rodeos.
5. CLARIDAD > CREATIVIDAD: búscas que entienda y actúe, no que te admire.

FRAMEWORK B7: Personaje + Problema + Guía + Plan + CTA + Fracaso + Éxito
"""
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER = "Jose Maria Moreno"
PHONE = "+34 615 606 285"


# ===================================================================
# LINEA A — PYMES LOCALES — B7 MONGEMALO
# ===================================================================

def b7_dia0(nombre, nicho, ciudad):
    """Día 0: PERSONAJE + PROBLEMA. Impacto emocional inmediato."""
    subject = "{}, un problema".format(nombre)
    body = """He buscado {} en {} en Google.

No aparecéis.

Eso significa que cada día hay gente buscando exactamente lo que hacéis. Y eligen a otro. Porque a vosotros no os encuentran.

Si eso os da igual, tirad este email.

Si no, respondedme. Arreglo eso en 5 días.

José María
+34 615 606 285
---
Responde OPT-OUT si prefieres no recibir más.""".format(nicho, ciudad)
    return subject, body


def b7_dia3(nombre, nicho, ciudad):
    """Día 3: FRACASO. Lo que pierden por no actuar. Describir, no adjetivar."""
    subject = "Lo que pasa cada lunes en {}".format(nombre)
    body = """Es lunes.

Alguien busca "{} en {}" en Google. Aparecen 3 resultados. Ninguno es {}.

Esa persona elige al primero. Llama. Reserva. Paga.

Mañana pasa lo mismo. Y pasado. Y la semana que viene.

No es un problema de vuestro trabajo. Es un problema de que nadie os encuentra.

Puedo cambiarlo. 497 EUR. Una vez. Sin mensualidades.

Si os interesa, respondedme. Si no, sin rencor.

José María
---
Responde OPT-OUT para no recibir más.""".format(nicho, ciudad, nombre)
    return subject, body


def b7_dia7(nombre, nicho, ciudad):
    """Día 7: PLAN + ÉXITO. Caso real. Concisión brutal."""
    subject = "Esto hice con una {} de {}".format(nicho, ciudad)
    body = """Una {} de {} me contactó hace 2 meses.

Mismo problema que vosotros: buen trabajo, cero presencia en Google.

Le hice 3 cosas:
1. Web con WhatsApp directo.
2. Google Maps optimizado.
3. SEO para aparecer en "{} en {}".

Resultado: 12 clientes nuevos al mes desde la web. No ha hecho nada más.

497 EUR. Entrega en 5 días.

Si queréis los mismos números, respondedme.

José María | {}
---
Responde OPT-OUT para no recibir más.""".format(nicho, ciudad, nicho, ciudad, PHONE)
    return subject, body


def b7_dia12(nombre, nicho, ciudad):
    """Día 12: PROBLEMA INTERNO. Objeción anticipada. Sin adjetivos."""
    subject = "497 EUR"
    body = """Probablemente pensáis una de estas dos cosas:

1. "Ya tenemos web."
La vi. No aparece en Google. No tiene WhatsApp. No convierte.
Tener web y tener clientes por la web son cosas diferentes.

2. "No tenemos presupuesto para eso."
497 EUR. Una sola vez. Se recupera con 2 clientes nuevos.
Cada mes sin aparecer en Google os cuesta más que eso.

No hay truco. No hay letra pequeña. No hay mensualidad.

Si os interesa, respondedme. Si no, es el penúltimo email que recibiréis.

José María
---
Responde OPT-OUT para no recibir más.""".format()
    return subject, body


def b7_dia18(nombre, nicho, ciudad):
    """Día 18: ÉXITO + CIERRE. Último mensaje. Puerta abierta."""
    subject = "Ultimo email para {}".format(nombre)
    body = """Es el último email que os escribo.

Llevo 18 días intentando que {} aparezca cuando alguien busca {} en {} en Google.

Si no os interesa, perfecto. No soy de insistir.

Pero cada semana que pasa sin aparecer ahí son clientes que van a otro. Y no vuelven.

Si algún día queréis arreglarlo, aquí estaré. {} o este email.

Os deseo lo mejor.

José María Moreno
Sistema 180
---
Responde OPT-OUT y te elimino de mi lista.""".format(nombre, nicho, ciudad, PHONE)
    return subject, body


# Secuencia B7
B7_SEQUENCE = {
    0: b7_dia0,
    3: b7_dia3,
    7: b7_dia7,
    12: b7_dia12,
    18: b7_dia18,
}


# ===================================================================
# LINEA B — INFOPRODUCTORES — B7 MONGEMALO
# ===================================================================

def b7b_dia0(nombre, nicho, ciudad):
    """Línea B - Día 0."""
    subject = "{}, una pregunta".format(nombre)
    body = """Vi tu contenido sobre {}.

Buen material. En serio.

Pero tengo una duda: ¿cuántos de tus seguidores te compran?

Si la respuesta es "pocos", el problema no es tu contenido. Es tu sistema de ventas.

Publicas para likes. No para ventas. Y eso te va a quemar.

Monto sistemas que convierten seguidores en compradores. Sin funnels. Sin VSLs.

Si facturas más de 5k/mes y quieres escalar, respondeme. Si no, ignora esto.

José María | {}
---
Responde OPT-OUT si prefieres no recibir más.""".format(nicho, PHONE)
    return subject, body


def b7b_dia3(nombre, nicho, ciudad):
    """Línea B - Día 3."""
    subject = "El problema real de tu negocio"
    body = """Publicas 5 veces por semana.

Engagement decente. Comentarios. Likes. DMs de gente que te dice "qué crack".

Facturación: la misma de hace 6 meses.

Es el patrón. Lo he visto 100 veces. Audiencia grande. Pipeline vacío.

No es tu culpa. Nadie te enseñó a convertir audiencia en dinero. Solo te enseñaron a crear contenido.

Yo arreglo eso. 497 EUR de piloto. Si funciona, hablamos de partnership.

¿Te interesa o estás bien así?

José María
---
Responde OPT-OUT para no recibir más.""".format()
    return subject, body


B7B_SEQUENCE = {
    0: b7b_dia0,
    3: b7b_dia3,
}


# ===================================================================
# MOTOR DE ENVIO
# ===================================================================

def send_email(to, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = "{} <{}>".format(SENDER, SMTP_EMAIL)
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
        print("  [ERROR] {}: {}".format(to, e))
        return False


def send_test(line="A"):
    """Envía secuencia completa a tu email para revisión."""
    seq = B7_SEQUENCE if line == "A" else B7B_SEQUENCE
    nombre = "Peluqueria Ejemplo" if line == "A" else "Coach Ejemplo"
    nicho = "peluqueria" if line == "A" else "coaching"
    ciudad = "Malaga" if line == "A" else "Online"

    print("Enviando B7 MONGEMALO Linea {} a {}...".format(line, SMTP_EMAIL))
    for day, gen in sorted(seq.items()):
        subj, body = gen(nombre, nicho, ciudad)
        subj = "[B7-MONGEMALO DIA {}] {}".format(day, subj)
        if send_email(SMTP_EMAIL, subj, body):
            print("  [OK] Dia {}".format(day))
        else:
            print("  [FAIL] Dia {}".format(day))
        time.sleep(2)


def run_campaign(leads, day=0, dry_run=True):
    gen = B7_SEQUENCE.get(day, b7_dia0)
    mode = "DRY" if dry_run else "REAL"
    print("=" * 60)
    print("  B7 MONGEMALO {} — DIA {} — {} leads".format(mode, day, len(leads)))
    print("=" * 60)

    sent = 0
    for lead in leads:
        nombre = lead.get("nombre", "")
        email = lead.get("email", "")
        nicho = lead.get("nicho", lead.get("query", ""))
        ciudad = lead.get("ciudad", lead.get("city", ""))
        if not email:
            continue

        subj, body = gen(nombre, nicho, ciudad)
        if dry_run:
            print("  [DRY] {} -> {}".format(email, subj))
        else:
            if send_email(email, subj, body):
                sent += 1
                print("  [OK] {} -> {}".format(email, subj))
                try:
                    from email_crm import log_email_sent
                    log_email_sent(email, subj, "b7mg_dia{}".format(day))
                except:
                    pass
            time.sleep(3)

    print("\n  Resultado: {}".format(sent if not dry_run else len([l for l in leads if l.get("email")])))
    return sent


if __name__ == "__main__":
    import sys
    if "--test-b" in sys.argv:
        send_test("B")
    elif "--test" in sys.argv:
        send_test("A")
    elif "--real" in sys.argv:
        from email_crm import get_unsent_leads
        day = 0
        for a in sys.argv:
            if a.startswith("--day="):
                day = int(a.split("=")[1])
        leads = get_unsent_leads(50)
        run_campaign(leads, day=day, dry_run=False)
    else:
        from email_crm import get_unsent_leads
        leads = get_unsent_leads(5)
        run_campaign(leads, day=0, dry_run=True)
