"""
PABLO — Script Agent v2.0 (Sistema 180)
Genera 128+ guiones/mes usando:
  - Framework A: Sistema B7 (carruseles, post fijado, email)
  - Framework B: Reel Corto 4 Bloques (reels 30-60s)
  - 15 Ángulos de comunicación
  - 4 Tipos de contenido (40/30/20/10)

Uso:
  python pablo_script_agent.py semana              # 28 guiones semanales
  python pablo_script_agent.py semana infoproductor # Para infoproductores
  python pablo_script_agent.py lote 5 3            # 5 guiones del ángulo 3
  python pablo_script_agent.py all                 # 128 guiones (mes completo)
"""
import os
import sys
import json
import random
from datetime import datetime
from sistema180_maestro import ANGULOS, FASES, FASE_ACTUAL, TIPOS_CONTENIDO, B7_PREGUNTAS, REEL_CORTO

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "guiones")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===================================================================
# CONFIGURACIÓN DE MARCA — JOSE MARÍA MORENO / SISTEMA 180
# ===================================================================

MARCA = {
    "nombre": "José María Moreno",
    "empresa": "Sistema 180",
    "servicio_pyme": "Web + SEO + WhatsApp para negocios locales",
    "servicio_infoproductor": "Sistema de captación automatizado con 57 agentes IA",
    "precio_pyme": "497€ una vez, 5 días, sin mensualidades",
    "precio_infoproductor": "desde 997€/mes + setup",
    "diferencial": "57 agentes IA, sin funnels, sin VSL, sin landing complicada",
    "cta_whatsapp": "+34 615 606 285",
    "palabra_clave_dm": "SISTEMA",
    "anti_posicionamiento": "Sin VSL, sin landing, sin funnel de 7 pasos",
    "tono": "Directo, sin relleno, como habla un amigo que sabe del tema. Sin emojis decorativos. Sin 'tips genéricos'. Dolor específico con cifras.",
}

# ===================================================================
# FRAMEWORK A — SISTEMA B7 (piezas largas)
# ===================================================================

def generar_b7(angulo_num, tipo_contenido, target="pyme"):
    """Genera un guión completo usando Sistema B7."""
    angulo = ANGULOS[angulo_num]
    hook = random.choice(angulo["hooks"])
    
    if target == "pyme":
        heroe = "un dueño de negocio local que trabaja 12 horas al día"
        problema = "tiene buen servicio pero no le llegan clientes nuevos desde internet"
        guia = "José María Moreno, fundador de Sistema 180"
        plan = "1. Web con botón WhatsApp. 2. Google Maps optimizado. 3. SEO local."
        cta = "Escribe SISTEMA al DM o WhatsApp al {}".format(MARCA["cta_whatsapp"])
        fracaso = "Seguir perdiendo clientes cada día porque la competencia aparece primero en Google"
        exito = "12 clientes nuevos al mes que vienen solos desde la web, sin depender del boca a boca"
        precio = MARCA["precio_pyme"]
    else:
        heroe = "un infoproductor que publica contenido bueno pero no escala"
        problema = "tiene seguidores pero no convierte, depende del algoritmo"
        guia = "José María Moreno y sus 57 agentes IA"
        plan = "1. Contenido con los 15 ángulos. 2. Bot que cualifica. 3. Sistema automatizado."
        cta = "Escribe SISTEMA al DM"
        fracaso = "Seguir publicando 5 veces por semana con la misma facturación que hace 6 meses"
        exito = "Un sistema que genera DMs de compra cada día sin depender del algoritmo"
        precio = MARCA["precio_infoproductor"]
    
    guion = {
        "id": "B7_{}_A{}_{}".format(target, angulo_num, datetime.now().strftime("%Y%m%d%H%M%S")),
        "framework": "B7",
        "angulo": angulo_num,
        "angulo_nombre": angulo["nombre"],
        "tipo_contenido": tipo_contenido,
        "formato": "carrusel_pixar / post_fijado / email",
        "duracion": "Lectura 2-3 min",
        "target": target,
        
        "guion": {
            "B1_personaje": heroe,
            "B2_problema": problema,
            "B3_guia": guia,
            "B4_plan": plan,
            "B5_cta": cta,
            "B6_fracaso": fracaso,
            "B7_exito": exito,
        },
        
        "texto_completo": """{}

{}

Esto le pasaba a {}. {}.

Hasta que encontró a {}.

El plan es simple:
{}

{}.

Si no actúas: {}.

Si actúas: {}.

{}

{}""".format(
            hook, 
            "-" * 40,
            heroe, problema,
            guia,
            plan,
            precio,
            fracaso,
            exito,
            cta,
            MARCA["nombre"]
        ),
        
        "cta_final": cta,
        "palabra_clave": MARCA["palabra_clave_dm"],
        "hashtags": ["#Sistema180", "#MarketingConIA", "#NegociosLocales", "#CaptaciónDeClientes"],
    }
    
    return guion


# ===================================================================
# FRAMEWORK B — REEL CORTO 4 BLOQUES (30-60s)
# ===================================================================

def generar_reel_corto(angulo_num, tipo_contenido, target="pyme"):
    """Genera un guión de reel corto con estructura 4 bloques."""
    angulo = ANGULOS[angulo_num]
    hook = random.choice(angulo["hooks"])
    
    if target == "pyme":
        identificacion = "Tienes un negocio que funciona. Haces bien tu trabajo. Tus clientes están contentos. Pero cada mes cierras igual. Los nuevos no llegan. Y no sabes por qué."
        reframe = "El problema no es tu servicio. El problema es que cuando alguien busca lo que haces en Google, no apareces. Aparece tu competencia. Y se lleva a TUS clientes sin hacer nada especial. Solo por estar ahí. Yo monto webs que aparecen en Google con botón de WhatsApp directo. {} Los que lo hicieron consiguieron 12 clientes nuevos al mes.".format(MARCA["precio_pyme"])
        cta = "Si facturas más de 3.000€/mes con tu negocio y quieres aparencer en Google, escribe SISTEMA. Si no, no me escribas."
    else:
        identificacion = "Publicas 5 veces por semana. Tienes miles de seguidores. Tu contenido es bueno. Pero la caja registradora sigue igual que hace 6 meses. Y cada lunes piensas: ¿qué estoy haciendo mal?"
        reframe = "No estás haciendo nada mal con tu contenido. Lo que te falta es un SISTEMA. Un sistema que convierta esas vistas en conversaciones de venta. Tengo 57 agentes IA que hacen exactamente eso: contenido, prospección, cualificación y cierre. Todo automático."
        cta = "Si facturas más de 5k/mes y quieres escalar sin quemarte, escribe SISTEMA al DM. Si no llegas a 5k, no me escribas todavía."
    
    guion = {
        "id": "REEL_{}_A{}_{}".format(target, angulo_num, datetime.now().strftime("%Y%m%d%H%M%S")),
        "framework": "Reel_4Bloques",
        "angulo": angulo_num,
        "angulo_nombre": angulo["nombre"],
        "tipo_contenido": tipo_contenido,
        "formato": "reel_vertical_9:16",
        "duracion": "30-50 segundos",
        "target": target,
        
        "guion": {
            "bloque1_hook": "[0-2s] {}".format(hook),
            "bloque2_identificacion": "[2-10s] {}".format(identificacion),
            "bloque3_reframe": "[10-40s] {}".format(reframe),
            "bloque4_cta": "[40-50s] {}".format(cta),
        },
        
        "texto_teleprompter": """{}\n\n{}\n\n{}\n\n{}""".format(hook, identificacion, reframe, cta),
        
        "cta_final": cta,
        "palabra_clave": MARCA["palabra_clave_dm"],
        "hashtags": ["#Sistema180", "#MarketingDigital", "#IA", "#Emprendimiento"],
    }
    
    return guion


# ===================================================================
# GENERADOR SEMANAL (28 GUIONES)
# ===================================================================

def generar_semana(target="pyme"):
    """Genera 28 guiones para una semana (4/día × 7 días).
    
    Distribución:
      40% dolor (11-12 piezas) → ángulos 1, 9, 11, 12
      30% objeción (8-9 piezas) → ángulos 2, 3, 7
      20% producto (5-6 piezas) → ángulos 4, 5, 8, 10, 13
      10% autoridad (2-3 piezas) → ángulos 6, 11, 15
      
    Mix formatos:
      70% reels cortos (Framework B)
      20% carruseles (Framework A / B7)
      10% posts / identidad
    """
    angulos_activos = FASES[FASE_ACTUAL]["angulos_activos"]
    guiones = []
    
    # Distribución por tipo
    plan = []
    
    # 40% dolor = 11 piezas
    dolor_angulos = [a for a in [1, 9, 11, 12] if a in angulos_activos]
    if not dolor_angulos:
        dolor_angulos = [angulos_activos[0]]
    for i in range(11):
        plan.append(("dolor", random.choice(dolor_angulos)))
    
    # 30% objeción = 9 piezas
    objecion_angulos = [a for a in [2, 3, 7] if a in angulos_activos]
    if not objecion_angulos:
        objecion_angulos = [angulos_activos[1] if len(angulos_activos) > 1 else angulos_activos[0]]
    for i in range(9):
        plan.append(("objecion", random.choice(objecion_angulos)))
    
    # 20% producto = 6 piezas
    producto_angulos = [a for a in [4, 5, 8, 10, 13] if a in angulos_activos]
    if not producto_angulos:
        producto_angulos = [angulos_activos[2] if len(angulos_activos) > 2 else angulos_activos[0]]
    for i in range(6):
        plan.append(("producto", random.choice(producto_angulos)))
    
    # 10% autoridad = 2 piezas
    autoridad_angulos = [a for a in [6, 11, 15] if a in angulos_activos]
    if not autoridad_angulos:
        autoridad_angulos = [angulos_activos[-1]]
    for i in range(2):
        plan.append(("autoridad", random.choice(autoridad_angulos)))
    
    random.shuffle(plan)
    
    # Generar guiones (70% reel, 20% B7, 10% B7 corto)
    for i, (tipo, angulo_num) in enumerate(plan):
        r = random.random()
        if r < 0.70:
            guion = generar_reel_corto(angulo_num, tipo, target)
        else:
            guion = generar_b7(angulo_num, tipo, target)
        
        guion["dia_semana"] = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"][i // 4]
        guion["slot"] = (i % 4) + 1
        guiones.append(guion)
    
    return guiones


def generar_mes(target="pyme"):
    """Genera 4 semanas = ~112 guiones."""
    all_guiones = []
    for semana in range(1, 5):
        guiones = generar_semana(target)
        for g in guiones:
            g["semana"] = semana
        all_guiones.extend(guiones)
    return all_guiones


# ===================================================================
# OUTPUT
# ===================================================================

def guardar_guiones(guiones, filename=None):
    """Save scripts to JSON and print summary."""
    if not filename:
        filename = "guiones_{}.json".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(guiones, f, ensure_ascii=False, indent=2)
    
    print("\n  Guardado en: {}".format(filepath))
    return filepath


def print_guiones(guiones, verbose=False):
    """Print script summary."""
    print("\n" + "=" * 70)
    print("  PABLO — {} GUIONES GENERADOS".format(len(guiones)))
    print("=" * 70)
    
    # Stats
    frameworks = {}
    angulos_used = {}
    tipos_used = {}
    
    for g in guiones:
        fw = g.get("framework", "?")
        frameworks[fw] = frameworks.get(fw, 0) + 1
        an = g.get("angulo_nombre", "?")
        angulos_used[an] = angulos_used.get(an, 0) + 1
        tp = g.get("tipo_contenido", "?")
        tipos_used[tp] = tipos_used.get(tp, 0) + 1
    
    print("\n  FRAMEWORKS:")
    for k, v in frameworks.items():
        print("    {} → {} guiones ({:.0f}%)".format(k, v, v/len(guiones)*100))
    
    print("\n  TIPOS DE CONTENIDO:")
    for k, v in sorted(tipos_used.items(), key=lambda x: -x[1]):
        print("    {} → {} ({:.0f}%)".format(k, v, v/len(guiones)*100))
    
    print("\n  ÁNGULOS USADOS:")
    for k, v in sorted(angulos_used.items(), key=lambda x: -x[1]):
        print("    {} → {}".format(k, v))
    
    if verbose:
        print("\n" + "-" * 70)
        for i, g in enumerate(guiones, 1):
            sem = g.get("semana", "")
            dia = g.get("dia_semana", "")
            slot = g.get("slot", "")
            print("\n  [{}/S{} Slot{}] {} | Ángulo: {} | Tipo: {}".format(
                dia, sem, slot, g["framework"], g["angulo_nombre"], g["tipo_contenido"]
            ))
            if g["framework"] == "Reel_4Bloques":
                print("    HOOK: {}".format(g["guion"]["bloque1_hook"][:80]))
                print("    CTA: {}".format(g["guion"]["bloque4_cta"][:80]))
            else:
                print("    B1: {}".format(g["guion"]["B1_personaje"][:60]))
                print("    CTA: {}".format(g["guion"]["B5_cta"][:80]))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "semana"
    target = sys.argv[2] if len(sys.argv) > 2 else "pyme"
    
    print("=" * 60)
    print("  PABLO — Script Agent v2.0")
    print("  Sistema 180 | Target: {} | Modo: {}".format(target, mode))
    print("=" * 60)
    
    if mode == "semana":
        guiones = generar_semana(target)
        print_guiones(guiones, verbose=True)
        guardar_guiones(guiones, "semana_{}.json".format(target))
    
    elif mode == "all" or mode == "mes":
        guiones = generar_mes(target)
        print_guiones(guiones)
        guardar_guiones(guiones, "mes_{}.json".format(target))
    
    elif mode == "lote":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        angulo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        guiones = [generar_reel_corto(angulo, "dolor") for _ in range(n)]
        print_guiones(guiones, verbose=True)
        guardar_guiones(guiones, "lote_a{}.json".format(angulo))
