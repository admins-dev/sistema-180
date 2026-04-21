import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import google.generativeai as genai
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, GEMINI_KEY

app = Flask(__name__)

# Configurar Gemini (El Cerrador / Cualificador)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3.1-pro')

# Configurar Twilio Client para envío proactivo (cuando entra un lead de IG)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None

def send_whatsapp_message(to_number, body_text):
    """JARVIS inicia la conversación proactivamente cuando Ghost Mouse consigue el número"""
    if not twilio_client:
        print("[!] TWILIO CREDENCIALES NO CONFIGURADAS")
        return
    message = twilio_client.messages.create(
        body=body_text,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=f"whatsapp:{to_number}"
    )
    return message.sid

@app.route("/whatsapp-webhook", methods=['POST'])
def whatsapp_reply():
    """Endpoint que recibe las respuestas de los leads por WhatsApp"""
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    
    print(f"[*] Mensaje de WhatsApp recibido de {sender_number}: {incoming_msg}")
    
    # JARVIS Piensa la respuesta para cualificar al prospecto
    prompt = f"""
    Eres JARVIS, el agente de ventas de alta conversión de Sistema 180.
    Tu objetivo es cualificar a este lead y mandarle un enlace de llamada.
    El lead ha escrito: "{incoming_msg}".
    Responde de forma natural, directa, y ofrécele nuestra Fábrica de Contenidos Automática.
    """
    
    response_text = model.generate_content(prompt).text
    
    # Responder por Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    
    return str(resp)

if __name__ == "__main__":
    print("[+] Jarvis WhatsApp Twilio API Iniciado en puerto 5001")
    app.run(host="0.0.0.0", port=5001)
