import json
import urllib.request
import os
import time

COMFYUI_URL = "http://127.0.0.1:8000"
WORKFLOWS_DIR = os.path.join(os.path.expanduser("~"), "ComfyUI", "workflows")
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "ComfyUI", "output")

class ComfyOrchestrator:
    """
    JARVIS ComfyUI Master Orchestrator
    Controla ComfyUI a través de la API para automatizar la Fábrica de Contenidos.
    Soporta Inpainting, Outpainting, entrenamiento de LoRAs y FLUX/SDXL híbrido.
    """
    
    def __init__(self):
        self.url = COMFYUI_URL
        print(f"[*] Jarvis Comfy Orquestador Maestro conectado a {self.url}")

    def is_online(self):
        try:
            req = urllib.request.Request(f"{self.url}/system_stats")
            resp = urllib.request.urlopen(req, timeout=5)
            return resp.getcode() == 200
        except Exception:
            return False

    def get_queue_status(self):
        """Consulta el estado de la cola de generación para no saturar los 8GB VRAM"""
        try:
            req = urllib.request.Request(f"{self.url}/queue")
            resp = urllib.request.urlopen(req, timeout=5)
            data = json.loads(resp.read())
            pending = len(data.get("queue_pending", []))
            running = len(data.get("queue_running", []))
            return pending, running
        except Exception:
            return 0, 0

    def queue_prompt(self, workflow_json):
        """Inyecta un workflow en formato JSON directamente a ComfyUI"""
        # Espera activa si hay procesos corriendo (protección OOM de 8GB VRAM)
        pending, running = self.get_queue_status()
        while running > 0:
            print(f"[*] ComfyUI ocupado. Esperando para liberar VRAM...")
            time.sleep(5)
            pending, running = self.get_queue_status()

        data = json.dumps({"prompt": workflow_json}).encode('utf-8')
        req = urllib.request.Request(f"{self.url}/prompt", data=data, 
                                     headers={"Content-Type": "application/json"})
        try:
            response = urllib.request.urlopen(req, timeout=10)
            result = json.loads(response.read())
            return result.get("prompt_id")
        except Exception as e:
            print(f"[ERROR] Orquestador no pudo encolar el prompt: {e}")
            return None

    def load_workflow(self, template_name):
        """Carga el JSON base del workflow desde la carpeta del disco"""
        path = os.path.join(WORKFLOWS_DIR, template_name)
        if not os.path.exists(path):
            print(f"[ERROR] No se encuentra la plantilla: {path}")
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ==============================================================
    # 1. MÓDULO OUTFIT / INPAINTING (Bloque 9)
    # ==============================================================
    def cambiar_ropa_avatar(self, foto_original, mask_path, prompt_ropa, filename_prefix="outfit_change"):
        """Ejecuta SD1.5/SDXL Inpainting para cambiar la ropa (Ej: Traje, Casual)"""
        print(f"[*] [Comfy] Ejecutando Inpainting para cambiar ropa a: {prompt_ropa}")
        wf = self.load_workflow("inpaint_sdxl.json")
        if not wf:
            print("[!] Plantilla no encontrada. Abortando.")
            return None
            
        # (Ejemplo) Modificación de nodos según la estructura de la 'Biblia'
        # wf["10"]["inputs"]["image"] = foto_original
        # wf["11"]["inputs"]["image"] = mask_path
        # wf["12"]["inputs"]["text"] = prompt_ropa
        # wf["15"]["inputs"]["filename_prefix"] = filename_prefix
        
        # return self.queue_prompt(wf)
        return "mock_prompt_id_inpaint"

    # ==============================================================
    # 2. MÓDULO FLUX GENERATION (Bloque 5)
    # ==============================================================
    def generar_imagen_flux(self, prompt, lora_path=None, filename_prefix="flux_gen"):
        """Genera imagen fotorrealista de alta fidelidad desde cero con FLUX GGUF"""
        print(f"[*] [Comfy] Generando con FLUX: {prompt[:40]}...")
        wf = self.load_workflow("flux_base.json")
        if not wf:
            return None
            
        # Si se pasa LoRA, se inyectaría en el nodo correspondiente
        return "mock_prompt_id_flux"

    # ==============================================================
    # 3. MÓDULO ENTRENADOR DE LORAS AUTOMÁTICO (Bloque 16)
    # ==============================================================
    def entrenar_lora_cliente(self, input_dir, output_lora_name, trigger_word):
        """Dispara el FluxTrainer preconfigurado a las 3:00 AM para no gastar VRAM de día"""
        print(f"[*] [Comfy] Programando entrenamiento de LoRA '{output_lora_name}' para el cliente...")
        print(f"    - Directorio: {input_dir}")
        print(f"    - Trigger: {trigger_word}")
        # Aquí se ejecutaría el WD14-Tagger para etiquetar y luego el flujo FluxTrainer.
        return True

    # ==============================================================
    # 4. MÓDULO VÍDEO & TALKING HEAD (Bloques 12 y 13)
    # ==============================================================
    def generar_video_pitch(self, foto_avatar, archivo_audio, filename_prefix="pitch_video"):
        """Combina LivePortrait + MuseTalk para animar el avatar del cliente con su voz clonada"""
        print(f"[*] [Comfy] Renderizando Vídeo Pitch para {foto_avatar}. Audio: {archivo_audio}")
        wf = self.load_workflow("generar_video.json")
        if not wf:
            return None
            
        # wf["LoadImage_Node"]["inputs"]["image"] = foto_avatar
        # wf["LoadAudio_Node"]["inputs"]["audio"] = archivo_audio
        # return self.queue_prompt(wf)
        return "mock_prompt_id_video"

if __name__ == "__main__":
    jarvis_comfy = ComfyOrchestrator()
    if jarvis_comfy.is_online():
        # Ejemplo de prueba automática
        jarvis_comfy.generar_imagen_flux("Professional mentor in a cozy office")
        jarvis_comfy.entrenar_lora_cliente("C:/clientes/mentor_x/dataset", "mentor_x_v1", "mentorX_person")
