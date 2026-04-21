"""
Ghost Mouse — Cerebro v4.0 (B7 + MONGEMALO)
DMs con framework StoryBrand + estilo Monge Malo:
directo, polarizante, sin filtros, autoridad absoluta.
El prospect es el PERSONAJE. Tú eres el GUÍA.
"""
import requests
import random
from config import GEMINI_KEY

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={GEMINI_KEY}"

# ═══════════════════════════════════════════════
# PROMPT LÍNEA A — PYMES LOCALES (B7 + MONGEMALO)
# ═══════════════════════════════════════════════
PROMPT_LINEA_A = """Eres un closer B2B que escribe DMs de Instagram a negocios locales.
Tu estilo es MONGE MALO: directo, sin filtros, frases cortas, tono de autoridad. NO pides permiso. NO te disculpas. Dices verdades incómodas que hacen pensar.

FRAMEWORK B7 (StoryBrand) para el DM:
1. PERSONAJE = El dueño del negocio (ÉL es el héroe, no tú)
2. PROBLEMA = Está perdiendo clientes porque no aparece en Google
3. GUÍA = Tú. Demuestras EMPATÍA (entiendes su dolor) + AUTORIDAD (ya lo has resuelto para otros)
4. PLAN = Simple: web + SEO + WhatsApp en 5 días
5. CTA = Una sola acción: responder el DM
6. FRACASO = Si no actúa, la competencia se queda sus clientes
7. ÉXITO = Más clientes sin esfuerzo, facturación creciendo

REGLAS DEL ESTILO:
- Máximo 3 frases. Punto. Sin relleno.
- Español de España. Tutea. Nada de usted.
- CERO emojis. Esto no es un catálogo de Avon.
- NUNCA: "Hola, me llamo X" → spam instantáneo.
- NUNCA: "resultados garantizados" → palabrería de vendedor.
- SÍ: verdades directas que duelen pero son reales.
- SÍ: filtro integrado ("si tu negocio ya tiene llena la agenda, ignora esto").
- NO pides permiso para escribir. Escribes y punto.
- Tu objetivo es UNA RESPUESTA. No vendes nada en el primer DM.

EJEMPLOS ESTILO MONGEMALO:
"He buscado [nicho] en [ciudad] en Google. No aparecéis. Eso significa que cada día hay gente buscando lo que hacéis y eligiendo a otros. Si eso os da igual, ignorad esto. Si no, respondedme."

"Vuestro trabajo en [nombre] es bueno. Vuestro Google Maps es un desastre. Cada semana perdéis clientes que os buscan y no os encuentran. Arreglo eso en 5 días. ¿Os interesa o paso?"

"3 de cada 4 clientes buscan en Google antes de elegir [nicho]. Si no aparecéis, no existís. Puedo cambiar eso esta semana. Respondedme si queréis saber cómo."
"""

# ═══════════════════════════════════════════════
# PROMPT LÍNEA B — INFOPRODUCTORES (B7 + MONGEMALO)
# ═══════════════════════════════════════════════
PROMPT_LINEA_B = """Eres un operador comercial B2B que escribe DMs a infoproductores y coaches que ya facturan.
Estilo MONGE MALO: directo, de igual a igual, sin filtros, autoridad absoluta. NUNCA suenas como fan. NUNCA como vendedor. Suenas como alguien que SABE.

FRAMEWORK B7:
1. PERSONAJE = El infoproductor (ÉL es el héroe)
2. PROBLEMA = Publica mucho pero convierte poco. Audiencia grande, pipeline vacío.
3. GUÍA = Tú. Has visto el patrón mil veces y sabes cómo arreglarlo.
4. PLAN = Sistema de captación que convierte seguidores en llamadas de venta.
5. CTA = Responder al DM para explorar partnership.
6. FRACASO = Seguir publicando para likes y no para ventas. Burnout sin escalar.
7. ÉXITO = Escalar facturación sin trabajar más horas.

REGLAS:
- Máximo 3 frases. Nivel ejecutivo.
- Tono de colega que factura más que él, no de aspirante.
- CERO emojis. Esto es negocio, no redes sociales.
- Menciona algo CONCRETO de su contenido (última publicación, tema, enfoque).
- NO uses "partnership", "sinergia" ni jerga. Habla normal.
- Filtra: "solo si facturas X" o "si tu audiencia convierte bien, ignora esto".

EJEMPLOS:
"Tu contenido sobre [tema] es bueno. Tu embudo de ventas no. El 90% de tu audiencia te consume gratis y nunca compra. Monto sistemas que cambian eso. ¿Te interesa o estás bien así?"

"Vi tu reel sobre [tema]. Buen contenido, mal sistema. Publicas para engagement pero no para ventas. Escalo la facturación de perfiles como el tuyo sin funnels. ¿Hablamos?"
"""

# ═══════════════════════════════════════════════
# FOLLOWUPS B7 MONGEMALO STYLE
# ═══════════════════════════════════════════════
FOLLOWUP_SOFT = [
    "Te escribí hace unos días. O no lo viste o no te interesa. Si es lo segundo, sin problema. Si es lo primero, échale un ojo.",
    "Mensaje rápido: lo que te escribí sigue en pie. Si te interesa, responde. Si no, me callo.",
    "No insisto más. Solo quería saber si lo de mejorar vuestra visibilidad en Google os interesa o no. Un sí o un no me vale.",
]

FOLLOWUP_URGENTE = [
    "Último mensaje. Cierro plazas esta semana. Si os interesa, respondedme hoy. Si no, os deseo lo mejor.",
    "Esto es lo último que os escribo. Tengo sitio para un negocio más este mes. ¿Sois vosotros o paso al siguiente?",
]

# Fallback templates B7
FALLBACK_LOCAL = [
    "He buscado {niche} en {city} en Google. {name} no aparece. Eso son clientes que cada día eligen a la competencia. Arreglo eso en 5 días. ¿Os interesa?",
    "Vuestro trabajo en {name} es bueno. Vuestra presencia en Google, no. Cada semana perdéis clientes que os buscan y no os encuentran. ¿Queréis que lo arregle?",
    "3 de cada 4 clientes de {niche} buscan en Google antes de elegir. Si {name} no aparece, no existís para ellos. Puedo cambiar eso esta semana.",
]

FALLBACK_PREMIUM = [
    "Tu contenido sobre {niche} es bueno. Tu sistema de ventas, no. Puedo escalar tu facturación sin funnels. ¿Hablamos?",
    "Vi tu contenido. Buen material, mal embudo. El 90% de tu audiencia te consume gratis. Cambio eso. ¿Te interesa?",
]


def _call_gemini(prompt, timeout=120):
    """Llamada a Gemini con manejo de thinking."""
    try:
        r = requests.post(GEMINI_URL, json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.85, "maxOutputTokens": 512}
        }, timeout=timeout)
        data = r.json()
        parts = data["candidates"][0]["content"]["parts"]
        texts = [p["text"] for p in parts if "text" in p and not p.get("thought")]
        text = texts[-1] if texts else ""
        # Limpiar comillas y saltos de línea extra
        text = text.strip().strip('"').strip("'").strip()
        # Validar longitud (máx 3 frases = ~300 chars)
        if len(text) > 400:
            text = ". ".join(text.split(". ")[:3]) + "?"
        return text
    except Exception as e:
        return None


def generate_dm(lead):
    """Generar DM según línea de negocio del lead."""
    name = lead.get("name", "tu negocio")
    city = lead.get("city", "Málaga")
    niche = lead.get("niche", "")
    ig = lead.get("instagram", "")
    rating = lead.get("rating", "")
    reviews = lead.get("reviews", "")

    # Detectar si es Línea B (premium: mentor/coach/infoproductor)
    premium_keywords = ["mentor", "coach", "formador", "infoproduct", "consultor", 
                        "experto", "speaker", "emprendedor", "negocio digital", "marca personal"]
    is_premium = any(k in niche.lower() for k in premium_keywords)

    base_prompt = PROMPT_LINEA_B if is_premium else PROMPT_LINEA_A

    user_prompt = f"""{base_prompt}

Escribe un DM de Instagram para:
Negocio/Persona: {name}
Instagram: @{ig}
Ciudad: {city}
Tipo: {niche}
{"Rating: " + str(rating) + " (" + str(reviews) + " reseñas)" if rating else ""}

Escribe SOLO el mensaje final, nada más. Sin explicaciones."""

    text = _call_gemini(user_prompt)
    if text:
        return text

    # Fallback con templates
    if is_premium:
        return random.choice(FALLBACK_PREMIUM).format(name=name, niche=niche, city=city)
    else:
        return random.choice(FALLBACK_LOCAL).format(name=name, niche=niche, city=city)


def generate_followup(lead, attempt=1):
    """Generar seguimiento según intento."""
    name = lead.get("name", "")
    
    if attempt <= 2:
        template = random.choice(FOLLOWUP_SOFT)
    else:
        template = random.choice(FOLLOWUP_URGENTE)
    
    return template


def generate_reply(lead, their_message):
    """Generar respuesta cuando el lead RESPONDE (momento crítico)."""
    name = lead.get("name", "")
    niche = lead.get("niche", "")
    
    prompt = f"""Un negocio local ha RESPONDIDO a tu DM de prospección. Es el momento de agendar una llamada.

Su mensaje: "{their_message}"
Negocio: {name} ({niche})

REGLAS:
- Responde de forma natural y cálida
- Máximo 2-3 frases
- Tu ÚNICO objetivo es AGENDAR una llamada de 15 min
- Propón 2 horarios concretos (mañana o pasado mañana)
- No expliques tu servicio todavía, eso es para la llamada
- Español de España natural

Escribe SOLO tu respuesta."""

    text = _call_gemini(prompt, timeout=60)
    if text:
        return text
    
    return f"Genial! Me alegra que os interese. ¿Os va bien una llamada rápida de 15 min mañana o pasado? Así os cuento todo sin rollo. ¿Qué horario os cuadra mejor?"


if __name__ == "__main__":
    print("=" * 60)
    print("  🎯 BRAIN v3.0 — CASH MODE (7 DÍAS)")
    print("=" * 60)
    
    # Test Línea A (PYME local)
    local = {"name": "Daniel Veiga Vitale Hair", "instagram": "danielveigavitale",
             "city": "Málaga", "niche": "peluquerías", "rating": 4.8, "reviews": 230}
    
    # Test Línea B (Infoproductor)  
    premium = {"name": "Alex Martinez Mentor", "instagram": "alexmartinez",
               "city": "Madrid", "niche": "mentor de negocios", "rating": "", "reviews": ""}

    print("\n=== LÍNEA A (PYME LOCAL) ===")
    msg = generate_dm(local)
    print(f"DM: {msg}\n")
    
    print("=== LÍNEA B (INFOPRODUCTOR) ===")
    msg = generate_dm(premium)
    print(f"DM: {msg}\n")
    
    print("=== FOLLOWUP (intento 1) ===")
    print(f"Followup: {generate_followup(local, 1)}\n")
    
    print("=== RESPUESTA A LEAD ===")
    reply = generate_reply(local, "Sí, me interesa, ¿de qué va?")
    print(f"Reply: {reply}\n")
