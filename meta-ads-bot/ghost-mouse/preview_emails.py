"""Preview de la campana de email marketing."""
from email_marketing import EMAIL_TEMPLATE_1, EMAIL_TEMPLATE_2, load_email_leads

leads = load_email_leads()
print(f"Total leads con email: {len(leads)}")
print()

# Preview primer email - peluqueria
lead = leads[0]
email = EMAIL_TEMPLATE_1.format(
    nombre_negocio=lead["nombre"],
    nicho=lead["query"],
    ciudad=lead["city"]
)
print("=== PREVIEW EMAIL #1 (Template Personalizado) ===")
print(f"Para: {lead['email']}")
print(email)

# Preview segundo estilo - restaurante
lead2 = leads[7]
email2 = EMAIL_TEMPLATE_2.format(
    nicho=lead2["query"],
    ciudad=lead2["city"]
)
print("\n=== PREVIEW EMAIL #2 (Template Google) ===")
print(f"Para: {lead2['email']}")
print(email2)

print("\n=== RESUMEN ===")
print(f"17 leads listos para enviar")
print(f"Falta: configurar SMTP_PASSWORD (App Password de Gmail)")
print(f"Comando para enviar: python email_marketing.py (con dry_run=False)")
