"""Multi-criteria relevance scoring for specialist matching.

Computes a weighted score (0-1) combining domain affinity, text relevance,
budget fit, rating, and availability. Used by both task-request matching
and general specialist search.
"""

from __future__ import annotations

from typing import Any

from app.utils.domain_affinity import compute_domain_score

# Weights for the scoring formula (must sum to 1.0)
W_DOMAIN = 0.35
W_TEXT = 0.25
W_BUDGET = 0.20
W_RATING = 0.15
W_AVAILABILITY = 0.05


def compute_budget_score(
    hourly_rate: float | None,
    budget_min: float | None,
    budget_max: float | None,
) -> float:
    """Score how well a specialist's rate fits the client's budget.

    Returns:
        1.0 if within range, linear decay outside, 0.5 if no budget specified.
    """
    if budget_min is None and budget_max is None:
        return 0.5  # No budget constraint — neutral

    if hourly_rate is None:
        return 0.3  # Specialist hasn't set a rate — slight penalty

    rate = float(hourly_rate)
    b_min = float(budget_min) if budget_min is not None else 0.0
    b_max = float(budget_max) if budget_max is not None else rate * 2

    # Perfect fit
    if b_min <= rate <= b_max:
        return 1.0

    # Linear decay: 50% over/under → score 0
    if rate < b_min:
        diff_ratio = (b_min - rate) / max(b_min, 1.0)
    else:
        diff_ratio = (rate - b_max) / max(b_max, 1.0)

    return max(0.0, 1.0 - diff_ratio * 2)


def compute_relevance_score(
    specialist_domains: list[str],
    target_domain: str,
    hourly_rate: float | None,
    budget_min: float | None,
    budget_max: float | None,
    avg_rating: float,
    availability: str,
    text_rank: float = 0.0,
) -> float:
    """Compute final relevance score for a specialist.

    Args:
        specialist_domains: List of specialist's domain strings.
        target_domain: The domain from the task request or search filter.
        hourly_rate: Specialist's hourly rate.
        budget_min: Minimum budget from task request.
        budget_max: Maximum budget from task request.
        avg_rating: Specialist's average rating (0-5).
        availability: Specialist's availability status.
        text_rank: PostgreSQL ts_rank value (0-1) for text matching.

    Returns:
        Float score between 0 and 1.
    """
    domain_score = compute_domain_score(specialist_domains, target_domain)
    budget_score = compute_budget_score(hourly_rate, budget_min, budget_max)
    rating_score = min(avg_rating / 5.0, 1.0) if avg_rating else 0.0
    availability_bonus = 1.0 if availability == "available" else 0.0

    # Normalize text_rank (ts_rank typically returns small values)
    # Clamp to 0-1 range
    text_score = min(max(text_rank, 0.0), 1.0)

    score = (
        W_DOMAIN * domain_score
        + W_TEXT * text_score
        + W_BUDGET * budget_score
        + W_RATING * rating_score
        + W_AVAILABILITY * availability_bonus
    )

    return round(score, 4)


def score_specialist(
    specialist: Any,
    target_domain: str,
    budget_min: float | None = None,
    budget_max: float | None = None,
    text_rank: float = 0.0,
) -> float:
    """Convenience wrapper that extracts fields from a SpecialistProfile ORM object.

    Args:
        specialist: SpecialistProfile ORM instance with loaded domains relationship.
        target_domain: Domain to match against.
        budget_min: Client's minimum budget.
        budget_max: Client's maximum budget.
        text_rank: FTS rank for text matching.

    Returns:
        Relevance score (0-1).
    """
    spec_domains = [d.domain for d in specialist.domains] if specialist.domains else []
    return compute_relevance_score(
        specialist_domains=spec_domains,
        target_domain=target_domain,
        hourly_rate=float(specialist.hourly_rate) if specialist.hourly_rate else None,
        budget_min=budget_min,
        budget_max=budget_max,
        avg_rating=float(specialist.avg_rating) if specialist.avg_rating else 0.0,
        availability=specialist.availability or "available",
        text_rank=text_rank,
    )
