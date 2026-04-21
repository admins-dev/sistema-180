import asyncio
import websockets
import json
import sys
import os
from datetime import datetime
from agents.agent_framework import orchestrator
from agents.miguel_onboarding import MiguelOnboarding
from agents.content_pipeline import ContentPipeline
from agents.sergio_ads import SergioAds
from agents.cristina_reports import CristinaReports

CONNECTED_CLIENTS = set()

async def broadcast(message):
    if CONNECTED_CLIENTS:
        await asyncio.gather(*[client.send(json.dumps(message)) for client in CONNECTED_CLIENTS])

# Sobreescribimos el método log de Agent para emitir eventos WebSocket
def patch_agent_log():
    original_methods = {}
    for a_id, agent in orchestrator.agents.items():
        original_methods[a_id] = agent.log
        
        def make_new_log(agt):
            orig_log = original_methods[agt.id]
            def new_log(msg):
                orig_log(msg)
                # Emit WebSocket
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

async def handler(websocket):
    CONNECTED_CLIENTS.add(websocket)
    try:
        # Enviar estado inicial de los 57 agentes
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
                
                # Ejecutar de forma asíncrona pero secuencial para mostrar en UI
                async def run_onboarding():
                    await broadcast({"type": "terminal_log", "msg": f"Iniciando onboarding para {client_data['nombre']}", "level": "info"})
                    miguel = MiguelOnboarding()
                    # Bloqueante, pero para demo sirve. En prod usar run_in_executor
                    client = miguel.execute(client_data)
                    client_id = client['id']
                    await broadcast({"type": "client_added", "client": client})
                    await asyncio.sleep(1)
                    
                    # Ejecutar Content Pipeline
                    await broadcast({"type": "terminal_log", "msg": "Iniciando Content Pipeline...", "level": "info"})
                    pipe = ContentPipeline(client_id)
                    pipe.run_pipeline()
                    await asyncio.sleep(1)
                    
                    # Ejecutar Ads y Reports
                    await broadcast({"type": "terminal_log", "msg": "Configurando Follow Me Ads y Reports...", "level": "info"})
                    SergioAds(client_id).execute()
                    CristinaReports(client_id).execute()
                    
                    await broadcast({"type": "terminal_log", "msg": f"Flujo completo configurado para {client_id}. Listo para vender.", "level": "success"})
                
                asyncio.create_task(run_onboarding())
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_CLIENTS.remove(websocket)

async def main():
    patch_agent_log()
    print("="*60)
    print("  ORQUESTADOR SISTEMA 180 — 57 AGENTES ACTIVOS")
    print("  WebSocket server en ws://localhost:8765")
    print("="*60)
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
