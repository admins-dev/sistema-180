import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class MetaAdsClient:
    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, access_token: str = None, ad_account_id: str = None):
        self.access_token = access_token or os.getenv("META_ACCESS_TOKEN")
        self.ad_account_id = ad_account_id or os.getenv("META_AD_ACCOUNT_ID")

        if not self.access_token or not self.ad_account_id:
            logger.warning("[MetaAds] META_ACCESS_TOKEN o META_AD_ACCOUNT_ID no configurados — client deshabilitado")
            self._disabled = True
            return

        self._disabled = False

        # Normalizar: asegurarse de que ad_account_id tenga prefijo act_
        if not self.ad_account_id.startswith("act_"):
            self.ad_account_id = f"act_{self.ad_account_id}"

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        logger.info(f"[MetaAds] Client initialized for {self.ad_account_id}")

    @property
    def is_ready(self) -> bool:
        return not getattr(self, '_disabled', True)

    def _get(self, path: str, params: dict = None) -> dict:
        if self._disabled:
            logger.warning("[MetaAds] Client disabled — skipping GET")
            return {}
        try:
            r = self.session.get(f"{self.BASE_URL}/{path}", params=params or {})
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            logger.error(f"[MetaAds] HTTP error: {e.response.status_code} — {e.response.text}")
            return {}
        except Exception as e:
            logger.error(f"[MetaAds] Error: {e}")
            return {}

    def _post(self, path: str, data: dict = None) -> dict:
        if self._disabled:
            logger.warning("[MetaAds] Client disabled — skipping POST")
            return {}
        try:
            r = self.session.post(f"{self.BASE_URL}/{path}", data=data or {})
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            logger.error(f"[MetaAds] HTTP error: {e.response.status_code} — {e.response.text}")
            return {}
        except Exception as e:
            logger.error(f"[MetaAds] Error: {e}")
            return {}

    def create_campaign(self, name: str, budget: int) -> dict:
        """
        Creates a campaign with PAUSED status.
        budget: daily budget in cents (e.g. 1000 = 10.00 EUR)
        Returns: {campaign_id, status}
        """
        data = {
            "name": name,
            "objective": "LEAD_GENERATION",
            "status": "PAUSED",
            "daily_budget": budget,
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            "special_ad_categories": "[]",
        }
        # Usar self.ad_account_id que ya incluye el prefijo act_
        result = self._post(f"{self.ad_account_id}/campaigns", data)
        if "id" not in result:
            return {"campaign_id": None, "status": "error"}
        return {"campaign_id": result["id"], "status": "PAUSED"}

    def pause_campaign(self, campaign_id: str) -> dict:
        """Pauses an active campaign."""
        result = self._post(campaign_id, {"status": "PAUSED"})
        if "success" in result and result["success"]:
            return {"status": "PAUSED"}
        return {"status": "error"}

    def get_metrics(self, campaign_id: str) -> dict:
        """Returns spend, leads, cpc, cpa for the campaign (lifetime)."""
        params = {
            "fields": "spend,actions,cost_per_action_type,cpc",
            "date_preset": "lifetime",
        }
        result = self._get(f"{campaign_id}/insights", params)
        data = result.get("data", [{}])
        if not data:
            return {"spend": 0, "leads": 0, "cpc": 0, "cpa": 0}

        row = data[0]
        spend = float(row.get("spend", 0))
        cpc = float(row.get("cpc", 0))

        leads = 0
        for action in row.get("actions", []):
            if action.get("action_type") == "lead":
                leads = int(action.get("value", 0))
                break

        cpa = 0
        for entry in row.get("cost_per_action_type", []):
            if entry.get("action_type") == "lead":
                cpa = float(entry.get("value", 0))
                break

        return {"spend": spend, "leads": leads, "cpc": cpc, "cpa": cpa}

    def get_account_info(self) -> dict:
        """Returns basic account info to verify token works."""
        if self._disabled:
            return {"error": "Client disabled"}
        result = self._get(self.ad_account_id, {"fields": "name,account_status,currency"})
        return result


if __name__ == "__main__":
    client = MetaAdsClient()
    if client.is_ready:
        info = client.get_account_info()
        print("Account Info:", info)
    else:
        print("Client not ready — check env vars")
