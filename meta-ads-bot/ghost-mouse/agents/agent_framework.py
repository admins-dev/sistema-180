import os
import json
from datetime import datetime
import time

class Agent:
    def __init__(self, id_str, name, layer, role):
        self.id = id_str
        self.name = name
        self.layer = layer
        self.role = role
        self.status = "standby" # standby, working, completed, error
        self.current_task = None
        self.logs = []

    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {self.name}: {msg}"
        self.logs.append(log_entry)
        print(log_entry)

    def process(self, client_id, **kwargs):
        self.status = "working"
        self.log(f"Iniciando tarea para cliente {client_id}")
        try:
            result = self.execute(client_id, **kwargs)
            self.status = "standby"
            self.log(f"Tarea completada")
            return result
        except Exception as e:
            self.status = "error"
            self.log(f"ERROR: {str(e)}")
            return None

    def execute(self, client_id, **kwargs):
        # Override in subclasses
        time.sleep(0.5) # Simulate work
        return True

class Orchestrator:
    def __init__(self):
        self.agents = {}
        self.clients = {}
        self._init_57_agents()
        
    def _add_agent(self, a_id, name, layer, role):
        self.agents[a_id] = Agent(a_id, name, layer, role)

    def _init_57_agents(self):
        # CAPA 1: Contenido & Guiones (14 agentes)
        self._add_agent("A01", "Pablo", 1, "Script Agent v2.0 (Generador masivo B7 y Reels)")
        self._add_agent("A02", "Adriana", 1, "Copy Orchestrator (Valida coherencia de marca y tono)")
        self._add_agent("A03", "Sofía", 1, "Content Head (Genera calendario y teleprompter)")
        self._add_agent("A04", "Alba", 1, "Caption Agent (Pies de foto hiper-optimizados SEO)")
        self._add_agent("A05", "Noa", 1, "Publisher (Conexión API Metricool)")
        self._add_agent("A06", "Leo", 1, "Trend Hunter (Analiza audios virales)")
        self._add_agent("A07", "Clara", 1, "Hook Specialist (Optimiza los primeros 2s)")
        self._add_agent("A08", "David", 1, "StoryBrand Architect (Estructura B7)")
        self._add_agent("A09", "Marta", 1, "Email Copywriter (Secuencia Mongemalo)")
        self._add_agent("A10", "Elena", 1, "Newsletter Editor")
        self._add_agent("A11", "Lucas", 1, "LinkedIn Post Generator")
        self._add_agent("A12", "Julia", 1, "Twitter/X Threads Generator")
        self._add_agent("A13", "Paula", 1, "Blog SEO Writer")
        self._add_agent("A14", "Víctor", 1, "Thumbnail Conceptualizer")

        # CAPA 2: Prospección & Comercial (15 agentes)
        self._add_agent("B01", "InstaScout", 2, "Buscador de perfiles target automático")
        self._add_agent("B02", "InstaMessenger", 2, "Ejecutor de DMs Masivos (Ghost Mouse)")
        self._add_agent("B03", "Natalia", 2, "CRM Pipeline Manager")
        self._add_agent("B04", "LinkedInGhost", 2, "Prospección Sales Navigator indetectable")
        self._add_agent("B05", "MapScraper", 2, "Google Maps Ghost Scraper")
        self._add_agent("B06", "Sergio", 2, "Follow Me Ads Manager")
        self._add_agent("B07", "Laura", 2, "Setter Instagram 1 (Warm leads)")
        self._add_agent("B08", "Diana", 2, "Setter Instagram 2 (Cold leads)")
        self._add_agent("B09", "Marcos", 2, "Follow-up Email Scheduler")
        self._add_agent("B10", "Irene", 2, "WhatsApp Closer Bot")
        self._add_agent("B11", "Tomás", 2, "Lead Scorer (0-10)")
        self._add_agent("B12", "Roberto", 2, "Competitor Audience Builder")
        self._add_agent("B13", "Silvia", 2, "Meta Ads Optimization")
        self._add_agent("B14", "Héctor", 2, "Retargeting Orchestrator")
        self._add_agent("B15", "Alicia", 2, "Objection Handler (LLM Sales)")

        # CAPA 3: Edición & Producción (14 agentes)
        self._add_agent("C01", "Carlos", 3, "Edit Orchestrator (Montaje Premiere/ComfyUI API)")
        self._add_agent("C02", "Mateo", 3, "Cut Master (Cortes limpios sin respiraciones)")
        self._add_agent("C03", "Carmen", 3, "Subtitles (Generación estilo Hormozi)")
        self._add_agent("C04", "Hugo", 3, "Zoom Dynamic (Movimiento cada 3 segundos)")
        self._add_agent("C05", "Bruno", 3, "Color Grading")
        self._add_agent("C06", "Diego", 3, "Sound Design (SFX en transiciones)")
        self._add_agent("C07", "Óscar", 3, "B-Roll Finder")
        self._add_agent("C08", "Gael", 3, "AI Avatar Generator (Talking Head)")
        self._add_agent("C09", "Vega", 3, "Voice Cloner (Es-ES AlvaroNeural)")
        self._add_agent("C10", "Mario", 3, "Music Sync")
        self._add_agent("C11", "Rocío", 3, "Graphic Overlay (Meme inserts)")
        self._add_agent("C12", "Félix", 3, "Render Manager")
        self._add_agent("C13", "Iván", 3, "Format Converter (9:16, 1:1, 16:9)")
        self._add_agent("C14", "Lara", 3, "Quality Control (Revisa sync lips)")

        # CAPA 4: Operaciones & Gestión (14 agentes)
        self._add_agent("D01", "Miguel", 4, "Onboarding Manager")
        self._add_agent("D02", "Fernando", 4, "Billing (Stripe/Bizum Invoice)")
        self._add_agent("D03", "Cristina", 4, "Reporting (KPIs Semanales)")
        self._add_agent("D04", "Andrea", 4, "Customer Support 24/7")
        self._add_agent("D05", "Javier", 4, "Lovable Web Builder")
        self._add_agent("D06", "Carmen", 4, "Notion Workspace Configurator")
        self._add_agent("D07", "Samuel", 4, "Server Monitor (Railway/Vercel)")
        self._add_agent("D08", "Raúl", 4, "DB Backup Manager")
        self._add_agent("D09", "Isabel", 4, "Contract Generator")
        self._add_agent("D10", "Blanca", 4, "Calendar Invites & Reminders")
        self._add_agent("D11", "Nico", 4, "Slack/Telegram Alerts")
        self._add_agent("D12", "Emma", 4, "Data Privacy (LOPD)")
        self._add_agent("D13", "Gabriel", 4, "NotebookLM Intellingence (Market Research)")
        self._add_agent("D14", "Alex", 4, "Swarm Controller (Supervisa fallos en otros agentes)")

    def get_agent(self, agent_id):
        return self.agents.get(agent_id)

    def register_client(self, client_data):
        c_id = client_data.get('id')
        self.clients[c_id] = client_data
        
        # Save client data
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'clients', c_id)
        os.makedirs(base_dir, exist_ok=True)
        with open(os.path.join(base_dir, 'config.json'), 'w', encoding='utf-8') as f:
            json.dump(client_data, f, indent=4, ensure_ascii=False)
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cliente {c_id} registrado. Carpeta creada.")
        return c_id

# Singleton orchestrator
orchestrator = Orchestrator()
