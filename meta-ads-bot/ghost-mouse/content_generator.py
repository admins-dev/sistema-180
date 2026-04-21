"""
Instagram Content Generator for Setter Profiles
Genera descripciones de posts para que ComfyUI o Canva los produzcan.
9 posts por setter = 45 posts totales para llenar los grids.
"""
from setter_profiles import SETTER_PROFILES

# =========================================================
# TEMPLATES DE POSTS POR TIPO
# Cada setter necesita 9 posts para parecer un perfil real
# Distribucion: 3 carruseles + 3 reels + 3 posts imagen
# =========================================================

POST_TEMPLATES = {
    "carrusel_tips": {
        "tipo": "Carrusel",
        "slides": 5,
        "estructura": [
            "Slide 1: Titulo impactante con dato o pregunta",
            "Slide 2-4: Tips o pasos numerados",
            "Slide 5: CTA 'Guardalo + Sigueme para mas'",
        ],
        "comfyui_prompt_base": "Professional instagram carousel slide, dark background, modern minimalist design, white and green accent text, clean typography, 1080x1350px",
    },
    "carrusel_caso": {
        "tipo": "Carrusel Caso de Exito",
        "slides": 4,
        "estructura": [
            "Slide 1: 'De X a Y en Z dias' (titulo resultado)",
            "Slide 2: El problema que tenia el cliente",  
            "Slide 3: Lo que hicimos (resumen)",
            "Slide 4: Resultados + CTA",
        ],
        "comfyui_prompt_base": "Professional case study instagram slide, before and after style, dark theme with green highlights, clean modern design, 1080x1350px",
    },
    "post_testimonio": {
        "tipo": "Post Imagen",
        "estructura": [
            "Fondo oscuro con comillas",
            "Texto del testimonio (inventado pero realista)",
            "Nombre y negocio del 'cliente'",
            "Estrellas de valoracion",
        ],
        "comfyui_prompt_base": "Professional testimonial instagram post, dark background, white quote text, 5 star rating, green accent, minimalist design, 1080x1080px",
    },
    "post_dato": {
        "tipo": "Post Imagen",
        "estructura": [
            "Numero grande impactante (estadistica)",
            "Texto explicativo corto debajo",
            "Logo o nombre del setter",
        ],
        "comfyui_prompt_base": "Instagram infographic post, big bold number statistic, dark background, emerald green accent, modern typography, 1080x1080px",
    },
    "post_presentacion": {
        "tipo": "Post Imagen",
        "estructura": [
            "Foto del setter (avatar)",
            "Texto: Quien soy + que hago",
            "CTA: Sigueme para tips de marketing",
        ],
        "comfyui_prompt_base": "Instagram introduction post, professional headshot style, dark overlay with white text, about me format, 1080x1080px",
    },
}


# =========================================================
# CONTENIDO ESPECIFICO POR SETTER
# =========================================================

def generate_content_plan(username):
    """Genera el plan de 9 posts para un setter especifico."""
    profile = SETTER_PROFILES.get(username)
    if not profile:
        return None
    
    nicho_principal = profile["target_niches"][0]
    nombre = profile["fullname"]
    ciudad = profile["city_focus"]
    
    posts = [
        # POST 1 - Presentacion personal
        {
            "orden": 1,
            "tipo": "Post Imagen",
            "titulo": f"Hola! Soy {nombre}",
            "caption": f"Soy {nombre} y ayudo a negocios de {nicho_principal} en {ciudad} a llenar su agenda con clientes nuevos cada semana.\n\nSi tienes un negocio de {nicho_principal} y quieres mas clientes, escribeme un DM.\n\n#marketinglocal #pymes #{nicho_principal.replace(' ', '')} #{ciudad.lower()} #negocioslocales",
            "imagen_desc": f"Foto profesional de {nombre} con overlay oscuro y texto 'Ayudo a {nicho_principal} a llenar su agenda'",
        },
        # POST 2 - Carrusel Tips
        {
            "orden": 2,
            "tipo": "Carrusel 5 slides",
            "titulo": f"5 errores que cometen los {nicho_principal} en Instagram",
            "caption": f"Si tienes un negocio de {nicho_principal}, estos errores te estan costando clientes.\n\nGuarda este post y empieza a corregirlos hoy.\n\nDM 'TIPS' si quieres que te ayude personalmente.",
            "slides_texto": [
                f"5 errores que cometen los {nicho_principal} en Instagram",
                "1. No publicar con regularidad\n2. Solo subir fotos del producto",
                "3. No responder DMs en menos de 1h\n4. No usar Google Maps",
                "5. No tener un enlace claro en la bio",
                f"Sigueme para mas tips de marketing para {nicho_principal} en {ciudad}",
            ],
        },
        # POST 3 - Testimonio
        {
            "orden": 3,
            "tipo": "Post Testimonio",
            "titulo": "Caso real",
            "caption": f"Resultados reales de un negocio de {nicho_principal} en {ciudad}.\n\nEn 2 semanas duplicamos sus consultas online.\n\nDM 'INFO' si quieres saber como.",
            "testimonio": f"Estaba harto de depender del boca a boca. {nombre} me monto un sistema y en 2 semanas ya tenia clientes llamando. Brutal.",
            "cliente_ficticio": f"Miguel R. - {nicho_principal.capitalize()} en {ciudad}",
        },
        # POST 4 - Dato impactante
        {
            "orden": 4,
            "tipo": "Post Dato",
            "titulo": "76% de tus clientes te buscan en Google",
            "caption": f"El 76% de las personas buscan en Google ANTES de ir a un negocio local.\n\nSi tu negocio de {nicho_principal} no aparece, esos clientes se van a tu competencia.\n\nDM 'AUDIT' y te hago un diagnostico gratis de tu presencia online.",
            "dato": "76%",
            "subtexto": "de tus clientes te buscan online antes de visitarte",
        },
        # POST 5 - Carrusel Caso de Exito
        {
            "orden": 5,
            "tipo": "Carrusel 4 slides",
            "titulo": f"De 3 a 15 clientes/semana",
            "caption": f"Caso real de un negocio de {nicho_principal} que paso de 3 a 15 clientes nuevos por semana.\n\nSin ads caros. Solo con su web y Google Maps bien hechos.\n\nDM 'CASO' para saber el proceso exacto.",
            "slides_texto": [
                f"De 3 a 15 clientes/semana - {nicho_principal.capitalize()} en {ciudad}",
                "ANTES: 3 clientes/semana, sin web, sin Google Maps, solo boca a boca",
                "LO QUE HICIMOS: Web profesional + Google Maps + formulario + WhatsApp",
                "DESPUES: 15 clientes/semana. +400% en 2 semanas. DM 'CASO' para mas info",
            ],
        },
        # POST 6 - Frase motivacional
        {
            "orden": 6,
            "tipo": "Post Imagen",
            "titulo": "Tu negocio merece mas",
            "caption": f"Tu {nicho_principal} merece estar lleno.\n\nNo es cuestion de suerte, es cuestion de tener las herramientas correctas.\n\nDM y te cuento como.",
            "imagen_desc": "Fondo oscuro, texto grande 'Tu negocio merece estar lleno' en blanco, acento verde",
        },
        # POST 7 - Carrusel Estrategia
        {
            "orden": 7,
            "tipo": "Carrusel 5 slides",
            "titulo": f"3 estrategias que funcionan para {nicho_principal}",
            "caption": f"Estas 3 estrategias son las que mejor funcionan para {nicho_principal} en 2026.\n\nNo necesitas gastar miles en ads.\n\nGuarda, comparte y DM 'ESTRATEGIA'.",
            "slides_texto": [
                f"3 estrategias que FUNCIONAN para {nicho_principal} en 2026",
                "1. Google Maps optimizado: fotos, horarios, resenas activas",
                "2. Web con boton de WhatsApp: el cliente te escribe en 1 clic",
                "3. Contenido local en Instagram: conecta con tu barrio",
                f"Sigueme @{username} para mas tips de captacion local",
            ],
        },
        # POST 8 - Reel/Video idea
        {
            "orden": 8,
            "tipo": "Post Imagen (placeholder de reel)",
            "titulo": f"Por que tu {nicho_principal} no crece en redes",
            "caption": f"La razon #1 por la que tu negocio de {nicho_principal} no crece en redes:\n\nNo tienes un sistema.\n\nPublicar sin estrategia = tirar el tiempo.\n\nDM 'SISTEMA' y te explico como montar uno.",
            "imagen_desc": f"Thumbnail oscuro con texto 'Por que tu {nicho_principal} NO crece en redes?' estilo clickbait profesional",
        },
        # POST 9 - CTA directo
        {
            "orden": 9,
            "tipo": "Post Imagen",
            "titulo": "Diagnostico GRATIS",
            "caption": f"Te hago un diagnostico GRATIS de la presencia online de tu {nicho_principal}.\n\nSin compromiso. 15 minutos.\n\nDM 'GRATIS' y te digo exactamente que mejorar para conseguir mas clientes.\n\n#diagnosticogratis #marketinglocal #{ciudad.lower()}",
            "imagen_desc": "Fondo negro, texto grande 'DIAGNOSTICO GRATIS' en verde, subtexto 'Para negocios locales - DM GRATIS'",
        },
    ]
    
    return {
        "username": username,
        "fullname": nombre,
        "total_posts": len(posts),
        "posts": posts,
    }


def generate_all_content_plans():
    """Genera planes de contenido para los 5 setters."""
    plans = {}
    for username in SETTER_PROFILES:
        plan = generate_content_plan(username)
        if plan:
            plans[username] = plan
    return plans


def print_content_plan(username):
    """Imprime el plan de contenido para un setter."""
    plan = generate_content_plan(username)
    if not plan:
        print(f"Setter @{username} no encontrado")
        return
    
    print(f"\n{'='*60}")
    print(f"  PLAN DE CONTENIDO: @{username} ({plan['fullname']})")
    print(f"  Total posts: {plan['total_posts']}")
    print(f"{'='*60}")
    
    for post in plan["posts"]:
        print(f"\n  --- Post {post['orden']} [{post['tipo']}] ---")
        print(f"  Titulo: {post['titulo']}")
        print(f"  Caption (preview): {post['caption'][:80]}...")


if __name__ == "__main__":
    print("CONTENT GENERATOR - SETTER PROFILES")
    print("=" * 60)
    
    for username in SETTER_PROFILES:
        print_content_plan(username)
    
    print(f"\n\n{'='*60}")
    print(f"  TOTAL: 5 setters x 9 posts = 45 posts")
    print(f"  Listos para producir en ComfyUI o Canva")
    print(f"{'='*60}")
