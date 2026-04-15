"""
lead_factory.py — Sistema 180
Lead Factory Engine: Google Maps → Instagram handles → prospects.json
Busca negocios locales automáticamente por ciudad y tipo.
"""
import os, json, re, time, logging, requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

MAPS_KEY = os.getenv('GOOGLE_MAPS_KEY', '')
GEMINI_KEY = os.getenv('GEMINI_API_KEY', '')

# Coordenadas base y zonas a prospectar
ZONES = {
    'alhaurin_el_grande': {'lat': 36.6453, 'lng': -4.6984, 'radius': 5000},
    'alhaurin_de_la_torre': {'lat': 36.6667, 'lng': -4.5667, 'radius': 4000},
    'coin':                 {'lat': 36.6603, 'lng': -4.7597, 'radius': 4000},
    'mijas':                {'lat': 36.5965, 'lng': -4.6378, 'radius': 5000},
    'fuengirola':           {'lat': 36.5403, 'lng': -4.6250, 'radius': 4000},
    'torremolinos':         {'lat': 36.6219, 'lng': -4.4997, 'radius': 4000},
    'benalmadena':          {'lat': 36.5997, 'lng': -4.5169, 'radius': 4000},
    'malaga_centro':        {'lat': 36.7213, 'lng': -4.4214, 'radius': 3000},
}

BUSINESS_TYPES = [
    'peluquería',
    'barbería',
    'centro de estética',
    'clínica dental',
    'fisioterapia',
    'spa',
    'uñas',
    'centro de belleza',
]


def search_places(query: str, lat: float, lng: float, radius: int = 5000) -> list[dict]:
    """Busca negocios con Google Places API (Nearby Search)."""
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    results = []
    params = {
        'query': query,
        'location': f'{lat},{lng}',
        'radius': radius,
        'language': 'es',
        'key': MAPS_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        for place in data.get('results', []):
            results.append({
                'place_id': place.get('place_id', ''),
                'name': place.get('name', ''),
                'address': place.get('formatted_address', ''),
                'rating': place.get('rating', 0),
                'reviews': place.get('user_ratings_total', 0),
            })
    except Exception as e:
        logger.error(f'Maps error: {e}')
    return results


def get_place_details(place_id: str) -> dict:
    """Obtiene detalles de un negocio (web, teléfono)."""
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    try:
        r = requests.get(url, params={
            'place_id': place_id,
            'fields': 'name,website,formatted_phone_number,url',
            'key': MAPS_KEY,
        }, timeout=10)
        data = r.json().get('result', {})
        return {
            'website': data.get('website', ''),
            'phone': data.get('formatted_phone_number', ''),
            'maps_url': data.get('url', ''),
        }
    except Exception as e:
        logger.error(f'Place details error: {e}')
        return {}


def extract_instagram_from_website(website: str) -> str:
    """Intenta encontrar el handle de Instagram en la web del negocio."""
    if not website:
        return ''
    try:
        r = requests.get(website, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        text = r.text
        # Buscar links de Instagram
        patterns = [
            r'instagram\.com/([a-zA-Z0-9_.]{2,30})',
            r'@([a-zA-Z0-9_.]{2,30})',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                if m not in ('sharer', 'share', 'intent', 'p', 'reel', 'explore', 'instagram'):
                    return f'@{m}'
    except Exception:
        pass
    return ''


def guess_instagram_handle(name: str, city: str) -> str:
    """Genera handles probables basados en el nombre del negocio."""
    # Limpiar nombre
    clean = name.lower()
    clean = re.sub(r'[áàä]', 'a', clean)
    clean = re.sub(r'[éèë]', 'e', clean)
    clean = re.sub(r'[íìï]', 'i', clean)
    clean = re.sub(r'[óòö]', 'o', clean)
    clean = re.sub(r'[úùü]', 'u', clean)
    clean = re.sub(r'[ñ]', 'n', clean)
    clean = re.sub(r'[^a-z0-9\s]', '', clean)
    parts = clean.split()[:3]
    city_clean = city.lower().replace(' ', '').replace('á','a').replace('é','e')[:8]

    handles = [
        '_'.join(parts),
        ''.join(parts),
        f"{''.join(parts[:2])}_{city_clean}",
    ]
    return handles[0]  # devuelve el más probable


def detect_pain(name: str, rating: float, reviews: int) -> str:
    """Detecta el dolor principal del negocio."""
    if rating < 4.0 and reviews > 10:
        return 'reseñas negativas, clientes insatisfechos'
    if reviews < 5:
        return 'poca presencia online, difícil de encontrar'
    return 'no contestan a clientes fuera de horario, pierden citas'


def generate_prospect_with_gemini(name: str, tipo: str, city: str, pain: str) -> str:
    """Usa Gemini Flash para generar el mensaje DM personalizado."""
    if not GEMINI_KEY:
        return ''
    try:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}'
        prompt = (
            f"Eres un vendedor experto en automatización para negocios locales en España.\n"
            f"Escribe un DM de Instagram para este negocio. REGLAS: máximo 3 líneas, "
            f"natural y directo, sin emojis de relleno, sin 'Hola equipo de X', "
            f"menciona el problema específico, termina con pregunta.\n\n"
            f"Negocio: {name}\nTipo: {tipo}\nCiudad: {city}\nProblema: {pain}\n\n"
            f"Responde SOLO con el mensaje."
        )
        r = requests.post(url, json={
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'maxOutputTokens': 120, 'temperature': 0.7},
        }, timeout=15)
        data = r.json()
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        logger.error(f'Gemini error: {e}')
        return ''


def run_lead_factory(zones: list[str] = None, types: list[str] = None,
                     max_per_zone: int = 10, save: bool = True) -> list[dict]:
    """
    Ejecuta la fábrica de leads completa.
    Devuelve lista de prospectos lista para pasar al prospector.
    """
    if not MAPS_KEY:
        logger.error('GOOGLE_MAPS_KEY no configurada')
        return []

    target_zones = {k: v for k, v in ZONES.items() if not zones or k in zones}
    target_types = types or BUSINESS_TYPES[:4]  # por defecto: peluquería, barbería, estética, dental

    prospects = []
    existing = set()

    # Cargar prospectos existentes para no duplicar
    if os.path.exists('prospects.json'):
        with open('prospects.json') as f:
            existing_list = json.load(f)
            existing = {p.get('instagram', '') for p in existing_list}
            prospects = existing_list

    new_count = 0
    for zone_name, coords in target_zones.items():
        city_display = zone_name.replace('_', ' ').title()
        for btype in target_types:
            query = f'{btype} {city_display}'
            logger.info(f'Buscando: {query}')
            places = search_places(query, coords['lat'], coords['lng'], coords['radius'])
            places = places[:max_per_zone]

            for place in places:
                name = place['name']
                details = get_place_details(place['place_id'])
                time.sleep(0.3)  # evitar rate limit Maps

                # Intentar obtener Instagram de la web
                ig_handle = extract_instagram_from_website(details.get('website', ''))
                if not ig_handle:
                    ig_handle = f'@{guess_instagram_handle(name, city_display)}'

                if ig_handle in existing:
                    continue

                pain = detect_pain(name, place.get('rating', 0), place.get('reviews', 0))

                prospect = {
                    'name': name,
                    'instagram': ig_handle,
                    'type': btype,
                    'city': city_display,
                    'pain': pain,
                    'rating': place.get('rating', 0),
                    'reviews': place.get('reviews', 0),
                    'phone': details.get('phone', ''),
                    'website': details.get('website', ''),
                    'source': 'google_maps',
                }
                prospects.append(prospect)
                existing.add(ig_handle)
                new_count += 1
                logger.info(f'  ✅ {name} — {ig_handle}')

    if save:
        with open('prospects.json', 'w') as f:
            json.dump(prospects, f, ensure_ascii=False, indent=2)
        logger.info(f'Guardados {new_count} prospectos nuevos (total: {len(prospects)})')

    return [p for p in prospects if p.get('source') == 'google_maps']
