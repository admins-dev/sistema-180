#!/usr/bin/env python3
"""
🧠 STRATEGIC BRAIN — Sistema 180 Marketing Intelligence
Cerebro estratégico para anuncios, contenido viral y automatización completa
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

class StrategicBrain:
    """Sistema de inteligencia estratégica para Sistema 180"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic()
        self.conversation_history = []
        self.strategies = {
            "volumen": [],
            "calidad": [],
            "hibrido": []
        }
        self.campaigns = {}
        self.roi_data = {}

    def analyze_budget_multiplication(self, initial_budget: float, multiplier: int = 10, platform: str = "meta_ads") -> dict:
        """
        Analiza estrategias para multiplicar presupuesto
        Ejemplo: 100€ → 1000€ ganancias
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system="""Eres un experto en marketing digital y multiplicación de ROI.
Analiza estrategias para multiplicar inversión publicitaria.
Sé específico, práctico y orientado a resultados.""",
            messages=[{
                "role": "user",
                "content": f"""Presupuesto inicial: {initial_budget}€
Objetivo: Multiplicar x{multiplier} (obtener {initial_budget * multiplier}€)
Plataforma: {platform}
Tiempo: 30 días

Genera:
1. Estrategia de segmentación de audiencia (máximo detalle)
2. Calendario de lanzamiento de campañas
3. A/B testing plan
4. Ajustes automáticos según performance
5. Puntos de parada (stop-loss) y escalado (x2 si funciona)
6. Métricas críticas a monitorear

Formato: JSON estructurado"""
            }]
        )

        return {
            "initial_budget": initial_budget,
            "target": initial_budget * multiplier,
            "strategy": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def generate_viral_content_strategy(self, niche: str, platforms: list = ["instagram", "tiktok"], volume_per_day: int = 5) -> dict:
        """
        Genera estrategia de contenido viral
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            system="""Eres un experto en viralidad y contenido de alto impacto.
Creas estrategias de contenido que explotan tendencias y psicología viral.
Conoces los algoritmos de cada plataforma.""",
            messages=[{
                "role": "user",
                "content": f"""NICHO: {niche}
PLATAFORMAS: {', '.join(platforms)}
VOLUMEN: {volume_per_day} posts/día
OBJETIVO: 10,000+ views por post en 7 días

Proporciona:
1. 5 formatos de contenido comprobados en {niche}
2. Hooks que funcionan (primeras 3 segundos)
3. Trending sounds/music por plataforma
4. Hashtag strategy (cuáles generan reach)
5. Horarios óptimos de publicación
6. Calendario de 7 días (qué publicar cada día)
7. Métricas de éxito (engagement rate, saves, shares)
8. Sistema de feedback loop (qué ajustar según datos)

Sé ESPECÍFICO con ejemplos reales."""
            }]
        )

        return {
            "niche": niche,
            "platforms": platforms,
            "daily_volume": volume_per_day,
            "strategy": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def volume_vs_quality_analysis(self, client_account: dict) -> dict:
        """
        Analiza si es mejor estrategia de volumen o calidad
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system="""Analiza estrategias de marketing.
Volumen = muchos posts, menos calidad, mayor reach
Calidad = pocos posts, alta calidad, mejor engagement y conversión

Decide cuál es óptima según datos.""",
            messages=[{
                "role": "user",
                "content": f"""Datos de cuenta:
{json.dumps(client_account, indent=2)}

Analiza:
1. Engagement rate actual (comentarios, likes, shares)
2. Conversion rate (clics → compras)
3. Cost per result
4. Audience quality
5. Competencia en nicho

Recomendación:
- 100% VOLUMEN: Si engagement < 2% y CPM bajo
- 100% CALIDAD: Si engagement > 5% y costo permite
- HÍBRIDO: Mezcla óptima

Proporciona plan detallado de implementación."""
            }]
        )

        return {
            "account": client_account.get("name"),
            "analysis": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def sales_automation_strategy(self, company: dict) -> dict:
        """
        Estrategia de ventas y administración automatizada
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2500,
            system="""Eres experto en automatización de ventas y gestión empresarial.
Conoces Sistema 180 completamente.
Creas sistemas que escalan sin intervención humana.""",
            messages=[{
                "role": "user",
                "content": f"""EMPRESA: {company.get('name')}
SERVICIOS: {', '.join(company.get('services', []))}
EQUIPO: {company.get('team_size')} personas
OBJETIVO: Automatización completa de ventas

Crea un sistema de:
1. Lead qualification automática (scoring)
2. Secuencias de email/WhatsApp automáticas
3. Calendario de seguimiento (día 1, 3, 7, 14, 30)
4. Reconversión de leads fríos
5. Upsell automático
6. Sistema de referrals
7. Dashboard de métricas en tiempo real
8. Alertas de oportunidades perdidas

Integra con:
- Telegram bot
- Notion (CRM)
- Meta Ads (prospecting)
- Email (Gmail)
- Instagram (DMs)

Formato: Plan de implementación con roles específicos."""
            }]
        )

        return {
            "company": company.get("name"),
            "automation_plan": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def autonomous_prospecting_strategy(self, target_audience: dict) -> dict:
        """
        Estrategia de prospecting autónomo por Instagram
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2500,
            system="""Eres experto en prospecting automático.
Creas sistemas que buscan, calificан y contactan leads sin intervención.
Conoces Instagram API, growth hacking y psicología de ventas.""",
            messages=[{
                "role": "user",
                "content": f"""TARGET AUDIENCE:
{json.dumps(target_audience, indent=2)}

Crea un sistema autónomo de prospecting que:

1. BÚSQUEDA (Instagram):
   - Hashtags a monitorear
   - Palabras clave en bio
   - Ubicación geográfica
   - Rango de followers
   - Engagement mínimo

2. FILTRADO (Machine learning):
   - Scoring de lead (0-100)
   - Probabilidad de conversión
   - Budget estimado
   - Fit con servicios

3. CONTACTO (Automático):
   - Primer DM personalizado
   - Hooks psicológicos
   - Call to action específico
   - Timing óptimo

4. SEGUIMIENTO:
   - Secuencia de mensajes
   - Reconversión si no responde
   - Variación de mensajes

5. INTEGRACIÓN:
   - Guardar en Notion
   - Crear tarea en bot
   - Notificar a equipo en Slack
   - Track de conversión

Plan detallado con ejemplos reales de mensajes."""
            }]
        )

        return {
            "target_audience": target_audience.get("description"),
            "prospecting_plan": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def sistema_180_comprehensive_strategy(self) -> dict:
        """
        Estrategia completa de Sistema 180 (7 patas + automatización)
        """
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system="""Conoces Sistema 180 perfectamente.
7 patas: Webs, Recepcionista IA, Afiliación, Marketplace, Avatares IA, Marca personal, Trading bots.
Creas planes de scaling exponencial.""",
            messages=[{
                "role": "user",
                "content": """SISTEMA 180 - ESTRATEGIA DE MULTIPLICACIÓN

Análisis actual:
- Situación: Early stage, 50 clientes en 40 días objetivo
- Stack: Telegram bot, Meta Ads, Notion, n8n, Vercel, Railway
- Equipo: 2 personas (Ares + José María)

Necesito plan de:

1. PRÓXIMAS 30 DÍAS (Sprint de scaling):
   - Qué priorizar (máximo 3 cosas)
   - Roles específicos (quién hace qué)
   - Métricas de éxito diarias
   - Puntos de parada (si no funciona)

2. AUTOMATIZACIÓN TOTAL:
   - Qué se puede automatizar HOY
   - Qué se automatiza en semana 2
   - Qué se automatiza en semana 4
   - Proceso 100% autónomo mes 2

3. SISTEMA DE INGRESOS (7 patas):
   - Ingresos recurrentes vs puntuales
   - Margen por pata
   - ROI por canal de adquisición
   - LTV (lifetime value) de cliente

4. ESTRUCTURA OPERATIVA:
   - SOP para cada proceso crítico
   - Checklists automáticas en Telegram
   - Dashboard de alertas
   - Métricas por proyecto

5. CRECIMIENTO EXPONENCIAL:
   - Estrategia de virality (contenido Ares)
   - Affiliate network (programa de referrals)
   - Product market fit (qué vende mejor)
   - Retention (cómo retener clientes)

6. BOT TELEGRAM MAESTRO:
   - Comandos por rol (equipo, clientes, partners)
   - Control remoto de sistemas (Notion, n8n, etc)
   - Alertas inteligentes
   - Reportes automáticos

Plan ejecutable mañana mismo."""
            }]
        )

        return {
            "plan": response.content[0].text,
            "created_at": datetime.now().isoformat()
        }

    def get_strategic_advice(self, query: str) -> str:
        """
        Obtén consejo estratégico conversacional
        """
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            system="""Eres el Strategic Brain de Sistema 180.
Experto en marketing, ventas, automatización y negocios.
Conoces TODO sobre Sistema 180.
Eres directo, práctico y orientado a resultados.
Das consejos que se pueden ejecutar HOY.

Si el usuario pide ejecutar algo desde el bot, lo proporciona en formato de comando.""",
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def save_strategy(self, name: str, strategy_type: str, content: dict):
        """Guarda una estrategia para reutilizar"""
        self.strategies[strategy_type].append({
            "name": name,
            "content": content,
            "created_at": datetime.now().isoformat()
        })

    def export_all_strategies(self) -> str:
        """Exporta todas las estrategias como JSON"""
        return json.dumps({
            "strategies": self.strategies,
            "campaigns": self.campaigns,
            "roi_data": self.roi_data,
            "exported_at": datetime.now().isoformat()
        }, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────
# FUNCIONES DE UTILIDAD
# ─────────────────────────────────────────────────────────

def create_strategic_brain() -> StrategicBrain:
    """Factory para crear el brain"""
    return StrategicBrain()


def quick_strategy(command: str) -> str:
    """Estrategia rápida sin crear instancia"""
    brain = StrategicBrain()
    return brain.get_strategic_advice(command)


if __name__ == "__main__":
    brain = StrategicBrain()

    print("\n" + "="*80)
    print("🧠 STRATEGIC BRAIN — Sistema 180")
    print("="*80 + "\n")

    # Ejemplo 1: Multiplicación de presupuesto
    print("📊 Análisis: 100€ → 1000€")
    result = brain.analyze_budget_multiplication(100, 10, "meta_ads")
    print(f"Estrategia:\n{result['strategy']}\n")

    # Ejemplo 2: Contenido viral
    print("\n🎬 Estrategia de contenido viral")
    result = brain.generate_viral_content_strategy("negocios locales", ["instagram", "tiktok"], 5)
    print(f"Plan:\n{result['strategy']}\n")

    # Ejemplo 3: Sistema 180 completo
    print("\n🚀 Plan Sistema 180 Completo")
    result = brain.sistema_180_comprehensive_strategy()
    print(f"Plan:\n{result['plan']}\n")

    print("\n✅ Strategic Brain listo. Úsalo desde el bot Telegram.")
