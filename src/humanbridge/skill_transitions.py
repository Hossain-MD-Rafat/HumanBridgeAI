"""Transparent occupation-profile similarity, filters and difference explanations."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SkillProfile:
    code: str
    title: str
    importance: dict[str, float]
    levels: dict[str, float | None] = field(default_factory=dict)


def scaled_importance(
    values: dict[str, float], features: list[str], minimum: float, maximum: float
) -> list[float]:
    """Normalize fixed source anchors; missing/suppressed values are never imputed."""
    if not features or len(features) != len(set(features)) or maximum <= minimum:
        raise ValueError("Invalid fixed skill schema or scale anchors")
    if set(values) != set(features):
        raise ValueError("A complete source skill profile is required")
    result = []
    for feature in features:
        value = values[feature]
        if (
            not isinstance(value, (float, int))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            raise ValueError("Skill importance must be a finite source measurement")
        if value < minimum or value > maximum:
            raise ValueError("Skill importance outside the source scale")
        result.append((value - minimum) / (maximum - minimum))
    return result


def cosine_components(
    first: list[float], second: list[float]
) -> tuple[float, list[float]]:
    """Return cosine and additive per-dimension contributions, not an overlap percent."""
    if (
        not first
        or len(first) != len(second)
        or any(not math.isfinite(x) or x < 0 for x in first + second)
    ):
        raise ValueError("Cosine needs equally sized, nonnegative finite vectors")
    denominator = math.sqrt(sum(x * x for x in first) * sum(x * x for x in second))
    if denominator == 0:
        raise ValueError("A zero-vector profile cannot be compared")
    contributions = [a * b / denominator for a, b in zip(first, second)]
    return min(1.0, max(0.0, sum(contributions))), contributions


def explain_pair(
    source: SkillProfile,
    target: SkillProfile,
    features: list[str],
    names: dict[str, str],
    config: dict,
) -> dict:
    a = scaled_importance(
        source.importance,
        features,
        config["importance_minimum"],
        config["importance_maximum"],
    )
    b = scaled_importance(
        target.importance,
        features,
        config["importance_minimum"],
        config["importance_maximum"],
    )
    similarity, contributions = cosine_components(a, b)
    shared = []
    differences = []
    for i, feature in enumerate(features):
        common = {
            "element_id": feature,
            "skill": names[feature],
            "source_importance": source.importance[feature],
            "target_importance": target.importance[feature],
        }
        if contributions[i] > 0:
            shared.append({**common, "cosine_contribution": contributions[i]})
        difference = target.importance[feature] - source.importance[feature]
        if difference > 1e-12:
            source_level = source.levels.get(feature)
            target_level = target.levels.get(feature)
            differences.append(
                {
                    **common,
                    "importance_difference": difference,
                    "source_occupation_level": source_level,
                    "target_occupation_level": target_level,
                    "occupation_level_difference": (
                        target_level - source_level
                        if source_level is not None and target_level is not None
                        else None
                    ),
                }
            )
    limit = config["explanation_skills"]
    shared.sort(key=lambda row: (-row["cosine_contribution"], row["element_id"]))
    differences.sort(
        key=lambda row: (
            -row["importance_difference"],
            -row["target_importance"],
            row["element_id"],
        )
    )
    shown = shared[:limit]
    return {
        "cosine_similarity": similarity,
        "skill_dimensions_compared": len(features),
        "shared_skill_contributions": shown,
        "remaining_skill_contribution": sum(
            row["cosine_contribution"] for row in shared[limit:]
        ),
        "priority_importance_differences": differences[:limit],
        "positive_importance_difference_count": len(differences),
        "interpretation": "Differences compare occupation requirements, not a person's missing skills or measured proficiency.",
    }


def rank_candidates(
    source_code: str,
    profiles: dict[str, SkillProfile],
    features: list[str],
    names: dict[str, str],
    contexts: dict[str, dict],
    config: dict,
    top_k: int = 5,
    min_national_median: float | None = None,
    min_median_retention: float | None = None,
    allowed_education: list[str] | None = None,
    allowed_related_experience: list[str] | None = None,
) -> dict:
    """Apply explicit source-context filters, then rank solely by skill cosine."""
    if source_code not in profiles:
        raise ValueError(
            "Source occupation has no eligible complete skill profile; use the coverage audit"
        )
    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or not 1 <= top_k <= config["maximum_results"]
    ):
        raise ValueError("top_k must be between 1 and 5")
    for value in (min_national_median, min_median_retention):
        if value is not None and (not math.isfinite(value) or value < 0):
            raise ValueError("Wage constraints must be finite and nonnegative")
    if allowed_education is not None and (
        not allowed_education
        or not set(allowed_education).issubset(config["education_categories"])
    ):
        raise ValueError(
            "Education filters must use explicit supported source categories"
        )
    if allowed_related_experience is not None and (
        not allowed_related_experience
        or not set(allowed_related_experience).issubset(
            config["related_experience_categories"]
        )
    ):
        raise ValueError(
            "Experience filters must use explicit supported source categories"
        )
    source = profiles[source_code]
    source_context = contexts[source_code]
    source_median = source_context["wage"]["median_annual_wage"]
    if min_median_retention is not None and (
        source_median is None or source_median <= 0
    ):
        raise ValueError(
            "Median-retention filtering requires a usable source national median wage"
        )
    # Verify the source before scanning targets; do not silently skip an invalid source vector.
    source_vector = scaled_importance(
        source.importance,
        features,
        config["importance_minimum"],
        config["importance_maximum"],
    )
    cosine_components(source_vector, source_vector)
    candidates = []
    excluded = Counter()
    for code in sorted(profiles):
        if code == source_code:
            continue
        context = contexts[code]
        median = context["wage"]["median_annual_wage"]
        if min_national_median is not None and (
            median is None or median < min_national_median
        ):
            excluded["median_wage_unavailable_or_below_threshold"] += 1
            continue
        retention = (
            median / source_median
            if median is not None and source_median is not None and source_median > 0
            else None
        )
        if min_median_retention is not None and (
            retention is None or retention < min_median_retention
        ):
            excluded["median_retention_unavailable_or_below_threshold"] += 1
            continue
        if (
            allowed_education is not None
            and context["preparation"].get("education") not in allowed_education
        ):
            excluded["entry_education_unavailable_or_not_allowed"] += 1
            continue
        if (
            allowed_related_experience is not None
            and context["preparation"].get("related_experience")
            not in allowed_related_experience
        ):
            excluded["related_experience_unavailable_or_not_allowed"] += 1
            continue
        try:
            explanation = explain_pair(source, profiles[code], features, names, config)
        except ValueError:
            excluded["incomparable_skill_profile"] += 1
            continue
        candidates.append(
            {
                "occupation_code": code,
                "title": profiles[code].title,
                **explanation,
                "national_median_retention_ratio": retention,
                "labor_context": context,
                "pathway_status": "unverified_skill_profile_candidate",
                "licensing_and_accessibility": "not_verified",
            }
        )
    candidates.sort(key=lambda row: (-row["cosine_similarity"], row["occupation_code"]))
    result = candidates[:top_k]
    for rank, row in enumerate(result, 1):
        row["rank"] = rank
    return {
        "source": {
            "occupation_code": source_code,
            "title": source.title,
            "labor_context": source_context,
        },
        "request": {
            "top_k": top_k,
            "min_national_median": min_national_median,
            "min_median_retention": min_median_retention,
            "allowed_education": (
                sorted(set(allowed_education))
                if allowed_education is not None
                else None
            ),
            "allowed_related_experience": (
                sorted(set(allowed_related_experience))
                if allowed_related_experience is not None
                else None
            ),
        },
        "eligible_skill_profiles": len(profiles),
        "eligible_after_filters": len(candidates),
        "filter_exclusions": dict(sorted(excluded.items())),
        "candidates": result,
        "ranking_basis": "Cosine of complete source-normalized occupation skill importance; context fields do not change ranking.",
        "limitations": config["limitations"],
        "ai_exposure": None,
        "human_dependency": None,
        "ranking_quality_metrics": None,
    }
