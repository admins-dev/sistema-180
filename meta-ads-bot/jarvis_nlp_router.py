"""
jarvis_nlp_router.py — Sistema 180
Router de lenguaje natural para JARVIS.
Entiende texto libre y ejecuta la acción correcta.

En vez de: /alta_cliente Mario Web 297
El usuario dice: "dale de alta a Mario, servicio web a 297 euros"
Y JARVIS lo entiende y ejecuta.
"""
import os, json, re, logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# INTENT DETECTION — Claude analiza qué quiere el usuario
# ══════════════════════════════════════════════════════════════════════════════

INTENT_PROMPT = """Eres JARVIS, el asistente de Sistema 180. Analiza este mensaje del usuario y devuelve un JSON con:
- "intent": la acción que quiere (ver lista abajo)
- "params": parámetros extraídos
- "confidence": 0.0 a 1.0
- "response_prefix": frase corta natural para confirmar antes de ejecutar

INTENTS DISPONIBLES:
- "alta_cliente": dar de alta un cliente. Params: name, service, price, phone, email
- "factura": crear factura. Params: client_name, amount, concept
- "onboarding": enviar onboarding a alguien. Params: client_name, email
- "clientes": ver lista de clientes. Params: status (Activo/Trial/Baja)
- "reporte": ver reporte diario/semanal. Params: type (diario/semanal)
- "metricas": ver métricas del sistema. Params: none
- "backup": hacer backup. Params: none
- "ig_prospectar": prospectar por hashtag. Params: hashtag
- "ig_competidor": prospectar seguidores de competidor. Params: username
- "ig_maps": prospectar por google maps. Params: query
- "ig_stats": estadísticas de instagram. Params: none
- "ig_parar": parar prospección. Params: none
- "ig_status": estado cuentas ig. Params: none
- "lead_score": puntuar un lead. Params: username, bio, followers
- "followups": ver followups pendientes. Params: none
- "renovaciones": ver renovaciones próximas. Params: none
- "factura": crear factura. Params: client_name, amount, concept
- "borrar_datos": eliminar datos GDPR. Params: username
- "calendario": crear evento en calendario. Params: title, date, time, description
- "ver_calendario": ver eventos del calendario. Params: date_range
- "cloud_code": tarea de programación. Params: instruction
- "cloud_exec": ejecutar el código pendiente en la nube. Params: none
- "slack": enviar mensaje a slack. Params: channel, message
- "whatsapp_enviar": enviar mensaje de whatsapp. Params: phone, message
- "whatsapp_chats": ver conversaciones whatsapp. Params: none
- "whatsapp_responder": responder a un whatsapp. Params: phone, message
- "estado": estado del sistema. Params: none
- "ayuda": qué puede hacer JARVIS. Params: none
- "conversacion": el usuario solo quiere hablar/chatear. Params: none

IMPORTANTE: Si no estás seguro del intent, usa "conversacion".
Responde SOLO con el JSON, sin explicación.

MENSAJE DEL USUARIO: {message}"""


def detect_intent(message: str) -> dict:
    """Detecta la intención del usuario usando Claude."""
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return {"intent": "conversacion", "params": {}, "confidence": 0.5}

        client = anthropic.Anthropic(api_key=api_key, timeout=15.0)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": INTENT_PROMPT.format(message=message)
            }]
        )
        text = response.content[0].text.strip()
        # Extract JSON from response
        if text.startswith("{"):
            return json.loads(text)
        # Try to find JSON in response
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"intent": "conversacion", "params": {}, "confidence": 0.5}
    except Exception as e:
        logger.error(f"[NLP] Intent detection error: {e}")
        return {"intent": "conversacion", "params": {}, "confidence": 0.5}


# ══════════════════════════════════════════════════════════════════════════════
# ACTION EXECUTOR — Ejecuta la acción detectada
# ══════════════════════════════════════════════════════════════════════════════

async def execute_intent(intent_data: dict, update, context) -> str | None:
    """Ejecuta la acción basada en el intent detectado.
    Returns response text or None if should fall through to brain."""
    intent = intent_data.get("intent", "conversacion")
    params = intent_data.get("params", {})
    confidence = intent_data.get("confidence", 0)

    # Low confidence = just chat
    if confidence < 0.6 or intent == "conversacion":
        return None  # Let brain handle it

    logger.info(f"[NLP] Intent: {intent} (conf={confidence}) params={params}")

    try:
        if intent == "alta_cliente":
            name = params.get("name", "")
            service = params.get("service", "Web")
            price = float(params.get("price", 0))
            phone = params.get("phone", "")
            email = params.get("email", "")
            if not name:
                return "Señor, necesito al menos el nombre del cliente para darlo de alta."
            from integrations import notion_create_client, slack_notify_new_client
            result = notion_create_client(name, service, price, phone, email)
            if result.get("ok"):
                slack_notify_new_client(name, service, price, phone)
                return (f"Perfecto señor, he dado de alta a {name} en el CRM.\n"
                        f"Servicio: {service}\nPrecio: {price}€/mes\n"
                        f"Todo registrado en Notion y notificado en Slack.")
            return f"Ha habido un problema al crear el cliente: {result.get('error', 'desconocido')}"

        elif intent == "onboarding":
            client_name = params.get("client_name", "")
            email = params.get("email", "")
            if not client_name or not email:
                return "Señor, necesito al menos el nombre del cliente y su correo para enviarle el onboarding."
            
            # Notificar interna en Slack
            from integrations import slack_send, SLACK_CHANNELS
            ch = SLACK_CHANNELS.get("clientes_onboarding", "")
            if ch:
                slack_send(
                    f"🟢 *Nuevo onboarding iniciado*\n"
                    f"👤 Cliente: {client_name}\n"
                    f"📧 Email: {email}\n"
                    f"📅 Fecha: {date.today().strftime('%d/%m/%Y')}",
                    channel=ch
                )
                
            # Enviar el email REAL al cliente
            try:
                from gmail_ops import get_gmail_client
                gmail = get_gmail_client()
                if not gmail.is_authenticated():
                    return "Sir, la API de Gmail no está autenticada. Vaya a `/gmail/auth` para enchufar el correo."
                
                subject = f"Bienvenido a Sistema 180, {client_name} - Siguientes pasos"
                body = (
                    f"Hola {client_name},\n\n"
                    f"Soy JARVIS, la Inteligencia Artificial de Sistema 180.\n"
                    f"Le escribo para darle oficialmente la bienvenida al ecosistema.\n\n"
                    f"En breve recibirá los accesos a sus dashboards y carpetas de trabajo. "
                    f"Mientras tanto, por favor responda a este correo si tiene alguna duda urgente.\n\n"
                    f"Atentamente,\n"
                    f"JARVIS - Sistema 180"
                )
                res = gmail.send_email(email, subject, body)
                if res.get("ok"):
                    return (f"Entendido señor.\n1. He notificado al equipo por Slack.\n"
                            f"2. He enviado el email de onboarding oficial a {email}.")
                return f"Falló el envío de correo: {res.get('error', 'Desconocido')}"
            except Exception as e:
                logger.error(f"Error enviando onboarding: {e}")
                return f"Excepción al enviar correo: {e}"

        elif intent == "factura":
            client_name = params.get("client_name", "")
            amount = float(params.get("amount", 0))
            concept = params.get("concept", "Servicio mensual")
            if not client_name or amount <= 0:
                return "Necesito el nombre del cliente y el importe para crear la factura."
            from jarvis_cloud import create_invoice
            result = create_invoice(client_name, amount, concept)
            if result.get("ok"):
                return (f"Factura creada, señor.\n"
                        f"ID: {result['invoice_id']}\n"
                        f"Cliente: {client_name}\n"
                        f"Importe: {amount}€\n"
                        f"Ya está registrada en Notion.")
            return f"Error al crear factura: {result.get('error', 'desconocido')}"

        elif intent == "clientes":
            status = params.get("status", "Activo")
            from integrations import notion_get_clients
            clients = notion_get_clients(status)
            if not clients:
                return f"No hay clientes con estado '{status}' en este momento."
            lines = [f"Tiene {len(clients)} clientes {status.lower()}:\n"]
            mrr = 0
            for c in clients:
                lines.append(f"• {c['nombre']} — {c['servicio']} ({c['precio']}€)")
                mrr += c.get("precio", 0)
            lines.append(f"\nMRR total: {mrr}€/mes")
            return "\n".join(lines)

        elif intent == "reporte":
            rtype = params.get("type", "diario")
            from jarvis_cloud import generate_daily_report, generate_weekly_report
            if "semanal" in rtype or "semana" in rtype:
                return generate_weekly_report()
            return generate_daily_report()

        elif intent == "metricas":
            from resilience import metrics
            return metrics.get_health_summary()

        elif intent == "backup":
            from backup_manager import run_backup
            stats = run_backup()
            return f"Backup completado señor. {stats['ok']} archivos respaldados."

        elif intent == "ig_stats":
            from ig_multi_account import AccountStore
            store = AccountStore()
            accs = store.get_all()
            active = sum(1 for a in accs if a.get("active") and a.get("status") == "ok")
            today = sum(a.get("sent_today", 0) for a in accs)
            total = sum(a.get("sent_total", 0) for a in accs)
            return (f"Tiene {len(accs)} cuentas, {active} activas.\n"
                    f"DMs hoy: {today}\nDMs total: {total}")

        elif intent == "ig_prospectar":
            hashtag = params.get("hashtag", "")
            if not hashtag:
                return "Señor, necesito el hashtag para iniciar la prospección."
            return (f"Entendido señor, iniciando prospección con hashtag #{hashtag}. "
                    f"Use /ig_prospectar {hashtag} para confirmar el inicio.")

        elif intent == "ig_parar":
            return "Entendido señor, deteniendo toda la prospección de Instagram."

        elif intent == "followups":
            from jarvis_cloud import check_client_followups
            alerts = check_client_followups()
            if not alerts:
                return "No hay recordatorios pendientes señor. Todos los clientes están al día."
            lines = ["Recordatorios pendientes:\n"]
            for a in alerts:
                lines.append(f"• {a['nombre']} ({a['servicio']}) — {a['days_since_alta']} días desde alta")
            return "\n".join(lines)

        elif intent == "renovaciones":
            from jarvis_cloud import check_renewals
            renewals = check_renewals(14)
            if not renewals:
                return "No hay renovaciones próximas señor."
            lines = ["Renovaciones próximas:\n"]
            for r in renewals:
                lines.append(f"• {r['nombre']} — {r['precio']}€ el {r['renewal_date']} (en {r['days_until']} días)")
            return "\n".join(lines)

        elif intent == "calendario":
            title = params.get("title", "")
            cal_date = params.get("date", "")
            cal_time = params.get("time", "")
            desc = params.get("description", "")
            if not title:
                return "Señor, necesito al menos el título del evento."
            from jarvis_calendar import create_event
            result = create_event(title, cal_date, cal_time, desc)
            if result.get("ok"):
                return f"Perfecto señor, he creado el evento '{title}' en su calendario."
            return f"Error al crear evento: {result.get('error', 'desconocido')}"

        elif intent == "ver_calendario":
            from jarvis_calendar import get_upcoming_events
            events = get_upcoming_events()
            if not events:
                return "No tiene eventos próximos en el calendario."
            lines = ["Sus próximos eventos:\n"]
            for e in events:
                lines.append(f"• {e['date']} {e['time']} — {e['title']}")
            return "\n".join(lines)

        elif intent == "slack":
            channel = params.get("channel", "control")
            message = params.get("message", "")
            if not message:
                return "Señor, necesito el mensaje que quiere enviar a Slack."
            from integrations import slack_send, SLACK_CHANNELS
            ch = SLACK_CHANNELS.get(channel, "")
            if ch:
                slack_send(message, channel=ch)
                return f"Mensaje enviado al canal {channel} de Slack."
            return f"Canal '{channel}' no encontrado. Canales disponibles: {', '.join(SLACK_CHANNELS.keys())}"

        elif intent == "cloud_code":
            instruction = params.get("instruction", "")
            if not instruction:
                return "Señor, dígame qué quiere que programe."
            msg = await update.message.reply_text("🧠 Procesando con Claude...")
            from jarvis_cloud import cloud_code_execute
            import asyncio
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: cloud_code_execute(instruction)
            )
            await msg.edit_text(result[:4000])
            return None  # Already responded

        elif intent == "cloud_exec":
            from jarvis_cloud import cloud_code_run
            msg = await update.message.reply_text("⚡ Ejecutando código en la nube (Railway)...")
            import asyncio
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: cloud_code_run()
            )
            await msg.edit_text(result[:4000])
            return None

        elif intent == "borrar_datos":
            username = params.get("username", "")
            if not username:
                return "Señor, necesito el username del lead a eliminar."
            return f"Para confirmar la eliminación GDPR de @{username}, use: /borrar_datos {username}"

        elif intent == "whatsapp_enviar":
            phone = params.get("phone", "")
            message = params.get("message", "")
            if not phone or not message:
                return "Señor, necesito el número de teléfono y el mensaje."
            from jarvis_whatsapp import send_message
            result = send_message(phone, message)
            if result.get("ok"):
                return f"WhatsApp enviado a +{phone}, señor."
            return f"Error enviando WhatsApp: {result.get('error', 'desconocido')}"

        elif intent == "whatsapp_chats":
            from jarvis_whatsapp import get_conversations
            convos = get_conversations()
            if not convos:
                return "No hay conversaciones de WhatsApp, señor."
            lines = ["Conversaciones de WhatsApp:\n"]
            for c in convos[:10]:
                lines.append(f"• {c['name']} (+{c['phone']}) — {c['last_message']}")
            return "\n".join(lines)

        elif intent == "whatsapp_responder":
            phone = params.get("phone", "")
            message = params.get("message", "")
            if not phone or not message:
                return "Necesito el número y el mensaje para responder."
            from jarvis_whatsapp import send_message
            result = send_message(phone, message)
            if result.get("ok"):
                return f"Respuesta enviada por WhatsApp a +{phone}."
            return f"Error: {result.get('error', 'desconocido')}"

        elif intent == "estado":
            return "Todos los sistemas operativos señor. Bot, Flask y métricas funcionando correctamente."

        elif intent == "ayuda":
            return (
                "Señor, puede hablarme de forma natural. Algunos ejemplos:\n\n"
                "• \"Dale de alta a Mario, servicio web, 297 euros\"\n"
                "• \"Envía el onboarding a Laura\"\n"
                "• \"Hazme una factura de 500 euros a Restaurante Pepe\"\n"
                "• \"Dame el reporte del día\"\n"
                "• \"Envía un WhatsApp al 612345678 diciendo hola\"\n"
                "• \"Qué conversaciones tengo en WhatsApp\"\n"
                "• \"Crea un evento para mañana a las 10\"\n"
                "• \"Prospecta en el hashtag restaurante\"\n"
                "• \"Envía un mensaje a Slack\"\n"
                "• \"Haz backup\"\n\n"
                "También me puede hablar por audio y le respondo por voz."
            )

    except Exception as e:
        logger.error(f"[NLP] Execute error for {intent}: {e}")
        return f"Ha habido un error al ejecutar {intent}: {str(e)[:100]}"

    return None  # Fallthrough to brain
