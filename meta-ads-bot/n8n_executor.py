"""
n8n Workflow Executor — Auto-execute workflows based on AI decisions
Handles high-confidence decisions autonomously
"""

import os
import requests
import json
import asyncio
from datetime import datetime
import logging
import sqlite3

logger = logging.getLogger(__name__)


class N8nExecutor:
    """Executes n8n workflows when AI confidence is high enough"""

    def __init__(self):
        self.webhook_base = os.getenv(
            "N8N_WEBHOOK_URL", "https://sistema180.app.n8n.cloud/webhook/"
        )
        self.api_key = os.getenv("N8N_API_KEY", "")

    async def execute_workflow(self, workflow_id: str, data: dict = None) -> dict:
        """Trigger n8n workflow via webhook"""

        try:
            webhook_url = f"{self.webhook_base}{workflow_id}"

            payload = {
                "action": "execute",
                "timestamp": datetime.now().isoformat(),
                "triggered_by": "maestro_brain",
                "data": data or {},
                "metadata": {
                    "execution_id": f"maestro_{workflow_id}_{int(datetime.now().timestamp())}",
                    "confidence": data.get("confidence", 0) if data else 0,
                },
            }

            response = requests.post(webhook_url, json=payload, timeout=30)

            if response.status_code == 200:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "execution_id": payload["metadata"]["execution_id"],
                    "response": response.json() if response.text else {},
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text[:200],
                }

        except Exception as e:
            logger.error(f"n8n execution error: {e}")
            return {"success": False, "error": str(e)}

    async def auto_execute_high_confidence(
        self,
        decision: dict,
        confidence_threshold: float = 0.85,
        max_value: float = 500,
    ) -> dict:
        """Auto-execute if confidence > threshold AND value < max"""

        confidence = decision.get("confidence_score", 0) / 100
        value = decision.get("money_impact", 0)

        if confidence >= confidence_threshold and value <= max_value:
            workflow_id = self._map_decision_to_workflow(decision)

            if workflow_id:
                result = await self.execute_workflow(workflow_id, decision)

                self._log_auto_execution(decision, result)

                return {"auto_executed": True, "result": result}

        return {"auto_executed": False, "reason": "Thresholds not met"}

    def _map_decision_to_workflow(self, decision: dict) -> str:
        """Map decision category to n8n workflow ID"""

        mapping = {
            "revenue": "kEHN2fzTCT5E8VOB",  # Revenue optimization flow
            "cost": "XyZ9aB2cD4eF6gH8",  # Cost reduction flow
            "growth": "P1qR2sT3uV4wX5yZ",  # Growth campaign flow
            "leads": "9oI8kJ7lM6nO5pQ4",  # Lead generation flow
            "campaign": "aB3cD4eF5gH6iJ7k",  # Campaign launcher flow
        }

        category = decision.get("category", "").lower()
        return mapping.get(category, "")

    def _log_auto_execution(self, decision: dict, result: dict) -> None:
        """Log auto-execution for audit trail"""

        try:
            conn = sqlite3.connect("/tmp/maestro_analytics.db")
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO decision_execution (
                    decision_id, executed_by, execution_method, executed_at
                )
                VALUES (?, ?, ?, ?)
            """,
                (
                    decision.get("id"),
                    "n8n_auto_executor",
                    "n8n_webhook",
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            conn.close()
            logger.info(f"Auto-execution logged: {decision.get('id')}")
        except Exception as e:
            logger.error(f"Execution logging error: {e}")

    async def get_workflow_status(self, workflow_id: str) -> dict:
        """Check status of a workflow"""
        try:
            if not self.api_key:
                return {"status": "unknown", "reason": "No API key configured"}

            url = f"https://sistema180.app.n8n.cloud/api/v1/workflows/{workflow_id}"
            headers = {"X-N8N-API-KEY": self.api_key}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return {"status": "active", "data": response.json()}
            else:
                return {"status": "error", "code": response.status_code}

        except Exception as e:
            logger.error(f"Workflow status check error: {e}")
            return {"status": "error", "error": str(e)}
