"""
Ghost Mouse — Cerebro con Gemini 3.1 Pro.
Genera mensajes personalizados segun nicho: local vs premium (mentores).
"""
import requests
import random
from config import GEMINI_KEY

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={GEMINI_KEY}"

PROMPT_LOCAL = """Eres un experto en ventas B2B por Instagram DM en España. Escribes mensajes para negocios LOCALES ofreciendo servicios de marketing digital y captacion de clientes.

REGLAS:
- Maximo 3 frases, CORTO y directo
- Tono casual pero profesional (tutea/vosotros)
- Maximo 1 emoji
- NO menciones precios
- SÉ específico sobre su negocio
- Objetivo: que RESPONDAN
- Español de España natural, como un humano real
- NO parece un bot

EJEMPLO:
"Buenas! He visto vuestro perfil y la verdad es que tenéis un trabajo increíble. Trabajo en captación de clientes para negocios como el vuestro y tengo una idea que os puede llenar la agenda. Os cuento?"
"""

PROMPT_PREMIUM = """Eres un experto en ventas B2B por Instagram DM en España. Escribes mensajes para MENTORES, COACHES e INFOPRODUCTORES ofreciendo servicios de marca personal, contenido y estrategia de ventas.

REGLAS:
- Maximo 3 frases, directo y con nivel alto
- Tono de igual a igual (no de vendedor sino de colega de negocio)
- Maximo 1 emoji
- NO menciones precios
- Menciona algo REAL de su contenido o perfil
- Objetivo: que RESPONDAN y quieran saber mas
- Español de España natural
- Suena como alguien que ENTIENDE su mundo

EJEMPLO:
"Buenas, he visto tu contenido sobre mentoría de negocios y se nota que dominas el tema. Trabajo escalando marcas personales como la tuya y tengo una estrategia que te puede multiplicar las ventas sin que tú tengas que hacer más contenido. Te interesa echarle un ojo?"
"""

# Fallback templates
OPENINGS_LOCAL = [
    "Buenas! He visto vuestro perfil de {name}",
    "Hola! He estado mirando {name} por aqui",
]
OPENINGS_PREMIUM = [
    "Buenas, he visto tu contenido sobre {niche}",
    "Hola! He visto tu perfil de {name}",
]
PITCH_LOCAL = ["Trabajo en captacion de clientes para negocios en {city}. Os cuento?"]
PITCH_PREMIUM = ["Trabajo escalando marcas personales y tengo una idea para ti. Hablamos?"]


def _call_gemini(prompt, timeout=120):
    """Llamada a Gemini con manejo de thinking."""
    try:
        r = requests.post(GEMINI_URL, json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.9, "maxOutputTokens": 8192}
        }, timeout=timeout)
        data = r.json()
        parts = data["candidates"][0]["content"]["parts"]
        texts = [p["text"] for p in parts if "text" in p and not p.get("thought")]
        text = texts[-1] if texts else ""
        return text.strip().strip('"').strip("'")
    except Exception as e:
        return None


def generate_dm(lead):
    """Generar DM segun nicho del lead."""
    name = lead.get("name", "tu negocio")
    city = lead.get("city", "")
    niche = lead.get("niche", "")
    ig = lead.get("instagram", "")
    rating = lead.get("rating", "")
    reviews = lead.get("reviews", "")

    # Detectar si es premium (mentor/coach/infoproductor)
    premium_keywords = ["mentor", "coach", "formador", "infoproduct", "consultor", "experto"]
    is_premium = any(k in niche.lower() for k in premium_keywords)

    base_prompt = PROMPT_PREMIUM if is_premium else PROMPT_LOCAL

    prompt = f"""{base_prompt}

Escribe un DM de Instagram para:
Negocio/Persona: {name}
Instagram: @{ig}
Ciudad: {city}
Tipo: {niche}
Rating: {rating} ({reviews} reseñas)

Escribe SOLO el mensaje, nada mas."""

    text = _call_gemini(prompt)
    if text:
        return text

    # Fallback
    if is_premium:
        o = random.choice(OPENINGS_PREMIUM).format(name=name, niche=niche)
        p = random.choice(PITCH_PREMIUM).format(name=name, city=city)
    else:
        o = random.choice(OPENINGS_LOCAL).format(name=name, city=city)
        p = random.choice(PITCH_LOCAL).format(name=name, city=city)
    return f"{o} y se nota la calidad. {p}"


def generate_followup(lead, previous_messages):
    """Generar seguimiento."""
    name = lead.get("name", "")
    context = "\n".join([f"- {m}" for m in previous_messages[-3:]])
    prompt = f"""Genera un SEGUIMIENTO corto (2 frases max) para un negocio.
Negocio: {name}
Mensajes anteriores: {context}
Escribe SOLO el mensaje."""
    text = _call_gemini(prompt, timeout=60)
    return text or f"Buenas de nuevo! Os escribi sobre marketing para {name}. Sigue en pie si os interesa!"


if __name__ == "__main__":
    # Test local
    local = {"name": "Daniel Veiga Vitale Hair", "instagram": "danielveigavitale",
             "city": "Malaga", "niche": "peluquerias", "rating": 4.8, "reviews": 230}
    # Test premium
    premium = {"name": "Alex Martinez Mentor", "instagram": "alexmartinez",
               "city": "Madrid", "niche": "mentor de negocios", "rating": "", "reviews": ""}

    print("=== LOCAL ===")
    msg = generate_dm(local)
    print(f"{msg}\n")
    print("=== PREMIUM ===")
    msg = generate_dm(premium)
    print(f"{msg}\n")
