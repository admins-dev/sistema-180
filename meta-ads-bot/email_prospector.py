"""
email_prospector.py — Sistema 180
Canal email: Google Maps → extrae emails → Gemini genera copy → envía automático
GDPR: Solo negocios con email público en su web (opt-in implícito por publicación)
"""
import os, re, json, time, smtplib, logging, requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_KEY      = os.getenv('GEMINI_API_KEY', '')
ANTHROPIC_KEY   = os.getenv('ANTHROPIC_API_KEY', '')
SMTP_EMAIL      = os.getenv('SMTP_EMAIL', '')       # tu email Gmail
SMTP_PASS    = os.getenv('SMTP_APP_PASS', '').replace(' ', '')  # App Password (sin espacios)
SMTP_NAME    = os.getenv('SMTP_NAME', 'José — Sistema 180')

SENT_EMAILS_FILE = 'sent_emails.json'

# ── Extraer emails de una web ──────────────────────────────────────────────
def extract_emails_from_website(url: str) -> list[str]:
    """Busca emails públicos en la web del negocio."""
    if not url:
        return []
    emails = set()
    try:
        r = requests.get(url, timeout=8,
                         headers={'User-Agent': 'Mozilla/5.0'})
        text = r.text
        found = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
        blacklist = {'example', 'test', 'noreply', 'no-reply', 'wordpress',
                     'woocommerce', 'schema', 'sentry', 'jquery'}
        for e in found:
            e = e.lower().strip()
            domain = e.split('@')[1]
            if not any(b in domain for b in blacklist) and len(e) < 60:
                emails.add(e)
    except Exception as e:
        logger.debug(f'Error extrayendo emails de {url}: {e}')
    return list(emails)[:3]  # máx 3 emails por negocio


# ── Buscar emails con Google Maps ──────────────────────────────────────────
def find_leads_with_emails(city: str, lat: float, lng: float,
                            business_type: str, limit: int = 20) -> list[dict]:
    """Google Maps → obtiene web → extrae email."""
    from lead_factory import search_places, get_place_details
    MAPS_KEY = os.getenv('GOOGLE_MAPS_KEY', '')
    if not MAPS_KEY:
        return []

    leads = []
    places = search_places(business_type + ' ' + city, lat, lng, radius=8000)

    for place in places[:limit * 2]:
        det = get_place_details(place['place_id'])
        time.sleep(0.2)

        website = det.get('website', '')
        emails = extract_emails_from_website(website)

        if not emails:
            continue

        # Detectar pain point
        rating = place.get('rating', 5.0)
        reviews = place.get('reviews', 0)
        pain_parts = []
        if not website:      pain_parts.append('sin web')
        if rating < 4.2:     pain_parts.append('reseñas bajas')
        if reviews < 15:     pain_parts.append('poca visibilidad')

        leads.append({
            'name':     place['name'],
            'city':     city,
            'type':     business_type,
            'emails':   emails,
            'website':  website,
            'phone':    det.get('phone', ''),
            'rating':   rating,
            'reviews':  reviews,
            'pain':     ', '.join(pain_parts) or 'no atienden clientes 24h',
        })

        if len(leads) >= limit:
            break

    logger.info(f'{city} / {business_type}: {len(leads)} leads con email')
    return leads


# ── Gemini: generar email de venta ─────────────────────────────────────────
def generate_sales_email(lead: dict) -> dict:
    """Genera asunto + cuerpo del email con Gemini."""
    name   = lead.get('name', 'tu negocio')
    city   = lead.get('city', '')
    pain   = lead.get('pain', 'perder clientes')
    btype  = lead.get('type', 'negocio')

    fallback = {
        'subject': f'¿Cuántos clientes pierde {name} por no contestar a tiempo?',
        'body': (
            f"Hola,\n\n"
            f"Vi {name} en Google Maps y quería preguntarte algo directamente: "
            f"¿cuántas llamadas o mensajes de clientes se quedan sin respuesta?\n\n"
            f"En Sistema 180 ayudamos a {btype}s como el tuyo con dos cosas:\n"
            f"• Web profesional que te posiciona en Google — desde 297€\n"
            f"• Bot IA que atiende WhatsApp 24h y cierra citas solo — 300€/mes\n\n"
            f"¿Tienes 5 minutos esta semana para una llamada rápida?\n\n"
            f"Un saludo,\nJosé María\nSistema 180\n"
            f"sistema-180.com"
        ),
    }

    if not ANTHROPIC_KEY and not GEMINI_KEY:
        return fallback

    prompt = (
        f"Eres José María de Sistema 180, agencia digital en España.\n"
        f"Vendes: 1) Web profesional 297€ 2) Bot IA WhatsApp 300€/mes "
        f"que atiende clientes y cierra citas automáticamente.\n\n"
        f"Escribe un email de venta en frío.\n"
        f"Negocio: {name} | Tipo: {btype} | Ciudad: {city}\n"
        f"Problema detectado: {pain}\n\n"
        f"FORMATO:\nASUNTO: [directo, sin clickbait]\nCUERPO:\n"
        f"[máximo 6 líneas, natural, sin spam words, CTA para llamada 5 min]\n"
        f"Firma: José María | Sistema 180 | sistema-180.com"
    )

    try:
        # Primero Claude Haiku 4.5, fallback a Gemini
        if ANTHROPIC_KEY:
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_KEY)
            msg = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=300,
                messages=[{'role': 'user', 'content': prompt}],
            )
            text = msg.content[0].text.strip()
        else:
            r = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}',
                json={'contents': [{'parts': [{'text': prompt}]}],
                      'generationConfig': {'maxOutputTokens': 300, 'temperature': 0.7}},
                timeout=12,
            )
            text = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()

        # Parsear asunto y cuerpo
        subject_match = re.search(r'ASUNTO:\s*(.+)', text)
        body_match    = re.search(r'CUERPO:\s*([\s\S]+)', text)

        return {
            'subject': subject_match.group(1).strip() if subject_match else fallback['subject'],
            'body':    body_match.group(1).strip()    if body_match    else text,
        }
    except Exception as e:
        logger.warning(f'Gemini email error: {e}')
        return fallback


# ── Enviar email vía Gmail SMTP ────────────────────────────────────────────
def send_email(to: str, subject: str, body: str) -> bool:
    """Envía email via Gmail con App Password."""
    if not SMTP_EMAIL or not SMTP_PASS:
        logger.error('SMTP_EMAIL y SMTP_APP_PASS no configurados')
        return False
    try:
        msg = MIMEMultipart('alternative')
        msg['From']    = f'{SMTP_NAME} <{SMTP_EMAIL}>'
        msg['To']      = to
        msg['Subject'] = subject
        msg['Reply-To'] = SMTP_EMAIL

        # Texto plano (mejor deliverability que HTML)
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASS)
            server.sendmail(SMTP_EMAIL, to, msg.as_string())

        logger.info(f'✅ Email enviado a {to}: {subject[:40]}')
        return True
    except Exception as e:
        logger.error(f'Error enviando a {to}: {e}')
        return False


# ── State: emails ya enviados ──────────────────────────────────────────────
def load_sent_emails() -> set:
    if os.path.exists(SENT_EMAILS_FILE):
        with open(SENT_EMAILS_FILE) as f:
            return set(json.load(f))
    return set()

def mark_email_sent(email: str, lead: dict):
    sent = load_sent_emails()
    sent.add(email)
    with open(SENT_EMAILS_FILE, 'w') as f:
        json.dump(list(sent), f)


# ── Campaña de email ───────────────────────────────────────────────────────
async def run_email_campaign(leads: list[dict], notify_fn=None,
                              daily_limit: int = 50) -> dict:
    """Envía emails a la lista de leads. Sin delay agresivo (email es más seguro)."""
    import asyncio
    results = {'sent': 0, 'failed': 0, 'skipped': 0}
    sent_emails = load_sent_emails()

    for lead in leads[:daily_limit]:
        for email in lead.get('emails', []):
            if email in sent_emails:
                results['skipped'] += 1
                continue

            content = generate_sales_email(lead)
            ok = send_email(email, content['subject'], content['body'])

            if ok:
                mark_email_sent(email, lead)
                results['sent'] += 1
                await asyncio.sleep(8)   # 8s entre emails (anti-spam SMTP)
            else:
                results['failed'] += 1

    if notify_fn:
        await notify_fn(
            f"📧 Email campaign done\n"
            f"✅ Enviados: {results['sent']}\n"
            f"❌ Fallidos: {results['failed']}\n"
            f"⏭ Ya enviados: {results['skipped']}"
        )
    return results
