"""
Niche normalizer.

Maps business categories to canonical niche names.
Handles Spanish-specific terminology and common variations.
"""

from __future__ import annotations

import unicodedata

# Canonical niche mapping: variant → standard name
_NICHE_MAP: dict[str, str] = {
    # Estética y belleza
    "clinica estetica": "estetica",
    "centro estetico": "estetica",
    "centro de estetica": "estetica",
    "estetica avanzada": "estetica",
    "medicina estetica": "estetica",
    "cirugia estetica": "estetica",
    "belleza": "estetica",
    "beauty": "estetica",
    "peluqueria": "peluqueria",
    "salon de belleza": "peluqueria",
    "barberia": "peluqueria",
    # Dental
    "clinica dental": "dental",
    "dentista": "dental",
    "odontologia": "dental",
    "ortodoncia": "dental",
    "implantes dentales": "dental",
    # Fitness
    "gimnasio": "fitness",
    "gym": "fitness",
    "crossfit": "fitness",
    "entrenamiento personal": "fitness",
    "personal trainer": "fitness",
    # Restauración
    "restaurante": "restauracion",
    "bar": "restauracion",
    "cafeteria": "restauracion",
    "tapas": "restauracion",
    "pizzeria": "restauracion",
    # Inmobiliaria
    "inmobiliaria": "inmobiliaria",
    "agencia inmobiliaria": "inmobiliaria",
    "real estate": "inmobiliaria",
    # Salud
    "fisioterapia": "fisioterapia",
    "fisioterapeuta": "fisioterapia",
    "psicologia": "psicologia",
    "psicologo": "psicologia",
    "nutricion": "nutricion",
    "nutricionista": "nutricion",
    "veterinario": "veterinaria",
    "clinica veterinaria": "veterinaria",
    # Legal y finanzas
    "abogado": "legal",
    "despacho de abogados": "legal",
    "asesoria": "asesoria",
    "asesoria fiscal": "asesoria",
    "gestoria": "asesoria",
    "contabilidad": "asesoria",
    # Educación
    "academia": "educacion",
    "formacion": "educacion",
    "autoescuela": "educacion",
    # Hogar
    "reformas": "reformas",
    "fontanero": "reformas",
    "electricista": "reformas",
    "pintor": "reformas",
    "carpinteria": "reformas",
    "limpieza": "limpieza",
    "jardineria": "jardineria",
}


def _strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_niche(niche: str | None) -> str | None:
    """
    Normalize a niche/category to a canonical name.

    - Lowercase, strip accents
    - Map to canonical category via alias dictionary

    Returns the canonical niche or the cleaned input if no mapping exists.
    """
    if not niche:
        return None

    result = niche.strip().lower()
    result = _strip_accents(result)
    result = " ".join(result.split())

    return _NICHE_MAP.get(result, result)
