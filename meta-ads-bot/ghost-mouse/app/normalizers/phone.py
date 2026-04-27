"""
Phone normalizer.

Parses phone numbers with the `phonenumbers` library.
Outputs E.164 format (+34612345678) for consistent deduplication.
"""

from __future__ import annotations

import phonenumbers


def normalize_phone(phone: str | None, country: str = "ES") -> str | None:
    """
    Normalize a phone number to E.164 international format.

    Examples:
        "952 12 34 56"    → "+34952123456"
        "+34 612 345 678" → "+34612345678"
        "612345678"       → "+34612345678"
        "invalid"         → None
        None              → None
    """
    if not phone:
        return None

    phone = phone.strip()
    if not phone:
        return None

    try:
        parsed = phonenumbers.parse(phone, country)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
        return None
    except phonenumbers.NumberParseException:
        return None


def is_mobile(phone: str | None, country: str = "ES") -> bool | None:
    """Check if a phone number is a mobile number."""
    if not phone:
        return None

    try:
        parsed = phonenumbers.parse(phone, country)
        number_type = phonenumbers.number_type(parsed)
        return number_type == phonenumbers.PhoneNumberType.MOBILE
    except phonenumbers.NumberParseException:
        return None
