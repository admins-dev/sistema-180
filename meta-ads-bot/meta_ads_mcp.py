#!/usr/bin/env python3
"""
Meta Ads MCP Server — Integración Claude AI + Meta Marketing API
Permite a Claude analizar campañas de Meta Ads en tiempo real.
"""

import os
import json
import asyncio
from typing import Optional
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Meta Ads API Configuration
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "")  # act_<numbers>

if not META_ACCESS_TOKEN:
    print("⚠️  META_ACCESS_TOKEN no configurado en .env")
    print("   Paso 1: Ve a developers.facebook.com")
    print("   Paso 2: Crea una Developer App (Part 1 de la guía)")
    print("   Paso 3: Genera un token de acceso (Step 1.5)")
    print("   Paso 4: Añade a .env: META_ACCESS_TOKEN=<token>")
    print("   Paso 5: Copia tu Ad Account ID y guarda: META_AD_ACCOUNT_ID=act_<numbers>")

class MetaAdsMCP:
    """MCP Server para Meta Ads Marketing API"""

    def __init__(self, access_token: str):
        self.token = access_token
        self.base_url = "https://graph.facebook.com/v21.0"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_campaigns(self, date_range: Optional[dict] = None) -> dict:
        """
        Obtiene lista de campañas con métricas.

        Args:
            date_range: {"start_date": "2026-04-01", "end_date": "2026-04-14"}
        """
        if not META_AD_ACCOUNT_ID:
            return {"error": "META_AD_ACCOUNT_ID no configurado"}

        url = f"{self.base_url}/{META_AD_ACCOUNT_ID}/campaigns"
        params = {
            "access_token": self.token,
            "fields": (
                "id,name,status,objective,daily_budget,lifetime_budget,"
                "insights.date_preset(last_7d){spend,impressions,clicks,actions,action_values}"
            ),
            "limit": 100
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                campaigns = []
                for campaign in data.get("data", []):
                    campaign_data = {
                        "id": campaign.get("id"),
                        "name": campaign.get("name"),
                        "status": campaign.get("status"),
                        "objective": campaign.get("objective"),
                        "daily_budget": campaign.get("daily_budget"),
                        "lifetime_budget": campaign.get("lifetime_budget"),
                    }

                    # Procesar insights si existen
                    if "insights" in campaign:
                        insights = campaign["insights"].get("data", [])
                        if insights:
                            latest = insights[0]
                            campaign_data["metrics"] = {
                                "spend": latest.get("spend", 0),
                                "impressions": latest.get("impressions", 0),
                                "clicks": latest.get("clicks", 0),
                                "date": latest.get("date"),
                            }

                            # Calcular CPM
                            spend = float(latest.get("spend", 0))
                            impressions = int(latest.get("impressions", 0))
                            if impressions > 0:
                                campaign_data["metrics"]["cpm"] = (spend / impressions) * 1000

                    campaigns.append(campaign_data)

                return {
                    "success": True,
                    "campaigns": campaigns,
                    "count": len(campaigns),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "error": f"API Error {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {"error": str(e)}

    def get_ad_sets(self, campaign_id: Optional[str] = None) -> dict:
        """
        Obtiene conjuntos de anuncios (ad sets) con métricas.
        """
        if not META_AD_ACCOUNT_ID:
            return {"error": "META_AD_ACCOUNT_ID no configurado"}

        if campaign_id:
            url = f"{self.base_url}/{campaign_id}/adsets"
        else:
            url = f"{self.base_url}/{META_AD_ACCOUNT_ID}/adsets"

        params = {
            "access_token": self.token,
            "fields": (
                "id,name,status,optimization_goal,daily_budget,"
                "insights.date_preset(last_7d){spend,impressions,clicks,actions,action_values}"
            ),
            "limit": 100
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ad_sets = [
                    {
                        "id": ad_set.get("id"),
                        "name": ad_set.get("name"),
                        "status": ad_set.get("status"),
                        "optimization_goal": ad_set.get("optimization_goal"),
                        "daily_budget": ad_set.get("daily_budget"),
                        "metrics": ad_set.get("insights", {}).get("data", [{}])[0]
                        if "insights" in ad_set else {},
                    }
                    for ad_set in data.get("data", [])
                ]
                return {
                    "success": True,
                    "ad_sets": ad_sets,
                    "count": len(ad_sets),
                }
            else:
                return {"error": f"API Error {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_account_insights(self) -> dict:
        """
        Obtiene análisis agregados de toda la cuenta (últimos 7 días).
        """
        if not META_AD_ACCOUNT_ID:
            return {"error": "META_AD_ACCOUNT_ID no configurado"}

        url = f"{self.base_url}/{META_AD_ACCOUNT_ID}/insights"
        params = {
            "access_token": self.token,
            "fields": "spend,impressions,clicks,actions,action_values,cpc,cpm,ctr",
            "date_preset": "last_7d",
            "time_zone": "Europe/Madrid"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    insights = data[0]
                    return {
                        "success": True,
                        "period": "last_7_days",
                        "metrics": {
                            "spend": insights.get("spend"),
                            "impressions": insights.get("impressions"),
                            "clicks": insights.get("clicks"),
                            "cpc": insights.get("cpc"),
                            "cpm": insights.get("cpm"),
                            "ctr": insights.get("ctr"),
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": "No data available"}
            else:
                return {"error": f"API Error {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def analyze_performance(self) -> dict:
        """
        Análisis completo de performance de campañas.
        Combina datos de campañas y métricas agregadas.
        """
        campaigns = self.get_campaigns()
        account_insights = self.get_account_insights()

        if not campaigns.get("success"):
            return {"error": "No se pudieron obtener campañas"}

        analysis = {
            "overview": account_insights.get("metrics", {}),
            "campaigns": campaigns.get("campaigns", []),
            "top_performers": [],
            "underperformers": [],
            "recommendations": []
        }

        # Identificar mejores y peores campañas por ROAS/CPM
        campaign_list = campaigns.get("campaigns", [])
        if campaign_list:
            # Ordenar por CPM (menor es mejor)
            sorted_by_cpm = sorted(
                [c for c in campaign_list if "metrics" in c],
                key=lambda x: float(x["metrics"].get("cpm", float('inf')))
            )

            analysis["top_performers"] = sorted_by_cpm[:3]
            analysis["underperformers"] = sorted_by_cpm[-3:] if len(sorted_by_cpm) > 3 else []

            # Recomendaciones básicas
            if analysis["underperformers"]:
                analysis["recommendations"].append(
                    "Considerar pausar o ajustar campañas con CPM alto"
                )
            if analysis["top_performers"]:
                analysis["recommendations"].append(
                    "Aumentar presupuesto en campañas con CPM bajo"
                )

        return analysis


# ─────────────────────────────────────────────────────────────
# Funciones para MCP Protocol
# ─────────────────────────────────────────────────────────────

async def handle_mcp_call(method: str, params: dict = None) -> dict:
    """
    Maneja llamadas MCP desde Claude.
    Implementa el protocolo MCP para integración con Claude.
    """
    if not META_ACCESS_TOKEN:
        return {"error": "META_ACCESS_TOKEN no configurado"}

    mcp = MetaAdsMCP(META_ACCESS_TOKEN)

    # Mapear métodos MCP a funciones
    if method == "get_campaigns":
        return mcp.get_campaigns()
    elif method == "get_ad_sets":
        campaign_id = params.get("campaign_id") if params else None
        return mcp.get_ad_sets(campaign_id)
    elif method == "get_account_insights":
        return mcp.get_account_insights()
    elif method == "analyze_performance":
        return mcp.analyze_performance()
    else:
        return {"error": f"Unknown method: {method}"}


# ─────────────────────────────────────────────────────────────
# Main — para testing local
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎯 META ADS MCP SERVER — TEST LOCAL")
    print("=" * 70 + "\n")

    if not META_ACCESS_TOKEN:
        print("❌ Token no configurado. Necesitas:")
        print("   1. Ir a developers.facebook.com")
        print("   2. Crear una app (seguir Part 1 de la guía)")
        print("   3. Generar token de acceso (Step 1.5)")
        print("   4. Guardar en .env: META_ACCESS_TOKEN=<token>")
        print("   5. Guardar en .env: META_AD_ACCOUNT_ID=act_<numbers>")
        print("\n")
    else:
        print(f"✅ Token configurado: {META_ACCESS_TOKEN[:30]}...")
        print(f"📊 Ad Account: {META_AD_ACCOUNT_ID}\n")

        print("Testing API calls...\n")

        mcp = MetaAdsMCP(META_ACCESS_TOKEN)

        print("1️⃣  Get Campaigns:")
        campaigns = mcp.get_campaigns()
        print(json.dumps(campaigns, indent=2, ensure_ascii=False)[:500])

        print("\n2️⃣  Account Insights:")
        insights = mcp.get_account_insights()
        print(json.dumps(insights, indent=2, ensure_ascii=False))

        print("\n3️⃣  Performance Analysis:")
        analysis = mcp.analyze_performance()
        print(f"   Total campaigns: {len(analysis.get('campaigns', []))}")
        print(f"   Top performer: {analysis['top_performers'][0]['name'] if analysis['top_performers'] else 'N/A'}")
        print(f"   Recommendations: {len(analysis.get('recommendations', []))}")

    print("\n" + "=" * 70)
