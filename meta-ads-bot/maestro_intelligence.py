#!/usr/bin/env python3
"""
🧠 MAESTRO INTELLIGENCE — Data aggregation + Learning loops
Conecta Notion, Stripe, Meta Ads → Pro Maestro aprende cada día
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Any
import requests

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE = "/tmp/maestro_analytics.db"

# ─── INITIALIZE DATABASE ───
def init_maestro_db():
    """Crea tablas de maestro_analytics.db"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # TABLE: decisions (hipótesis de Pro Maestro)
    c.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        category TEXT,
        analysis_type TEXT,
        hypothesis TEXT,
        recommendation TEXT,
        confidence_score INTEGER,
        source_data TEXT,
        tags TEXT,
        status TEXT DEFAULT 'pending',
        expected_impact REAL
    )
    """)

    # TABLE: decision_execution (cuándo se ejecutó)
    c.execute("""
    CREATE TABLE IF NOT EXISTS decision_execution (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        decision_id INTEGER,
        execution_date TEXT,
        executed_by TEXT,
        method TEXT,
        n8n_execution_id TEXT,
        status TEXT DEFAULT 'pending',
        notes TEXT,
        FOREIGN KEY(decision_id) REFERENCES decisions(id)
    )
    """)

    # TABLE: decision_results (impacto real)
    c.execute("""
    CREATE TABLE IF NOT EXISTS decision_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        decision_id INTEGER,
        execution_id INTEGER,
        result_date TEXT,
        metric_type TEXT,
        baseline_value REAL,
        result_value REAL,
        delta REAL,
        delta_percent REAL,
        success BOOLEAN,
        actual_vs_predicted TEXT,
        learnings TEXT,
        FOREIGN KEY(decision_id) REFERENCES decisions(id),
        FOREIGN KEY(execution_id) REFERENCES decision_execution(id)
    )
    """)

    # TABLE: patterns (lo que aprendemos)
    c.execute("""
    CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT,
        description TEXT,
        conditions TEXT,
        success_rate REAL,
        occurrences INTEGER,
        last_applied TEXT,
        revenue_impact_avg REAL,
        confidence REAL,
        tags TEXT,
        source TEXT,
        created_at TEXT
    )
    """)

    # TABLE: data_snapshots (histórico de métricas)
    c.execute("""
    CREATE TABLE IF NOT EXISTS data_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_date TEXT,
        snapshot_type TEXT,
        notion_clients_count INTEGER,
        notion_revenue_month REAL,
        notion_expenses_month REAL,
        stripe_mrr REAL,
        stripe_arr REAL,
        meta_ads_spend REAL,
        meta_ads_roas REAL,
        leads_pipeline_value REAL,
        leads_conversion_rate REAL,
        agentes_activos INTEGER,
        metadata TEXT,
        raw_data TEXT
    )
    """)

    # TABLE: forecasts (predicciones)
    c.execute("""
    CREATE TABLE IF NOT EXISTS forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        forecast_date TEXT,
        metric TEXT,
        period TEXT,
        predicted_value REAL,
        confidence_level INTEGER,
        methodology TEXT,
        actual_value REAL,
        accuracy REAL,
        created_by TEXT
    )
    """)

    conn.commit()
    conn.close()
    logger.info("✅ maestro_analytics.db initialized")


# ─── NOTION DATA PIPELINE ───
class NotionDataPipeline:
    """Lee datos REALES de Notion"""

    @staticmethod
    def fetch_clients_db() -> list:
        """Retorna clientes activos de Notion"""
        try:
            notion_token = os.getenv("NOTION_TOKEN")
            clients_db_id = os.getenv("NOTION_CLIENTS_DB_ID")

            if not notion_token or not clients_db_id:
                logger.warning("⚠️  NOTION_TOKEN o NOTION_CLIENTS_DB_ID no configurados")
                return []

            headers = {
                "Authorization": f"Bearer {notion_token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }

            # Paginate results
            all_clients = []
            start_cursor = None

            while True:
                payload = {
                    "filter": {
                        "property": "Status",
                        "status": {"equals": "Activo"}
                    }
                }
                if start_cursor:
                    payload["start_cursor"] = start_cursor

                response = requests.post(
                    f"https://api.notion.com/v1/databases/{clients_db_id}/query",
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code != 200:
                    logger.error(f"❌ Notion clients query failed: {response.status_code}")
                    return all_clients

                data = response.json()

                for page in data.get("results", []):
                    props = page.get("properties", {})
                    client = {
                        "id": page["id"],
                        "name": props.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Unknown"),
                        "service": props.get("Service", {}).get("select", {}).get("name", "Unknown"),
                        "price_month": props.get("Price", {}).get("number", 0),
                        "status": "Activo"
                    }
                    all_clients.append(client)

                if data.get("has_more"):
                    start_cursor = data.get("next_cursor")
                else:
                    break

            logger.info(f"✅ Fetched {len(all_clients)} active clients from Notion")
            return all_clients

        except Exception as e:
            logger.error(f"❌ Notion fetch_clients error: {e}")
            return []

    @staticmethod
    def fetch_invoices_db() -> tuple[float, list]:
        """Retorna total de ingresos del mes actual y detalles"""
        try:
            notion_token = os.getenv("NOTION_TOKEN")
            invoices_db_id = os.getenv("NOTION_INVOICES_DB_ID")

            if not invoices_db_id:
                logger.warning("⚠️  NOTION_INVOICES_DB_ID no configurado")
                return 0.0, []

            headers = {
                "Authorization": f"Bearer {notion_token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }

            # Get current month
            now = datetime.now()
            first_day = datetime(now.year, now.month, 1).isoformat()

            payload = {
                "filter": {
                    "and": [
                        {
                            "property": "Date",
                            "date": {"on_or_after": first_day}
                        },
                        {
                            "property": "Status",
                            "select": {"equals": "Pagada"}
                        }
                    ]
                }
            }

            response = requests.post(
                f"https://api.notion.com/v1/databases/{invoices_db_id}/query",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code != 200:
                return 0.0, []

            data = response.json()
            invoices = []
            total = 0.0

            for page in data.get("results", []):
                props = page.get("properties", {})
                amount = props.get("Amount", {}).get("number", 0)
                invoices.append({
                    "id": page["id"],
                    "client": props.get("Client", {}).get("title", [{}])[0].get("text", {}).get("content", "Unknown"),
                    "amount": amount
                })
                total += amount

            logger.info(f"✅ Fetched invoices: €{total} from {len(invoices)} transactions")
            return total, invoices

        except Exception as e:
            logger.error(f"❌ Notion fetch_invoices error: {e}")
            return 0.0, []

    @staticmethod
    def fetch_expenses_db() -> tuple[float, list]:
        """Retorna gastos del mes actual"""
        try:
            notion_token = os.getenv("NOTION_TOKEN")
            expenses_db_id = os.getenv("NOTION_EXPENSES_DB_ID")

            if not expenses_db_id:
                return 0.0, []

            headers = {
                "Authorization": f"Bearer {notion_token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }

            now = datetime.now()
            first_day = datetime(now.year, now.month, 1).isoformat()

            response = requests.post(
                f"https://api.notion.com/v1/databases/{expenses_db_id}/query",
                headers=headers,
                json={"filter": {"property": "Date", "date": {"on_or_after": first_day}}},
                timeout=10
            )

            if response.status_code != 200:
                return 0.0, []

            data = response.json()
            expenses = []
            total = 0.0

            for page in data.get("results", []):
                props = page.get("properties", {})
                amount = props.get("Amount", {}).get("number", 0)
                expenses.append({
                    "id": page["id"],
                    "category": props.get("Category", {}).get("select", {}).get("name", "Unknown"),
                    "amount": amount
                })
                total += amount

            return total, expenses

        except Exception as e:
            logger.error(f"❌ Notion fetch_expenses error: {e}")
            return 0.0, []


# ─── STRIPE DATA PIPELINE ───
class StripeDataPipeline:
    """Lee datos de Stripe API"""

    @staticmethod
    def fetch_revenue_current_month() -> float:
        """Ingresos pagados este mes"""
        try:
            stripe_key = os.getenv("STRIPE_SECRET_KEY")
            if not stripe_key:
                return 0.0

            now = datetime.now()
            first_day = int(datetime(now.year, now.month, 1).timestamp())
            today = int(now.timestamp())

            response = requests.get(
                "https://api.stripe.com/v1/charges",
                auth=(stripe_key, ""),
                params={
                    "created[gte]": first_day,
                    "created[lt]": today,
                    "status": "succeeded",
                    "limit": 100
                },
                timeout=10
            )

            if response.status_code != 200:
                return 0.0

            data = response.json()
            total = sum(c["amount"] / 100 for c in data.get("data", []))
            logger.info(f"✅ Stripe revenue current month: €{total}")
            return total

        except Exception as e:
            logger.error(f"❌ Stripe revenue error: {e}")
            return 0.0

    @staticmethod
    def fetch_subscriptions_mrr() -> tuple[float, int]:
        """MRR y ARR de suscripciones activas"""
        try:
            stripe_key = os.getenv("STRIPE_SECRET_KEY")
            if not stripe_key:
                return 0.0, 0

            response = requests.get(
                "https://api.stripe.com/v1/subscriptions",
                auth=(stripe_key, ""),
                params={"status": "active", "limit": 100},
                timeout=10
            )

            if response.status_code != 200:
                return 0.0, 0

            data = response.json()
            mrr = 0.0
            count = 0

            for sub in data.get("data", []):
                amount = sub.get("items", {}).get("data", [{}])[0].get("price", {}).get("recurring", {}).get("aggregate_usage") or 0
                if not amount:
                    amount = sub.get("items", {}).get("data", [{}])[0].get("price", {}).get("unit_amount", 0) / 100
                mrr += amount
                count += 1

            logger.info(f"✅ Stripe MRR: €{mrr} ({count} subscriptions)")
            return mrr, count

        except Exception as e:
            logger.error(f"❌ Stripe subscriptions error: {e}")
            return 0.0, 0


# ─── DATA SNAPSHOT ───
def create_data_snapshot() -> dict:
    """Fotografía del sistema en este momento"""

    # Collect data from all pipelines
    clients = NotionDataPipeline.fetch_clients_db()
    revenue, invoices = NotionDataPipeline.fetch_invoices_db()
    expenses, expense_list = NotionDataPipeline.fetch_expenses_db()
    stripe_revenue = StripeDataPipeline.fetch_revenue_current_month()
    mrr, subscription_count = StripeDataPipeline.fetch_subscriptions_mrr()

    # Meta Ads data (placeholder - integrate later)
    meta_spend = 300.0  # TODO: fetch from Meta Ads API
    meta_roas = 2.1  # TODO: calculate from conversions

    snapshot = {
        "snapshot_date": datetime.now().isoformat(),
        "snapshot_type": "realtime",
        "notion_clients_count": len(clients),
        "notion_revenue_month": revenue,
        "notion_expenses_month": expenses,
        "stripe_mrr": mrr,
        "stripe_arr": mrr * 12,
        "meta_ads_spend": meta_spend,
        "meta_ads_roas": meta_roas,
        "leads_pipeline_value": 0.0,  # TODO
        "leads_conversion_rate": 0.15,  # TODO
        "agentes_activos": 0,  # TODO
        "raw_data": json.dumps({
            "clients": clients,
            "invoices": invoices,
            "expenses": expense_list
        })
    }

    # Persist to DB
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO data_snapshots (
        snapshot_date, snapshot_type, notion_clients_count,
        notion_revenue_month, notion_expenses_month, stripe_mrr,
        stripe_arr, meta_ads_spend, meta_ads_roas, raw_data
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        snapshot["snapshot_date"],
        snapshot["snapshot_type"],
        snapshot["notion_clients_count"],
        snapshot["notion_revenue_month"],
        snapshot["notion_expenses_month"],
        snapshot["stripe_mrr"],
        snapshot["stripe_arr"],
        snapshot["meta_ads_spend"],
        snapshot["meta_ads_roas"],
        snapshot["raw_data"]
    ))
    conn.commit()
    conn.close()

    logger.info(f"✅ Snapshot created: {len(clients)} clients, €{revenue} revenue, €{expenses} expenses")
    return snapshot


# ─── LEARNING SYSTEM ───
def save_decision(category: str, hypothesis: str, recommendation: str,
                  confidence: int, source_data: dict, tags: str) -> int:
    """Guarda una decisión de Pro Maestro"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO decisions (
        timestamp, category, hypothesis, recommendation,
        confidence_score, source_data, tags, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        category,
        hypothesis,
        recommendation,
        confidence,
        json.dumps(source_data),
        tags,
        "pending"
    ))
    conn.commit()
    decision_id = c.lastrowid
    conn.close()

    logger.info(f"✅ Decision saved (ID: {decision_id}, confidence: {confidence}%)")
    return decision_id


def execute_decision(decision_id: int, executed_by: str = "telegram",
                     method: str = "n8n_workflow", n8n_id: str = None):
    """Marca una decisión como ejecutada"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO decision_execution (
        decision_id, execution_date, executed_by, method,
        n8n_execution_id, status
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        decision_id,
        datetime.now().isoformat(),
        executed_by,
        method,
        n8n_id,
        "running"
    ))
    conn.commit()
    execution_id = c.lastrowid
    conn.close()

    logger.info(f"✅ Decision {decision_id} marked as executing")
    return execution_id


def record_decision_result(decision_id: int, execution_id: int,
                          metric_type: str, baseline: float,
                          result: float, learnings: str):
    """Guarda el resultado real de una decisión"""
    delta = result - baseline
    delta_pct = (delta / baseline * 100) if baseline != 0 else 0
    success = delta > 0

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO decision_results (
        decision_id, execution_id, result_date, metric_type,
        baseline_value, result_value, delta, delta_percent,
        success, learnings
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        decision_id,
        execution_id,
        datetime.now().isoformat(),
        metric_type,
        baseline,
        result,
        delta,
        delta_pct,
        success,
        learnings
    ))
    conn.commit()
    conn.close()

    status = "✅" if success else "❌"
    logger.info(f"{status} Decision {decision_id} result: {metric_type} delta {delta_pct:.1f}%")


def update_pattern_confidence(pattern_id: int, success: bool, impact: float):
    """Actualiza confianza de un patrón"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Get current pattern
    c.execute("SELECT * FROM patterns WHERE id = ?", (pattern_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return

    success_rate, occurrences, confidence = row[4], row[5], row[8]

    # Recalculate
    new_success_rate = (success_rate * occurrences + (100 if success else 0)) / (occurrences + 1)
    new_confidence = min(
        confidence + (5 if success else -2),
        100
    )

    c.execute("""
    UPDATE patterns SET
        success_rate = ?, occurrences = ?, confidence = ?,
        last_applied = ?, revenue_impact_avg = ?
    WHERE id = ?
    """, (
        new_success_rate,
        occurrences + 1,
        new_confidence,
        datetime.now().isoformat(),
        impact,
        pattern_id
    ))

    conn.commit()
    conn.close()

    logger.info(f"✅ Pattern {pattern_id} updated: success_rate={new_success_rate:.1f}%, confidence={new_confidence:.0f}%")


if __name__ == "__main__":
    init_maestro_db()
    snapshot = create_data_snapshot()
    print(json.dumps(snapshot, indent=2, default=str))
