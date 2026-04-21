import os
import json
from datetime import datetime
import uuid
import sys
from agents.agent_framework import orchestrator

class MiguelOnboarding:
    def __init__(self):
        self.agent = orchestrator.get_agent("D01")
        
    def execute(self, raw_data):
        self.agent.status = "working"
        client_id = f"client_{uuid.uuid4().hex[:8]}"
        self.agent.log(f"Iniciando onboarding para nuevo cliente ID: {client_id}")
        
        # Validar y procesar datos brutos (Mock behavior simulating DB save)
        client_config = {
            "id": client_id,
            "nombre": raw_data.get("nombre", "Cliente Desconocido"),
            "nicho": raw_data.get("nicho", "General"),
            "ciudad": raw_data.get("ciudad", "España"),
            "competidores": raw_data.get("competidores", []),
            "publico_objetivo": raw_data.get("publico_objetivo", "Todos"),
            "servicios": raw_data.get("servicios", []),
            "precio_medio": raw_data.get("precio_medio", "100€"),
            "ig_actual": raw_data.get("ig_actual", ""),
            "tono": raw_data.get("tono", "Profesional y directo"),
            "budget_ads": raw_data.get("budget_ads", "5€/dia"),
            "status": "onboarding_completado",
            "created_at": datetime.now().isoformat()
        }
        
        # Guardar cliente
        orchestrator.register_client(client_config)
        self.agent.log(f"Carpeta y configuración cliente {client_id} creadas con éxito.")
        
        # Lanzar estrategia a 6 meses
        self._generate_6_month_strategy(client_id)
        
        # Lanzar disparadores en el orquestador
        self.agent.log(f"Activando Capa 1 y Capa 2 para cliente {client_id}...")
        self.agent.status = "standby"
        
        return client_config

    def _generate_6_month_strategy(self, client_id):
        self.agent.log("Generando estrategia a 6 meses...")
        strategy = {
            "mes_1": "Warm-up perfil, testeo de ángulos principales. Follow Me Ads a 2€/día.",
            "mes_2": "Densidad de contenido, Reels diarios, optimización objeciones. Ads a 5€/día.",
            "mes_3": "Captación directa. Escalado de Ads a competidores 10€/día.",
            "mes_4": "Retargeting activo en Meta. Prospección IG DMs.",
            "mes_5": "Consolidación embudo de ventas WhatsApp.",
            "mes_6": "Scale up o mantenimiento según LTV."
        }
        client_dir = os.path.join(os.path.dirname(__file__), '..', 'clients', client_id)
        with open(os.path.join(client_dir, 'strategy.json'), 'w', encoding='utf-8') as f:
            json.dump(strategy, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    miguel = MiguelOnboarding()
    demo_data = {
        "nombre": "Peluquería María Demo",
        "nicho": "Peluquería",
        "ciudad": "Málaga",
        "competidores": ["@peluqueria_ana", "@hair_malaga"],
        "precio_medio": "45€"
    }
    miguel.execute(demo_data)
