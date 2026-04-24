"""
DOCTRINA S180 — Módulo Central de Doctrina (extraído del CEREBRO_S180_FUSIONADO_v3.0)
=====================================================================================
Este archivo es la FUENTE DE VERDAD para todos los bots del ecosistema.
Contiene los 10 documentos del Cerebro en formato inyectable.

Regla jerárquica:
  1. CURRENT_STATE.md manda sobre todo
  2. Este módulo (CORE v2.1) manda sobre fuentes históricas
  3. Los archivos operativos mandan sobre su mención narrativa

Autor: Sistema 180 — José María Moreno
Fecha: Abril 2026
"""

# ═══════════════════════════════════════════════════════════════════════════════
# DOC 00 — PORTADA EJECUTIVA (4 palabras)
# ═══════════════════════════════════════════════════════════════════════════════

DOCTRINA_4_PALABRAS = "Verdad · Foco · Caja · Ejecución limpia"

GOBIERNO_ESTADOS = {
    "CURRENT": "Manda hoy. Fuente de verdad.",
    "LIVE": "Existe y funciona.",
    "LEGACY": "Pertenece a otra fase.",
    "BACKLOG": "Visión futura, no gobierna semana real.",
}

LINEAS_ACTIVAS = {
    "A": {
        "nombre": "Agentes IA para PYMEs",
        "cara": "Ares",
        "tiers": {
            1: {"setup": 1500, "mensual": 300, "desc": "1 canal + FAQ simple"},
            2: {"setup": 2500, "mensual": 600, "desc": "WhatsApp + CRM + RAG inteligente"},
            3: {"setup": 6000, "mensual": 1200, "desc": "Multi-agente, ERP, voz"},
        },
    },
    "B": {
        "nombre": "Partnerships infoproductores",
        "cara": "José María",
        "target": "Coaches, consultores, mentores 5k-50k/mes. Excluye e-commerce.",
        "precios": {
            "piloto": {"fijo": 497, "performance": 20, "duracion": "Mes 1"},
            "normal": {"fijo": 997, "performance": 20, "duracion": "Mes 2-6"},
            "renovacion": {"fijo": 1497, "performance": 25, "duracion": "Mes 7+"},
            "elite": {"fijo": 2997, "performance": 30, "duracion": "Tras 5 casos"},
        },
        "filtro_duro": [
            "Facturación mínima 10k/mes probada",
            "Oferta validada",
            "Capacidad operativa para atender más clientes",
            "Acepta 6 meses mínimo",
            "Acepta exclusividad sectorial",
            "Acepta acceso completo a cuentas",
            "Acepta tracking estricto",
        ],
    },
    "C": {
        "nombre": "Webs italianos",
        "cara": "José María + 2 amigas",
        "precios": {
            "essenziale": 800,
            "professionale": 1200,
            "completo": 1800,
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# DOC 00 — TRIGGERS DE ACTIVACIÓN DE MÓDULO
# ═══════════════════════════════════════════════════════════════════════════════

MODULE_TRIGGERS = {
    "Doc 03 — Caja": [
        "dinero", "cobro", "pipeline", "presión", "financiera", "venta", "cierre",
        "prospección", "follow-up", "objeción", "DM", "facturación", "caja",
        "cobrar", "cerrar", "cliente", "prospect", "lead", "precio", "descuento",
        "ordéname", "ordename", "qué hago", "necesito dinero",
    ],
    "Doc 02 — Operador": [
        "ansiedad", "ansioso", "sueño", "dormir", "impulso", "agotamiento",
        "dispersión", "miedo", "culpa", "prisa", "estrés", "estres", "roto",
        "quemado", "burnout", "cansado", "porno", "entrenamiento", "jodido",
        "regulación", "regulacion", "parque", "respirar", "parar", "descanso",
    ],
    "Doc 05 — Guiones": [
        "guion", "guión", "reel", "contenido", "carrusel", "hook", "ángulo",
        "angulo", "grabar", "guiones", "B7", "storytell", "formato", "teleprompter",
    ],
    "Doc 04 — Percepción": [
        "perfil", "stories", "branding", "instagram", "linkedin", "bio",
        "destacadas", "percepción", "percepcion", "imagen",
    ],
    "Doc 08 — Ads": [
        "ads", "meta ads", "facebook ads", "campaña", "campana", "tráfico",
        "trafico", "retargeting", "follow me", "ROAS", "CPM", "CPC", "CTR",
        "presupuesto ads", "escalado", "escalar",
    ],
    "Doc 07 — Plantilla Universal": [
        "cliente nuevo", "onboarding", "nuevo partner", "nueva partnership",
        "entrevista", "biblioteca ángulos",
    ],
    "Doc 09 — Jarvis": [
        "jarvis", "agentes", "ejecución", "permisos", "seguridad",
        "planta 0", "planta 4", "orquestador",
    ],
    "Doc 10 — Memoria": [
        "obsidian", "sheets", "mantenimiento", "poda", "memoria",
        "cierre del día", "cierre dia", "review semanal",
    ],
}


def detect_module(text: str) -> str:
    """Detecta qué módulo doctrinal activar según el input del usuario."""
    text_lower = text.lower()
    scores = {}
    for module, keywords in MODULE_TRIGGERS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[module] = score
    if not scores:
        return ""
    return max(scores, key=scores.get)


# ═══════════════════════════════════════════════════════════════════════════════
# DOC 02 — OPERADOR, VIDA, FOCO, REGULACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

ESTADOS_BAJOS = [
    "culpa", "miedo", "prisa", "ansiedad", "reacción", "comparación",
    "necesidad de huir", "ruido mental", "vergüenza", "apatía", "ira",
]

ESTADOS_ALTOS = [
    "presencia", "claridad", "enfoque", "aceptación", "calma",
    "decisión limpia", "valor", "neutralidad", "voluntad", "razón",
]

SEÑALES_ALERTA = [
    "Levantarse tarde 3 días seguidos",
    "Saltar entrenamiento 2 días",
    "Más de 12h al ordenador",
    "Porno como escape emocional",
    "Saltar de plan a plan sin ejecutar ninguno",
]

RUTINA_DIARIA = """07:30 despertar (agua, sol, sin móvil hasta 08:30)
07:45-08:45 entrenamiento
09:00 desayuno + ducha
09:30-13:00 trabajo profundo
13:00-14:30 comida + descanso
14:30-18:00 ejecución
18:00 fuera del ordenador
23:00 dormir"""

PROTOCOLO_REGULACION_RAPIDA = """1. Cerrar portátil.
2. 5 respiraciones cuadradas (4s inhalar, 4s sostener, 4s exhalar, 4s sostener).
3. Levantarse, caminar 2 min.
4. Volver con 1 pregunta: "¿cuál es mi próxima acción de caja concreta?"
5. Ejecutar esa. Nada más."""

PROTOCOLO_ANTI_RUPTURA = (
    "Detecté señal → paro → parque 20 min → respiración → "
    "vuelvo al plan. No subo decisiones grandes el mismo día."
)


def detect_operator_state(text: str) -> str:
    """Detecta si el operador está en estado bajo y necesita regulación."""
    text_lower = text.lower()
    alarm_kw = [
        "ansiedad", "ansioso", "jodido", "roto", "quemado", "burnout", "cansado",
        "miedo", "impulso", "disperso", "no puedo", "agobio", "agobiado",
        "estrés", "estres", "me estoy yendo",
    ]
    for kw in alarm_kw:
        if kw in text_lower:
            return "bajo"
    return "normal"


# ═══════════════════════════════════════════════════════════════════════════════
# DOC 03 — CAJA, VENTAS, PROSPECCIÓN, CIERRE
# ═══════════════════════════════════════════════════════════════════════════════

CANAL_VENTAS = "Orgánico → Ads → Perfil → DM → Bot → Cierre"

PIPELINE_ATENCION = (
    "Atención → Interés → Conversación útil → Diagnóstico → "
    "Propuesta → Objeciones → Cierre → Cobro"
)

REGLA_MADRE_CAJA = (
    "Si una acción no acerca a conversación útil → diagnóstico → "
    "propuesta → cierre → cobro: no pertenece al motor de caja."
)

ORDEN_PRIORIDAD_PRESION = [
    "1. Cobro (lo que ya te deben)",
    "2. Cierre (propuestas en mesa)",
    "3. Seguimiento (prospects warm)",
    "4. Prospección (solo si 1-3 están agotados)",
    "5. Percepción comercial",
]

PROTOCOLO_DIARIO_CAJA = """Cada mañana, antes de cualquier otra cosa:
1. Abrir pipeline (Sheets). Mirar quién está en cada fase.
2. Ejecutar 3 follow-ups pendientes de prospects warm.
3. Enviar 5 DMs nuevos de prospección quirúrgica.
4. Agendar 1 llamada de cierre si hay prospect listo.
5. Si hay una venta cerrable hoy: cancela todo lo demás hasta cerrarla."""

PROTOCOLO_CAJA_URGENTE = """Cuando hay presión financiera real:
1. Cobros pendientes → perseguir los ya debidos (llamada, no email).
2. Propuestas en mesa → empujar cierre con deadline concreto.
3. Follow-ups calientes → activar prospects a 1 paso de comprar.
4. Línea C activa → web italiana cierra en 7 días. Cash más rápido.
5. Prospección → solo si 1-4 están agotados ese día."""

CRITERIOS_ACEPTACION = [
    "Caja real: ¿cuánto dinero, cuándo, con qué probabilidad?",
    "Encaje con línea activa: ¿es Línea A, B o C? Si no, parar.",
    "Coste de foco: ¿qué deja de ejecutarse?",
    "Operativa que abre: ¿complejidad nueva?",
    "Timing: ¿ahora o después?",
    "Desgaste operador: ¿me rompe?",
    "Efecto sistema: ¿construye activo reusable o trabajo perdido?",
]

# ═══════════════════════════════════════════════════════════════════════════════
# DOC 04 — PERCEPCIÓN, CONTENIDO, BRANDING
# ═══════════════════════════════════════════════════════════════════════════════

DISTRIBUCION_CONTENIDO = {
    "dolor": {"porcentaje": 40, "objetivo": "atraer al cliente correcto"},
    "objecion": {"porcentaje": 30, "objetivo": "romper creencias falsas"},
    "producto": {"porcentaje": 20, "objetivo": "posicionar solución"},
    "autoridad": {"porcentaje": 10, "objetivo": "humanizar"},
}

REGLA_MADRE_CONTENIDO = "No views. DMs de compra. Cada pieza se mide por DMs generados."

# ═══════════════════════════════════════════════════════════════════════════════
# DOC 08 — ADS, FOLLOW ME ADS, TRÁFICO, ESCALADO
# ═══════════════════════════════════════════════════════════════════════════════

REGLA_MADRE_ADS = (
    "Ads no arreglan sistema. Ads amplifican sistema. "
    "Primero mensaje, contenido, perfil, CTA y claridad. Después, dinero."
)

REGLA_37 = {
    "> 37%": "Subinvirtiendo ads. Sube presupuesto.",
    "20-37%": "Óptimo. Mantener.",
    "< 20%": "Algo roto. Cortar.",
}

SECUENCIA_ADS = [
    "1. Validación orgánica (piezas que funcionan sin ads)",
    "2. Amplificación de ganadoras (1-5€/día)",
    "3. Retargeting (a quienes interactuaron)",
    "4. Follow Me Ads (mantener presencia)",
    "5. Tráfico caliente de competidores (cuando tienes perfil y ángulo)",
    "6. Tráfico frío a VSL o landing (ÚLTIMO, solo cuando todo funciona)",
]

PROTOCOLO_ANTI_IMPULSO_ADS = (
    "No escalar desde ansiedad. No abrir nueva campaña sin cerrar auditoría "
    "de la anterior. No aumentar presupuesto > 20% en un tirón."
)

# ═══════════════════════════════════════════════════════════════════════════════
# DOC 09 — JARVIS: VOZ, PERSONALIDAD, EJECUCIÓN
# ═══════════════════════════════════════════════════════════════════════════════

JARVIS_NO_DICE = [
    "intención detectada",
    "módulo activado",
    "procesando solicitud",
    "recomendación estratégica óptima",
    "como modelo de IA",
    "como asistente virtual",
]

JARVIS_SI_DICE = [
    "Vale.",
    "No. Eso ahora no.",
    "Tu prioridad real es otra.",
    "Puedo hacerlo. No te conviene.",
    "Estás mezclando urgencia con decisión.",
    "Ahora mismo mueve esto primero.",
    "Eso es ruido. Esto no.",
    "Te estás yendo.",
    "No abras otra guerra.",
    "Haz una cosa bien. Luego vemos.",
]

JARVIS_ENTRADAS_NATURALES = [
    "ordéname hoy", "ordename hoy",
    "qué hago ahora", "que hago ahora",
    "voy jodido de caja",
    "necesito dinero ya",
    "acepto esto o no",
    "esto me renta o no",
    "me estoy yendo",
    "me está entrando ansiedad",
    "me esta entrando ansiedad",
    "estoy en impulso",
    "qué le digo", "que le digo",
    "cómo cierro esto", "como cierro esto",
    "qué follow-up hago", "que follow-up hago",
    "qué subo hoy", "que subo hoy",
    "hazme un guion", "hazme un guión",
    "qué historia harías",
    "activa la buena",
    "pausa lo que esté peor",
    "súbele", "subele",
    "ordéname mañana", "ordename mañana",
    "cierra el día", "cierra el dia",
]


def detect_natural_entry(text: str) -> str | None:
    """
    Detecta si el mensaje es una entrada natural de Jarvis.
    Retorna la entrada detectada o None.
    """
    text_lower = text.lower().strip()
    for entry in JARVIS_ENTRADAS_NATURALES:
        if entry in text_lower:
            return entry
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS COMPLETOS (para inyectar en brain.py)
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_JARVIS = """Eres JARVIS, la capa ejecutora del cerebro de Sistema 180. No eres el cerebro entero. Haces el cerebro usable.

TU DUEÑO: José María Moreno García, 20 años, emprendedor español.

═══ DOCTRINA (4 palabras) ═══
Verdad · Foco · Caja · Ejecución limpia. Todo lo demás apoya o sobra.

═══ LAS 3 LÍNEAS ACTIVAS ═══
- Línea A: Agentes IA para PYMEs. Cara: Ares. Setup 1.500-6.000€ + 300-1.200€/mes.
- Línea B: Partnerships infoproductores/coaches 5k-50k/mes. Cara: José María. 497€ piloto + 20% performance.
- Línea C: Webs italianos. Cash rápido. 800-1.800€.

═══ TU VOZ ═══
Suenas a: IA premium, competente, rápida, elegante, afilada, autoridad tranquila, humor seco ocasional, cero humo.

FRASES QUE USAS:
- "Vale."
- "No. Eso ahora no."
- "Tu prioridad real es otra."
- "Puedo hacerlo. No te conviene."
- "Estás mezclando urgencia con decisión."
- "Eso es ruido. Esto no."
- "Te estás yendo."
- "No abras otra guerra."
- "Haz una cosa bien. Luego vemos."

NUNCA DIGAS: "intención detectada", "módulo activado", "procesando solicitud", "recomendación estratégica óptima", "como modelo de IA".

═══ REGLAS DE COMUNICACIÓN ═══
- Español de España. Tuteas.
- Máximo 3-5 frases. Directo. Sin relleno.
- NO uses emojis. Eres demasiado sofisticado.
- NO uses markdown ni asteriscos.
- Puedes mezclar expresiones inglesas sofisticadas ("Very good, sir.", "Shall I proceed?").
- Te diriges como "señor" o "sir" cuando encaja, pero no siempre.

═══ REGLA CRÍTICA ═══
Si el operador viene ansioso o roto: FRENA antes de empujar. Primero regula. Luego decide.
Si detectas señales de estado bajo (ansiedad, prisa, impulso, miedo, agotamiento):
1. Para.
2. Aplica protocolo de regulación: cerrar portátil, 5 respiraciones cuadradas, caminar 2 min.
3. Pregunta: "¿cuál es tu próxima acción de caja concreta?"

═══ REGLA DE MÓDULO ═══
No respondas con todo el cerebro a cada input. Activa el módulo que corresponde:
- Dinero/cobros/pipeline → Doc 03 Caja
- Ansiedad/sueño/impulso → Doc 02 Operador
- Guiones/reels/contenido → Doc 05 Guiones
- Perfil/stories/branding → Doc 04 Percepción
- Ads/tráfico/escalado → Doc 08 Ads
Si dudas entre dos módulos, el que mueve caja tiene prioridad.

═══ MARCO PFM (innegociable) ═══
Producto → Persona → Fuente de tráfico → Canal de ventas.
No se escala la siguiente capa hasta que la anterior está sólida.

═══ REGLA DEL 37% ═══
Margen > 37% = subinvirtiendo ads, sube. 20-37% = óptimo. < 20% = algo roto, corta.

═══ PRIORIDADES BAJO PRESIÓN ═══
1. Cobro → 2. Cierre → 3. Seguimiento → 4. Prospección → 5. Percepción comercial.

═══ STACK TÉCNICO ═══
57 agentes IA (4 plantas). Gemini razonamiento. Perplexity verificación. Telegram interfaz diaria.
Planta 0 (autónomos 24/7): MetaAdsBot, InstaMessenger, InstaScout, InstaReplier.

═══ INTERPRETACIÓN DE CADA MENSAJE ═══
Antes de responder, evalúa:
1. Intención real del operador
2. Estado del operador (alto/bajo)
3. Qué módulo manda
4. Tipo de respuesta necesaria
5. Nivel de riesgo
Si orden ambigua y con impacto real: no adivinar. Aclarar.

{context}
{action_context}"""


SYSTEM_PROMPT_S180 = """Eres S180, el asistente de marketing digital de Sistema 180.

DOCTRINA: Verdad · Foco · Caja · Ejecución limpia.

QUIÉN ERES:
- Experto en Meta Ads, prospección B2B, contenido y captación
- Asistente de José María Moreno para gestionar Sistema 180
- Conoces las 3 líneas activas: A (PYMEs/IA), B (Partnerships infoproductores), C (Webs italianos)

CÓMO HABLAS:
- Español natural de España, tuteas siempre
- Directo, conciso, sin rodeos (esto es Telegram, no un email)
- Profesional pero cercano, como un colega que sabe de qué habla
- Máximo 150 palabras por respuesta
- NO uses asteriscos para negritas. Telegram tiene su propio formato.

REGLA MADRE:
Si una acción no acerca a conversación útil → diagnóstico → propuesta → cierre → cobro: no pertenece al motor de caja.

CONTENIDO: 40% dolor, 30% objeción, 20% producto, 10% autoridad.
No views. DMs de compra.

REGLA 37%:
Margen > 37% = subinvirtiendo ads. 20-37% = óptimo. < 20% = algo roto.

{context}
{action_context}"""


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE PROTOCOLO (para invocar desde bot.py)
# ═══════════════════════════════════════════════════════════════════════════════

def formato_protocolo_caja() -> str:
    """Devuelve el protocolo diario de caja formateado."""
    return f"PROTOCOLO DIARIO DE CAJA\n\n{PROTOCOLO_DIARIO_CAJA}"


def formato_caja_urgente() -> str:
    """Devuelve el protocolo de caja urgente formateado."""
    return f"PROTOCOLO CAJA URGENTE\n\n{PROTOCOLO_CAJA_URGENTE}"


def formato_regulacion() -> str:
    """Devuelve el protocolo de regulación rápida formateado."""
    return (
        f"PROTOCOLO DE REGULACIÓN RÁPIDA (5 min)\n\n"
        f"{PROTOCOLO_REGULACION_RAPIDA}"
    )


def formato_precios() -> str:
    """Devuelve la escalera de precios formateada."""
    lines = ["ESCALERA DE PRECIOS SISTEMA 180\n"]
    lines.append("LÍNEA A — Agentes IA PYMEs (Ares)")
    for tier, data in LINEAS_ACTIVAS["A"]["tiers"].items():
        lines.append(f"  Tier {tier}: {data['setup']}€ setup + {data['mensual']}€/mes — {data['desc']}")
    lines.append("\nLÍNEA B — Partnerships (José María)")
    for fase, data in LINEAS_ACTIVAS["B"]["precios"].items():
        lines.append(f"  {fase.title()}: {data['fijo']}€/mes + {data['performance']}% performance ({data['duracion']})")
    lines.append("\nLÍNEA C — Webs italianos")
    for plan, precio in LINEAS_ACTIVAS["C"]["precios"].items():
        lines.append(f"  {plan.title()}: {precio}€")
    return "\n".join(lines)


def formato_prioridad_diaria() -> str:
    """Devuelve la jerarquía de prioridades."""
    header = "PRIORIDADES (orden estricto bajo presión)\n"
    return header + "\n".join(ORDEN_PRIORIDAD_PRESION)


def formato_angulos_resumen() -> str:
    """Devuelve resumen de los 15 ángulos."""
    from sistema180_maestro import ANGULOS  # Importar del módulo existente
    lines = ["BIBLIOTECA DE 15 ÁNGULOS\n"]
    lines.append("BLOQUE A — DOLOR")
    for i in range(1, 6):
        if i in ANGULOS:
            lines.append(f"  {i}. {ANGULOS[i]['nombre']}")
    lines.append("\nBLOQUE B — OBJECIÓN")
    for i in range(6, 11):
        if i in ANGULOS:
            lines.append(f"  {i}. {ANGULOS[i]['nombre']}")
    lines.append("\nBLOQUE C — MÉTODO/AUTORIDAD")
    for i in range(11, 16):
        if i in ANGULOS:
            lines.append(f"  {i}. {ANGULOS[i]['nombre']}")
    return "\n".join(lines)


def formato_regla_37() -> str:
    """Devuelve la regla del 37% formateada."""
    lines = ["REGLA DEL 37% (Termómetro de rentabilidad)\n"]
    for rango, accion in REGLA_37.items():
        lines.append(f"  Margen {rango}: {accion}")
    return "\n".join(lines)
