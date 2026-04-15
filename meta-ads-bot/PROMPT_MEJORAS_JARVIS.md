# PROMPT PARA CLAUDE CODE — Mejora Completa del Sistema JARVIS

Lee CLAUDE.md primero para el contexto completo del sistema y las reglas de seguridad.

---

## MISIÓN

Mejora TODO el sistema JARVIS de Sistema 180. Mantén INTACTA toda la lógica de seguridad existente en `system_protection.py` y `jarvis_architecture.py`. No borres ni debilites ninguna protección.

---

## MEJORAS REQUERIDAS

### 1. JARVIS FRONTEND (`templates/jarvis.html`)

**Problemas actuales:**
- La UI es funcional pero básica — necesita sentirse más premium, como el JARVIS real de Iron Man
- El layout de 3 columnas se rompe en pantallas pequeñas (no es responsive)
- Los paneles laterales tienen texto muy pequeño (0.34rem-0.44rem) — difícil de leer
- No hay indicador visual cuando Perplexity busca en internet
- No hay historial de chat persistente (se pierde al recargar)
- La esfera 3D no reacciona al estado de "searching" (solo idle/listening/thinking/speaking)
- Falta panel de seguridad que muestre las acciones pendientes/aprobadas del SecurityGate
- Los voice wave bars son muy básicos (solo barras random)
- No hay tema oscuro/claro toggle
- No muestra las imágenes generadas con tamaño adecuado en el chat
- Falta un botón para limpiar el chat (/api/clear existe pero no hay UI)
- El botón de micrófono no tiene feedback visual cuando está procesando

**Mejoras:**
- Hacer responsive (mobile-first)
- Añadir estado "searching" (color morado/violeta) para cuando Perplexity busca
- Panel de SecurityGate en vivo (acciones pendientes, aprobadas, rechazadas)
- Mejorar voice wave con visualización real del audio (usar analyser del AudioContext que ya existe)
- Añadir botón de limpiar chat
- Guardar historial en localStorage
- Mejorar legibilidad de paneles sin perder estética cyberpunk
- Animación de carga para respuestas (typing indicator)
- Mostrar timestamp en cada mensaje

### 2. JARVIS SERVER (`jarvis_server.py`)

**Problemas actuales:**
- La Gemini API key está leaked/bloqueada — el fallback a Groq funciona pero la lógica es Gemini-first
- El endpoint `/api/tts` crea un nuevo event loop cada request (`asyncio.new_event_loop()`) — fuga de recursos
- No hay rate limiting en ningún endpoint (cualquiera puede spammear)
- No hay autenticación — los endpoints están abiertos (a diferencia de `server.py` que tiene `require_api_key`)
- La memoria del chat (`_memory`) crece sin límite en RAM — no hay persistencia
- El sistema de búsqueda (`_needs_search`) es muy básico — solo keywords hardcodeadas
- No hay endpoint para ver el estado del SecurityGate
- No hay manejo de errores granular — todos los errores devuelven genérico
- Bare `except:` en múltiples lugares (líneas 88, 108) — oculta errores reales
- El kill switch existe (`/api/killswitch`) pero no hay confirmación ni autenticación

**Mejoras:**
- Hacer Groq el primario (funciona) y Gemini el fallback (cuando regeneren la key)
- Reutilizar un solo event loop para Edge TTS (o usar asyncio.run)
- Añadir rate limiting (flask-limiter ya está en requirements.txt)
- Añadir autenticación básica (token en header o cookie de sesión)
- Persistir memoria del chat en archivo JSON o SQLite
- Mejorar detección de búsqueda con NLP (usar el módulo nlp.py que ya existe)
- Endpoint `/api/security` para mostrar SecurityGate status
- Capturar excepciones específicas, no bare except
- Kill switch debe requerir confirmación doble

### 3. BRAIN.PY (`brain.py`)

**Problemas actuales:**
- Memoria en RAM (`_memory: dict`) — se pierde al reiniciar
- `_gemini()` usa `gemini-2.0-flash` (viejo) — debería usar `gemini-3.1-pro-preview` como jarvis_server
- La función `_gemini()` construye la conversación como texto plano en vez de usar el formato nativo de Gemini (systemInstruction + contents)
- No hay límite de tokens por conversación completa — puede exceder el context window
- No hay resumen de conversación antigua (cuando se llega a MAX_MEMORY=12, simplemente trunca)
- La función `chat()` duplica lógica de `think()` — debería refactorizarse

**Mejoras:**
- Persistir memoria en SQLite o JSON (directorio `~/.jarvis/data/`)
- Actualizar modelo Gemini a `gemini-3.1-pro-preview`
- Usar formato nativo Gemini para conversación (systemInstruction + contents)
- Implementar resumen de conversación cuando se llega al límite
- Unificar `chat()` y `think()` en una sola interfaz limpia
- Añadir tracking de tokens usados

### 4. NLP.PY (`nlp.py`)

**Problemas actuales:**
- `_call_gemini()` usa `gemini-2.0-flash` — actualizar a versión actual
- El keyword fallback es limitado — solo 5 intents
- No detecta intents de JARVIS (modo conversación general, preguntas estratégicas, etc.)
- No tiene cache de intents frecuentes
- No hay métricas de qué provider responde más rápido/mejor

**Mejoras:**
- Actualizar modelo Gemini
- Añadir más intents: `strategy_question`, `general_chat`, `search_web`, `generate_image`
- Cache de intents recientes en memoria
- Tracking de latencia por provider

### 5. BOT.PY (`bot.py`)

**Problemas actuales:**
- El voice handler descarga a `/tmp/voice_...` — no funciona bien en Windows
- `handle_text()` no integra el SecurityGate de `jarvis_architecture.py`
- Las acciones de Meta Ads en `handle_text()` se ejecutan sin pasar por SecurityGate
- No hay comando para ver/aprobar/rechazar decisiones pendientes del SecurityGate
- No hay comando `/jarvis` para activar modo JARVIS desde Telegram
- `import requests` dentro de funciones (líneas 202, 232, 257) — debería estar arriba

**Mejoras:**
- Usar `tempfile.mkstemp()` para archivos temporales (cross-platform)
- Integrar SecurityGate en el flujo conversacional — toda acción de Meta Ads pasa por el gate
- Añadir comandos `/pendientes`, `/aprobar <id>`, `/rechazar <id>`
- Añadir comando `/jarvis` que cambia la personalidad del brain a modo JARVIS (usando jarvis_server.JARVIS_SYSTEM)
- Mover imports al top del archivo

### 6. INTEGRACIÓN JARVIS ↔ BOT

**Problema:** JARVIS web (jarvis_server.py) y el bot Telegram (bot.py) son sistemas completamente separados. No comparten:
- Memoria de conversación
- SecurityGate (cada uno tiene su instancia)
- Estado del sistema

**Mejora:**
- Crear un módulo `shared_state.py` que centralice:
  - Singleton de SecurityGate (una sola instancia para todo)
  - Memoria de conversación persistente (SQLite)
  - Estado del sistema compartido
- Tanto `jarvis_server.py` como `bot.py` importan de `shared_state.py`

---

## REGLAS ABSOLUTAS

1. **NO TOCAR la lógica de seguridad** — solo puedes AMPLIAR, nunca reducir
2. **NO eliminar archivos** existentes
3. **NO cambiar los puertos** (5180 para JARVIS, 5000 para server)
4. **NO exponer a internet** — todo sigue siendo localhost
5. **Solo [a-z0-9_]** en nombres de CommandHandler de Telegram
6. **NO usar PyAutoGUI** ni módulos bloqueados por system_protection
7. **Mantener el cascade de providers**: siempre tener fallback
8. **Commits pequeños** — un archivo o feature por commit

---

## ORDEN DE EJECUCIÓN SUGERIDO

1. `shared_state.py` [NUEVO] — Centralizar estado compartido
2. `brain.py` — Refactorizar memoria y providers
3. `nlp.py` — Actualizar modelos y añadir intents
4. `jarvis_server.py` — Seguridad + TTS fix + nuevos endpoints
5. `bot.py` — Integrar SecurityGate + nuevos comandos
6. `templates/jarvis.html` — UI premium + responsive + SecurityGate panel
7. Testear todo end-to-end

---

## VERIFICACIÓN

Después de cada cambio:
1. `python -c "import system_protection"` — debe imprimir protecciones activadas
2. `python -c "from jarvis_architecture import get_jarvis; j=get_jarvis(); print(j.get_summary())"` — debe funcionar
3. `python jarvis_server.py` — debe arrancar en 127.0.0.1:5180 sin errores
4. `python bot.py` — debe conectar a Telegram sin errores
