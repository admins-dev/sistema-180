"""
PLAN GUERRA 9 DÍAS — Conseguir 497€ (1 cliente)
Unifica todos los leads y dispara por TODOS los canales.
"""
import json
import sqlite3
import os
from datetime import datetime

DB = "crm.db"
EMAIL_DB = "email_crm.db"

def merge_all_leads():
    """Merge all lead sources into crm.db."""
    conn = sqlite3.connect(DB)
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
            created_at TEXT
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
    
    total_new = 0
    
    # 1. Import from emails_leads.json
    if os.path.exists("emails_leads.json"):
        with open("emails_leads.json", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            email = item.get("email", "")
            if email and "@" in email:
                try:
                    conn.execute("""INSERT OR IGNORE INTO leads 
                        (email, nombre, nicho, ciudad, source, status, created_at)
                        VALUES (?, ?, ?, ?, 'json_leads', 'nuevo', ?)""",
                        (email, item.get("nombre", ""), item.get("nicho", ""),
                         item.get("ciudad", "Malaga"), datetime.now().isoformat()))
                    total_new += 1
                except: pass
        print("  emails_leads.json -> importado")
    
    # 2. Import from emails_leads_massive.json
    if os.path.exists("emails_leads_massive.json"):
        with open("emails_leads_massive.json", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            email = item.get("email", "")
            if email and "@" in email:
                try:
                    conn.execute("""INSERT OR IGNORE INTO leads 
                        (email, nombre, nicho, ciudad, source, status, created_at)
                        VALUES (?, ?, ?, ?, 'json_massive', 'nuevo', ?)""",
                        (email, item.get("nombre", ""), item.get("nicho", ""),
                         item.get("ciudad", "Malaga"), datetime.now().isoformat()))
                    total_new += 1
                except: pass
        print("  emails_leads_massive.json -> importado")
    
    # 3. Import from leads.json (Instagram leads)
    if os.path.exists("leads.json"):
        with open("leads.json", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            email = item.get("email", "")
            if email and "@" in email:
                try:
                    conn.execute("""INSERT OR IGNORE INTO leads 
                        (email, nombre, nicho, ciudad, instagram, source, status, created_at)
                        VALUES (?, ?, ?, ?, ?, 'json_ig', 'nuevo', ?)""",
                        (email, item.get("nombre", ""), item.get("nicho", ""),
                         item.get("ciudad", "Malaga"), item.get("instagram", ""),
                         datetime.now().isoformat()))
                    total_new += 1
                except: pass
        print("  leads.json -> importado")
    
    # 4. Import from email_crm.db
    try:
        econn = sqlite3.connect(EMAIL_DB)
        rows = econn.execute("SELECT * FROM leads").fetchall()
        cols = [d[0] for d in econn.execute("SELECT * FROM leads LIMIT 1").description]
        for row in rows:
            d = dict(zip(cols, row))
            email = d.get("email", "")
            if email and "@" in email:
                try:
                    conn.execute("""INSERT OR IGNORE INTO leads 
                        (email, nombre, nicho, ciudad, source, status, created_at)
                        VALUES (?, ?, ?, ?, 'email_crm', 'nuevo', ?)""",
                        (email, d.get("nombre", ""), d.get("nicho", ""),
                         d.get("ciudad", "Malaga"), datetime.now().isoformat()))
                except: pass
        
        # Also import sent emails to avoid double-sending
        try:
            sent_rows = econn.execute("SELECT * FROM emails_sent").fetchall()
            sent_cols = [d[0] for d in econn.execute("SELECT * FROM emails_sent LIMIT 1").description]
            for row in sent_rows:
                d = dict(zip(sent_cols, row))
                try:
                    conn.execute("""INSERT OR IGNORE INTO emails_sent 
                        (email, subject, template, sent_at)
                        VALUES (?, ?, ?, ?)""",
                        (d.get("email", ""), d.get("subject", ""),
                         d.get("template", ""), d.get("sent_at", "")))
                except: pass
        except: pass
        
        econn.close()
        print("  email_crm.db -> importado")
    except Exception as e:
        print("  email_crm.db error: {}".format(e))
    
    # 5. Import from ghost_crm.db
    try:
        gconn = sqlite3.connect("ghost_crm.db")
        rows = gconn.execute("SELECT * FROM leads").fetchall()
        cols = [d[0] for d in gconn.execute("SELECT * FROM leads LIMIT 1").description]
        for row in rows:
            d = dict(zip(cols, row))
            ig = d.get("instagram", d.get("ig_username", ""))
            email = d.get("email", "")
            if not email and ig:
                email = "{}@instagram.placeholder".format(ig)
            if email:
                try:
                    conn.execute("""INSERT OR IGNORE INTO leads 
                        (email, nombre, nicho, ciudad, instagram, source, status, created_at)
                        VALUES (?, ?, ?, ?, ?, 'ghost_crm', 'nuevo', ?)""",
                        (email, d.get("nombre", d.get("business_name", "")),
                         d.get("nicho", d.get("category", "")),
                         d.get("ciudad", "Malaga"), ig,
                         datetime.now().isoformat()))
                except: pass
        gconn.close()
        print("  ghost_crm.db -> importado")
    except Exception as e:
        print("  ghost_crm.db error: {}".format(e))
    
    conn.commit()
    
    # Stats
    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    nuevos = conn.execute("SELECT COUNT(*) FROM leads WHERE email NOT IN (SELECT email FROM emails_sent)").fetchone()[0]
    contactados = conn.execute("SELECT COUNT(DISTINCT email) FROM emails_sent").fetchone()[0]
    
    print("\n" + "=" * 60)
    print("  RESULTADO UNIFICACIÓN")
    print("  Total leads en CRM: {}".format(total))
    print("  Ya contactados por email: {}".format(contactados))
    print("  NUEVOS SIN CONTACTAR: {}".format(nuevos))
    print("=" * 60)
    
    # List unsent leads
    unsent = conn.execute("""
        SELECT email, nombre, nicho, ciudad FROM leads 
        WHERE email NOT IN (SELECT email FROM emails_sent)
        AND email NOT LIKE '%placeholder%'
    """).fetchall()
    
    print("\n  LEADS LISTOS PARA DISPARAR:")
    for i, (email, nombre, nicho, ciudad) in enumerate(unsent, 1):
        print("  {}. {} ({}) - {} {}".format(i, email, nombre, nicho, ciudad))
    
    conn.close()
    return len(unsent)


if __name__ == "__main__":
    print("=" * 60)
    print("  PLAN GUERRA 9 DIAS — UNIFICANDO LEADS")
    print("=" * 60)
    n = merge_all_leads()
    
    print("\n" + "=" * 60)
    print("  PLAN DE ATAQUE (9 DIAS PARA 497€)")
    print("=" * 60)
    print("""
  DIA 1 (HOY): 
    - Enviar emails DIA 0 a TODOS los nuevos leads ({} pendientes)
    - Activar setters Instagram (Laura, Marta)
    - LinkedIn Ghost: buscar + conectar 5 perfiles
    
  DIA 2-3:
    - Follow-up DIA 3 a los 42 ya contactados
    - Responder cualquier respuesta INMEDIATAMENTE
    - LinkedIn: conectar 5 más + vagabundear
    
  DIA 4-5:
    - Follow-up DIA 7 (con BOTÓN de compra)
    - LinkedIn: mensajes a conexiones aceptadas
    - Instagram: 2da ronda DMs
    
  DIA 6-7:
    - Follow-up DIA 12 (provocación directa)
    - Todo el que responda → WhatsApp → Bizum
    
  DIA 8-9:
    - Follow-up DIA 18 (despedida)
    - Cierre agresivo a cualquier lead tibio
    
  NECESITAS: 1 CLIENTE DE 497€ = DEUDA PAGADA
  
  CONVERSIÓN ESPERADA:
    - ~80 emails enviados → ~5-8 respuestas (6-10%)
    - ~5-8 respuestas → 1-2 cierres (20-30%)
    - 1 cierre × 497€ = 497€ ✓
""".format(n))
