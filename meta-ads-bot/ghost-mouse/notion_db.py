import requests
import json
from datetime import datetime
from config import NOTION_TOKEN

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def search_database(query=""):
    """Busca una base de datos en Notion por nombre"""
    url = "https://api.notion.com/v1/search"
    payload = {
        "query": query,
        "filter": {"value": "database", "property": "object"}
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get("results", [])
    print(f"Error buscando BD: {response.status_code}", response.text)
    return []

def add_lead(database_id, nombre, nick, nicho, estado="Frío", setter="Sistema"):
    """Añade un lead a la BD de Notion"""
    url = "https://api.notion.com/v1/pages"
    
    # Asumiendo estructura de propiedades común. Si la BD es diferente, ajustaremos.
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nombre": {"title": [{"text": {"content": nombre}}]},
            "Usuario IG": {"rich_text": [{"text": {"content": nick}}]},
            "Nicho": {"select": {"name": nicho}},
            "Estado": {"select": {"name": estado}},
            "Setter (Ghost Mouse)": {"select": {"name": setter}},
            "Fecha Contacto": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"[Notion] Lead '{nombre}' añadido correctamente.")
        return response.json()
    else:
        print(f"[Notion ERROR] No se pudo añadir lead '{nombre}':", response.text)
        return None

def get_leads(database_id, estado=None):
    """Obtiene leads de la BD filtrados por estado"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    
    payload = {}
    if estado:
        payload["filter"] = {
            "property": "Estado",
            "select": {"equals": estado}
        }
        
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get("results", [])
    print(f"Error obteniendo leads: {response.text}")
    return []

if __name__ == "__main__":
    # Test connection and find DBs
    print("Buscando bases de datos en Notion...")
    dbs = search_database()
    for db in dbs:
        title = db.get("title", [{}])[0].get("plain_text", "Sin título") if db.get("title") else "Sin título"
        print(f"[{title}] ID: {db['id']}")
