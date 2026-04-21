import os
import json
import time
import sys
from datetime import datetime
from agents.agent_framework import orchestrator

class SergioAds:
    def __init__(self, client_id):
        self.client_id = client_id
        self.agent = orchestrator.get_agent("B06")
        self.client_dir = os.path.join(os.path.dirname(__file__), '..', 'clients', client_id)
        
        with open(os.path.join(self.client_dir, 'config.json'), 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def execute(self):
        self.agent.status = "working"
        budget = self.config.get("budget_ads", "5€/dia")
        competitors = self.config.get("competidores", [])
        
        self.agent.log(f"Iniciando configuración Follow Me Ads para {self.client_id}")
        self.agent.log(f"Competidores detectados: {', '.join(competitors)}")
        self.agent.log(f"Presupuesto diario: {budget}")
        
        time.sleep(1) # Simulating API to Meta
        
        campaign_config = {
            "campaign_name": f"FollowMe_{self.config['nicho'].replace(' ', '')}",
            "objective": "MESSAGES",
            "daily_budget": budget,
            "audiences": [
                {
                    "name": "Lookalike_Competitors",
                    "sources": competitors,
                    "type": "intersection"
                },
                {
                    "name": "Retargeting_Profile",
                    "days": 7
                }
            ],
            "creatives": "Pulling from top performing reels",
            "cta": "SISTEMA",
            "status": "active",
            "launched_at": datetime.now().isoformat()
        }
        
        os.makedirs(os.path.join(self.client_dir, "ads"), exist_ok=True)
        with open(os.path.join(self.client_dir, "ads", "current_campaign.json"), 'w', encoding='utf-8') as f:
            json.dump(campaign_config, f, indent=4, ensure_ascii=False)
            
        self.agent.log(f"Campaña lanzada correctamente.")
        self.agent.status = "standby"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sergio = SergioAds(sys.argv[1])
        sergio.execute()
    else:
        print("Falta client_id")
