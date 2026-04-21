import asyncio
import websockets
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

import google.generativeai as genai

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
# El modelo genai.GenerativeModel('gemini-1.5-pro-latest') será el cerebro (emulando Gemini 3.1 Pro backend)

sys.path.append(os.path.dirname(__file__))

from agents.agent_framework import orchestrator
from agents.miguel_onboarding import MiguelOnboarding
from agents.content_pipeline import ContentPipeline
from agents.sergio_ads import SergioAds
from agents.cristina_reports import CristinaReports

CONNECTED_CLIENTS = set()

# Memoria de Enjambre (Swarm Memory)
SWARM_MEMORY = [
    {"role": "user", "parts": ["Bienvenido. Tú eres JARVIS, el Master Orchestrator de Sistema 180. Tienes a tu cargo a 57 agentes IA. Tu objetivo es coordinarlos, entender al CEO, y dar órdenes precisas."]},
    {"role": "model", "parts": ["Conectado. A la espera de órdenes, señor."]}
]

async def broadcast(message):
    if CONNECTED_CLIENTS:
        await asyncio.gather(*[client.send(json.dumps(message)) for client in CONNECTED_CLIENTS])

def patch_agent_log():
    original_methods = {}
    for a_id, agent in orchestrator.agents.items():
        original_methods[a_id] = agent.log
        
        def make_new_log(agt):
            orig_log = original_methods[agt.id]
            def new_log(msg):
                orig_log(msg)
                asyncio.create_task(broadcast({
                    "type": "agent_log",
                    "agent_id": agt.id,
                    "agent_name": agt.name,
                    "layer": agt.layer,
                    "status": agt.status,
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }))
            return new_log
            
        agent.log = make_new_log(agent)


async def ask_gemini(system_prompt, user_query, memory=None):
    if not GEMINI_API_KEY:
        await asyncio.sleep(1)
        return "ERROR: GEMINI_API_KEY no detectada en .env. Por favor, añádela."
        
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest') # Equivale contextualmente a Gemini 3.1 Pro Enterprise
        chat = model.start_chat(history=memory or [])
        response = chat.send_message(f"SYSTEM INSTRUCTION: {system_prompt}\n\nUSER MESSAGE: {user_query}")
        # Guardar en memoria proporcionada
        if memory is not None:
            memory.append({"role": "user", "parts": [user_query]})
            memory.append({"role": "model", "parts": [response.text]})
        return response.text
    except Exception as e:
        return f"Error de Conexión Neuronal (Gemini): {str(e)}"


async def handle_despacho(data, websocket):
    agent_id = data.get("agent_id")
    msg = data.get("msg")
    agent = orchestrator.get_agent(agent_id)
    
    if not agent:
        await websocket.send(json.dumps({"type": "chat_reply", "msg": "Agente no encontrado.", "source": "System"}))
        return

    agent.status = "working"
    await broadcast({"type": "agent_log", "agent_id": agent.id, "status": "working", "message": "Procesando petición en Despacho", "agent_name": agent.name, "layer": agent.layer})
    
    sys_prompt = f"Eres {agent.name}, {agent.role}. Responde de forma inmersiva y técnica sobre tu área. Cumple la orden del CEO del Sistema 180."
    reply = await ask_gemini(sys_prompt, msg)
    
    agent.status = "standby"
    await broadcast({"type": "agent_log", "agent_id": agent.id, "status": "standby", "message": "Respuesta enviada", "agent_name": agent.name, "layer": agent.layer})
    
    await websocket.send(json.dumps({
        "type": "chat_reply",
        "msg": reply,
        "source": agent.name,
        "mode": "despacho"
    }))


async def handle_reunion(data, websocket):
    msg = data.get("msg")
    
    # Broadcast user msg visually
    await broadcast({
        "type": "chat_reply",
        "msg": msg,
        "source": "CEO",
        "mode": "reunion"
    })

    # JARVIS Piensa
    await broadcast({"type": "terminal_log", "msg": "JARVIS procesando instrucción de la Sala...", "level": "system"})
    sys_prompt = "Actúa como JARVIS, coordinador de 57 agentes. Responde primero al CEO confirmando la orden, y luego en párrafos cortos asigna a 2-3 agentes (mencionándolos con @Nombre) las tareas relativas."
    
    jarvis_reply = await ask_gemini(sys_prompt, msg, SWARM_MEMORY)
    
    await broadcast({
        "type": "chat_reply",
        "msg": jarvis_reply,
        "source": "JARVIS",
        "mode": "reunion"
    })
    
    # Simular que los agentes mencionados responden tras un tiempo
    for agent_id, agent in orchestrator.agents.items():
        if f"@{agent.name}" in jarvis_reply:
            async def agent_ack(a):
                await asyncio.sleep(2)
                a.status = "working"
                await broadcast({"type": "agent_log", "agent_id": a.id, "status": "working", "message": "Ejecutando orden de JARVIS", "agent_name": a.name, "layer": a.layer})
                await asyncio.sleep(1)
                
                ack_reply = await ask_gemini(f"Eres {a.name}, y acabas de recibir una orden en la sala de reuniones. Da un breve reporte confirmando tu ejecución.", "Orden recibida", [])
                
                a.status = "standby"
                await broadcast({"type": "agent_log", "agent_id": a.id, "status": "standby", "message": "Orden completada", "agent_name": a.name, "layer": a.layer})
                await broadcast({
                    "type": "chat_reply",
                    "msg": ack_reply,
                    "source": a.name,
                    "mode": "reunion"
                })
            asyncio.create_task(agent_ack(agent))


async def handler(websocket):
    CONNECTED_CLIENTS.add(websocket)
    try:
        agents_state = {aid: {"name": a.name, "layer": a.layer, "status": a.status, "role": a.role} 
                        for aid, a in orchestrator.agents.items()}
        await websocket.send(json.dumps({
            "type": "init_agents",
            "agents": agents_state
        }))
        
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "add_client":
                client_data = data.get("client_data")
                async def run_onboarding():
                    await broadcast({"type": "terminal_log", "msg": f"Iniciando onboarding para {client_data['nombre']}", "level": "info"})
                    miguel = MiguelOnboarding()
                    client = miguel.execute(client_data)
                    client_id = client['id']
                    await broadcast({"type": "client_added", "client": client})
                    await asyncio.sleep(1)
                    
                    await broadcast({"type": "terminal_log", "msg": "Iniciando Content Pipeline...", "level": "info"})
                    pipe = ContentPipeline(client_id)
                    pipe.run_pipeline()
                    await asyncio.sleep(1)
                    
                    await broadcast({"type": "terminal_log", "msg": "Configurando Follow Me Ads y Reports...", "level": "info"})
                    SergioAds(client_id).execute()
                    CristinaReports(client_id).execute()
                    
                    await broadcast({"type": "terminal_log", "msg": f"Flujo completo configurado para {client_id}. Listo para vender.", "level": "success"})
                
                asyncio.create_task(run_onboarding())
            
            elif action == "chat_despacho":
                asyncio.create_task(handle_despacho(data, websocket))
                
            elif action == "chat_reunion":
                asyncio.create_task(handle_reunion(data, websocket))
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_CLIENTS.remove(websocket)


async def main():
    patch_agent_log()
    PORT = int(os.environ.get("PORT", 8765))
    print("="*60)
    print("  ORQUESTADOR SISTEMA 180 — GEMINI 3.1 LLM INTEGRATED")
    print(f"  WebSocket server corriendo en 0.0.0.0:{PORT}")
    print("="*60)
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
