"""
Setter Profiles v3.0 — Perfiles de Instagram optimizados para B2B
Cada setter tiene una identidad, bio y estilo de comunicación definido.
Máxima credibilidad para generar respuestas de PYMES locales.
"""

# ═══════════════════════════════════════════════
# PERFILES DE SETTER — LÍNEA A (PYMES LOCALES)
# ═══════════════════════════════════════════════

SETTER_PROFILES = {
    "lauramtz.95": {
        "fullname": "Laura Martínez",
        "role": "Setter Línea A — Salud & Belleza",
        "target_niches": ["peluquerías", "clínicas estéticas", "centros de belleza", 
                          "spas", "barbershops", "centros de uñas", "dermatología"],
        "city_focus": "Málaga",
        "instagram_bio": [
            "Laura Martínez | Marketing Local 📍Málaga",
            "Ayudo a negocios de salud y belleza a llenar su agenda",
            "📩 DM para saber cómo",
            "⬇️ Casos reales"
        ],
        "personality": "Cercana, empática, profesional. Habla como una amiga que sabe de negocios.",
        "highlight_covers": ["Resultados", "Clientes", "Proceso", "Sobre mí"],
        "content_pillars": [
            "Tips de marketing para peluquerías/clínicas",
            "Antes/después de clientes (resultados)",
            "Día a día trabajando con negocios locales",
            "Frases motivacionales de emprendimiento"
        ],
        "posts_needed": 9,  # Mínimo 9 posts para parecer perfil real
        "post_ideas": [
            "Carrusel: '5 errores que cometen las peluquerías en Instagram'",
            "Reel: 'Así llené la agenda de una clínica estética en 2 semanas'",
            "Post imagen: Testimonio de cliente (diseño canva)",
            "Reel: 'Por qué tu negocio de belleza no crece en redes'",
            "Carrusel: '3 estrategias que funcionan para negocios locales'",
            "Post: Frase motivacional sobre emprendimiento femenino",
            "Reel: 'Lo que nadie te dice sobre captar clientes online'",
            "Carrusel: 'Caso de éxito: peluquería X pasó de 3 a 15 citas/día'",
            "Post: Presentación personal 'Quién soy y qué hago'"
        ]
    },
    
    "carlosruiz.88": {
        "fullname": "Carlos Ruiz",
        "role": "Setter Línea A — Hostelería & Gastronomía",
        "target_niches": ["restaurantes", "bares", "cafeterías", "catering", 
                          "food trucks", "panaderías", "heladerías"],
        "city_focus": "Málaga",
        "instagram_bio": [
            "Carlos Ruiz | Captación de Clientes 📍Málaga",
            "Lleno restaurantes y bares con clientes nuevos cada semana",
            "📩 Escríbeme y te cuento cómo",
            "⬇️ Resultados reales"
        ],
        "personality": "Directo, enrollado, tío de confianza. Habla como un colega que entiende hostelería.",
        "highlight_covers": ["Casos", "Método", "Reviews", "Yo"],
        "content_pillars": [
            "Marketing digital para restaurantes",
            "Resultados y casos de clientes",
            "Trucos de captación para hostelería",
            "Contenido personal (vida emprendedor)"
        ],
        "posts_needed": 9,
        "post_ideas": [
            "Carrusel: '5 formas de llenar tu restaurante sin pagar ads caros'",
            "Reel: 'Este bar pasó de vacío a lista de espera'",
            "Post: Testimonio de restaurante cliente",
            "Reel: 'Por qué Google Maps es tu mejor amigo si tienes un bar'",
            "Carrusel: 'Cómo conseguir reseñas de 5 estrellas en automático'",
            "Post: Dato curioso sobre marketing gastronómico",
            "Reel: 'Lo que los restaurantes que triunfan hacen diferente'",
            "Carrusel: 'De 0 a 50 reservas online/semana — caso real'",
            "Post: Presentación personal con storytelling"
        ]
    },
    
    "anabelenn.90": {
        "fullname": "Ana Torres",
        "role": "Setter Línea A — Fitness & Bienestar",
        "target_niches": ["gimnasios", "personal trainers", "centros de yoga", 
                          "pilates", "crossfit", "nutricionistas", "fisioterapeutas"],
        "city_focus": "Málaga",
        "instagram_bio": [
            "Ana Torres | Marketing para Gimnasios 📍Málaga",
            "Ayudo a centros fitness a conseguir +30 altas/mes",
            "📩 DM para tu plan personalizado",
            "⬇️ Mira los resultados"
        ],
        "personality": "Energética, motivadora, fit. Habla con la pasión de alguien que vive el mundo fitness.",
        "highlight_covers": ["Resultados", "Gym Life", "Tips", "Contacto"],
        "content_pillars": [
            "Marketing digital para gimnasios",
            "Captación de socios para centros fitness",
            "Resultados de clientes (antes/después)",
            "Contenido lifestyle fitness/wellness"
        ],
        "posts_needed": 9,
        "post_ideas": [
            "Carrusel: '5 estrategias para conseguir socios sin bajar precio'",
            "Reel: 'Cómo este gym pasó de 80 a 200 socios en 3 meses'",
            "Post: Testimonio de gimnasio cliente",
            "Reel: 'El error #1 que cometen los gimnasios en Instagram'",
            "Carrusel: 'Captación de altas: guía paso a paso'",
            "Post: Frase motivacional fitness + negocio",
            "Reel: 'Por qué las ofertas de enero NO funcionan'",
            "Carrusel: 'Caso real: personal trainer facturando x3'",
            "Post: Presentación personal con valores"
        ]
    },
    
    "pablofdezz86": {
        "fullname": "Pablo Fernández",
        "role": "Setter Línea A — Servicios Profesionales",
        "target_niches": ["abogados", "contables", "asesores", "inmobiliarias", 
                          "seguros", "dentistas", "médicos", "veterinarios"],
        "city_focus": "Málaga",
        "instagram_bio": [
            "Pablo Fernández | Clientes para Profesionales 📍Málaga",
            "Genero clientes cualificados para despachos y consultas",
            "📩 DM = Diagnóstico gratis de captación",
            "⬇️ Casos de éxito"
        ],
        "personality": "Serio pero accesible, profesional, datos y resultados. Habla con la seriedad que esperan abogados y dentistas.",
        "highlight_covers": ["Método", "Datos", "Clientes", "Bio"],
        "content_pillars": [
            "Marketing para servicios profesionales",
            "Captación de pacientes/clientes B2B",
            "Datos y métricas de resultados",
            "Educación sobre marketing digital profesional"
        ],
        "posts_needed": 9,
        "post_ideas": [
            "Carrusel: 'Marketing para abogados: lo que funciona en 2026'",
            "Reel: 'Cómo esta clínica dental llenó agenda en 15 días'",
            "Post: Estadística impactante + CTA",
            "Reel: 'Por qué el boca a boca ya no es suficiente'",
            "Carrusel: 'De 0 a 40 pacientes nuevos/mes — caso real'",
            "Post: Infografía sobre captación digital",
            "Reel: 'Las inmobiliarias que triunfan hacen esto'",
            "Carrusel: '3 formas de conseguir clientes sin puerta fría'",
            "Post: Presentación profesional con credenciales"
        ]
    },
    
    "martadiaz.24": {
        "fullname": "Marta Díaz",
        "role": "Setter Línea A — Comercio & Retail",
        "target_niches": ["tiendas de ropa", "joyerías", "floristerías", "tiendas gourmet",
                          "ópticas", "zapaterías", "papelerías", "tiendas de muebles"],
        "city_focus": "Málaga",
        "instagram_bio": [
            "Marta Díaz | Marketing para Tiendas 📍Málaga",
            "Llevo clientes nuevos a tu tienda cada semana",
            "📩 Escríbeme para saber cómo",
            "⬇️ Mira lo que hemos conseguido"
        ],
        "personality": "Creativa, visual, detallista. Habla el idioma del retail y la estética de producto.",
        "highlight_covers": ["Tiendas", "Antes/Después", "Ideas", "Hola!"],
        "content_pillars": [
            "Marketing visual para retail",
            "Estrategias de captación para tiendas físicas",
            "Casos de éxito de comercios locales",
            "Tendencias de marketing local"
        ],
        "posts_needed": 9,
        "post_ideas": [
            "Carrusel: '5 trucos para que tu tienda venda más en Instagram'",
            "Reel: 'Esta tienda de ropa triplicó ventas con esta estrategia'",
            "Post: Testimonio de tienda cliente",
            "Reel: 'Por qué tu tienda necesita Google Maps YA'",
            "Carrusel: 'Captación de clientes para comercio local — guía'",
            "Post: Inspiración visual de tiendas que lo hacen bien",
            "Reel: 'Cómo competir con Amazon siendo tienda local'",
            "Carrusel: 'Caso real: floristería pasó de 10 a 60 pedidos/semana'",
            "Post: Presentación personal + misión"
        ]
    }
}


def get_profile(username):
    """Obtener perfil de setter por username."""
    return SETTER_PROFILES.get(username, None)


def get_bio_text(username):
    """Obtener bio formateada para copiar y pegar en Instagram."""
    profile = get_profile(username)
    if not profile:
        return None
    return "\n".join(profile["instagram_bio"])


def print_all_profiles():
    """Imprimir todos los perfiles para revisión rápida."""
    for username, profile in SETTER_PROFILES.items():
        print(f"\n{'='*50}")
        print(f"@{username} — {profile['fullname']}")
        print(f"Rol: {profile['role']}")
        print(f"Nichos: {', '.join(profile['target_niches'][:4])}")
        print(f"\n📱 BIO INSTAGRAM:")
        print(get_bio_text(username))
        print(f"\n📌 HIGHLIGHTS: {' | '.join(profile['highlight_covers'])}")
        print(f"📷 Posts necesarios: {profile['posts_needed']}")
        print(f"\n🎯 Ideas de contenido:")
        for i, idea in enumerate(profile['post_ideas'][:5], 1):
            print(f"   {i}. {idea}")


if __name__ == "__main__":
    print("🎯 SETTER PROFILES v3.0 — CASH MODE")
    print("=" * 60)
    print_all_profiles()
