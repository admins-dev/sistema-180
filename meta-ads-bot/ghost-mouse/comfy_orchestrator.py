import json
import urllib.request
import os
import time

COMFYUI_URL = "http://127.0.0.1:8188"
WORKFLOWS_DIR = r"c:\ComfyUI\workflows"
OUTPUT_DIR = r"c:\ComfyUI\ComfyUI_windows_portable\ComfyUI\output"

class ComfyOrchestrator:
    def __init__(self):
        self.url = COMFYUI_URL
        print(f"[*] Jarvis ComfyUI Orchestrator inicializado en {self.url}")

    def is_online(self):
        try:
            req = urllib.request.Request(f"{self.url}/system_stats")
            resp = urllib.request.urlopen(req, timeout=5)
            return resp.getcode() == 200
        except:
            return False

    def queue_prompt(self, workflow_json):
        """Inyecta un JSON workflow directamente en la API de ComfyUI"""
        data = json.dumps({"prompt": workflow_json}).encode('utf-8')
        req = urllib.request.Request(f"{self.url}/prompt", data=data, 
                                     headers={"Content-Type": "application/json"})
        try:
            response = urllib.request.urlopen(req, timeout=10)
            result = json.loads(response.read())
            return result.get("prompt_id")
        except Exception as e:
            print(f"[ERROR] No se pudo encolar el prompt: {e}")
            return None

    def load_workflow(self, workflow_file):
        """Carga un JSON de workflow desde la carpeta de plantillas"""
        path = os.path.join(WORKFLOWS_DIR, workflow_file)
        if not os.path.exists(path):
            print(f"[ERROR] Workflow no encontrado: {path}")
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run_inpainting_flux(self, input_image_path, mask_image_path, prompt, output_filename="inpaint_result.png"):
        """Ejemplo: Llama a un workflow de Inpainting usando la API de ComfyUI"""
        print(f"[*] Solicitando Inpainting con FLUX. Prompt: {prompt[:50]}...")
        # Aquí cargaríamos el JSON del Workflow 32/34 (Inpainting de la Biblia)
        # wf = self.load_workflow("inpaint_flux.json")
        # Y modificaríamos los inputs:
        # wf["LoadImage_Node"]["inputs"]["image"] = input_image_path
        # wf["LoadImage_Mask_Node"]["inputs"]["image"] = mask_image_path
        # wf["CLIPTextEncode_Node"]["inputs"]["text"] = prompt
        # wf["SaveImage_Node"]["inputs"]["filename_prefix"] = output_filename
        
        # prompt_id = self.queue_prompt(wf)
        # print(f"[*] Encolado correctamente. ID: {prompt_id}")
        # return prompt_id
        pass

if __name__ == "__main__":
    jarvis = ComfyOrchestrator()
    if jarvis.is_online():
        print("[+] ComfyUI está ONLINE. Listo para orquestar nodos.")
    else:
        print("[-] ComfyUI offline. Jarvis no puede orquestar en este momento.")
