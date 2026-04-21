import sqlite3
import json
import os

# Check email_crm.db
print("=== EMAIL CRM ===")
conn = sqlite3.connect("email_crm.db")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    c = conn.execute("SELECT COUNT(*) FROM {}".format(t[0])).fetchone()[0]
    print("  {} = {} rows".format(t[0], c))
conn.close()

# Check ghost_crm.db
print("\n=== GHOST CRM ===")
conn = sqlite3.connect("ghost_crm.db")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    c = conn.execute("SELECT COUNT(*) FROM {}".format(t[0])).fetchone()[0]
    print("  {} = {} rows".format(t[0], c))
conn.close()

# Check JSON files
print("\n=== JSON LEADS ===")
for f in ["emails_leads.json", "emails_leads_massive.json", "leads.json"]:
    if os.path.exists(f):
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            print("  {} = {} entries".format(f, len(data)))
        elif isinstance(data, dict):
            total = sum(len(v) if isinstance(v, list) else 1 for v in data.values())
            print("  {} = {} entries (dict)".format(f, total))
