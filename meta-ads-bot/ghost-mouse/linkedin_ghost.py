"""
LinkedIn Ghost Prospector v2.0 — Sistema 180
PROMPT MAESTRO: Sistema Integral de Prospección y Cierre en LinkedIn

Basado en el framework de 6 fases + mejoras críticas:
  1. WARM-UP progresivo (anti-detección)
  2. Lead Scoring automático (0-10)
  3. Actividad de "vagabundeo" (feed, likes aleatorios)
  4. Mensajes con imperfección humana
  5. Disparadores de eventos (cambio empleo, posts recientes)

FRAMEWORK 6 FASES:
  1. Fundamentos → Oferta irresistible + nicho ultra-específico
  2. Posicionamiento → Perfil optimizado (SEO + B7)
  3. Prospección → Sales Navigator / búsquedas booleanas
  4. Conexión → Solicitudes <300 chars, NUNCA vender en msg 1
  5. Cierre → Nutrición → Booking → WhatsApp
  6. Medición → KPIs semanales (>30% aceptación, >15% respuesta)

REGLA DE ORO: NUNCA VENDER EN EL PRIMER MENSAJE.

Uso:
  python linkedin_ghost.py buscar [pyme|infoproductor]
  python linkedin_ghost.py conectar
  python linkedin_ghost.py mensajes
  python linkedin_ghost.py vagabundear
  python linkedin_ghost.py auto
  python linkedin_ghost.py report
"""
import os
import sys
import time
import random
import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

from human_cursor import move_mouse, human_click, human_type, human_scroll
from linkedin_engine import (
    init_linkedin_db, get_daily_counts, log_action, save_linkedin_lead,
    MAX_CONNECTIONS_DAY, MAX_MESSAGES_DAY, MAX_PROFILE_VISITS_DAY,
    LINKEDIN_SEARCH_QUERIES, DB
)

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
LINKEDIN_PROFILE_DIR = os.path.join(PROFILES_DIR, "linkedin_main")
os.makedirs(LINKEDIN_PROFILE_DIR, exist_ok=True)

PHONE = "+34 615 606 285"

# ===================================================================
# WARM-UP SYSTEM (Crítica #1: Calentamiento progresivo)
# ===================================================================
# LinkedIn detecta picos de actividad. 
# Semana 1: 3 conexiones/día, 5 visitas
# Semana 2: 5 conexiones/día, 10 visitas
# Semana 3: 7 conexiones/día, 20 visitas
# Semana 4+: 8 conexiones/día, 40 visitas (velocidad crucero)

def get_warmup_limits():
    """Get current limits based on account age."""
    warmup_file = os.path.join(LINKEDIN_PROFILE_DIR, "warmup.json")
    if os.path.exists(warmup_file):
        with open(warmup_file) as f:
            data = json.load(f)
        start = datetime.fromisoformat(data["start_date"])
        days = (datetime.now() - start).days
    else:
        data = {"start_date": datetime.now().isoformat()}
        with open(warmup_file, "w") as f:
            json.dump(data, f)
        days = 0
    
    # MODO URGENCIA: Con Premium, podemos ser más agresivos
    if days < 3:
        return {"connections": 5, "messages": 8, "visits": 15, "phase": "WARM-UP RAPIDO"}
    elif days < 7:
        return {"connections": 7, "messages": 12, "visits": 30, "phase": "ACELERANDO"}
    else:
        return {"connections": 8, "messages": 15, "visits": 40, "phase": "CRUCERO"}


# ===================================================================
# LEAD SCORING (Crítica #3: Puntuación antes de conectar)
# ===================================================================

def score_lead(nombre, cargo, empresa="", actividad_reciente=False, cambio_empleo=False):
    """Score a lead 1-10 based on profile quality indicators."""
    score = 5  # Base
    
    # Cargo indicadores (+)
    cargos_hot = ["fundador", "ceo", "director", "propietario", "dueño", "owner",
                  "gerente", "coach", "mentor", "consultor", "formador"]
    cargos_cold = ["intern", "becario", "estudiante", "junior", "assistant"]
    
    cargo_l = cargo.lower()
    if any(c in cargo_l for c in cargos_hot):
        score += 2
    if any(c in cargo_l for c in cargos_cold):
        score -= 3
    
    # Actividad reciente (+2)
    if actividad_reciente:
        score += 2
    
    # Cambio de empleo reciente (+1) — Disparador de evento
    if cambio_empleo:
        score += 1
    
    # Tiene empresa definida (+1)
    if empresa and len(empresa) > 2:
        score += 1
    
    return max(1, min(10, score))


# ===================================================================
# MENSAJES ANTI-SPAM (NUNCA VENDER EN MSG 1)
# ===================================================================
# Crítica #2: Más imperfección humana, variabilidad

# FASE 4: Notas de conexión (<300 chars) — SOLO curiosidad, NO venta
CONNECTION_NOTES_V2 = {
    "pyme": [
        "Hola {nombre}, vi que tienes un negocio en {ciudad}. Me dedico a lo digital para negocios locales. Solo quería conectar por si algún día puedo echarte una mano!",
        "Hola {nombre}! Trabajo con negocios como el tuyo en {ciudad}. No voy a venderte nada jaja solo quiero ampliar red. Un saludo",
        "Hola {nombre}, he visto tu perfil y me ha parecido interesante lo que hacéis. ¿Conectamos?",
        "{nombre}, un placer! Trabajo en marketing digital para negocios locales en {ciudad}. Quería conectar sin más. Saludos!",
    ],
    "infoproductor": [
        "Hola {nombre}! He visto tu contenido y me ha molado. Estoy en el mundo de la automatización con IA. ¿Conectamos?",
        "{nombre}, vi un post tuyo que me hizo pensar. Trabajo montando sistemas de captación con IA. Me molaría estar en contacto.",
        "Hola {nombre}! Me dedico a ayudar a creadores de contenido a escalar con sistemas automatizados. Solo quería conectar!",
        "{nombre}, tu perfil me ha parecido muy interesante. Yo estoy por la zona de captación con IA. ¿Conectamos? Un saludo!",
    ],
}

# FASE 5: Follow-up 1 (3 días después) — Valor, NO venta
FOLLOWUP1_V2 = {
    "pyme": """Oye {nombre}, gracias por conectar!

Una cosa rápida que te quería compartir: he estado mirando cómo están los negocios de {ciudad} en Google y hay un dato que me llama la atención.

El 85% de los negocios locales no aparecen en las primeras 3 posiciones. Y el 76% de la gente que busca algo local va al primer resultado.

No te lo digo para venderte nada (de verdad). Solo me pareció interesante y pensé que te podía ser útil.

Si algún día te apetece que le eche un ojo a cómo estáis posicionados, me dices. Sin compromiso.

Un saludo!""",

    "infoproductor": """Hey {nombre}, gracias por aceptar!

Estuve pensando en algo que quizás te resulte útil. He notado que muchos creadores con buen contenido tienen un cuello de botella en la conversión de seguidores a compradores.

No es un problema de contenido, es de sistema. La mayoría depende del algoritmo y eso es una ruleta.

No te voy a soltar un speech de ventas jaja, pero si algún día te interesa ver cómo otros están resolviendo esto con automatización, hablamos.

Un saludo!""",
}

# FASE 5: Follow-up 2 (5 días después) — Caso real + puerta abierta
FOLLOWUP2_V2 = {
    "pyme": """Hola {nombre}, perdona que te vuelva a escribir.

Solo quería comentarte una cosa rápida: la semana pasada ayudé a un negocio de {ciudad} a configurar bien su Google Maps y en 2 semanas empezaron a recibir llamadas de gente que les encontraba por ahí.

Fue algo bastante sencillo la verdad. Si algún día os apetece que le eche un ojo al vuestro, me escribes. 

Si no, sin problema ninguno. Te deseo lo mejor con el negocio.

José María
WhatsApp: {phone}""",

    "infoproductor": """Hey {nombre}, último mensaje que te mando (no quiero ser pesado jaja).

Solo quería dejarte un dato: un creador con perfil similar al tuyo pasó de 2-3 ventas/mes a 9 después de montar un sistema de captación automatizado. Le llevó 21 días.

Si en algún momento te interesa saber cómo funciona, escríbeme. Si no, encantado de estar conectados igualmente.

{phone} (WhatsApp)""",
}

# FASE 5: Follow-up 3 (10 días después) — Cierre suave
FOLLOWUP3_V2 = {
    "pyme": """Hola {nombre}, última vez que te molesto.

Solo te dejo mi WhatsApp por si algún día lo necesitas: {phone}

Monto webs para negocios locales que generan clientes desde Google. 497€, 5 días, sin mensualidades.

Si algún día os interesa, ya sabéis dónde encontrarme. Mucha suerte!""",

    "infoproductor": """Hola {nombre}, cierro el loop.

Si algún día quieres montar un sistema que convierta seguidores en compradores sin depender del algoritmo, escríbeme: {phone}

57 agentes IA trabajando 24/7. Sin funnels. Sin VSL.

Encantado de estar conectado. Un abrazo!""",
}


# ===================================================================
# VAGABUNDEO (Crítica: Simular humano distraído)
# ===================================================================

async def vagabundear(page, duration_min=3):
    """Simulate a human casually browsing LinkedIn feed.
    This makes the account look natural before prospecting."""
    print("\n  [VAGABUNDEO] Simulando navegación natural ({} min)...".format(duration_min))
    
    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    await asyncio.sleep(random.uniform(3, 6))
    
    end_time = time.time() + (duration_min * 60)
    actions = 0
    
    while time.time() < end_time:
        action = random.choice(["scroll", "scroll", "scroll", "like", "pause", "profile_peek"])
        
        if action == "scroll":
            await human_scroll(page, "down", random.randint(200, 500))
            await asyncio.sleep(random.uniform(2, 8))
            actions += 1
        
        elif action == "like":
            # Occasionally like a post (30% chance when we see one)
            like_btns = page.locator('button[aria-label*="Recomendar"], button[aria-label*="Like"]')
            count = await like_btns.count()
            if count > 0 and random.random() < 0.3:
                idx = random.randint(0, min(count - 1, 3))
                try:
                    box = await like_btns.nth(idx).bounding_box()
                    if box and box["y"] > 100 and box["y"] < 700:
                        await human_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                        print("    ♥ Like aleatorio")
                        actions += 1
                except:
                    pass
            await asyncio.sleep(random.uniform(3, 8))
        
        elif action == "pause":
            # Just stop and "read" — like a real human
            await asyncio.sleep(random.uniform(5, 15))
        
        elif action == "profile_peek":
            # Click on someone's name briefly, then go back
            names = page.locator('a.app-aware-link span[aria-hidden="true"]')
            count = await names.count()
            if count > 0:
                idx = random.randint(0, min(count - 1, 5))
                try:
                    box = await names.nth(idx).bounding_box()
                    if box and box["y"] > 100 and box["y"] < 600:
                        await human_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                        await asyncio.sleep(random.uniform(3, 8))
                        await page.go_back()
                        await asyncio.sleep(random.uniform(2, 4))
                        print("    👁 Perfil visitado")
                        actions += 1
                except:
                    pass
    
    print("    ✓ Vagabundeo: {} acciones en {} min".format(actions, duration_min))


# ===================================================================
# MOTOR PRINCIPAL
# ===================================================================

async def human_delay(min_s=1, max_s=3):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def open_linkedin():
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=LINKEDIN_PROFILE_DIR,
        channel="msedge",
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--window-position=50,30",
            "--window-size=1280,850",
        ],
        viewport={"width": 1260, "height": 800},
        locale="es-ES",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        ignore_https_errors=True,
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
    return pw, ctx, page


async def check_login(page):
    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    await human_delay(3, 6)
    search = page.locator('input[aria-label*="Buscar"], input[aria-label*="Search"]')
    return await search.count() > 0


async def search_profiles(page, query, max_results=8):
    """Search LinkedIn for profiles."""
    search_box = page.locator('input[aria-label*="Buscar"], input[aria-label*="Search"]').first
    box = await search_box.bounding_box()
    if box:
        await human_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
        await human_delay(0.5, 1)
    
    await page.keyboard.press("Control+A")
    await page.keyboard.press("Backspace")
    await human_type(page, query)
    await human_delay(0.5, 1)
    await page.keyboard.press("Enter")
    await human_delay(3, 5)
    
    # Click "Personas"
    try:
        people = page.locator('button:has-text("Personas"), button:has-text("People"), button:has-text("Gente")')
        if await people.count() > 0:
            pbox = await people.first.bounding_box()
            if pbox:
                await human_click(page, pbox["x"]+pbox["width"]/2, pbox["y"]+pbox["height"]/2)
                await human_delay(2, 4)
    except:
        pass
    
    profiles = []
    results = page.locator('div.entity-result__item, li.reusable-search__result-container')
    count = await results.count()
    
    for i in range(min(count, max_results)):
        try:
            r = results.nth(i)
            name_el = r.locator('span[aria-hidden="true"]').first
            title_el = r.locator('div.entity-result__primary-subtitle').first
            link_el = r.locator('a[href*="/in/"]').first
            
            name = (await name_el.text_content()).strip() if await name_el.count() > 0 else ""
            title = (await title_el.text_content()).strip() if await title_el.count() > 0 else ""
            href = await link_el.get_attribute("href") if await link_el.count() > 0 else ""
            
            if name:
                lead_score = score_lead(name, title)
                profiles.append({
                    "nombre": name, "cargo": title,
                    "url": href.split("?")[0] if href else "",
                    "score": lead_score,
                })
                log_action("visit")
        except:
            continue
    
    # Sort by score (highest first)
    profiles.sort(key=lambda x: x["score"], reverse=True)
    return profiles


async def send_connection(page, profile_url, note):
    """Send connection request with Ghost Mouse."""
    await page.goto(profile_url, wait_until="domcontentloaded")
    await human_delay(3, 6)
    log_action("visit")
    
    # Read the profile (scroll)
    await human_scroll(page, "down", random.randint(200, 400))
    await human_delay(2, 5)
    await human_scroll(page, "up", random.randint(100, 200))
    await human_delay(1, 2)
    
    # Connect
    connect = page.locator('button:has-text("Conectar"), button:has-text("Connect")')
    if await connect.count() > 0:
        cbox = await connect.first.bounding_box()
        if cbox:
            await human_click(page, cbox["x"]+cbox["width"]/2, cbox["y"]+cbox["height"]/2)
            await human_delay(1, 2)
    else:
        # Try More → Connect
        more = page.locator('button[aria-label*="Más"], button[aria-label*="More"]')
        if await more.count() > 0:
            mbox = await more.first.bounding_box()
            if mbox:
                await human_click(page, mbox["x"]+mbox["width"]/2, mbox["y"]+mbox["height"]/2)
                await human_delay(1, 2)
                conn_opt = page.locator('span:has-text("Conectar")')
                if await conn_opt.count() > 0:
                    obox = await conn_opt.first.bounding_box()
                    if obox:
                        await human_click(page, obox["x"]+obox["width"]/2, obox["y"]+obox["height"]/2)
                        await human_delay(1, 2)
        else:
            return False
    
    # Add note
    add_note = page.locator('button:has-text("Añadir nota"), button:has-text("Add a note")')
    if await add_note.count() > 0:
        nbox = await add_note.first.bounding_box()
        if nbox:
            await human_click(page, nbox["x"]+nbox["width"]/2, nbox["y"]+nbox["height"]/2)
            await human_delay(1, 2)
        
        textarea = page.locator('textarea[name="message"], textarea#custom-message')
        if await textarea.count() > 0:
            tbox = await textarea.first.bounding_box()
            if tbox:
                await human_click(page, tbox["x"]+tbox["width"]/2, tbox["y"]+tbox["height"]/2)
                await human_delay(0.3, 0.8)
                await human_type(page, note[:300])
                await human_delay(1, 2)
        
        send = page.locator('button:has-text("Enviar"), button:has-text("Send")')
        if await send.count() > 0:
            sbox = await send.first.bounding_box()
            if sbox:
                await human_click(page, sbox["x"]+sbox["width"]/2, sbox["y"]+sbox["height"]/2)
                await human_delay(1, 2)
    
    log_action("connection")
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE linkedin_leads SET status='connection_sent', connection_sent_at=? WHERE profile_url=?",
                 (datetime.now().isoformat(), profile_url))
    conn.commit()
    conn.close()
    return True


def get_note(tipo, nombre, ciudad="Málaga"):
    notes = CONNECTION_NOTES_V2.get(tipo, CONNECTION_NOTES_V2["pyme"])
    note = random.choice(notes)
    return note.format(nombre=nombre, ciudad=ciudad, phone=PHONE)[:300]


def get_msg(fase, tipo, nombre, ciudad="Málaga"):
    templates = {
        1: FOLLOWUP1_V2,
        2: FOLLOWUP2_V2,
        3: FOLLOWUP3_V2,
    }
    t = templates.get(fase, FOLLOWUP1_V2)
    return t.get(tipo, t["pyme"]).format(nombre=nombre, ciudad=ciudad, phone=PHONE)


def weekly_report():
    """FASE 6: KPIs semanales."""
    conn = sqlite3.connect(DB)
    total = conn.execute("SELECT COUNT(*) FROM linkedin_leads").fetchone()[0]
    sent = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE connection_sent_at IS NOT NULL").fetchone()[0]
    accepted = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE connection_accepted_at IS NOT NULL").fetchone()[0]
    msg1 = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE msg1_sent_at IS NOT NULL").fetchone()[0]
    replied = conn.execute("SELECT COUNT(*) FROM linkedin_leads WHERE replied_at IS NOT NULL").fetchone()[0]
    conn.close()
    
    accept_rate = (accepted / sent * 100) if sent > 0 else 0
    reply_rate = (replied / msg1 * 100) if msg1 > 0 else 0
    limits = get_warmup_limits()
    
    print("=" * 60)
    print("  LINKEDIN KPIs — FASE 6")
    print("  Fase: {}".format(limits["phase"]))
    print("=" * 60)
    print("  Total leads:        {}".format(total))
    print("  Conexiones enviadas: {}".format(sent))
    print("  Aceptadas:           {} ({:.1f}%) {}".format(
        accepted, accept_rate, "✓" if accept_rate >= 30 else "✗ (objetivo >30%)"))
    print("  Mensajes enviados:   {}".format(msg1))
    print("  Respondieron:        {} ({:.1f}%) {}".format(
        replied, reply_rate, "✓" if reply_rate >= 15 else "✗ (objetivo >15%)"))
    print("")
    print("  Límites hoy: {} conex | {} msgs | {} visitas".format(
        limits["connections"], limits["messages"], limits["visits"]))
    print("=" * 60)


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "report"
    tipo = sys.argv[2] if len(sys.argv) > 2 else "pyme"
    
    init_linkedin_db()
    limits = get_warmup_limits()
    
    print("=" * 60)
    print("  LINKEDIN GHOST v2.0 — PROMPT MAESTRO")
    print("  Modo: {} | Tipo: {} | Fase: {}".format(mode, tipo, limits["phase"]))
    print("=" * 60)
    
    if mode == "report":
        weekly_report()
        return
    
    pw, ctx, page = await open_linkedin()
    
    try:
        logged_in = await check_login(page)
        if not logged_in:
            print("\n  [!] Inicia sesión en LinkedIn. Pulsa Enter cuando termines...")
            input()
        
        if mode == "vagabundear":
            await vagabundear(page, duration_min=5)
        
        elif mode == "buscar":
            queries = LINKEDIN_SEARCH_QUERIES.get(tipo, LINKEDIN_SEARCH_QUERIES["pyme"])
            total = []
            for q in queries[:5]:
                print("\n  Buscando: {}".format(q))
                profiles = await search_profiles(page, q)
                for p in profiles:
                    if p["score"] >= 5:  # Solo leads con score >= 5
                        save_linkedin_lead(p["url"], p["nombre"], p["cargo"], ciudad="Málaga", tipo=tipo)
                        total.append(p)
                        print("    [{}⭐] {} — {}".format(p["score"], p["nombre"], p["cargo"][:40]))
                    else:
                        print("    [{}⭐ SKIP] {} — score bajo".format(p["score"], p["nombre"]))
                await human_delay(8, 15)
            print("\n  Total leads cualificados: {}".format(len(total)))
        
        elif mode == "conectar":
            db = sqlite3.connect(DB)
            leads = db.execute("""
                SELECT profile_url, nombre, tipo, ciudad FROM linkedin_leads
                WHERE status = 'nuevo' ORDER BY created_at DESC LIMIT ?
            """, (limits["connections"],)).fetchall()
            db.close()
            
            # Vagabundear antes (parecer natural)
            await vagabundear(page, duration_min=2)
            
            sent = 0
            for url, nombre, t, ciudad in leads:
                counts = get_daily_counts()
                if counts["connections"] >= limits["connections"]:
                    print("  Límite diario alcanzado")
                    break
                note = get_note(t or tipo, nombre, ciudad or "Málaga")
                print("\n  → {} | Nota: {}...".format(nombre, note[:60]))
                if await send_connection(page, url, note):
                    sent += 1
                    print("    ✓ Conexión enviada")
                await human_delay(30, 90)
            print("\n  Total: {} conexiones".format(sent))
        
        elif mode == "auto":
            # 1. Vagabundear primero (parecer natural)
            await vagabundear(page, duration_min=3)
            # 2. Buscar perfiles
            queries = LINKEDIN_SEARCH_QUERIES.get(tipo, LINKEDIN_SEARCH_QUERIES["pyme"])
            for q in queries[:3]:
                profiles = await search_profiles(page, q)
                for p in profiles:
                    if p["score"] >= 5:
                        save_linkedin_lead(p["url"], p["nombre"], p["cargo"], ciudad="Málaga", tipo=tipo)
                await human_delay(8, 15)
            # 3. Conectar
            db = sqlite3.connect(DB)
            leads = db.execute("SELECT profile_url, nombre, tipo, ciudad FROM linkedin_leads WHERE status='nuevo' LIMIT ?",
                              (limits["connections"],)).fetchall()
            db.close()
            for url, nombre, t, ciudad in leads:
                counts = get_daily_counts()
                if counts["connections"] >= limits["connections"]:
                    break
                note = get_note(t or tipo, nombre, ciudad or "Málaga")
                await send_connection(page, url, note)
                await human_delay(30, 90)
            # 4. Report
            weekly_report()
        
        print("\n  Pulsa Enter para cerrar...")
        input()
    
    finally:
        await ctx.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
