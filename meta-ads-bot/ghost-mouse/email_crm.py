"""
Sistema 180 - CRM de Email Marketing v1.0
Trackea todos los emails enviados, abiertos, respondidos.
Conecta con el scraper masivo de Google Maps.
"""
import json
import os
import sqlite3
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "email_crm.db")


def get_db():
    """Conectar a la base de datos SQLite del CRM."""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            email TEXT UNIQUE,
            telefono TEXT,
            website TEXT,
            nicho TEXT,
            ciudad TEXT,
            fuente TEXT DEFAULT 'google_maps',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS emails_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            email_to TEXT,
            asunto TEXT,
            template TEXT,
            status TEXT DEFAULT 'sent',
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
            opened_at TEXT,
            replied_at TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            fecha TEXT UNIQUE,
            emails_enviados INTEGER DEFAULT 0,
            emails_abiertos INTEGER DEFAULT 0,
            emails_respondidos INTEGER DEFAULT 0,
            leads_nuevos INTEGER DEFAULT 0,
            cierres INTEGER DEFAULT 0,
            facturado REAL DEFAULT 0
        )
    """)
    db.commit()
    return db


def add_lead(nombre, email, nicho="", ciudad="", website="", telefono="", fuente="google_maps"):
    """Agregar un lead al CRM."""
    db = get_db()
    try:
        db.execute(
            "INSERT OR IGNORE INTO leads (nombre, email, nicho, ciudad, website, telefono, fuente) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nombre, email, nicho, ciudad, website, telefono, fuente)
        )
        db.commit()
    except Exception as e:
        print("  Error agregando lead: {}".format(e))
    finally:
        db.close()


def add_leads_bulk(leads_list):
    """Agregar lista de leads al CRM."""
    db = get_db()
    count = 0
    for lead in leads_list:
        try:
            db.execute(
                "INSERT OR IGNORE INTO leads (nombre, email, nicho, ciudad, website, fuente) VALUES (?, ?, ?, ?, ?, ?)",
                (lead.get("nombre", ""), lead.get("email", ""), lead.get("query", lead.get("nicho", "")),
                 lead.get("city", lead.get("ciudad", "")), lead.get("website", ""), lead.get("fuente", "google_maps"))
            )
            count += 1
        except:
            pass
    db.commit()
    db.close()
    print("  {} leads importados al CRM".format(count))
    return count


def log_email_sent(email_to, asunto, template="template_1"):
    """Registrar un email enviado."""
    db = get_db()
    lead = db.execute("SELECT id FROM leads WHERE email = ?", (email_to,)).fetchone()
    lead_id = lead["id"] if lead else None

    db.execute(
        "INSERT INTO emails_sent (lead_id, email_to, asunto, template) VALUES (?, ?, ?, ?)",
        (lead_id, email_to, asunto, template)
    )

    # Actualizar stats del dia
    hoy = date.today().isoformat()
    db.execute(
        "INSERT INTO daily_stats (fecha, emails_enviados) VALUES (?, 1) ON CONFLICT(fecha) DO UPDATE SET emails_enviados = emails_enviados + 1",
        (hoy,)
    )
    db.commit()
    db.close()


def log_email_opened(email_to):
    """Marcar un email como abierto."""
    db = get_db()
    db.execute("UPDATE emails_sent SET opened_at = ? WHERE email_to = ? AND opened_at IS NULL",
               (datetime.now().isoformat(), email_to))
    hoy = date.today().isoformat()
    db.execute(
        "INSERT INTO daily_stats (fecha, emails_abiertos) VALUES (?, 1) ON CONFLICT(fecha) DO UPDATE SET emails_abiertos = emails_abiertos + 1",
        (hoy,)
    )
    db.commit()
    db.close()


def log_email_replied(email_to):
    """Marcar un email como respondido."""
    db = get_db()
    db.execute("UPDATE emails_sent SET replied_at = ?, status = 'replied' WHERE email_to = ? AND replied_at IS NULL",
               (datetime.now().isoformat(), email_to))
    hoy = date.today().isoformat()
    db.execute(
        "INSERT INTO daily_stats (fecha, emails_respondidos) VALUES (?, 1) ON CONFLICT(fecha) DO UPDATE SET emails_respondidos = emails_respondidos + 1",
        (hoy,)
    )
    db.commit()
    db.close()


def get_daily_report():
    """Resumen del dia."""
    db = get_db()
    hoy = date.today().isoformat()

    stats = db.execute("SELECT * FROM daily_stats WHERE fecha = ?", (hoy,)).fetchone()
    total_leads = db.execute("SELECT COUNT(*) as c FROM leads").fetchone()["c"]
    total_sent = db.execute("SELECT COUNT(*) as c FROM emails_sent").fetchone()["c"]
    total_replied = db.execute("SELECT COUNT(*) as c FROM emails_sent WHERE status = 'replied'").fetchone()["c"]
    pending = db.execute("SELECT COUNT(*) as c FROM leads WHERE email NOT IN (SELECT email_to FROM emails_sent)").fetchone()["c"]

    report = {
        "fecha": hoy,
        "leads_totales": total_leads,
        "emails_totales_enviados": total_sent,
        "emails_respondidos": total_replied,
        "leads_sin_contactar": pending,
        "hoy": {
            "enviados": stats["emails_enviados"] if stats else 0,
            "abiertos": stats["emails_abiertos"] if stats else 0,
            "respondidos": stats["emails_respondidos"] if stats else 0,
        }
    }

    db.close()
    return report


def get_unsent_leads(limit=50):
    """Leads que aun no han sido contactados."""
    db = get_db()
    rows = db.execute("""
        SELECT * FROM leads 
        WHERE email NOT IN (SELECT email_to FROM emails_sent)
        ORDER BY created_at ASC
        LIMIT ?
    """, (limit,)).fetchall()
    db.close()
    return [dict(r) for r in rows]


def import_from_json(filepath):
    """Importar leads desde emails_leads.json al CRM."""
    with open(filepath, "r", encoding="utf-8") as f:
        leads = json.load(f)
    return add_leads_bulk(leads)


def print_dashboard():
    """Imprimir dashboard del CRM."""
    report = get_daily_report()

    print("=" * 60)
    print("  SISTEMA 180 - CRM EMAIL MARKETING")
    print("  Fecha: {}".format(report["fecha"]))
    print("=" * 60)
    print("")
    print("  TOTALES:")
    print("    Leads en base: {}".format(report["leads_totales"]))
    print("    Emails enviados: {}".format(report["emails_totales_enviados"]))
    print("    Respondidos: {}".format(report["emails_respondidos"]))
    print("    Sin contactar: {}".format(report["leads_sin_contactar"]))
    print("")
    print("  HOY ({})".format(report["fecha"]))
    print("    Enviados hoy: {}".format(report["hoy"]["enviados"]))
    print("    Abiertos hoy: {}".format(report["hoy"]["abiertos"]))
    print("    Respondidos hoy: {}".format(report["hoy"]["respondidos"]))
    print("")

    # Leads pendientes
    pending = get_unsent_leads(10)
    if pending:
        print("  PROXIMOS LEADS A CONTACTAR:")
        for l in pending[:10]:
            print("    - {} ({}) [{}]".format(l["nombre"], l["email"], l["nicho"]))


if __name__ == "__main__":
    # Importar leads existentes
    leads_file = os.path.join(os.path.dirname(__file__), "emails_leads.json")
    if os.path.exists(leads_file):
        print("Importando leads desde emails_leads.json...")
        import_from_json(leads_file)

    print_dashboard()
