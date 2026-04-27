"""
Fuzzy deduplication — name+city similarity matching.

Uses rapidfuzz for fast string matching with configurable thresholds:
  - ≥90: probable_duplicate (very likely the same business)
  - ≥75: possible_duplicate (might be the same, review recommended)
  - <75: no_duplicate

Only runs on leads that passed exact dedup (no place_id/domain/phone match).
"""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.lead import Lead


# Thresholds for fuzzy matching
THRESHOLD_PROBABLE = 90  # Very likely the same business
THRESHOLD_POSSIBLE = 75  # Might be the same, flag for review


@dataclass
class FuzzyMatch:
    """Result of a fuzzy deduplication check."""
    is_duplicate: bool
    duplicate_type: str | None  # probable | possible
    duplicate_of_id: str | None
    reason: str | None
    score: float  # 0-100 similarity score
    method: str | None  # which rapidfuzz method was used


def _compute_similarity(name1: str, name2: str) -> tuple[float, str]:
    """
    Compute best similarity score between two names using multiple methods.

    Returns (score, method_name).
    """
    scores = {
        "token_sort_ratio": fuzz.token_sort_ratio(name1, name2),
        "token_set_ratio": fuzz.token_set_ratio(name1, name2),
        "ratio": fuzz.ratio(name1, name2),
    }
    best_method = max(scores, key=scores.get)  # type: ignore
    return scores[best_method], best_method


def find_fuzzy_duplicates(
    session: Session,
    normalized_name: str | None,
    city_normalized: str | None,
    exclude_id: str | None = None,
    threshold_probable: int = THRESHOLD_PROBABLE,
    threshold_possible: int = THRESHOLD_POSSIBLE,
) -> list[FuzzyMatch]:
    """
    Find fuzzy duplicates by comparing normalized_name within the same city.

    Only compares against non-duplicate leads in the same city.
    Returns ALL matches above the possible threshold, sorted by score descending.
    """
    if not normalized_name:
        return []

    # Build query: same city, not already marked as duplicate
    stmt = select(Lead).where(
        Lead.is_duplicate == False,
        Lead.normalized_name.isnot(None),
    )
    if city_normalized:
        stmt = stmt.where(Lead.city_normalized == city_normalized)
    if exclude_id:
        stmt = stmt.where(Lead.id != exclude_id)

    candidates = session.execute(stmt).scalars().all()
    matches: list[FuzzyMatch] = []

    for candidate in candidates:
        if not candidate.normalized_name:
            continue

        score, method = _compute_similarity(normalized_name, candidate.normalized_name)

        if score >= threshold_probable:
            matches.append(FuzzyMatch(
                is_duplicate=True,
                duplicate_type="probable",
                duplicate_of_id=candidate.id,
                reason=(
                    f"Fuzzy match: '{normalized_name}' ≈ '{candidate.normalized_name}' "
                    f"(score={score:.1f}, method={method})"
                ),
                score=score,
                method=method,
            ))
        elif score >= threshold_possible:
            matches.append(FuzzyMatch(
                is_duplicate=True,
                duplicate_type="possible",
                duplicate_of_id=candidate.id,
                reason=(
                    f"Possible match: '{normalized_name}' ~ '{candidate.normalized_name}' "
                    f"(score={score:.1f}, method={method})"
                ),
                score=score,
                method=method,
            ))

    # Sort by score descending
    matches.sort(key=lambda m: m.score, reverse=True)
    return matches
