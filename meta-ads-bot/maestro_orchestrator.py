"""
MAESTRO ORCHESTRATOR — Crew Leader coordinating all agents
Parallel execution of data gathering, analysis, and autonomous decision-making
Based on CrewAI multi-agent orchestration pattern
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
import json

from meta_agent import MetaAdsAgent
from maestro_intelligence import StripeDataPipeline, create_data_snapshot
from n8n_executor import N8nExecutor
from autonomous_executor import AutonomousExecutor

logger = logging.getLogger(__name__)


class MaestroOrchestrator:
    """Orchestrates all specialized agents for autonomous business optimization"""

    def __init__(self):
        self.meta_agent = MetaAdsAgent()
        self.stripe_agent = StripeDataPipeline()
        self.n8n_executor = N8nExecutor()
        self.autonomous_executor = AutonomousExecutor()
        self.execution_log = []

    async def run_daily_cycle(self) -> Dict[str, Any]:
        """Run complete daily optimization cycle with all agents"""

        logger.info("🚀 Starting Maestro daily cycle...")
        start_time = datetime.now()

        try:
            # 1. PARALLEL DATA GATHERING (all agents simultaneously)
            logger.info("📊 Gathering data from all sources...")
            data_tasks = await asyncio.gather(
                self._gather_meta_data(),
                self._gather_stripe_data(),
                self._gather_notion_data(),
                return_exceptions=True
            )

            meta_data = data_tasks[0] if isinstance(data_tasks[0], dict) else {}
            stripe_data = data_tasks[1] if isinstance(data_tasks[1], dict) else {}
            notion_data = data_tasks[2] if isinstance(data_tasks[2], dict) else {}

            # 2. UNIFIED SNAPSHOT
            unified_snapshot = self._merge_snapshots(meta_data, stripe_data, notion_data)

            logger.info(f"✅ Data gathered: Meta={bool(meta_data)}, Stripe={bool(stripe_data)}, Notion={bool(notion_data)}")

            # 3. ANALYSIS & RECOMMENDATIONS
            logger.info("🧠 Analyzing data and generating recommendations...")
            analysis = await self._analyze_snapshot(unified_snapshot)

            # 4. AUTO-EXECUTION OF HIGH-CONFIDENCE DECISIONS
            logger.info("⚡ Auto-executing high-confidence decisions...")
            execution_results = await self._auto_execute_decisions(analysis.get("decisions", []))

            # 5. COMPILE DAILY REPORT
            daily_report = await self._compile_daily_report(
                unified_snapshot,
                analysis,
                execution_results
            )

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Daily cycle complete in {elapsed:.1f}s")

            return daily_report

        except Exception as e:
            logger.error(f"Daily cycle error: {e}")
            return {"error": str(e), "status": "failed"}

    async def _gather_meta_data(self) -> Dict[str, Any]:
        """Gather Meta Ads data"""
        try:
            data = await self.meta_agent.analyze_campaigns()
            recommendations = await self.meta_agent.get_recommendations(data)
            return {
                "source": "meta_ads",
                "metrics": data,
                "recommendations": recommendations
            }
        except Exception as e:
            logger.error(f"Meta data gathering error: {e}")
            return {}

    async def _gather_stripe_data(self) -> Dict[str, Any]:
        """Gather Stripe subscription data"""
        try:
            mrr_data = self.stripe_agent.fetch_subscriptions_mrr()
            churn_data = self.stripe_agent.detect_churn()
            return {
                "source": "stripe",
                "mrr": mrr_data,
                "churn": churn_data
            }
        except Exception as e:
            logger.error(f"Stripe data gathering error: {e}")
            return {}

    async def _gather_notion_data(self) -> Dict[str, Any]:
        """Gather Notion CRM data"""
        try:
            # Use existing snapshot function
            snapshot = create_data_snapshot()
            return {
                "source": "notion",
                "snapshot": snapshot
            }
        except Exception as e:
            logger.error(f"Notion data gathering error: {e}")
            return {}

    def _merge_snapshots(
        self,
        meta_data: Dict,
        stripe_data: Dict,
        notion_data: Dict
    ) -> Dict[str, Any]:
        """Merge all data sources into unified snapshot"""

        unified = {
            "timestamp": datetime.now().isoformat(),
            "meta_ads": meta_data.get("metrics", {}),
            "stripe": stripe_data.get("mrr", {}),
            "churn_risk": stripe_data.get("churn", {}),
            "notion": notion_data.get("snapshot", {}),
            "snapshot_source": "all_agents"
        }

        return unified

    async def _analyze_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze unified snapshot and generate recommendations"""

        # Health scoring
        health_score = self._calculate_health_score(snapshot)

        # Generate decisions
        decisions = self._generate_decisions(snapshot, health_score)

        return {
            "health_score": health_score,
            "decisions": decisions,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_health_score(self, snapshot: Dict[str, Any]) -> float:
        """Calculate 0-100 business health score"""

        score = 50  # Base score

        # Meta Ads health
        roas = snapshot.get("meta_ads", {}).get("roas", 0)
        if roas >= 2.0:
            score += 20
        elif roas >= 1.5:
            score += 10

        # Stripe health
        mrr = snapshot.get("stripe", {}).get("stripe_mrr", 0)
        if mrr > 1000:
            score += 20
        elif mrr > 500:
            score += 10

        # Churn risk
        churn = snapshot.get("churn_risk", {}).get("churn_events_24h", 0)
        if churn == 0:
            score += 10
        elif churn > 2:
            score -= 10

        return min(100, max(0, score))

    def _generate_decisions(
        self,
        snapshot: Dict[str, Any],
        health_score: float
    ) -> List[Dict[str, Any]]:
        """Generate AI decisions based on snapshot"""

        decisions = []

        # Meta Ads decision
        roas = snapshot.get("meta_ads", {}).get("roas", 0)
        if roas >= 2.0:
            decisions.append({
                "id": 1,
                "category": "revenue",
                "hypothesis": "Healthy ROAS means more budget will scale",
                "recommendation": "Increase Meta Ads budget by €50",
                "confidence_score": 87,
                "money_impact": 250,
                "timeline": "hours"
            })

        # Churn mitigation decision
        churn_events = snapshot.get("churn_risk", {}).get("churn_events_24h", 0)
        if churn_events > 0:
            decisions.append({
                "id": 2,
                "category": "risk",
                "hypothesis": "Recent churn requires intervention",
                "recommendation": "Launch win-back campaign for canceled customers",
                "confidence_score": 76,
                "money_impact": 500,
                "timeline": "days"
            })

        # Growth decision
        if health_score >= 70:
            decisions.append({
                "id": 3,
                "category": "growth",
                "hypothesis": "Business is healthy, time to scale",
                "recommendation": "Recruit 5 new affiliates this week",
                "confidence_score": 82,
                "money_impact": 1000,
                "timeline": "days"
            })

        return decisions

    async def _auto_execute_decisions(
        self,
        decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Auto-execute high-confidence decisions"""

        results = []

        for decision in decisions:
            confidence = decision.get("confidence_score", 0) / 100
            value = decision.get("money_impact", 0)

            # Execute if confidence > 85% AND value < €500
            if confidence > 0.85 and value < 500:
                logger.info(f"⚡ Auto-executing: {decision['recommendation']}")

                # Execute via AutonomousExecutor
                exec_result = await self.autonomous_executor.execute_decision(decision)

                results.append({
                    "decision_id": decision.get("id"),
                    "executed": exec_result.get("executed", False),
                    "result": exec_result,
                    "timestamp": datetime.now().isoformat()
                })

                # Also try n8n if configured
                n8n_result = await self.n8n_executor.auto_execute_high_confidence(decision)
                if n8n_result.get("auto_executed"):
                    results[-1]["n8n_executed"] = True

            else:
                results.append({
                    "decision_id": decision.get("id"),
                    "executed": False,
                    "reason": f"Confidence {confidence:.0%} or value €{value} doesn't meet threshold",
                    "timestamp": datetime.now().isoformat()
                })

        return results

    async def _compile_daily_report(
        self,
        snapshot: Dict[str, Any],
        analysis: Dict[str, Any],
        execution_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compile comprehensive daily report"""

        # Count executions
        executed_count = sum(1 for r in execution_results if r.get("executed"))
        total_decisions = len(execution_results)

        report = {
            "timestamp": datetime.now().isoformat(),
            "health_score": analysis.get("health_score", 0),
            "decisions_generated": total_decisions,
            "decisions_executed": executed_count,
            "execution_results": execution_results,
            "key_metrics": {
                "meta_roas": snapshot.get("meta_ads", {}).get("roas", 0),
                "stripe_mrr": snapshot.get("stripe", {}).get("stripe_mrr", 0),
                "churn_24h": snapshot.get("churn_risk", {}).get("churn_events_24h", 0),
            },
            "next_actions": [
                r for r in execution_results
                if not r.get("executed")
            ][:3],  # Top 3 pending
            "status": "complete"
        }

        return report

    async def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""

        return {
            "agents": {
                "meta_agent": "ready",
                "stripe_agent": "ready",
                "n8n_executor": "ready",
                "autonomous_executor": "ready"
            },
            "last_cycle": self.execution_log[-1] if self.execution_log else None,
            "status": "operational",
            "timestamp": datetime.now().isoformat()
        }
