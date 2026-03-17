"""Domain affinity map for smart specialist matching.

Instead of exact domain string matching, this module provides
weighted relationships between domains so that related specialists
can be discovered (e.g., an AI/ML request also surfaces Engineering
and Science specialists with lower relevance scores).
"""

# Affinity scores: 1.0 = exact match, 0.5-0.7 = strongly related, 0.3 = loosely related
DOMAIN_AFFINITY: dict[str, dict[str, float]] = {
    "AI/ML": {
        "Engineering": 0.7,
        "Science": 0.6,
        "Education": 0.3,
    },
    "Law": {
        "Business": 0.6,
        "Finance": 0.5,
    },
    "Finance": {
        "Business": 0.7,
        "Law": 0.5,
        "Marketing": 0.3,
    },
    "Medicine": {
        "Science": 0.6,
        "Education": 0.3,
    },
    "Engineering": {
        "AI/ML": 0.7,
        "Science": 0.5,
        "Design": 0.3,
    },
    "Design": {
        "Marketing": 0.5,
        "Engineering": 0.3,
    },
    "Marketing": {
        "Business": 0.6,
        "Design": 0.5,
        "Finance": 0.3,
    },
    "Education": {
        "Science": 0.5,
        "AI/ML": 0.3,
        "Medicine": 0.3,
    },
    "Science": {
        "AI/ML": 0.6,
        "Engineering": 0.5,
        "Medicine": 0.5,
        "Education": 0.4,
    },
    "Business": {
        "Finance": 0.7,
        "Marketing": 0.6,
        "Law": 0.5,
    },
    "Other": {},
}


def get_related_domains(domain: str) -> dict[str, float]:
    """Return a dict of {domain_name: affinity_score} including exact match at 1.0.

    For "Other", returns an empty dict (no domain preference).
    For unknown domains, returns just the domain itself at 1.0.
    """
    if domain == "Other":
        return {}

    result = {domain: 1.0}
    related = DOMAIN_AFFINITY.get(domain, {})
    result.update(related)
    return result


def get_all_related_domain_names(domain: str) -> list[str]:
    """Return a flat list of domain names (exact + related) for SQL IN queries."""
    related = get_related_domains(domain)
    return list(related.keys()) if related else []


def compute_domain_score(
    specialist_domains: list[str], target_domain: str
) -> float:
    """Compute the best domain match score for a specialist against a target domain.

    Returns 1.0 for exact match, 0.5-0.7 for related domains, 0 for no match.
    For "Other" target, returns 0.5 (neutral — other factors decide).
    """
    if target_domain == "Other":
        return 0.5  # Neutral score; text/budget/rating will differentiate

    if not specialist_domains:
        return 0.0

    related = get_related_domains(target_domain)
    best_score = 0.0

    for spec_domain in specialist_domains:
        score = related.get(spec_domain, 0.0)
        if score > best_score:
            best_score = score

    return best_score
