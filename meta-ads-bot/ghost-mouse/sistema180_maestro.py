"""
SISTEMA 180 — CONFIGURACIÓN MAESTRA v1.0
15 Ángulos de Comunicación + B7 + 4 Tipos de Contenido
Autor: José María Moreno
"""

# ===================================================================
# LOS 15 ÁNGULOS DE COMUNICACIÓN
# ===================================================================

ANGULOS = {
    1: {
        "nombre": "Dolor agudo del infoproductor",
        "ataca": "el dolor inmediato que el cliente siente cada día",
        "efecto": "reconocimiento instantáneo 'soy yo'",
        "intensidad": "Alta",
        "riesgo": "Bajo",
        "nivel_conciencia": ["N4", "N5"],
        "hooks": [
            "Llevas 8 meses publicando y facturas lo mismo que hace un año",
            "40k seguidores. 2 clientes al mes. Algo está muy roto",
            "Tu problema no es que no vendas. Es que nadie te escribe",
            "Publicas 5 veces por semana y Stripe sigue vacío",
        ],
    },
    2: {
        "nombre": "Objeción principal del mercado",
        "ataca": "la excusa mental con la que el cliente justifica no cambiar",
        "efecto": "rompe bloqueo para pasar a la acción",
        "intensidad": "Media",
        "riesgo": "Bajo",
        "nivel_conciencia": ["N5"],
        "hooks": [
            "No necesitas más seguidores para vender. Necesitas sistema",
            "No es el algoritmo. Tu contenido no convierte",
            "Te dicen que tu servicio es caro. Mentira. Tu problema es otro",
            "Más contenido no te va a salvar. Mejor contenido sí",
        ],
    },
    3: {
        "nombre": "Enemigo común",
        "ataca": "construye tribu contra un 'ellos'",
        "efecto": "identificación grupal + diferenciación",
        "intensidad": "Muy alta",
        "riesgo": "Medio",
        "nivel_conciencia": ["N4", "N5"],
        "hooks": [
            "Mientras tú montas tu funnel número 7, tu competidor factura con 1 post fijado",
            "Los VSL de 45 minutos están muertos. Nadie los ve",
            "Los gurús del hustle 24/7 te están mintiendo",
            "Funnels no venden. Sistemas sí",
        ],
    },
    4: {
        "nombre": "Método propio (diferencial)",
        "ataca": "posiciona TU sistema vs genérico del mercado",
        "efecto": "te hace único, memorable",
        "intensidad": "Media",
        "riesgo": "Bajo",
        "nivel_conciencia": ["N5"],
        "hooks": [
            "Así monto un sistema de captación en 21 días sin VSL ni landing",
            "Mi sistema tiene 57 agentes IA trabajando 24/7 para mis clientes",
            "Ads → Perfil → DM → Bot → Cierre. Nada más",
            "El Sistema B7 aplicado a tu marca personal",
        ],
    },
    5: {
        "nombre": "Casos y resultados",
        "ataca": "la duda de 'funciona pero no para mí'",
        "efecto": "prueba social tangible",
        "intensidad": "Media",
        "riesgo": "Bajo",
        "nivel_conciencia": ["N5"],
        "hooks": [
            "Empecé con 669 seguidores. En 30 días llegué a X",
            "Cliente X pasó de 2 ventas/mes a 9 con el sistema",
            "Así monté el bot de ManyChat para [cliente]",
            "Antes / después de aplicar el Sistema 180",
        ],
    },
    6: {
        "nombre": "Identidad / manifiesto",
        "ataca": "conecta valores, construye tribu",
        "efecto": "fidelización profunda",
        "intensidad": "Baja",
        "riesgo": "Muy bajo",
        "nivel_conciencia": ["N3", "N4", "N5"],
        "hooks": [
            "No busco views. Busco DMs de compra",
            "Prefiero 100 vistas con 1 comprador que 100k sin ventas",
            "El contenido que no genera DMs es ruido bonito",
            "Cobrar poco no te hace más accesible. Te hace menos creíble",
        ],
    },
    7: {
        "nombre": "Contradicción / contra-narrativa",
        "ataca": "el consenso aceptado del mercado",
        "efecto": "genera debate, memorabilidad, shares",
        "intensidad": "Muy alta",
        "riesgo": "Alto",
        "nivel_conciencia": ["N4", "N5"],
        "hooks": [
            "Todos dicen 'publica más'. Yo digo 'publica distinto'",
            "Los gurús del marketing te dicen X. Lo que funciona es Y",
            "No necesitas vender más barato. Necesitas vender mejor",
            "Viralidad es enemiga de la facturación",
        ],
    },
    8: {
        "nombre": "Educacional profundo",
        "ataca": "a quien no sabe por dónde empezar",
        "efecto": "autoridad + atrae N3",
        "intensidad": "Baja",
        "riesgo": "Muy bajo",
        "nivel_conciencia": ["N3", "N4"],
        "hooks": [
            "Te explico en 60s cómo funciona un bot de ManyChat",
            "Los 3 tipos de ads en Meta que de verdad funcionan",
            "Así estructuras un reel que convierte",
            "La diferencia entre lead, MQL y SQL explicada simple",
        ],
    },
    9: {
        "nombre": "Urgencia / coste de no actuar",
        "ataca": "la procrastinación del cliente",
        "efecto": "empuja a tomar decisión ahora",
        "intensidad": "Alta",
        "riesgo": "Medio",
        "nivel_conciencia": ["N5"],
        "hooks": [
            "Cada mes sin sistema = X euros perdidos",
            "Llevas 2 años esperando 'el momento adecuado'. El momento es hoy",
            "Mientras piensas, tu competidor ejecuta",
            "Cada DM que no respondes en 1h es un cliente que se va",
        ],
    },
    10: {
        "nombre": "Detrás de escena (BTS)",
        "ataca": "el escepticismo / humaniza",
        "efecto": "construye cercanía + credibilidad",
        "intensidad": "Baja",
        "riesgo": "Muy bajo",
        "nivel_conciencia": ["N3", "N4", "N5"],
        "hooks": [
            "Así configuro los agentes IA de un cliente nuevo",
            "Mi setup de grabación semanal en 2h",
            "Cómo escribo los guiones de mis clientes en bloque",
            "Un día normal montando Sistema 180",
        ],
    },
    11: {
        "nombre": "Storytelling personal",
        "ataca": "la frialdad de los datos",
        "efecto": "conexión emocional fuerte",
        "intensidad": "Media",
        "riesgo": "Bajo",
        "nivel_conciencia": ["N3", "N4", "N5"],
        "hooks": [
            "Hace 6 meses tenía 200€ en el banco. Hoy...",
            "Fallé mi primera reunión con un cliente. Así lo arreglé",
            "Por qué dejé la universidad para montar Sistema 180",
            "El momento en que entendí que tenía que cambiar todo",
        ],
    },
    12: {
        "nombre": "Comparación antes/después",
        "ataca": "la duda de progreso",
        "efecto": "prueba visual del cambio",
        "intensidad": "Media",
        "riesgo": "Bajo",
        "nivel_conciencia": ["N4", "N5"],
        "hooks": [
            "Mi perfil antes vs ahora",
            "Este cliente antes del sistema / después",
            "Lo que publicaba antes / lo que publico ahora",
            "Mi facturación antes de tener sistema / después",
        ],
    },
    13: {
        "nombre": "Listados / frameworks",
        "ataca": "a quien quiere pasos accionables",
        "efecto": "alto guardado, autoridad técnica",
        "intensidad": "Baja",
        "riesgo": "Muy bajo",
        "nivel_conciencia": ["N3", "N4", "N5"],
        "hooks": [
            "7 errores que cometes en tu bio de Instagram",
            "Los 4 tipos de contenido que sí venden",
            "5 KPIs que debes mirar cada semana",
            "El checklist de un perfil que convierte",
        ],
    },
    14: {
        "nombre": "Conversación directa / debate",
        "ataca": "genera engagement y comentarios",
        "efecto": "algoritmo + visibilidad",
        "intensidad": "Baja",
        "riesgo": "Muy bajo",
        "nivel_conciencia": ["N5"],
        "hooks": [
            "¿Qué prefieres: 10k seguidores o 10 clientes? Comenta",
            "Pregunta directa: ¿por qué NO contratas a alguien como yo?",
            "Decime: ¿cuál es tu mayor traba para escalar?",
            "Respondo sinceramente: ¿la IA reemplaza a los consultores?",
        ],
    },
    15: {
        "nombre": "Predicción / visión de futuro",
        "ataca": "el FOMO + autoridad de visión",
        "efecto": "te posiciona como referente de futuro",
        "intensidad": "Alta",
        "riesgo": "Medio",
        "nivel_conciencia": ["N4", "N5"],
        "hooks": [
            "En 2027 los infoproductores sin IA no van a poder competir",
            "El 80% de las agencias van a desaparecer en 3 años",
            "Por qué el modelo VSL + landing va a morir antes de 2027",
            "Lo que va a pasar con Instagram cuando entre la IA generativa",
        ],
    },
}

# ===================================================================
# FASES Y ÁNGULOS ACTIVOS POR FASE
# ===================================================================

FASES = {
    1: {
        "nombre": "Arrancar marca desde cero (mes 1-2)",
        "angulos_activos": [1, 2, 4, 5, 6, 8, 13],
        "razon": "Sin tribu previa, necesitas identificarte, romper objeciones, mostrar método y educar.",
    },
    2: {
        "nombre": "Tribu construida (mes 3-6)",
        "angulos_activos": [1, 2, 3, 4, 5, 7, 11],
        "razon": "Ya tienes audiencia que te defiende, puedes polarizar más.",
    },
    3: {
        "nombre": "Autoridad consolidada (mes 6-12)",
        "angulos_activos": [1, 4, 5, 7, 10, 12, 15],
        "razon": "Datos reales, puedes predecir y mostrar transformaciones.",
    },
}

# Fase actual de Sistema 180
FASE_ACTUAL = 1

# ===================================================================
# 4 TIPOS DE CONTENIDO
# ===================================================================

TIPOS_CONTENIDO = {
    "dolor": {
        "porcentaje": 40,
        "objetivo": "atraer, que el cliente diga 'soy yo'",
        "angulos": [1, 9, 11, 12],
        "cta": "palabra clave al DM (AUDITORÍA, SISTEMA)",
    },
    "objecion": {
        "porcentaje": 30,
        "objetivo": "romper creencias y excusas mentales",
        "angulos": [2, 3, 7],
        "cta": "comentario con palabra clave",
    },
    "producto": {
        "porcentaje": 20,
        "objetivo": "posicionar tu solución sin vender agresivo",
        "angulos": [4, 5, 8, 10, 13],
        "cta": "directo ('si quieres esto para ti, escribe X')",
    },
    "autoridad": {
        "porcentaje": 10,
        "objetivo": "humanizar, construir confianza",
        "angulos": [6, 11, 15],
        "cta": "suave o ninguno",
    },
}

# ===================================================================
# SISTEMA B7
# ===================================================================

B7_PREGUNTAS = [
    "¿Qué quiere el héroe/cliente?",
    "¿Qué o quién se lo impide?",
    "¿Cómo me posiciono como guía?",
    "¿Qué plan le doy?",
    "¿Qué CTA le comunico?",
    "¿Cómo será su vida si NO actúa?",
    "¿Cómo será su vida si SÍ actúa?",
]

# ===================================================================
# FRAMEWORK REEL CORTO 4 BLOQUES
# ===================================================================

REEL_CORTO = {
    "bloque1": "HOOK (0-2s): frase que detiene scroll",
    "bloque2": "IDENTIFICACIÓN (2-10s): describe situación exacta",
    "bloque3": "REFRAME (10-40s): explica por qué le pasa",
    "bloque4": "CTA (40-50s): palabra clave al DM con filtro",
}

# ===================================================================
# ESCALERA DE PRECIOS
# ===================================================================

ESCALERA = {
    1: {"nombre": "Validación", "setup": 0, "mensual": 297, "performance": 20, "requisito": "0 casos"},
    2: {"nombre": "Oferta Real", "setup": 997, "mensual": 497, "performance": 15, "requisito": "3 casos"},
    3: {"nombre": "Consolidada", "setup": 1997, "mensual": 997, "performance": 20, "requisito": "10 casos"},
    4: {"nombre": "Elite", "setup": 4997, "mensual": 1997, "performance": 30, "requisito": "20 casos"},
}

# ===================================================================
# FUNCIONES DE GENERACIÓN
# ===================================================================

import random


def get_angulos_activos():
    """Devuelve los 7 ángulos activos de la fase actual."""
    return FASES[FASE_ACTUAL]["angulos_activos"]


def get_hook(angulo_num):
    """Devuelve un hook aleatorio del ángulo especificado."""
    angulo = ANGULOS.get(angulo_num)
    if angulo:
        return random.choice(angulo["hooks"])
    return ""


def generar_email_con_angulo(angulo_num, nombre, nicho, ciudad):
    """Genera un email frío usando un ángulo específico de los 15."""
    angulo = ANGULOS[angulo_num]
    hook = random.choice(angulo["hooks"])

    # Adaptar hook a PYME local (reemplazar contexto infoproductor → negocio local)
    adaptaciones = {
        "seguidores": "clientes",
        "Stripe": "caja registradora",
        "infoproductor": "negocio",
        "publicando": "trabajando",
        "contenido": "servicio",
        "DMs": "llamadas",
        "reel": "publicidad",
        "funnel": "publicidad online",
        "VSL": "vídeo promocional",
    }

    hook_adaptado = hook
    for old, new in adaptaciones.items():
        hook_adaptado = hook_adaptado.replace(old, new)

    # Formateo estilo Luis Monge Malo: minúsculas, como si fuera enviado por un amigo
    subject = "¿Por qué {} se está llevando a vuestros clientes?".format(nicho)

    body = """Hola.

El otro día me di cuenta de una cosa curiosa trabajando con negocios en {ciudad}.
Resulta que {}.

Y lo peor no es eso. Lo peor es que me puse a hacer una prueba sencilla: busqué "{} en {}" en Google como si fuera un cliente normal.
Vuestros competidores aparecían con todo reluciente. Vosotros, en cambio, estabais invisibles.

Es curioso cómo funciona la mente humana (y el mercado). Si pasas por delante de un restaurante y está vacío, no entras. Si buscas un servicio en internet y el de al lado tiene un ecosistema digital sólido y tú no, el cliente automáticamente asume que la competencia es mejor.

No porque sean mejores profesionales que vosotros. Simplemente porque ponen menos barreras para que les compren.

Y aquí viene el dolor real si hacemos la cuenta de la vieja: 
Imagina a 10 personas al día buscando exactamente lo que hacéis y terminando en el negocio de otro. Multiplica lo que os deja un cliente por 10 al día, por 30 días... Es una hemorragia de miles de euros mensuales que, literalmente, le estáis regalando a la competencia.

La moraleja de todo esto es que hoy en día el mejor producto no siempre gana. Gana el negocio que hace más fácil la compra.

Afortunadamente, tiene fácil solución. 
Me dedico a crear ecosistemas digitales y embudos que cortan esta hemorragia. Puedo dejaros todo el sistema montado y funcionando en 5 días por 497 EUR. Un único pago que recuperáis con los primeros 3 clientes que dejen de irse al negocio de enfrente.

Si os gustaría recuperar el control de esas reservas y dejar de perder dinero, respondedme a este email y os cuento cómo va.
Si preferís que se lo sigan llevando ellos, ignorad este correo y tan amigos.

Un saludo,

José María Moreno
Sistema 180""".format(hook_adaptado.lower(), nicho, ciudad)

    return subject, body


def print_angulos_activos():
    """Imprime los ángulos activos de la fase actual."""
    fase = FASES[FASE_ACTUAL]
    print("=" * 60)
    print("  FASE {}: {}".format(FASE_ACTUAL, fase["nombre"]))
    print("  Razón: {}".format(fase["razon"]))
    print("=" * 60)
    for num in fase["angulos_activos"]:
        a = ANGULOS[num]
        print("\n  ÁNGULO {}: {}".format(num, a["nombre"]))
        print("  Intensidad: {} | Riesgo: {}".format(a["intensidad"], a["riesgo"]))
        print("  Hooks:")
        for h in a["hooks"]:
            print("    → {}".format(h))


if __name__ == "__main__":
    print_angulos_activos()
