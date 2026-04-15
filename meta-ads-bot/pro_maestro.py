#!/usr/bin/env python3
"""
🧠 PRO MAESTRO — Sistema de Inteligencia Empresarial Autónoma
Aprende de datos REALES de la empresa, optimiza procesos, incrementa ingresos, reduce gastos.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from anthropic import Anthropic
from maestro_intelligence import (
    NotionDataPipeline, StripeDataPipeline,
    create_data_snapshot, save_decision, record_decision_result
)

load_dotenv()
logger = logging.getLogger(__name__)

class ProMaestro:
    """Sistema de inteligencia empresarial que aprende y optimiza automáticamente."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic()
        self.conversation_history = []
        self.analytics = {
            "ingresos": {},
            "gastos": {},
            "clientes": {},
            "campanas": {},
            "oportunidades": []
        }
        # Get real data once
        self.latest_snapshot = create_data_snapshot()

    def analyze_company_metrics(self, company_data: dict = None) -> dict:
        """
        Analiza métricas REALES de la empresa desde Notion + Stripe.

        Args:
            company_data: opcional, si se pasa datos específicos. Si no, usa snapshot real.
        """
        # Si no pasamos datos, usar snapshot real
        if not company_data:
            snapshot = self.latest_snapshot
            company_data = {
                "clientes_activos": snapshot.get("notion_clients_count", 0),
                "ingresos_mes": snapshot.get("notion_revenue_month", 0),
                "gastos_mes": snapshot.get("notion_expenses_month", 0),
                "stripe_mrr": snapshot.get("stripe_mrr", 0),
                "meta_ads_spend": snapshot.get("meta_ads_spend", 0),
                "meta_ads_roas": snapshot.get("meta_ads_roas", 0),
                "tasa_conversion": snapshot.get("leads_conversion_rate", 0),
                "timestamp": snapshot.get("snapshot_date")
            }

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system="""Eres un analista empresarial experto en Sistema 180.
Analizas datos REALES de la empresa (Notion, Stripe) y generas insights accionables.
Eres directo, específico y enfocado en resultados medibles.
Busca oportunidades de crecimiento y optimización.""",
            messages=[{
                "role": "user",
                "content": f"""Analiza estos datos REALES actuales de Sistema 180 (datos de Notion + Stripe):

{json.dumps(company_data, indent=2, ensure_ascii=False)}

Proporciona:
1. Estado actual (ratio de salud: 0-100)
2. Fortalezas (qué está funcionando bien)
3. Debilidades críticas (dónde se pierde dinero)
4. Oportunidades (dónde ganar dinero rápido)
5. Recomendaciones prioritarias (top 3 acciones para HOY)

Sé ESPECÍFICO con números reales y % de mejora esperada.
Referencia las métricas Stripe/Meta Ads directamente."""
            }]
        )

        analysis = response.content[0].text

        # Guarda análisis como decisión
        save_decision(
            category="analysis",
            hypothesis="Análisis de métricas del día",
            recommendation=analysis,
            confidence=75,
            source_data=company_data,
            tags="metrics,daily"
        )

        return {
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "source": "real_data"
        }

    def optimize_revenue_streams(self, revenue_data: dict = None) -> dict:
        """
        Optimiza las 7 patas de ingresos de Sistema 180.

        Args:
            revenue_data: {
                "webs": {"activas": 5, "ingresos_mes": 1500, "potencial": 5000},
                "recepcionista_ia": {"clientes": 3, "ingresos_mes": 900, "potencial": 3000},
                "afiliacion": {"afiliados": 10, "ingresos_mes": 500, "potencial": 2000},
                "marketplace": {"listings": 50, "ingresos_mes": 300, "potencial": 2000},
                "avatares_ia": {"ordenes_mes": 20, "ingresos_mes": 400, "potencial": 1500},
                "marca_personal": {"subscribers": 5000, "ingresos_mes": 200, "potencial": 3000},
                "trading_bots": {"capital_gestionado": 10000, "ingresos_mes": 150, "potencial": 500}
            }
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            system="""Eres experto en multiplicación de ingresos para agencias digitales.
Conoces las 7 patas de Sistema 180.
Generas estrategias específicas para ESCALAR cada fuente de ingreso.""",
            messages=[{
                "role": "user",
                "content": f"""Optimiza las 7 patas de ingresos de Sistema 180:

{json.dumps(revenue_data, indent=2, ensure_ascii=False)}

Para CADA pata:
1. Brecha actual vs potencial
2. Cuello de botella (qué impide crecer)
3. Plan de escalado (pasos específicos)
4. Proyección: 30 días, 90 días, 6 meses
5. Recursos necesarios

Objetivo: Aumentar ingresos mensuales de {sum(x.get('ingresos_mes', 0) for x in revenue_data.values())}€ a {sum(x.get('potencial', 0) for x in revenue_data.values())}€

Sé AGRESIVO pero realista."""
            }]
        )

        return {
            "strategy": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def reduce_expenses(self, expense_data: dict) -> dict:
        """
        Identifica oportunidades para reducir gastos.

        Args:
            expense_data: {
                "categoria": {
                    "nombre": "Servidores",
                    "gasto_mes": 500,
                    "descripcion": "Railway, Vercel, n8n..."
                }
            }
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system="""Eres experto en optimización de costos para startups.
Identificas gastos ineficientes y propones alternativas.
Buscas ahorrar sin sacrificar calidad.""",
            messages=[{
                "role": "user",
                "content": f"""Optimiza estos gastos mensuales de Sistema 180:

{json.dumps(expense_data, indent=2, ensure_ascii=False)}

Para CADA categoría:
1. ¿Es necesario este gasto?
2. ¿Hay alternativa más barata?
3. ¿Se puede automatizar o eliminar?
4. Ahorro mensual potencial (€ + %)

Objetivo: Reducir gastos mensuales totales en 20-30%

Sé ESPECÍFICO: "Cambiar de Railway a [alternativa] ahorra €X"."""
            }]
        )

        return {
            "recommendations": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def identify_opportunities(self, market_data: dict) -> dict:
        """
        Identifica oportunidades de negocio basadas en datos del mercado y clientes.
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2500,
            system="""Eres estratega de negocios para Sistema 180.
Identificas oportunidades donde hay dinero rápido.
Piensas en términos de 30 días, 90 días, 6 meses.""",
            messages=[{
                "role": "user",
                "content": f"""Basándote en estos datos de mercado y clientes de Sistema 180:

{json.dumps(market_data, indent=2, ensure_ascii=False)}

Identifica TOP 5 oportunidades donde ganar dinero:

Para CADA oportunidad:
1. Descripción (qué es, a quién le vendo)
2. Potencial de ingresos (mes 1, mes 3, mes 6)
3. Inversión necesaria (tiempo + dinero)
4. Pasos concretos (qué hacer MAÑANA)
5. Riesgo (alto/medio/bajo)
6. Tiempo para ROI

Ranking por: Dinero rápido (mes 1) + Mantenibilidad."""
            }]
        )

        return {
            "opportunities": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def optimize_operations(self, operations_data: dict) -> dict:
        """
        Optimiza procesos operativos para reducir tiempo y aumentar eficiencia.
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2500,
            system="""Eres experto en automatización y optimización de procesos.
Conoces Sistema 180 completamente.
Buscas liberar tiempo para las actividades que generan dinero.""",
            messages=[{
                "role": "user",
                "content": f"""Optimiza estos procesos operativos de Sistema 180:

{json.dumps(operations_data, indent=2, ensure_ascii=False)}

Para CADA proceso:
1. Tiempo actual invertido
2. Cuello de botella (dónde se pierde tiempo)
3. Solución de automatización (herramienta + cómo)
4. Tiempo ahorrado (por semana/mes)
5. Costo de implementación
6. Timeline (cuánto tarda en setup)

Objetivo: Liberar 20+ horas/semana de trabajo manual

Prioriza por: Ahorro de tiempo + Bajo costo + Fácil implementación."""
            }]
        )

        return {
            "optimizations": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def generate_daily_maestro_report(self, company_snapshot: dict) -> str:
        """
        Genera reporte diario del "Pro Maestro" con análisis y recomendaciones.
        """
        self.conversation_history.append({
            "role": "user",
            "content": f"""Buenos días. Hoy es {datetime.now().strftime('%d/%m/%Y')}.

Estado actual de Sistema 180:
{json.dumps(company_snapshot, indent=2, ensure_ascii=False)}

Dame el REPORTE DIARIO DEL PRO MAESTRO:

1. 🎯 OBJETIVO DEL DÍA
   - La acción #1 que hoy generará dinero
   - Por qué (oportunidad o urgencia)

2. 💰 OPORTUNIDAD RÁPIDA
   - Dinero fácil hoy (sin preparación)
   - Pasos concretos (qué hacer ya)

3. 🚀 PROYECTO SEMANA
   - Qué lanzar esta semana
   - Impacto esperado (ingresos)

4. ⚠️ ALERTA CRÍTICA
   - Qué podría romperse
   - Cómo prevenirlo

5. 📊 MÉTRICA DEL DÍA
   - Qué debe crecer HOY
   - Target: 5% de mejora

FORMATO: Concreto, ejecutable, motivante."""
        })

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            system="""Eres el Pro Maestro de Sistema 180.
Cada mañana das el reporte que pone la empresa en movimiento.
Eres conciso, motivante, directo.
Solo lo esencial para generar dinero HOY.""",
            messages=self.conversation_history
        )

        report = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": report
        })

        return report

    def ai_decision_maker(self, situation: str, options: list = None) -> str:
        """
        Toma decisiones empresariales con IA cuando hay duda.
        """
        self.conversation_history.append({
            "role": "user",
            "content": f"""Situación: {situation}

{f"Opciones a considerar: {', '.join(options)}" if options else ""}

¿Cuál es la mejor decisión? (dinero, rapidez, riesgo)"""
        })

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            system="""Eres el asesor de negocios de José María.
Tomas decisiones claras basadas en: dinero, rapidez, riesgo.
Eres directo: "Sí, haz esto porque..." o "No, aquí está el peligro...".""",
            messages=self.conversation_history
        )

        decision = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": decision
        })

        return decision

    def export_full_analysis(self) -> str:
        """Exporta análisis completo como JSON."""
        return json.dumps({
            "timestamp": datetime.now().isoformat(),
            "analytics": self.analytics,
            "conversation_turns": len(self.conversation_history)
        }, indent=2, ensure_ascii=False)


def create_pro_maestro() -> ProMaestro:
    """Factory para crear instancia del Pro Maestro."""
    return ProMaestro()


if __name__ == "__main__":
    maestro = create_pro_maestro()

    print("\n" + "="*80)
    print("🧠 PRO MAESTRO — Sistema de Inteligencia Empresarial")
    print("="*80 + "\n")

    # Ejemplo: Análisis de métricas
    company_data = {
        "clientes_activos": 15,
        "ingresos_mes": 4500,
        "gastos_mes": 2000,
        "ticket_promedio": 300,
        "tasa_conversion": 0.15,
        "costo_adquisicion": 50,
        "churn_rate": 0.05,
        "nuevos_clientes_mes": 5
    }

    print("📊 Analizando métricas actuales...")
    result = maestro.analyze_company_metrics(company_data)
    print(f"\n{result['analysis']}\n")

    # Ejemplo: Reporte diario
    print("\n" + "="*80)
    print("📋 REPORTE DIARIO DEL PRO MAESTRO")
    print("="*80 + "\n")

    snapshot = {
        "fecha": datetime.now().isoformat(),
        "clientes": company_data["clientes_activos"],
        "ingresos_acumulados": company_data["ingresos_mes"]
    }

    report = maestro.generate_daily_maestro_report(snapshot)
    print(report)

    print("\n✅ Pro Maestro listo. Úsalo desde el bot Telegram.")
