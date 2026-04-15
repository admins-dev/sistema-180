"""
outreach_engine.py — Sistema 180
Motor de outreach continuo 24/7.
- Rellena el pool de leads automáticamente cuando baja de umbral
- Envía DMs sin parar rotando cuentas, respetando límites anti-ban
- A/B testing: 70% campeón, 30% experimentación
- Ciclo de aprendizaje cada 50 DMs enviados
- Monitoreo de respuestas (inspecciona inbox y actualiza DB)
"""
import os, asyncio, random, logging, time
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

from outreach_db import LeadPool, MessageBank, DmLog, db_report

# Config
LEAD_POOL_MIN     = 100   # Rellena cuando hay menos de esto pendientes
LEARNING_EVERY    = 50    # Ciclo aprendizaje cada N DMs
INBOX_CHECK_EVERY = 300   # Segundos entre checks de inbox
FILL_ZONES = [
    ("Marbella",        36.5100, -4.8861),
    ("Málaga",          36.7213, -4.4214),
    ("Fuengirola",      36.5403, -4.6250),
    ("Torremolinos",    36.6219, -4.4997),
    ("Benalmádena",     36.5997, -4.5169),
    ("Mijas",           36.5965, -4.6378),
    ("Estepona",        36.4278, -5.1473),
    ("Nerja",           36.7460, -3.8729),
    ("Vélez-Málaga",    36.7831, -4.1002),
    ("Antequera",       37.0209, -4.5607),
    ("Ronda",           36.7463, -5.1641),
    ("Algeciras",       36.1427, -5.4553),
    ("Sevilla",         37.3891, -5.9845),
    ("Granada",         37.1773, -3.5986),
    ("Córdoba",         37.8882, -4.7794),
    ("Almería",         36.8340, -2.4637),
]
FILL_TYPES = [
    "peluquería", "barbería", "centro de estética",
    "clínica dental", "fisioterapia", "spa", "uñas", "salón de belleza",
]


class OutreachEngine:
    """Motor de outreach continuo. Singleton controlado por start()/stop()."""

    def __init__(self, notify_fn=None):
        self._running      = False
        self._task         = None
        self._notify       = notify_fn   # async fn(str)
        self._dms_since_learn = 0
        self._last_inbox_check = 0
        self._fill_idx     = 0   # round-robin zonas/tipos
        self.pool   = LeadPool()
        self.bank   = MessageBank()
        self.dmlog  = DmLog()

    # ── Control ───────────────────────────────────────────────────────────────

    def start(self, notify_fn=None):
        if self._running:
            return False
        if notify_fn:
            self._notify = notify_fn
        self._running = True
        self._task = asyncio.ensure_future(self._loop())
        logger.info("OutreachEngine iniciado")
        return True

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("OutreachEngine detenido")

    @property
    def is_running(self) -> bool:
        return self._running

    # ── Loop principal ────────────────────────────────────────────────────────

    async def _loop(self):
        await self._notify_safe("🟢 Motor de outreach iniciado. Enviando DMs continuamente...")
        while self._running:
            try:
                # 1. Rellenar pool si baja del umbral
                pending = self.pool.pending_count()
                if pending < LEAD_POOL_MIN:
                    await self._fill_pool()

                # 2. Intentar enviar un DM
                sent = await self._send_one()

                # 3. Ciclo de aprendizaje
                if sent:
                    self._dms_since_learn += 1
                    if self._dms_since_learn >= LEARNING_EVERY:
                        await self._run_learning()
                        self._dms_since_learn = 0

                # 4. Check inbox cada INBOX_CHECK_EVERY segundos
                if time.time() - self._last_inbox_check > INBOX_CHECK_EVERY:
                    await self._check_inbox()
                    self._last_inbox_check = time.time()

                # 5. Pausa entre intentos
                if sent:
                    delay = random.uniform(35, 75)
                    await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(30)  # sin cuentas disponibles: esperar

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"OutreachEngine loop error: {e}", exc_info=True)
                await asyncio.sleep(60)

        await self._notify_safe("🔴 Motor de outreach detenido.")

    # ── Enviar un DM ──────────────────────────────────────────────────────────

    async def _send_one(self) -> bool:
        from ig_multi_account import get_store, get_best_session, generate_dm

        store = get_store()
        best_acc = store.best_account()
        if not best_acc:
            return False   # todas las cuentas en límite hoy

        leads = self.pool.get_pending(limit=5)
        if not leads:
            return False   # pool vacío

        lead = leads[0]
        sess = get_best_session()
        if not sess:
            return False

        # Variante A/B
        variant = self.bank.get_for_ab_test(lead.get("business_type", "default"))

        if variant:
            msg_text = variant["message"]
            variant_id = variant["id"]
            self.bank.record_sent(variant_id)
        else:
            msg_text = generate_dm(
                business_name=lead.get("business_name", ""),
                ig_username=lead.get("ig_username", ""),
                bio=lead.get("bio", ""),
                city=lead.get("city", ""),
                tipo=lead.get("business_type", "default"),
            )
            variant_id = None

        # Obtener IG id si no lo tenemos
        ig_id = lead.get("ig_id")
        ig_username = lead.get("ig_username", "")
        if not ig_id and ig_username:
            try:
                ig_id = str(sess.cl.user_id_from_username(ig_username))
                with __import__("outreach_db").get_conn() as conn:
                    conn.execute("UPDATE leads SET ig_id=? WHERE id=?", (ig_id, lead["id"]))
            except Exception as e:
                logger.warning(f"user_id_from_username({ig_username}): {e}")
                self.pool.mark(lead["id"], "error")
                return False

        # Enviar
        ok = await asyncio.get_event_loop().run_in_executor(
            None, lambda: sess.send_dm(ig_id, msg_text)
        )

        if ok:
            self.pool.mark(lead["id"], "sent")
            dm_id = self.dmlog.record(lead["id"], sess.username, msg_text, variant_id)
            logger.info(f"✅ DM enviado a @{ig_username} desde @{sess.username}")
            return True
        else:
            self.pool.mark(lead["id"], "error")
            return False

    # ── Rellenar pool ─────────────────────────────────────────────────────────

    async def _fill_pool(self):
        """Rellena el pool con leads de Google Maps y búsquedas de hashtag."""
        maps_key = os.getenv("GOOGLE_MAPS_KEY", "")
        if not maps_key:
            return

        # Round-robin: siguiente zona/tipo
        zone_name, lat, lng = FILL_ZONES[self._fill_idx % len(FILL_ZONES)]
        btype = FILL_TYPES[self._fill_idx % len(FILL_TYPES)]
        self._fill_idx += 1

        logger.info(f"Rellenando pool: {btype} en {zone_name}")

        new_count = await asyncio.get_event_loop().run_in_executor(
            None, lambda: self._fill_from_maps(zone_name, btype, lat, lng)
        )

        if new_count > 0:
            logger.info(f"Pool +{new_count} leads ({btype} / {zone_name})")
        await asyncio.sleep(2)

    def _fill_from_maps(self, city: str, btype: str, lat: float, lng: float) -> int:
        """Sincronizado: Google Maps → extrae IG → añade a pool."""
        try:
            from lead_factory import search_places, get_place_details
            from ig_multi_account import find_ig_handle, generate_dm, _detect_type
        except ImportError as e:
            logger.error(f"Import error en _fill_from_maps: {e}")
            return 0

        places = search_places(f"{btype} {city}", lat, lng, radius=8000)
        leads_to_add = []

        for place in places[:30]:
            name = place.get("name", "")
            details = get_place_details(place.get("place_id", ""))
            website = details.get("website", "")
            phone   = details.get("phone", "")

            # Intentar encontrar Instagram
            handle = find_ig_handle(name, city, website)
            if not handle:
                continue

            if self.pool.is_known(handle):
                continue

            leads_to_add.append({
                "ig_username":   handle,
                "business_name": name,
                "business_type": _detect_type(name, ""),
                "city":          city,
                "phone":         phone,
                "website":       website,
                "source":        "maps",
                "priority":      5,
            })

        return self.pool.bulk_upsert(leads_to_add)

    # ── Check inbox ───────────────────────────────────────────────────────────

    async def _check_inbox(self):
        """Revisa inbox de todas las cuentas buscando respuestas a DMs."""
        from ig_multi_account import get_store, _sessions

        store = get_store()
        for acc in store.get_all():
            if acc.get("status") != "ok":
                continue
            username = acc["username"]
            sess = _sessions.get(username)
            if not sess or not sess.cl:
                continue
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda s=sess: self._process_inbox(s)
                )
            except Exception as e:
                logger.warning(f"check_inbox({username}): {e}")

    def _process_inbox(self, sess):
        """Sincronizado: lee inbox y actualiza DB con respuestas."""
        try:
            threads = sess.cl.direct_threads(amount=20)
            for thread in threads:
                if not thread.messages:
                    continue
                last_msg = thread.messages[0]
                # Si el último mensaje es de ellos (reply a nuestro DM)
                if str(last_msg.user_id) != str(sess.cl.user_id):
                    reply_text = getattr(last_msg, "text", "") or ""
                    if not reply_text:
                        continue

                    # Buscar el lead en DB por username del thread
                    try:
                        other_user = [u for u in thread.users if str(u.pk) != str(sess.cl.user_id)]
                        if not other_user:
                            continue
                        their_username = other_user[0].username
                    except Exception:
                        continue

                    with __import__("outreach_db").get_conn() as conn:
                        lead = conn.execute(
                            "SELECT id FROM leads WHERE ig_username=?", (their_username,)
                        ).fetchone()
                        if not lead:
                            continue
                        lead_id = lead[0]

                        # Actualizar estado lead
                        conn.execute(
                            "UPDATE leads SET status='replied' WHERE id=? AND status='sent'",
                            (lead_id,)
                        )

                        # Buscar el DM original para actualizar replied
                        dm = conn.execute(
                            "SELECT id, variant_id FROM dms WHERE lead_id=? AND replied=0 ORDER BY sent_at DESC LIMIT 1",
                            (lead_id,)
                        ).fetchone()
                        if dm:
                            sentiment = self._classify_sentiment(reply_text)
                            conn.execute(
                                "UPDATE dms SET replied=1, reply_text=?, sentiment=? WHERE id=?",
                                (reply_text[:300], sentiment, dm[0])
                            )
                            if dm[1]:  # variant_id
                                self.bank.record_reply(dm[1], converted=(sentiment == "positive"))

                    logger.info(f"Respuesta de @{their_username}: {reply_text[:60]}")

        except Exception as e:
            logger.warning(f"_process_inbox: {e}")

    def _classify_sentiment(self, text: str) -> str:
        """Clasificación de sentimiento rápida sin API."""
        text_low = text.lower()
        positive = ["sí", "si", "interesa", "dime", "cuéntame", "quiero", "info",
                    "precio", "cómo funciona", "como funciona", "perfecto", "me interesa",
                    "adelante", "genial", "claro", "por supuesto", "vale"]
        negative = ["no gracias", "no me interesa", "stop", "para", "déjame",
                    "dejame", "basta", "no quiero", "spam", "reportar"]
        for w in positive:
            if w in text_low:
                return "positive"
        for w in negative:
            if w in text_low:
                return "negative"
        return "neutral"

    # ── Aprendizaje ───────────────────────────────────────────────────────────

    async def _run_learning(self):
        result = await asyncio.get_event_loop().run_in_executor(
            None, self.bank.run_learning_cycle
        )
        if any(result.values()):
            await self._notify_safe(
                f"🧠 *Ciclo de aprendizaje*\n"
                f"✅ {result['promoted']} campeones actualizados\n"
                f"🗑 {result['retired']} variantes retiradas\n"
                f"✨ {result['generated']} variantes nuevas generadas"
            )

    # ── Notify safe ───────────────────────────────────────────────────────────

    async def _notify_safe(self, msg: str):
        if self._notify:
            try:
                await self._notify(msg)
            except Exception:
                pass


# Singleton
_engine: OutreachEngine | None = None

def get_engine() -> OutreachEngine:
    global _engine
    if _engine is None:
        _engine = OutreachEngine()
    return _engine


# ══════════════════════════════════════════════════════════════════════════════
# Status report
# ══════════════════════════════════════════════════════════════════════════════

def engine_status_report() -> str:
    engine = get_engine()
    pool   = LeadPool()
    dmlog  = DmLog()

    status = "🟢 ACTIVO" if engine.is_running else "🔴 DETENIDO"
    stats  = dmlog.get_full_stats()
    counts = pool.count_by_status()

    return (
        f"⚙️ *Motor Outreach: {status}*\n\n"
        f"👥 *Pool de leads:*\n"
        f"  ⏳ Pendientes: {counts.get('pending', 0)}\n"
        f"  📤 Enviados: {counts.get('sent', 0)}\n"
        f"  💬 Respondieron: {counts.get('replied', 0)}\n"
        f"  💰 Convertidos: {counts.get('converted', 0)}\n\n"
        f"📊 *DMs:*\n"
        f"  Total: {stats['total_sent']} | Hoy: {stats['today']['sent']}\n"
        f"  Reply rate: {stats['reply_rate']}\n"
        f"  Conversiones: {stats['total_converted']}\n\n"
        f"🧠 *A/B Testing activo* — ciclo cada {LEARNING_EVERY} DMs"
    )
