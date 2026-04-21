"""
Sistema 180 - Pipeline Maestro de Ventas v1.0
Script unificado que ejecuta todo el flujo de prospecting:
1. Buscar leads (Google Maps + emails)
2. Generar DMs personalizados
3. Enviar emails frios
4. Trackear resultados

USO: python sales_pipeline.py [buscar|emails|dm|todo]
"""
import sys
import json
import os
import time

# Imports del proyecto
from config import ACCOUNTS
from brain import generate_dm, generate_followup, generate_reply
from email_marketing import (
    EMAIL_TEMPLATE_1, EMAIL_TEMPLATE_2, 
    send_campaign, save_email_leads, load_email_leads,
    generate_personalized_email
)
from setter_profiles import SETTER_PROFILES, get_bio_text
from catalogo_precios import CATALOGO_LINEA_A, PLAN_CIERRE_9_DIAS
from lead_finder import load_leads, get_unsent_leads

LEADS_FILE = os.path.join(os.path.dirname(__file__), "leads.json")


def mostrar_estado():
    """Muestra el estado actual del pipeline."""
    print("=" * 60)
    print("  SISTEMA 180 - ESTADO DEL PIPELINE DE VENTAS")
    print("=" * 60)
    
    # Leads Instagram
    ig_leads = load_leads()
    ig_unsent = get_unsent_leads()
    print(f"\n  [INSTAGRAM]")
    print(f"    Leads totales: {len(ig_leads)}")
    print(f"    Con Instagram: {len([l for l in ig_leads if l.get('instagram')])}")
    print(f"    DMs pendientes: {len(ig_unsent)}")
    print(f"    DMs enviados: {len([l for l in ig_leads if l.get('dm_sent')])}")
    
    # Leads Email
    email_leads = load_email_leads()
    print(f"\n  [EMAIL]")
    print(f"    Leads con email: {len(email_leads)}")
    print(f"    Emails enviados: {len([l for l in email_leads if l.get('enviado')])}")
    print(f"    Pendientes: {len([l for l in email_leads if not l.get('enviado')])}")
    
    # Setters
    print(f"\n  [SETTERS]")
    for username, profile in SETTER_PROFILES.items():
        print(f"    @{username} ({profile['fullname']}) -> {profile['target_niches'][0]}")
    
    # Cuentas Instagram
    print(f"\n  [CUENTAS IG]")
    for acc in ACCOUNTS:
        print(f"    @{acc['username']} / proxy: {acc['proxy']['server']}")
    
    # Objetivo
    plan = PLAN_CIERRE_9_DIAS
    print(f"\n  [OBJETIVO]")
    print(f"    Meta: {plan['objetivo_total']} EUR antes del {plan['deadline']}")
    print(f"    Dias restantes: 9")
    
    # Productos
    print(f"\n  [PRODUCTOS]")
    for key, tier in CATALOGO_LINEA_A.items():
        print(f"    {tier['nombre']}: {tier['precio']} EUR")


def generar_dms_demo():
    """Genera DMs de prueba para verificar calidad."""
    print("\n" + "=" * 60)
    print("  GENERANDO DMs DE PRUEBA")
    print("=" * 60)
    
    test_leads = [
        {"name": "Peluqueria Vitale Hair", "instagram": "vitalehair",
         "city": "Malaga", "niche": "peluquerias", "rating": 4.7, "reviews": 180},
        {"name": "Restaurante El Pimpi", "instagram": "elpimpi",
         "city": "Malaga", "niche": "restaurantes", "rating": 4.5, "reviews": 3200},
        {"name": "CrossFit Malaga Centro", "instagram": "crossfitmalaga",
         "city": "Malaga", "niche": "gimnasios", "rating": 4.9, "reviews": 95},
        {"name": "Clinica Dental Sonrisa", "instagram": "clinicasonrisa",
         "city": "Malaga", "niche": "clinicas dentales", "rating": 4.8, "reviews": 120},
        {"name": "Abogados Martinez", "instagram": "abogadosmartinez",
         "city": "Malaga", "niche": "abogados", "rating": 4.6, "reviews": 45},
    ]
    
    for lead in test_leads:
        print(f"\n  --- @{lead['instagram']} ({lead['niche']}) ---")
        dm = generate_dm(lead)
        print(f"  DM: {dm}")
        print(f"  Chars: {len(dm)}")


def generar_emails_demo():
    """Genera emails de prueba."""
    print("\n" + "=" * 60)
    print("  GENERANDO EMAILS DE PRUEBA")
    print("=" * 60)
    
    test_leads = [
        {"nombre": "Clinica Dental Sonrisa", "email": "info@clinicasonrisa.es",
         "query": "clinicas dentales", "city": "Malaga"},
        {"nombre": "Restaurante Casa Juan", "email": "reservas@casajuan.es",
         "query": "restaurantes", "city": "Malaga"},
    ]
    
    for lead in test_leads:
        email = EMAIL_TEMPLATE_1.format(
            nombre_negocio=lead["nombre"],
            nicho=lead["query"],
            ciudad=lead["city"]
        )
        print(f"\n  --- {lead['nombre']} ({lead['email']}) ---")
        print(f"  {email[:200]}...")


def plan_diario():
    """Muestra el plan de hoy."""
    print("\n" + "=" * 60)
    print("  PLAN DE HOY")
    print("=" * 60)
    
    plan = PLAN_CIERRE_9_DIAS["plan_diario"]
    for dia, tarea in plan.items():
        marker = ">>" if "hoy" in dia else "  "
        print(f"  {marker} {dia}: {tarea}")


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ["estado"]
    
    command = args[0].lower()
    
    if command == "estado":
        mostrar_estado()
    elif command == "dms":
        generar_dms_demo()
    elif command == "emails":
        generar_emails_demo()
    elif command == "plan":
        plan_diario()
    elif command == "bios":
        print("\n  BIOS DE SETTERS (copiar y pegar en Instagram):")
        for username in SETTER_PROFILES:
            print(f"\n  --- @{username} ---")
            print(f"  {get_bio_text(username)}")
    elif command == "todo":
        mostrar_estado()
        plan_diario()
    else:
        print("  Uso: python sales_pipeline.py [estado|dms|emails|plan|bios|todo]")


if __name__ == "__main__":
    main()
