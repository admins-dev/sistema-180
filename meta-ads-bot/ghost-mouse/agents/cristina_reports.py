import os
import json
import time
import sys
from datetime import datetime
from agents.agent_framework import orchestrator

class CristinaReports:
    def __init__(self, client_id):
        self.client_id = client_id
        self.agent = orchestrator.get_agent("D03")
        self.client_dir = os.path.join(os.path.dirname(__file__), '..', 'clients', client_id)
        
    def execute(self):
        self.agent.status = "working"
        self.agent.log(f"Generando reporte semanal para {self.client_id}...")
        time.sleep(1)
        
        # Simulating data gathering from various agents/platforms
        report = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "kpis": {
                "alcance_total": "12,450",
                "engagement_rate": "4.2%",
                "dms_recibidos": 45,
                "leads_cualificados": 12,
                "ventas_cerradas": 2,
                "roas_ads": "3.5x"
            },
            "acciones_realizadas": [
                "28 guiones generados y programados",
                "Follow Me Ads activo en competidores top",
                "DMs automatizados respondiendo a 'SISTEMA'"
            ],
            "recomendaciones": "Aumentar budget de ads a 10€/día en el Reel #4 que tiene mejor conversión a DM."
        }
        
        os.makedirs(os.path.join(self.client_dir, "reports"), exist_ok=True)
        report_num = len(os.listdir(os.path.join(self.client_dir, "reports"))) + 1
        with open(os.path.join(self.client_dir, "reports", f"report_w{report_num}.json"), 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
            
        self.agent.log(f"Reporte W{report_num} generado y enviado al dashboard.")
        self.agent.status = "standby"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cristina = CristinaReports(sys.argv[1])
        cristina.execute()
    else:
        print("Falta client_id")
