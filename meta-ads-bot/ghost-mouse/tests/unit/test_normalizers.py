"""Tests for normalizers — pure functions, easy to test."""

import pytest

from app.normalizers.name import normalize_name
from app.normalizers.city import normalize_city
from app.normalizers.domain import normalize_domain, domains_match
from app.normalizers.phone import normalize_phone
from app.normalizers.niche import normalize_niche


# ═══════════════════════════════════════════
# NAME NORMALIZER
# ═══════════════════════════════════════════

class TestNormalizeName:
    def test_strips_legal_suffix_sl(self):
        assert normalize_name("Clinica Estetica SL") == "clinica estetica"

    def test_strips_legal_suffix_sa(self):
        assert normalize_name("Grupo Dental S.A.") == "grupo dental"

    def test_strips_legal_suffix_slu(self):
        assert normalize_name("Beauty Center S.L.U.") == "beauty center"

    def test_lowercase(self):
        assert normalize_name("CLINICA PREMIUM") == "clinica premium"

    def test_strips_accents(self):
        assert normalize_name("Clínica Estética") == "clinica estetica"

    def test_none_input(self):
        assert normalize_name(None) is None

    def test_empty_string(self):
        assert normalize_name("") is None

    def test_whitespace_only(self):
        assert normalize_name("   ") is None

    def test_collapses_whitespace(self):
        assert normalize_name("Clinica   Dental   Sur") == "clinica dental sur"


# ═══════════════════════════════════════════
# CITY NORMALIZER
# ═══════════════════════════════════════════

class TestNormalizeCity:
    def test_basic_lowercase(self):
        assert normalize_city("Malaga") == "malaga"

    def test_strips_accents(self):
        assert normalize_city("Málaga") == "malaga"

    def test_alias_barna(self):
        assert normalize_city("Barna") == "barcelona"

    def test_alias_bcn(self):
        assert normalize_city("BCN") == "barcelona"

    def test_none_input(self):
        assert normalize_city(None) is None

    def test_preserves_unknown(self):
        assert normalize_city("Ronda") == "ronda"


# ═══════════════════════════════════════════
# DOMAIN NORMALIZER
# ═══════════════════════════════════════════

class TestNormalizeDomain:
    def test_strips_protocol_and_path(self):
        assert normalize_domain("https://www.clinica-estetica.es/servicios") == "clinica-estetica.es"

    def test_strips_www(self):
        assert normalize_domain("http://www.example.com") == "example.com"

    def test_lowercase(self):
        assert normalize_domain("HTTPS://WWW.EXAMPLE.COM") == "example.com"

    def test_bare_domain(self):
        assert normalize_domain("example.es") == "example.es"

    def test_none_input(self):
        assert normalize_domain(None) is None

    def test_empty_string(self):
        assert normalize_domain("") is None


class TestDomainsMatch:
    def test_same_domain_different_urls(self):
        assert domains_match(
            "https://www.test.es/page",
            "http://test.es/contact"
        ) is True

    def test_different_domains(self):
        assert domains_match("https://a.es", "https://b.es") is False

    def test_none_inputs(self):
        assert domains_match(None, "https://test.es") is False
        assert domains_match("https://test.es", None) is False


# ═══════════════════════════════════════════
# PHONE NORMALIZER
# ═══════════════════════════════════════════

class TestNormalizePhone:
    def test_spanish_mobile(self):
        assert normalize_phone("612 345 678") == "+34612345678"

    def test_with_country_code(self):
        assert normalize_phone("+34 952 123 456") == "+34952123456"

    def test_landline(self):
        assert normalize_phone("952 12 34 56") == "+34952123456"

    def test_invalid(self):
        assert normalize_phone("invalid") is None

    def test_none_input(self):
        assert normalize_phone(None) is None

    def test_empty_string(self):
        assert normalize_phone("") is None


# ═══════════════════════════════════════════
# NICHE NORMALIZER
# ═══════════════════════════════════════════

class TestNormalizeNiche:
    def test_clinica_estetica(self):
        assert normalize_niche("Clinica Estetica") == "estetica"

    def test_clinica_dental(self):
        assert normalize_niche("Clínica Dental") == "dental"

    def test_gimnasio(self):
        assert normalize_niche("Gimnasio") == "fitness"

    def test_none_input(self):
        assert normalize_niche(None) is None

    def test_unknown_niche_passthrough(self):
        assert normalize_niche("Tienda de bicicletas") == "tienda de bicicletas"

    def test_strips_accents(self):
        assert normalize_niche("Peluquería") == "peluqueria"
