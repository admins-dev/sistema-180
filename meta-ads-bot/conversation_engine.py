"""
conversation_engine.py — Sistema 180
Motor de conversación con contexto por usuario.
Mantiene histórico de mensajes y genera respuestas naturales.
"""
import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_URL = "https://api.anthropic.com/v1/messages"


class ConversationEngine:
    """Maneja contexto conversacional por usuario con histórico."""

    def __init__(self):
        self.user_contexts: dict[int, list] = {}  # {user_id: [msg1, msg2, ...]}

    def _get_context_window(self, user_id: int, window_size: int = 10) -> list:
        """Obtiene últimos N mensajes para contexto."""
        if user_id not in self.user_contexts:
            return []
        return self.user_contexts[user_id][-window_size:]

    async def process_user_message(
        self, user_id: int, message: str
    ) -> dict:
        """
        Procesa mensaje del usuario manteniendo contexto.

        Returns:
            {
                'intent': str,
                'response': str (natural language),
                'needs_clarification': bool,
                'next_question': str or None,
                'params': dict,
                'confidence': float
            }
        """
        # Inicializar contexto del usuario si no existe
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []

        # Agregar mensaje del usuario al contexto
        self.user_contexts[user_id].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })

        # Obtener últimos 10 mensajes para contexto
        context_messages = self._get_context_window(user_id, window_size=10)

        # Procesar con Claude manteniendo contexto
        result = await self._process_with_claude(
            message=message,
            context_history=context_messages,
            user_id=user_id
        )

        # Agregar respuesta de la IA al contexto
        self.user_contexts[user_id].append({
            'role': 'assistant',
            'content': result.get('response', ''),
            'timestamp': datetime.now().isoformat()
        })

        return result

    async def _process_with_claude(
        self, message: str, context_history: list, user_id: int
    ) -> dict:
        """Usa Claude para interpretar intent con contexto conversacional."""
        if not ANTHROPIC_API_KEY:
            return {
                'intent': 'error',
                'response': 'Error: API no configurada',
                'needs_clarification': False,
                'params': {},
                'confidence': 0.0
            }

        system_prompt = """Eres un asistente conversacional para un bot de Meta Ads de Sistema 180.
Tu trabajo es:
1. Entender la intención del usuario en lenguaje natural
2. Hacer preguntas aclaratorias si falta información
3. Responder de forma amigable, SIN JSON, en español

INTENTS disponibles:
- "get_metrics": usuario pide datos/métricas/estadísticas
- "create_campaign": usuario quiere crear campaña
- "pause_campaign": usuario quiere pausar campaña
- "report": usuario pide reporte/resumen
- "list_campaigns": usuario quiere listar campañas
- "greeting": saludo del usuario
- "unknown": no encaja en otras categorías

REGLAS:
1. Si falta información (nombre, presupuesto, etc.), responde preguntando de forma natural.
   NO devuelvas error, pregunta amigablemente.
   Ej: "¿Cuál sería el presupuesto para la campaña? (entre 1 y 50 euros)"

2. Si la información es clara, responde normalmente y extrae params.

3. Responde SIEMPRE en lenguaje natural, conversacional.

4. Responde con un JSON valido con esta estructura:
{
  "intent": "...",
  "response": "tu respuesta conversacional aquí",
  "needs_clarification": true/false,
  "next_question": "la pregunta concreta si needs_clarification es true, o null",
  "params": {
    "nombre": "...",
    "presupuesto": 50.5,
    "campaign_id": "...",
    etc.
  },
  "confidence": 0.0-1.0
}

EJEMPLOS:

Usuario: "Cuántos clientes tengo?"
Bot responde:
{
  "intent": "get_metrics",
  "response": "Voy a traerte tus métricas de clientes. Dame un momento...",
  "needs_clarification": false,
  "next_question": null,
  "params": {},
  "confidence": 0.95
}

Usuario: "Lanza una campaña"
Bot responde:
{
  "intent": "create_campaign",
  "response": "Claro, voy a crear una campaña. Primero necesito algunos datos:\n¿Cuál sería el nombre de la campaña?",
  "needs_clarification": true,
  "next_question": "¿Cuál es el nombre de la campaña?",
  "params": {},
  "confidence": 0.85
}

Usuario: "Una campaña para peluquerías con 100 euros"
Bot responde:
{
  "intent": "create_campaign",
  "response": "Perfecto, voy a crear una campaña para peluquerías con 100 euros. Un momento...",
  "needs_clarification": false,
  "next_question": null,
  "params": {
    "nombre": "Campaña peluquerías",
    "presupuesto": 100
  },
  "confidence": 0.90
}
"""

        # Construir mensajes para Claude (sin el mensaje actual)
        messages_for_claude = []
        for msg in context_history[:-1]:  # Excluir el último que es el actual
            messages_for_claude.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Agregar el mensaje actual del usuario
        messages_for_claude.append({
            'role': 'user',
            'content': message
        })

        try:
            response = requests.post(
                API_URL,
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 512,
                    "system": system_prompt,
                    "messages": messages_for_claude,
                },
                timeout=10,
            )
            response.raise_for_status()
            raw = response.json()["content"][0]["text"].strip()
            result = json.loads(raw)

            # Validar estructura
            result.setdefault('intent', 'unknown')
            result.setdefault('response', 'No entendí bien, ¿puedes reformular?')
            result.setdefault('needs_clarification', False)
            result.setdefault('next_question', None)
            result.setdefault('params', {})
            result.setdefault('confidence', 0.0)

            return result

        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error procesando con Claude: {e}")
            return {
                'intent': 'error',
                'response': 'Disculpa, hubo un error. Intenta de nuevo.',
                'needs_clarification': False,
                'next_question': None,
                'params': {},
                'confidence': 0.0
            }

    def clear_user_context(self, user_id: int):
        """Limpia el contexto de un usuario (ej: logout)."""
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
            logger.info(f"Contexto de usuario {user_id} limpiado")


# Instancia global singleton
_conversation_engine = None


def get_conversation_engine() -> ConversationEngine:
    """Obtiene la instancia global del motor de conversación."""
    global _conversation_engine
    if _conversation_engine is None:
        _conversation_engine = ConversationEngine()
    return _conversation_engine


if __name__ == "__main__":
    import asyncio

    async def test():
        engine = get_conversation_engine()

        # Simular conversación
        test_messages = [
            "Hola, cuántas campañas tengo?",
            "Crea una nueva",
            "Para peluquerías",
            "Con 25 euros",
        ]

        for msg in test_messages:
            result = await engine.process_user_message(123, msg)
            print(f"\n📝 User: {msg}")
            print(f"🤖 Intent: {result['intent']}")
            print(f"💬 Response: {result['response']}")
            if result['needs_clarification']:
                print(f"❓ Next Q: {result['next_question']}")

    asyncio.run(test())
