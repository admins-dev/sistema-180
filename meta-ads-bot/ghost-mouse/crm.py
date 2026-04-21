"""
Ghost Mouse — CRM Database.
Controla todo el pipeline de ventas: leads, DMs, respuestas, cierres.
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "ghost_crm.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Crear tablas del CRM."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            instagram TEXT,
            website TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            niche TEXT,
            rating REAL,
            reviews INTEGER,
            maps_url TEXT,
            status TEXT DEFAULT 'new',
            -- Status: new, contacted, responded, interested, closed, rejected
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(instagram)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            account TEXT NOT NULL,
            message TEXT NOT NULL,
            direction TEXT DEFAULT 'out',
            -- Direction: out (nosotros), in (respuesta)
            status TEXT DEFAULT 'sent',
            -- Status: sent, delivered, read, failed
            sent_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        );

        CREATE TABLE IF NOT EXISTS accounts_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL,
            date TEXT NOT NULL,
            dms_sent INTEGER DEFAULT 0,
            dms_failed INTEGER DEFAULT 0,
            responses INTEGER DEFAULT 0,
            UNIQUE(account, date)
        );

        CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
        CREATE INDEX IF NOT EXISTS idx_leads_ig ON leads(instagram);
        CREATE INDEX IF NOT EXISTS idx_msgs_lead ON messages(lead_id);
    """)
    conn.commit()
    conn.close()
    print("[CRM] Base de datos inicializada")


# === LEADS ===

def add_lead(name, instagram=None, city=None, niche=None, **kwargs):
    """Añadir un lead al CRM."""
    conn = get_db()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO leads (name, instagram, city, niche, website, phone, address, rating, reviews, maps_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, instagram, city, niche,
            kwargs.get("website"), kwargs.get("phone"),
            kwargs.get("address"), kwargs.get("rating"),
            kwargs.get("reviews"), kwargs.get("maps_url"),
        ))
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    except:
        return None
    finally:
        conn.close()


def import_leads_from_json(json_path=None):
    """Importar leads desde el archivo JSON del lead_finder."""
    if json_path is None:
        json_path = os.path.join(os.path.dirname(__file__), "leads.json")
    
    if not os.path.exists(json_path):
        print("[CRM] No hay leads.json")
        return 0
    
    with open(json_path, "r", encoding="utf-8") as f:
        leads = json.load(f)
    
    imported = 0
    for lead in leads:
        ig = lead.get("instagram")
        if ig and ig != "popular":  # Filtrar falsos positivos
            result = add_lead(
                name=lead.get("name", ""),
                instagram=ig,
                city=lead.get("location", ""),
                niche=lead.get("query", ""),
                website=lead.get("website", ""),
                address=lead.get("address", ""),
            )
            if result:
                imported += 1
    
    print(f"[CRM] {imported} leads importados")
    return imported


def get_leads_to_contact(limit=20):
    """Obtener leads pendientes de contactar."""
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM leads
        WHERE status = 'new' AND instagram IS NOT NULL AND instagram != 'popular'
        ORDER BY rating DESC, reviews DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_lead_status(lead_id, status):
    """Actualizar estado de un lead."""
    conn = get_db()
    conn.execute("""
        UPDATE leads SET status = ?, updated_at = datetime('now') WHERE id = ?
    """, (status, lead_id))
    conn.commit()
    conn.close()


def get_pipeline_stats():
    """Estadísticas del pipeline."""
    conn = get_db()
    stats = {}
    for status in ["new", "contacted", "responded", "interested", "closed", "rejected"]:
        count = conn.execute("SELECT COUNT(*) FROM leads WHERE status = ?", (status,)).fetchone()[0]
        stats[status] = count
    stats["total"] = sum(stats.values())
    conn.close()
    return stats


# === MENSAJES ===

def log_message(lead_id, account, message, direction="out", status="sent"):
    """Registrar un mensaje enviado/recibido."""
    conn = get_db()
    conn.execute("""
        INSERT INTO messages (lead_id, account, message, direction, status)
        VALUES (?, ?, ?, ?, ?)
    """, (lead_id, account, message, direction, status))
    
    if direction == "out":
        update_lead_status(lead_id, "contacted")
        # Actualizar stats
        today = datetime.now().strftime("%Y-%m-%d")
        conn.execute("""
            INSERT INTO accounts_stats (account, date, dms_sent)
            VALUES (?, ?, 1)
            ON CONFLICT(account, date)
            DO UPDATE SET dms_sent = dms_sent + 1
        """, (account, today))
    
    conn.commit()
    conn.close()


def get_dms_sent_today(account):
    """Cuantos DMs ha enviado una cuenta hoy."""
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    row = conn.execute("""
        SELECT dms_sent FROM accounts_stats WHERE account = ? AND date = ?
    """, (account, today)).fetchone()
    conn.close()
    return row[0] if row else 0


def was_already_contacted(instagram):
    """Verificar si ya contactamos a este usuario."""
    conn = get_db()
    row = conn.execute("""
        SELECT COUNT(*) FROM leads WHERE instagram = ? AND status != 'new'
    """, (instagram,)).fetchone()
    conn.close()
    return row[0] > 0


# === INIT ===
init_db()

if __name__ == "__main__":
    # Importar leads existentes
    import_leads_from_json()
    
    # Mostrar stats
    stats = get_pipeline_stats()
    print(f"\n{'='*40}")
    print(f"  CRM PIPELINE")
    print(f"{'='*40}")
    for status, count in stats.items():
        bar = "█" * count
        print(f"  {status:12s} {count:4d} {bar}")
    print(f"{'='*40}")
