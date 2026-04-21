"""
Ghost Mouse — Plantillas de mensajes para DMs.
Variables: {nombre}, {negocio}, {ciudad}
"""

TEMPLATES = [
    "Hola! He visto {negocio} y me parece genial lo que haceis. Trabajo en marketing digital y he ayudado a negocios como el tuyo a duplicar sus clientes en 30 dias. Te gustaria saber como? 🚀",
    
    "Buenas! Soy especialista en marketing digital para negocios locales en {ciudad}. He analizado vuestro perfil y creo que puedo ayudaros a conseguir muchos mas clientes. Os interesa una consulta gratuita?",
    
    "Hola! Vi {negocio} y me encanto. Trabajo ayudando a negocios locales a crecer online. Tengo algunas ideas que podrian funcionar muy bien para vosotros. Puedo explicaros en 2 minutos?",
    
    "Buenas tardes! He estado viendo negocios interesantes en {ciudad} y {negocio} destaca mucho. Trabajo en marketing digital y tengo una estrategia que esta funcionando muy bien para negocios como el vuestro. Os cuento?",
    
    "Hola! Enhorabuena por {negocio}, se ve que haceis un trabajo increible. Soy consultor de marketing digital y tengo una propuesta que podria ayudaros a llegar a muchos mas clientes. Os interesa?",
]

def get_message(lead, template_index=None):
    """Generar mensaje personalizado para un lead."""
    import random
    
    if template_index is None:
        template_index = random.randint(0, len(TEMPLATES) - 1)
    
    template = TEMPLATES[template_index % len(TEMPLATES)]
    
    msg = template.format(
        nombre=lead.get("name", ""),
        negocio=lead.get("name", "vuestro negocio"),
        ciudad=lead.get("location", "vuestra ciudad"),
    )
    
    return msg
