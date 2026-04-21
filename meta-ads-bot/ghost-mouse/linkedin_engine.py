"""
Sistema 180 — LinkedIn Prospecting Engine v1.0
Motor de prospección B2B por LinkedIn.
Usa los 15 ángulos + B7 + Mongemalo adaptados a LinkedIn.

LÍMITES SEGUROS (anti-ban):
  - 50 conexiones/semana
  - 15 mensajes/día
  - 40 visitas perfil/día
  - Delay humano entre acciones (30-90s)
"""
import os
import json
import time
import random
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

DB = os.path.join(os.path.dirname(__file__), "crm.db")
PHONE = "+34 615 606 285"

# Límites diarios anti-ban
MAX_CONNECTIONS_DAY = 8    # 50/semana = ~8/día
MAX_MESSAGES_DAY = 15
MAX_PROFILE_VISITS_DAY = 40
DELAY_MIN = 30  # segundos entre acciones
DELAY_MAX = 90

# ===================================================================
# MENSAJES LINKEDIN — ESTILO B7 MONGEMALO (15 ÁNGULOS ADAPTADOS)
# ===================================================================

# Nota de conexión (300 caracteres máx)
CONNECTION_NOTES = {
    "pyme": [
        # Ángulo 1: Dolor agudo
        "Hola {nombre}. He buscado {nicho} en {ciudad} en Google y no aparecéis. Sé cómo arreglarlo en 5 días. ¿Hablamos?",
        # Ángulo 5: Casos
        "Hola {nombre}. Acabo de ayudar a una {nicho} de {ciudad} a conseguir 12 clientes nuevos/mes con su web. ¿Os interesa?",
        # Ángulo 9: Urgencia
        "Hola {nombre}. Cada día que {nicho} no aparece en Google, alguien elige a vuestra competencia. Puedo cambiarlo por 497€.",
        # Ángulo 7: Contradicción
        "Hola {nombre}. El 90% de los negocios de {ciudad} tiene web pero CERO clientes desde internet. ¿Os pasa lo mismo?",
    ],
    "infoproductor": [
        # Ángulo 1: Dolor
        "Hola {nombre}. Vi tu contenido. Muy bueno. Pero ¿cuántos seguidores te compran? Si la respuesta duele, hablemos.",
        # Ángulo 3: Enemigo común
        "Hola {nombre}. Mientras montas tu funnel nº7, hay gente facturando con 1 post fijado + bot. ¿Quieres ver cómo?",
        # Ángulo 4: Método propio
        "Hola {nombre}. Tengo 57 agentes IA que montan sistemas de captación para infoproductores. Sin VSL. Sin landing. ¿Hablamos?",
        # Ángulo 2: Objeción
        "Hola {nombre}. No necesitas más seguidores para vender. Necesitas un sistema. Monto uno en 21 días. ¿Te interesa?",
    ],
}

# Mensaje 1 tras aceptar conexión (SIN límite caracteres)
FOLLOWUP_MSG1 = {
    "pyme": """Gracias por conectar, {nombre}.

Te cuento en 30 segundos lo que hago:

Monto webs para negocios locales que hacen 3 cosas:
1. Apareces en Google cuando alguien busca "{nicho} en {ciudad}"
2. Botón de WhatsApp directo para que te llamen
3. Google Maps bien configurado

Resultado típico: 12 clientes nuevos al mes desde la web.

497 EUR. Una vez. Sin mensualidades. Entrega en 5 días.

Si te interesa, escríbeme por WhatsApp al {phone} y te cuento.

Si no, sin rencor. Suerte con el negocio.""",

    "infoproductor": """Gracias por aceptar, {nombre}.

Monto sistemas de captación para infoproductores con IA.

No VSL. No funnel de 7 pasos. No landing de 3000 palabras.

El sistema es simple: Contenido → Ads → Perfil → DM → Bot → Cierre.

Tengo 57 agentes IA que automatizan el 80% del proceso.

Si facturas +5k/mes y quieres escalar sin quemarte, hablemos.

WhatsApp: {phone}

Si no, sin problema. Buen contenido el tuyo.""",
}

# Mensaje 2 - Si no responde en 3 días
FOLLOWUP_MSG2 = {
    "pyme": """Hola {nombre}, no te quiero molestar.

Solo una pregunta directa: ¿habéis mirado alguna vez cuántos clientes os está quitando Google al mes?

Si la respuesta es "no", probablemente son más de los que pensáis.

Última vez que os escribo. Si algún día os interesa: {phone}""",

    "infoproductor": """Hola {nombre}, última vez que te escribo.

Solo un dato: el 90% de infoproductores que conozco publican 5 veces por semana y venden lo mismo que hace un año.

El problema no es el contenido. Es que no tienen un sistema que convierta.

Si algún día quieres montarlo: {phone}""",
}

# ===================================================================
# BÚSQUEDA DE PERFILES TARGET
# ===================================================================

LINKEDIN_SEARCH_QUERIES = {
    "pyme": [
        "dueño peluquería Málaga",
        "propietario restaurante Málaga",
        "dueño gimnasio Málaga",
        "directora clínica dental Málaga",
        "propietario taller mecánico Málaga",
        "dueño inmobiliaria Málaga",
        "fisioterapeuta Málaga autónomo",
        "psicólogo consulta privada Málaga",
        "propietario autoescuela Málaga",
        "dueña centro estética Málaga",
        "veterinario clínica Málaga",
        "propietario óptica Málaga",
        "dueño bar restaurante Torremolinos",
        "dueño negocio Marbella",
        "autónomo Málaga servicios",
    ],
    "infoproductor": [
        "coach online España",
        "consultor marketing digital",
        "formador online emprendimiento",
        "mentor negocios digitales",
        "infoproductor España",
        "creador de cursos online",
        "consultora de marca personal",
        "coach de nutrición online",
        "mentor financiero España",
        "formador ventas B2B",
    ],
}


# ===================================================================
# CRM LINKEDIN
# ===================================================================

def init_linkedin_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS linkedin_leads (
            profile_url TEXT PRIMARY KEY,
            nombre TEXT,
            cargo TEXT,
            empresa TEXT,
            ciudad TEXT,
            tipo TEXT DEFAULT 'pyme',
            status TEXT DEFAULT 'nuevo',
            connection_sent_at TEXT,
            connection_accepted_at TEXT,
            msg1_sent_at TEXT,
            msg2_sent_at TEXT,
            replied_at TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS linkedin_daily_log (
            date TEXT,
            connections_sent INTEGER DEFAULT 0,
            messages_sent INTEGER DEFAULT 0,
            profiles_visited INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_daily_counts(date=None):
    """Get today's action counts to respect limits."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT connections_sent, messages_sent, profiles_visited FROM linkedin_daily_log WHERE date=?",
        (date,)
    ).fetchone()
    conn.close()
    if row:
        return {"connections": row[0], "messages": row[1], "visits": row[2]}
    return {"connections": 0, "messages": 0, "visits": 0}


def log_action(action_type):
    """Log a LinkedIn action for rate limiting."""
    date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB)
    conn.execute("""
        INSERT INTO linkedin_daily_log (date, connections_sent, messages_sent, profiles_visited)
        VALUES (?, 0, 0, 0)
        ON CONFLICT(date) DO NOTHING
    """, (date,))
    
    col_map = {
        "connection": "connections_sent",
        "message": "messages_sent", 
        "visit": "profiles_visited",
    }
    col = col_map.get(action_type)
    if col:
        conn.execute(
            "UPDATE linkedin_daily_log SET {} = {} + 1 WHERE date = ?".format(col, col),
            (date,)
        )
    conn.commit()
    conn.close()


def save_linkedin_lead(profile_url, nombre, cargo="", empresa="", ciudad="", tipo="pyme"):
    conn = sqlite3.connect(DB)
    try:
        conn.execute("""
            INSERT OR IGNORE INTO linkedin_leads 
            (profile_url, nombre, cargo, empresa, ciudad, tipo, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'nuevo', ?)
        """, (profile_url, nombre, cargo, empresa, ciudad, tipo, datetime.now().isoformat()))
        conn.commit()
    except:
        pass
    conn.close()


def get_connection_note(tipo, nombre, nicho="", ciudad="Málaga"):
    """Get a random connection note for the lead type."""
    notes = CONNECTION_NOTES.get(tipo, CONNECTION_NOTES["pyme"])
    note = random.choice(notes)
    return note.format(nombre=nombre, nicho=nicho, ciudad=ciudad)[:300]


def get_followup1(tipo, nombre, nicho="", ciudad="Málaga"):
    template = FOLLOWUP_MSG1.get(tipo, FOLLOWUP_MSG1["pyme"])
    return template.format(nombre=nombre, nicho=nicho, ciudad=ciudad, phone=PHONE)


def get_followup2(tipo, nombre, nicho="", ciudad="Málaga"):
    template = FOLLOWUP_MSG2.get(tipo, FOLLOWUP_MSG2["pyme"])
    return template.format(nombre=nombre, phone=PHONE)


def human_delay():
    """Simulate human behavior with random delay."""
    delay = random.uniform(DELAY_MIN, DELAY_MAX)
    print("    [WAIT] {:.0f}s...".format(delay))
    time.sleep(delay)


# ===================================================================
# REPORTS
# ===================================================================

def daily_report():
    """Print daily LinkedIn prospecting report."""
    conn = sqlite3.connect(DB)
    
    total = conn.execute("SELECT COUNT(*) FROM linkedin_leads").fetchone()[0]
    nuevo = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE status='nuevo'").fetchone()[0]
    conn_sent = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE connection_sent_at IS NOT NULL").fetchone()[0]
    accepted = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE connection_accepted_at IS NOT NULL").fetchone()[0]
    msg1 = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE msg1_sent_at IS NOT NULL").fetchone()[0]
    replied = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE replied_at IS NOT NULL").fetchone()[0]
    
    counts = get_daily_counts()
    
    conn.close()
    
    print("=" * 60)
    print("  LINKEDIN REPORT — {}".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("=" * 60)
    print("  Total leads: {}".format(total))
    print("  Nuevos: {}".format(nuevo))
    print("  Conexiones enviadas: {}".format(conn_sent))
    print("  Conexiones aceptadas: {}".format(accepted))
    print("  Mensajes enviados: {}".format(msg1))
    print("  Respondieron: {}".format(replied))
    print("")
    print("  HOY:")
    print("  Conexiones: {}/{}".format(counts["connections"], MAX_CONNECTIONS_DAY))
    print("  Mensajes: {}/{}".format(counts["messages"], MAX_MESSAGES_DAY))
    print("  Visitas: {}/{}".format(counts["visits"], MAX_PROFILE_VISITS_DAY))
    print("=" * 60)


if __name__ == "__main__":
    init_linkedin_db()
    
    print("=" * 60)
    print("  LINKEDIN PROSPECTING ENGINE v1.0")
    print("  Sistema 180 — B7 + Mongemalo")
    print("=" * 60)
    print("\n  NOTAS DE CONEXIÓN (ejemplos):")
    print("\n  --- PYME ---")
    for i, note in enumerate(CONNECTION_NOTES["pyme"], 1):
        print("  {}. {}".format(i, note.format(
            nombre="Peluquería María", nicho="peluquería", ciudad="Málaga"
        )[:300]))
    
    print("\n  --- INFOPRODUCTOR ---")
    for i, note in enumerate(CONNECTION_NOTES["infoproductor"], 1):
        print("  {}. {}".format(i, note.format(
            nombre="Carlos Coach", nicho="coaching", ciudad="Online"
        )[:300]))
    
    print("\n  FOLLOW-UP 1 (ejemplo PYME):")
    print(get_followup1("pyme", "Peluquería María", "peluquería", "Málaga"))
    
    daily_report()
