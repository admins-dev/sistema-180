"""Tests for deduplication logic."""

import pytest
from unittest.mock import MagicMock

from app.dedupe.exact import find_exact_duplicate, DuplicateMatch
from app.dedupe.fuzzy import find_fuzzy_duplicates, _compute_similarity


class TestComputeSimilarity:
    def test_identical_strings(self):
        score, method = _compute_similarity("clinica dental sur", "clinica dental sur")
        assert score == 100.0

    def test_different_strings(self):
        score, method = _compute_similarity("clinica dental", "restaurante la playa")
        assert score < 50

    def test_similar_strings(self):
        score, method = _compute_similarity("clinica dental sur", "clinica dental del sur")
        assert score > 80

    def test_reordered_words(self):
        score, method = _compute_similarity("dental clinica sur", "clinica dental sur")
        assert score > 85  # token_sort_ratio handles this


class TestFindFuzzyDuplicates:
    """Test fuzzy matching thresholds."""

    def test_empty_name_returns_empty(self):
        session = MagicMock()
        result = find_fuzzy_duplicates(session, None, "malaga")
        assert result == []
