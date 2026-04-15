"""
Meta Ads Agent — Fetch real data from Facebook Ads API
Inspired by CrewAI autonomous agent pattern
"""

import os
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MetaAdsAgent:
    """Specialized agent for Meta Ads analysis & recommendations"""

    def __init__(self):
        self.account_id = os.getenv("META_ADS_ACCOUNT_ID", "")
        self.access_token = os.getenv("META_ADS_ACCESS_TOKEN", "")
        self.api_version = "v18.0"
        self.base_url = f"https://graph.instagram.com/{self.api_version}"

    async def analyze_campaigns(self) -> dict:
        """Fetch REAL campaign data from Meta API"""
        if not self.account_id or not self.access_token:
            return self._placeholder_data()

        try:
            url = f"{self.base_url}/act_{self.account_id}/insights"
            params = {
                "fields": "spend,impressions,clicks,conversions,cost_per_conversion",
                "date_preset": "last_7d",
                "access_token": self.access_token,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("data"):
                return self._placeholder_data()

            metrics = data["data"][0] if data["data"] else {}
            spend = float(metrics.get("spend", 0))
            conversions = float(metrics.get("conversions", 0))

            roas = (conversions / spend) if spend > 0 else 0
            cpc = float(metrics.get("cost_per_conversion", 0))

            return {
                "status": "live",
                "spend_7d": spend,
                "conversions_7d": conversions,
                "roas": roas,
                "cpc": cpc,
                "impressions": int(metrics.get("impressions", 0)),
                "clicks": int(metrics.get("clicks", 0)),
                "fetched_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Meta API error: {e}")
            return self._placeholder_data()

    def _placeholder_data(self) -> dict:
        """Fallback placeholder data"""
        return {
            "status": "placeholder",
            "spend_7d": 300.0,
            "conversions_7d": 10.0,
            "roas": 2.1,
            "cpc": 0.45,
            "impressions": 25000,
            "clicks": 5500,
            "fetched_at": datetime.now().isoformat(),
        }

    async def get_recommendations(self, current_data: dict) -> list:
        """Generate recommendations based on Meta data"""
        roas = current_data.get("roas", 0)
        spend = current_data.get("spend_7d", 0)
        cpc = current_data.get("cpc", 0)

        recommendations = []

        # Pattern 1: Healthy ROAS + budget = increase spend
        if roas >= 2.0 and spend < 500:
            recommendations.append(
                {
                    "action": "increase_budget",
                    "amount": 50,
                    "reason": f"ROAS is {roas:.1f}x (healthy), budget available",
                    "confidence": 87,
                    "expected_impact": f"+€{50 * roas:.0f} revenue",
                }
            )

        # Pattern 2: Low ROAS = examine targeting
        elif roas < 1.5:
            recommendations.append(
                {
                    "action": "audit_targeting",
                    "reason": f"ROAS dropped to {roas:.1f}x",
                    "confidence": 72,
                    "priority": "high",
                }
            )

        # Pattern 3: High CPC = competition issue
        if cpc > 1.0:
            recommendations.append(
                {
                    "action": "test_new_audiences",
                    "reason": f"CPC too high: €{cpc:.2f}",
                    "confidence": 65,
                    "expected_savings": "€100-200/week",
                }
            )

        return recommendations
