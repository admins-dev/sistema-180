"""
outreach_db.py — Sistema 180
Base de datos SQLite auto-retroalimentada para outreach masivo.
- Pool de leads siempre lleno (Maps + IG hashtags + competidores)
- A/B testing automático de mensajes (promueve ganadores, retira perdedores)
- Aprende qué funciona: tipo negocio, hora de envío, zona, variante de mensaje
- Genera nuevas variantes con Claude cuando el pool de mensajes es bajo
"""
import sqlite3, os, json, logging
from datetime import datetime, date
from pathlib import Path
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DB_PATH = Path("outreach.db")

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS leads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_username   TEXT    UNIQUE,
    ig_id         TEXT,
    business_name TEXT,
    business_type TEXT    DEFAULT 'default',
    city          TEXT,
    phone         TEXT,
    website       TEXT,
    followers     INTEGER DEFAULT 0,
    bio           TEXT,
    source        TEXT    DEFAULT 'maps',   -- maps|hashtag|competitor|manual
    discovered_at TEXT    DEFAULT (datetime('now')),
    status        TEXT    DEFAULT 'pending', -- pending|sent|replied|converted|rejected|dnc
    priority      INTEGER DEFAULT 5         -- 1=hot, 10=cold
);

CREATE TABLE IF NOT EXISTS dms (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER REFERENCES leads(id),
    account     TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    variant_id  INTEGER,
    sent_at     TEXT    DEFAULT (datetime('now')),
    replied     INTEGER DEFAULT 0,
    reply_text  TEXT,
    sentiment   TEXT,     -- positive|negative|neutral|null
    converted   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS variants (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    business_type  TEXT    NOT NULL,
    message        TEXT    NOT NULL,
    sent_count     INTEGER DEFAULT 0,
    reply_count    INTEGER DEFAULT 0,
    convert_count  INTEGER DEFAULT 0,
    reply_rate     REAL    DEFAULT 0.0,
    active         INTEGER DEFAULT 1,
    champion       INTEGER DEFAULT 0,    -- 1 = mejor variante del tipo
    created_at     TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS account_perf (
    username    TEXT PRIMARY KEY,
    sent_today  INTEGER DEFAULT 0,
    sent_total  INTEGER DEFAULT 0,
    replies     INTEGER DEFAULT 0,
    reply_rate  REAL    DEFAULT 0.0,
    last_reset  TEXT,
    last_active TEXT
);

CREATE TABLE IF NOT EXISTS learning_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT    DEFAULT (datetime('now')),
    event      TEXT,   -- variant_promoted|variant_retired|variant_generated|champion_updated
    detail     TEXT
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_type   ON leads(business_type);
CREATE INDEX IF NOT EXISTS idx_dms_lead     ON dms(lead_id);
CREATE INDEX IF NOT EXISTS idx_variants_type ON variants(business_type, active);
"""

# ── Mensajes base iniciales por tipo ──────────────────────────────────────────
SEED_VARIANTS = {
    "peluqueria": [
        "Vi tu peluquería y me surgió una duda — ¿cuántos clientes pierdes por no contestar fuera de horario? Tengo algo que puede ayudarte.",
        "¿Tu peluquería tiene citas entrando solas? Hay una forma de automatizarlo sin complicaciones.",
        "Hola, vi tu salón. Una IA puede atender a tus clientes 24h por WhatsApp y cerrar citas automáticamente. ¿Te interesa ver cómo funciona?",
    ],
    "barberia": [
        "¿Cuántas llamadas para cita no puedes atender? Hay una forma de no perder ninguna.",
        "Vi tu barbería. ¿Cuántos clientes pierdes porque no puedes contestar mientras trabajas?",
        "Un bot de WhatsApp puede cerrar citas por ti mientras atiendes. ¿Quieres verlo en acción?",
    ],
    "estetica": [
        "Tus fotos están muy bien. ¿Tienes citas entrando solas por Instagram? Se puede automatizar.",
        "Vi tu centro de estética. ¿Sabes cuántos clientes mandan DM y no vuelven si no contestas en 5 min?",
        "Hola, vi tu trabajo. Una IA puede gestionar tus citas y contestar consultas 24h. ¿Te lo enseño?",
    ],
    "clinica": [
        "Vi tu clínica. ¿Cuántos pacientes pierdes por no contestar a tiempo? Hay algo que puede ayudarte.",
        "¿Tu consulta tiene lista de espera? Una IA puede gestionar citas y consultas 24h por WhatsApp.",
        "Hola, vi tu clínica. ¿Cuánto tiempo pierdes al día contestando WhatsApps de citas?",
    ],
    "default": [
        "Vi tu negocio — ¿cuántos clientes pierdes porque no contestas rápido? Tengo una solución sencilla.",
        "¿Sabías que el 67% de clientes se van si no contestas en 5 min? Una IA puede atender por ti 24h.",
        "Hola, vi tu negocio. ¿Tienes sistema para no perder clientes fuera de horario? Te enseño cómo.",
    ],
}


@contextmanager
def get_conn():
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Crea el schema y siembra variantes iniciales si la DB es nueva."""
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        for btype, messages in SEED_VARIANTS.items():
            for msg in messages:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO variants (business_type, message) VALUES (?,?)",
                        (btype, msg)
                    )
                except Exception:
                    pass
    logger.info(f"DB inicializada en {DB_PATH}")


# ══════════════════════════════════════════════════════════════════════════════
# LeadPool
# ══════════════════════════════════════════════════════════════════════════════

class LeadPool:

    def upsert(self, ig_username: str, **kwargs) -> int | None:
        """Inserta lead. Ignora si ya existe. Retorna id."""
        cols = ["ig_username"] + list(kwargs.keys())
        vals = [ig_username] + list(kwargs.values())
        placeholders = ",".join(["?"] * len(cols))
        col_str = ",".join(cols)
        try:
            with get_conn() as conn:
                cur = conn.execute(
                    f"INSERT OR IGNORE INTO leads ({col_str}) VALUES ({placeholders})",
                    vals
                )
                if cur.lastrowid:
                    return cur.lastrowid
                row = conn.execute("SELECT id FROM leads WHERE ig_username=?", (ig_username,)).fetchone()
                return row["id"] if row else None
        except Exception as e:
            logger.error(f"LeadPool.upsert: {e}")
            return None

    def bulk_upsert(self, leads: list[dict]) -> int:
        """Inserta múltiples leads. Retorna cuántos son nuevos."""
        count = 0
        for lead in leads:
            ig = lead.pop("ig_username", None)
            if ig and self.upsert(ig, **lead):
                count += 1
        return count

    def get_pending(self, limit: int = 50, business_type: str = None, city: str = None) -> list[dict]:
        """Saca leads pendientes ordenados por prioridad."""
        sql = "SELECT * FROM leads WHERE status='pending'"
        params = []
        if business_type:
            sql += " AND business_type=?"
            params.append(business_type)
        if city:
            sql += " AND city=?"
            params.append(city)
        sql += " ORDER BY priority ASC, discovered_at DESC LIMIT ?"
        params.append(limit)
        with get_conn() as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def count_by_status(self) -> dict:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) as n FROM leads GROUP BY status"
            ).fetchall()
            return {r["status"]: r["n"] for r in rows}

    def mark(self, lead_id: int, status: str):
        with get_conn() as conn:
            conn.execute("UPDATE leads SET status=? WHERE id=?", (status, lead_id))

    def pending_count(self) -> int:
        with get_conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM leads WHERE status='pending'").fetchone()[0]

    def is_known(self, ig_username: str) -> bool:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM leads WHERE ig_username=? AND status!='pending'", (ig_username,)
            ).fetchone()
            return row is not None


# ══════════════════════════════════════════════════════════════════════════════
# MessageBank — A/B testing + aprendizaje
# ══════════════════════════════════════════════════════════════════════════════

class MessageBank:

    def get_best(self, business_type: str) -> dict | None:
        """Devuelve el campeón actual, o la variante con mejor reply_rate activa."""
        with get_conn() as conn:
            # Primero el campeón explícito
            row = conn.execute(
                "SELECT * FROM variants WHERE business_type=? AND champion=1 AND active=1",
                (business_type,)
            ).fetchone()
            if row:
                return dict(row)
            # Fallback: mejor reply_rate con al menos 5 envíos
            row = conn.execute(
                "SELECT * FROM variants WHERE business_type=? AND active=1 AND sent_count>=5 "
                "ORDER BY reply_rate DESC LIMIT 1",
                (business_type,)
            ).fetchone()
            if row:
                return dict(row)
            # Cualquier variante activa
            row = conn.execute(
                "SELECT * FROM variants WHERE business_type=? AND active=1 "
                "ORDER BY RANDOM() LIMIT 1",
                (business_type,)
            ).fetchone()
            return dict(row) if row else None

    def get_for_ab_test(self, business_type: str) -> dict | None:
        """Para A/B: 70% campeón, 30% variante aleatoria activa."""
        import random
        if random.random() < 0.70:
            return self.get_best(business_type)
        with get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM variants WHERE business_type=? AND active=1 "
                "ORDER BY RANDOM() LIMIT 1",
                (business_type,)
            ).fetchone()
            return dict(row) if row else self.get_best(business_type)

    def record_sent(self, variant_id: int):
        with get_conn() as conn:
            conn.execute(
                "UPDATE variants SET sent_count=sent_count+1, "
                "reply_rate=CAST(reply_count AS REAL)/MAX(sent_count+1,1) "
                "WHERE id=?", (variant_id,)
            )

    def record_reply(self, variant_id: int, converted: bool = False):
        with get_conn() as conn:
            conn.execute(
                "UPDATE variants SET reply_count=reply_count+1, "
                f"{'convert_count=convert_count+1,' if converted else ''}"
                "reply_rate=CAST(reply_count+1 AS REAL)/MAX(sent_count,1) "
                "WHERE id=?", (variant_id,)
            )

    def run_learning_cycle(self):
        """
        Ciclo de aprendizaje:
        1. Actualiza reply_rate de todas las variantes
        2. Promueve campeones por tipo
        3. Retira variantes con reply_rate < 30% del promedio (si tienen >20 envíos)
        4. Genera nuevas variantes si hay < 3 activas por tipo
        """
        retired = 0
        promoted = 0
        generated = 0

        with get_conn() as conn:
            # 1. Actualizar reply_rate
            conn.execute("""
                UPDATE variants SET
                    reply_rate = CAST(reply_count AS REAL) / MAX(sent_count, 1)
                WHERE sent_count > 0
            """)

            # 2. Promover campeón por tipo
            types = [r[0] for r in conn.execute("SELECT DISTINCT business_type FROM variants").fetchall()]
            for btype in types:
                conn.execute(
                    "UPDATE variants SET champion=0 WHERE business_type=?", (btype,)
                )
                best = conn.execute(
                    "SELECT id FROM variants WHERE business_type=? AND active=1 AND sent_count>=5 "
                    "ORDER BY reply_rate DESC LIMIT 1", (btype,)
                ).fetchone()
                if best:
                    conn.execute("UPDATE variants SET champion=1 WHERE id=?", (best[0],))
                    promoted += 1

            # 3. Retirar perdedores (>20 envíos y reply_rate < 50% del promedio del tipo)
            for btype in types:
                avg = conn.execute(
                    "SELECT AVG(reply_rate) FROM variants WHERE business_type=? AND active=1 AND sent_count>=5",
                    (btype,)
                ).fetchone()[0] or 0
                if avg > 0:
                    cur = conn.execute(
                        "UPDATE variants SET active=0 "
                        "WHERE business_type=? AND sent_count>=20 AND reply_rate < ? AND champion=0",
                        (btype, avg * 0.4)
                    )
                    retired += cur.rowcount

            # Log
            if retired or promoted:
                conn.execute(
                    "INSERT INTO learning_log (event, detail) VALUES (?,?)",
                    ("cycle", json.dumps({"promoted": promoted, "retired": retired}))
                )

        # 4. Generar nuevas variantes si hay < 3 activas por tipo
        for btype in ["peluqueria", "barberia", "estetica", "clinica", "default"]:
            with get_conn() as conn:
                active_count = conn.execute(
                    "SELECT COUNT(*) FROM variants WHERE business_type=? AND active=1", (btype,)
                ).fetchone()[0]
            if active_count < 3:
                new_msg = self._generate_variant(btype)
                if new_msg:
                    with get_conn() as conn:
                        conn.execute(
                            "INSERT OR IGNORE INTO variants (business_type, message) VALUES (?,?)",
                            (btype, new_msg)
                        )
                        conn.execute(
                            "INSERT INTO learning_log (event, detail) VALUES (?,?)",
                            ("variant_generated", json.dumps({"type": btype, "msg": new_msg[:80]}))
                        )
                    generated += 1

        logger.info(f"[Learning] Ciclo: {promoted} promovidos, {retired} retirados, {generated} generados")
        return {"promoted": promoted, "retired": retired, "generated": generated}

    def _generate_variant(self, business_type: str) -> str | None:
        """Genera nueva variante con Claude basada en los mejores mensajes del tipo."""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not anthropic_key:
            return None
        try:
            with get_conn() as conn:
                top = conn.execute(
                    "SELECT message, reply_rate FROM variants WHERE business_type=? "
                    "ORDER BY reply_rate DESC LIMIT 3", (business_type,)
                ).fetchall()
            examples = "\n".join(f"- {r['message']} (reply_rate: {r['reply_rate']:.0%})" for r in top)

            from anthropic import Anthropic
            msg = Anthropic(api_key=anthropic_key).messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=150,
                system=(
                    "Creas DMs de Instagram para negocios locales en España. "
                    "2-3 líneas max. Natural, sin spam, sin emojis de relleno. "
                    "Termina con pregunta abierta. Solo el texto del DM."
                ),
                messages=[{
                    "role": "user",
                    "content": (
                        f"Tipo de negocio: {business_type}\n"
                        f"Mensajes que mejor funcionan:\n{examples}\n\n"
                        "Genera un nuevo DM diferente y potencialmente mejor. Solo el texto."
                    )
                }],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            logger.warning(f"generate_variant error: {e}")
            return None

    def add_variant(self, business_type: str, message: str) -> int:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO variants (business_type, message) VALUES (?,?)",
                (business_type, message)
            )
            return cur.lastrowid

    def get_stats(self) -> list[dict]:
        with get_conn() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT business_type, COUNT(*) as total, SUM(sent_count) as sent, "
                "SUM(reply_count) as replies, AVG(reply_rate) as avg_rate, "
                "MAX(reply_rate) as best_rate "
                "FROM variants WHERE active=1 GROUP BY business_type"
            ).fetchall()]


# ══════════════════════════════════════════════════════════════════════════════
# DmLog
# ══════════════════════════════════════════════════════════════════════════════

class DmLog:

    def record(self, lead_id: int, account: str, message: str, variant_id: int = None) -> int:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO dms (lead_id, account, message, variant_id) VALUES (?,?,?,?)",
                (lead_id, account, message, variant_id)
            )
            return cur.lastrowid

    def mark_replied(self, dm_id: int, reply_text: str, sentiment: str, converted: bool = False):
        with get_conn() as conn:
            conn.execute(
                "UPDATE dms SET replied=1, reply_text=?, sentiment=?, converted=? WHERE id=?",
                (reply_text[:500], sentiment, int(converted), dm_id)
            )

    def get_today_stats(self) -> dict:
        with get_conn() as conn:
            today = str(date.today())
            row = conn.execute(
                "SELECT COUNT(*) as sent, SUM(replied) as replies, SUM(converted) as conversions "
                "FROM dms WHERE DATE(sent_at)=?", (today,)
            ).fetchone()
            return dict(row) if row else {"sent": 0, "replies": 0, "conversions": 0}

    def get_account_today(self, account: str) -> int:
        with get_conn() as conn:
            today = str(date.today())
            return conn.execute(
                "SELECT COUNT(*) FROM dms WHERE account=? AND DATE(sent_at)=?", (account, today)
            ).fetchone()[0]

    def get_full_stats(self) -> dict:
        with get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM dms").fetchone()[0]
            replied = conn.execute("SELECT COUNT(*) FROM dms WHERE replied=1").fetchone()[0]
            converted = conn.execute("SELECT COUNT(*) FROM dms WHERE converted=1").fetchone()[0]
            today = self.get_today_stats()
        return {
            "total_sent": total,
            "total_replies": replied,
            "total_converted": converted,
            "reply_rate": f"{(replied/max(total,1)*100):.1f}%",
            "conversion_rate": f"{(converted/max(total,1)*100):.1f}%",
            "today": today,
        }


# ══════════════════════════════════════════════════════════════════════════════
# Helpers: DB report para Telegram
# ══════════════════════════════════════════════════════════════════════════════

def db_report() -> str:
    pool  = LeadPool()
    dml   = DmLog()
    bank  = MessageBank()

    counts = pool.count_by_status()
    stats  = dml.get_full_stats()
    msg_stats = bank.get_stats()

    lines = [
        "📊 *Sistema Outreach — Estado DB*\n",
        "👥 *Lead Pool:*",
    ]
    for s, n in counts.items():
        emoji = {"pending":"⏳","sent":"📤","replied":"💬","converted":"💰","rejected":"❌","dnc":"🚫"}.get(s,"•")
        lines.append(f"  {emoji} {s}: {n}")

    lines += [
        f"\n📤 *DMs Enviados:*",
        f"  Total: {stats['total_sent']} | Hoy: {stats['today']['sent']}",
        f"  Reply rate: {stats['reply_rate']} | Conversiones: {stats['total_converted']}",
        f"\n🧠 *Mensajes (A/B):*",
    ]
    for ms in msg_stats:
        lines.append(
            f"  {ms['business_type']}: {ms['total']} variantes | "
            f"mejor {ms['best_rate']:.0%} reply | avg {ms['avg_rate']:.0%}"
        )
    return "\n".join(lines)


# Init automático al importar
init_db()
