import os
import json
import time
from datetime import datetime
from agents.agent_framework import orchestrator

class ContentPipeline:
    def __init__(self, client_id):
        self.client_id = client_id
        self.client_dir = os.path.join(os.path.dirname(__file__), '..', 'clients', client_id)
        
        with open(os.path.join(self.client_dir, 'config.json'), 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def run_pipeline(self):
        # 1. PABLO (A01)
        pablo = orchestrator.get_agent("A01")
        pablo.status = "working"
        pablo.log(f"Generando 28 guiones semanales para {self.config['nombre']}")
        time.sleep(1) # Simulación
        raw_scripts = [f"Borrador de guion {i} (Ángulo X) para {self.config['nicho']}" for i in range(1, 29)]
        pablo.status = "standby"

        # 2. ADRIANA (A02)
        adriana = orchestrator.get_agent("A02")
        adriana.status = "working"
        adriana.log(f"Validando coherencia de marca y tono '{self.config['tono']}'...")
        time.sleep(1)
        validated_scripts = []
        for s in raw_scripts:
            validated_scripts.append(s + f" [Validado: Tono {self.config['tono']}]")
        
        # Save Scripts
        os.makedirs(os.path.join(self.client_dir, "guiones"), exist_ok=True)
        with open(os.path.join(self.client_dir, "guiones", "semana_1.json"), 'w', encoding='utf-8') as f:
            json.dump(validated_scripts, f, indent=4, ensure_ascii=False)
        adriana.status = "standby"

        # 3. SOFÍA (A03)
        sofia = orchestrator.get_agent("A03")
        sofia.status = "working"
        sofia.log("Estructurando calendario y generando teleprompter...")
        time.sleep(1)
        calendar = {
            "Lunes": validated_scripts[0:4],
            "Martes": validated_scripts[4:8],
            "Miercoles": validated_scripts[8:12],
            "Jueves": validated_scripts[12:16],
            "Viernes": validated_scripts[16:20],
            "Sabado": validated_scripts[20:24],
            "Domingo": validated_scripts[24:28]
        }
        os.makedirs(os.path.join(self.client_dir, "calendars"), exist_ok=True)
        with open(os.path.join(self.client_dir, "calendars", "cal_semana_1.json"), 'w', encoding='utf-8') as f:
            json.dump(calendar, f, indent=4, ensure_ascii=False)
        sofia.status = "standby"

        # 4. ALBA (A04)
        alba = orchestrator.get_agent("A04")
        alba.status = "working"
        alba.log("Generando captions, hashtags agresivos y CTA con palabra clave...")
        time.sleep(1)
        captions = {f"post_{i}": f"Caption super agresivo para vender {self.config['precio_medio']}. Escribe SISTEMA. #marketing #{self.config['nicho'].replace(' ','')}" for i in range(1, 29)}
        os.makedirs(os.path.join(self.client_dir, "captions"), exist_ok=True)
        with open(os.path.join(self.client_dir, "captions", "cap_semana_1.json"), 'w', encoding='utf-8') as f:
            json.dump(captions, f, indent=4, ensure_ascii=False)
        alba.status = "standby"

        print(f"[{datetime.now().strftime('%H:%M:%S')}] PIPELINE DE CONTENIDO COMPLETADO PARA {self.client_id}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pipe = ContentPipeline(sys.argv[1])
        pipe.run_pipeline()
    else:
        print("Falta client_id")
