import sqlite3
conn = sqlite3.connect("crm.db")
t = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
n = conn.execute("SELECT COUNT(*) FROM leads WHERE status='nuevo'").fetchone()[0]
try:
    e = conn.execute("SELECT COUNT(DISTINCT email) FROM emails_sent").fetchone()[0]
except:
    e = 0
print("Total leads:", t)
print("Nuevos (sin contactar):", n)
print("Ya contactados:", e)
print()
rows = conn.execute("SELECT nicho, ciudad, COUNT(*) as c FROM leads GROUP BY nicho, ciudad ORDER BY c DESC LIMIT 15").fetchall()
print("TOP NICHOS:")
for r in rows:
    print("  {} {} -> {} leads".format(r[0], r[1], r[2]))
conn.close()
