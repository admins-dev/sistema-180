"""Acceso directo a SMSPool via API - sin navegador, sin captcha."""
import json
import urllib.request
import urllib.parse
import time

API_BASE = "https://api.smspool.net"

# Paso 1: Buscar el ID del servicio Instagram
print("Buscando servicio Instagram...")
data = json.loads(urllib.request.urlopen(f"{API_BASE}/service/retrieve_all").read())
ig_id = None
for s in data:
    if "instagram" in s.get("name", "").lower():
        ig_id = s["ID"]
        print(f"  Encontrado: {s['name']} (ID: {ig_id})")
        break

if not ig_id:
    print("ERROR: No se encontro servicio Instagram")
    exit(1)

# Paso 2: Ver precio para Espana
print("\nConsultando precio para Espana...")
url = f"{API_BASE}/request/price?country=ES&service={ig_id}"
price_data = json.loads(urllib.request.urlopen(url).read())
print(f"  Precio: {json.dumps(price_data, indent=2)}")

# Paso 3: Consultar paises disponibles
print("\nPaises disponibles para Instagram:")
url2 = f"{API_BASE}/country/retrieve_all"
countries = json.loads(urllib.request.urlopen(url2).read())
for c in countries:
    if c.get("short_name") == "ES" or c.get("name") == "Spain":
        print(f"  Espana: ID={c.get('ID')}, name={c.get('name')}")
        break

print("\n=== INFO COMPLETA ===")
print(f"Servicio Instagram ID: {ig_id}")
print("Para comprar un numero necesitas un API key.")
print("El API key se obtiene desde el panel de SMSPool.")
