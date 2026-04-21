"""
Sistema 180 - Catalogo de Productos y Precios v3.0
Precios competitivos basados en investigacion del mercado espanol 2026.
Objetivo: cerrar 3.000 EUR antes del 30 de abril.

MERCADO ESPANOL (datos reales 2026):
- Landing page: 300-1.500 EUR (freelance 300-800, agencia 600-1.500)
- Web corporativa 3-5 pags: 800-2.500 EUR
- Tienda online basica: 1.800-5.000 EUR
- Low-cost freelance: 500-1.500 EUR
- Agencia premium: 1.300-6.000 EUR

NUESTRA ESTRATEGIA: Posicionarnos en la FRANJA MEDIA-BAJA con entrega rapida.
Somos mas baratos que una agencia pero mas profesionales que un freelance barato.
Precio con terminacion en 7 (psicologia de precios).
"""

# =========================================================
# CATALOGO LINEA A - PYMES LOCALES ESPANA
# Cara: Ares (cuando vuelva 23 abril)
# =========================================================

CATALOGO_LINEA_A = {
    "tier_1_starter": {
        "nombre": "Web Starter",
        "precio": 497,
        "descripcion": "Landing page profesional para negocios que necesitan presencia online YA",
        "ideal_para": "Peluquerias, bares, tiendas pequenas que no tienen web",
        "incluye": [
            "Landing page responsive (1 pagina)",
            "Formulario de contacto funcional",
            "Boton de WhatsApp directo",
            "Dominio .es o .com (1 ano)",
            "Hosting (1 ano)",
            "Certificado SSL",
            "SEO basico (Google My Business)",
            "Aviso legal + Cookies RGPD",
            "Entrega en 5 dias laborables",
        ],
        "no_incluye": [
            "Textos (los proporciona el cliente o +97 EUR)",
            "Fotos profesionales (usar las del cliente)",
            "Mantenimiento post-entrega",
        ],
        "pago": "50% al firmar, 50% al entregar",
        "margen_estimado": "~85% (coste real: dominio 12EUR + hosting 60EUR/ano)",
        "tiempo_entrega": "5 dias",
        "upsell": "Mantenimiento 47 EUR/mes",
    },
    
    "tier_2_profesional": {
        "nombre": "Web Profesional",
        "precio": 997,
        "descripcion": "Web corporativa completa para negocios que quieren captar clientes online",
        "ideal_para": "Clinicas, gimnasios, restaurantes, abogados que quieren agenda llena",
        "incluye": [
            "Web corporativa 3-5 paginas",
            "Diseno personalizado con su marca",
            "Formulario de contacto + reservas",
            "Boton WhatsApp + Click-to-call",
            "Integracion Google Maps",
            "Dominio + Hosting (1 ano)",
            "SSL + RGPD completo",
            "SEO on-page (meta tags, velocidad, schema)",
            "Google Analytics configurado",
            "Responsive perfecto (movil/tablet)",
            "2 ronda de revisiones",
            "Entrega en 7 dias laborables",
        ],
        "no_incluye": [
            "Redaccion de contenido (+197 EUR)",
            "Sesion de fotos (+297 EUR)",
            "Mantenimiento post-entrega",
        ],
        "pago": "50% al firmar, 50% al entregar",
        "margen_estimado": "~80%",
        "tiempo_entrega": "7 dias",
        "upsell": "Mantenimiento 97 EUR/mes + Google Ads 197 EUR/mes",
    },
    
    "tier_3_captacion": {
        "nombre": "Sistema Captacion",
        "precio": 1497,
        "descripcion": "Web + sistema automatizado de captacion de clientes con IA",
        "ideal_para": "Negocios que quieren llenar agenda automaticamente cada semana",
        "incluye": [
            "Todo lo del Tier 2 (Web Profesional)",
            "Chatbot IA en la web (FAQ automatico)",
            "Sistema de reservas online integrado",
            "Embudo de captacion (landing + formulario + email)",
            "Integracion con CRM basico",
            "3 emails automaticos de bienvenida",
            "Pixel de Meta configurado",
            "Google My Business optimizado",
            "Formacion 30min para el cliente",
            "Soporte 30 dias post-entrega",
        ],
        "pago": "40% firma, 30% mitad proyecto, 30% entrega",
        "margen_estimado": "~75%",
        "tiempo_entrega": "10-14 dias",
        "upsell": "Gestion de ads 297 EUR/mes + Mantenimiento 147 EUR/mes",
    },
}

# =========================================================
# CATALOGO LINEA C - WEBS PARA ITALIANOS
# Via amigas con contactos
# =========================================================

CATALOGO_LINEA_C = {
    "web_italia": {
        "nombre": "Sito Web Professionale",
        "precio": 800,  # IVA incluido
        "precio_premium": 1000,  # Con extras
        "descripcion": "Sito web professionale per attivita locali italiane",
        "incluye": [
            "Landing page o web 2-3 pagine",
            "Design responsive personalizzato",
            "Modulo di contatto",
            "Dominio + hosting (1 anno)",
            "Certificato SSL",
            "Conformita GDPR",
            "Consegna 5-7 giorni",
        ],
        "pago": "50% firma, 50% consegna",
        "split": "50/50 con amigas (captacion vs ejecucion)",
        "beneficio_neto": "400-500 EUR por web",
    }
}


# =========================================================
# ESTRATEGIA DE CIERRE RAPIDO (9 DIAS)
# Objetivo: 3.000 EUR antes del 30 abril
# =========================================================

PLAN_CIERRE_9_DIAS = {
    "objetivo_total": 3000,
    "deadline": "30 abril 2026",
    "escenarios": [
        {
            "nombre": "Escenario A: 6 x Starter",
            "ventas": "6 webs Starter a 497 EUR",
            "total": 2982,
            "dificultad": "MEDIA - muchos cierres pero precio bajo",
        },
        {
            "nombre": "Escenario B: 3 x Profesional",
            "ventas": "3 webs Profesional a 997 EUR",
            "total": 2991,
            "dificultad": "MEDIA-ALTA - menos cierres pero precio medio",
        },
        {
            "nombre": "Escenario C: 2 x Profesional + 1 Starter + 1 Italia",
            "ventas": "2x997 + 1x497 + 1x800(50%=400)",
            "total": 2891,
            "dificultad": "OPTIMA - diversificado entre lineas",
        },
        {
            "nombre": "Escenario D: 1 x Captacion + 1 x Profesional + 1 Italia",
            "ventas": "1x1497 + 1x997 + 1x800(50%=400)",
            "total": 2894,
            "dificultad": "IDEAL - alto ticket + diversificacion",
        },
    ],
    "plan_diario": {
        "dia_1_hoy": "Preparar perfiles setters + generar contenido ComfyUI",
        "dia_2": "Subir contenido a perfiles + empezar prospecting manual",
        "dia_3": "100 DMs con setters operativos + contactar amigas para Italia",
        "dia_4": "Seguimiento DMs + agendar primeras auditorias",
        "dia_5": "Auditorias gratuitas 15min + cerrar primer cliente",
        "dia_6": "Entregar primera web (si cerro dia 5) + seguir prospectando",
        "dia_7": "Segundo cierre + cobrar 50% primer cliente",
        "dia_8": "Entregas + tercer cierre",
        "dia_9": "Cobros finales + facturacion",
    }
}


def print_catalogo():
    """Imprimir catalogo para revision rapida."""
    print("=" * 60)
    print("  SISTEMA 180 - CATALOGO DE PRECIOS v3.0")
    print("  Mercado Espanol 2026 - Posicionamiento Franja Media")
    print("=" * 60)
    
    print("\n--- LINEA A: PYMES ESPANA ---")
    for key, tier in CATALOGO_LINEA_A.items():
        print(f"\n  [{tier['nombre']}] {tier['precio']} EUR")
        print(f"  Ideal: {tier['ideal_para']}")
        print(f"  Entrega: {tier['tiempo_entrega']}")
        print(f"  Incluye: {len(tier['incluye'])} items")
    
    print("\n--- LINEA C: ITALIA ---")
    it = CATALOGO_LINEA_C["web_italia"]
    print(f"\n  [{it['nombre']}] {it['precio']}-{it['precio_premium']} EUR")
    print(f"  Split: {it['split']}")
    print(f"  Beneficio neto: {it['beneficio_neto']}")
    
    print("\n--- ESCENARIOS PARA 3.000 EUR ---")
    for esc in PLAN_CIERRE_9_DIAS["escenarios"]:
        print(f"\n  {esc['nombre']}")
        print(f"  {esc['ventas']} = {esc['total']} EUR")
        print(f"  Dificultad: {esc['dificultad']}")


if __name__ == "__main__":
    print_catalogo()
