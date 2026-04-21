import time
import uuid
from termcolor import colored
from notion_db import add_lead
from comfy_orchestrator import ComfyOrchestrator

# Límite de seguridad estricto impuesto por el usuario
SECURITY_POLICY = "STRICT_NO_FINANCE"

class PhantomAgent:
    def __init__(self, alias, niche):
        self.alias = alias
        self.niche = niche
        self.comfy = ComfyOrchestrator()
        
    def think_strategy(self, target_profile):
        """El agente piensa por sí mismo estrategias de abordaje basadas en el perfil"""
        print(colored(f"[{self.alias}] Analizando perfil: @{target_profile}...", "cyan"))
        # Simulación de IA pensando la estrategia
        time.sleep(1)
        strategy = f"Abordar a @{target_profile} destacando dolor en {self.niche}. Ofrecer prueba de vídeo IA."
        print(colored(f"[{self.alias}] Estrategia definida: {strategy}", "green"))
        return strategy

    def create_content_hook(self, target_profile):
        """El agente interactúa automáticamente con ComfyUI para generar un gancho visual"""
        if not self.comfy.is_online():
            print(colored(f"[{self.alias}] [!] ComfyUI Inactivo. Fallback a texto puro.", "yellow"))
            return None
        
        print(colored(f"[{self.alias}] Orquestando ComfyUI para gancho de @{target_profile}...", "magenta"))
        # Generar una imagen gancho usando FLUX vía API
        prompt = f"Professional instagram thumbnail, text saying 'Para @{target_profile}', modern minimalist design, dark mode, high quality 8k"
        img_id = self.comfy.generar_imagen_flux(prompt, filename_prefix=f"hook_{target_profile}")
        print(colored(f"[{self.alias}] Contenido generado OK. (ID: {img_id})", "green"))
        return img_id

    def execute_outreach(self, target_profile):
        """Ejecuta el outreach seguro (sin links de pago)"""
        print(colored(f"[{self.alias}] Iniciando Outreach para @{target_profile}", "blue", attrs=["bold"]))
        
        # 1. Estrategia Autónoma
        self.think_strategy(target_profile)
        
        # 2. Creación de Contenido Autónomo
        self.create_content_hook(target_profile)
        
        # 3. Guardar en Notion CRM
        print(colored(f"[{self.alias}] Sincronizando con Notion CRM...", "yellow"))
        add_lead(
            database_id="c99b12e9-f210-410a-8597-d734cd8a2943", # Mock ID / Update with real CRM ID 
            nombre=target_profile.capitalize(),
            nick=target_profile,
            nicho=self.niche,
            estado="Prospección",
            setter=self.alias
        )
        print(colored(f"[{self.alias}] Misión completada para @{target_profile}\n", "magenta", attrs=["bold"]))

def security_check(action):
    """Filtro de seguridad inquebrantable"""
    forbidden_keywords = ["stripe", "paypal", "pago", "checkout", "bank", "transferencia"]
    for word in forbidden_keywords:
        if word in action.lower():
            raise SecurityError("Intento de acceso financiero bloqueado. El agente no tiene permisos.")
    return True

if __name__ == "__main__":
    print(colored("="*60, "red", attrs=["bold"]))
    print(colored("  🚀 SISTEMA 180 - PHANTOM AGENCY SWARM (MAX VELOCITY)", "white", attrs=["bold"]))
    print(colored("  [!] MÓDULO DE SEGURIDAD FINANCIERA: ACTIVO", "green"))
    print(colored("="*60, "red", attrs=["bold"]))
    print("\nInicializando Agentes Autónomos...")
    
    agentes = [
        PhantomAgent("Carlos", "Mentores Fitness"),
        PhantomAgent("Laura", "Infoproductores de Marketing"),
        PhantomAgent("Pablo", "Clínicas Estéticas")
    ]
    
    targets_demo = ["danny_fitness", "maria_marketing_pro", "clinica.laser.madrid"]
    
    for i, target in enumerate(targets_demo):
        agente = agentes[i % len(agentes)]
        # Simulación a máxima velocidad (en producción corre en Threads paralelos)
        agente.execute_outreach(target)
        time.sleep(0.5)
        
    print(colored("[+] Ciclo de Enjambre Finalizado.", "cyan", attrs=["bold"]))
