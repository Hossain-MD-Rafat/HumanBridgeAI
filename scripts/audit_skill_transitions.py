"""Audit real-data coverage and ranking contracts, not career recommendation quality."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.skill_transitions import rank_candidates
from humanbridge.transition_data import load_transition_data


def validate_contract(result: dict) -> None:
    candidates = result["candidates"]
    source = result["source"]["occupation_code"]
    request = result["request"]
    if len(candidates) > request["top_k"] or len(
        {r["occupation_code"] for r in candidates}
    ) != len(candidates):
        raise ValueError("Duplicate or excess candidate records")
    order = [(-row["cosine_similarity"], row["occupation_code"]) for row in candidates]
    if order != sorted(order):
        raise ValueError("Nondeterministic ranking order")
    source_median = result["source"]["labor_context"]["wage"]["median_annual_wage"]
    for index, row in enumerate(candidates, 1):
        if row["occupation_code"] == source or row["rank"] != index:
            raise ValueError("Self recommendation or nonconsecutive ranks")
        value = row["cosine_similarity"]
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError("Invalid cosine value")
        total = (
            sum(x["cosine_contribution"] for x in row["shared_skill_contributions"])
            + row["remaining_skill_contribution"]
        )
        if not math.isclose(total, value, abs_tol=1e-12):
            raise ValueError("Explanation components do not sum to similarity")
        context = row["labor_context"]
        median = context["wage"]["median_annual_wage"]
        if request["min_national_median"] is not None and (
            median is None or median < request["min_national_median"]
        ):
            raise ValueError("Wage constraint violation")
        if request["min_median_retention"] is not None and (
            median is None
            or source_median is None
            or median / source_median < request["min_median_retention"]
        ):
            raise ValueError("Retention constraint violation")
        for key, field in [
            ("allowed_education", "education"),
            ("allowed_related_experience", "related_experience"),
        ]:
            if (
                request[key] is not None
                and context["preparation"][field] not in request[key]
            ):
                raise ValueError("Preparation constraint violation")
        if row["licensing_and_accessibility"] != "not_verified":
            raise ValueError("Unsupported feasibility claim")


def main() -> None:
    config_path = ROOT / "config/skill_transition.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    data = load_transition_data(ROOT, ROOT / "data/processed/core.sqlite3", config)
    cohort = json.loads(
        (ROOT / "config/review_cohort.json").read_text(encoding="utf-8")
    )
    if cohort["source_snapshot"] != config["source_snapshot"]:
        raise ValueError("Case studies use another snapshot")
    cases = []
    checks = 0
    for source in cohort["occupations"]:
        code = source["occupation_code"]
        args = (code, data.profiles, data.features, data.names, data.contexts, config)
        unfiltered = rank_candidates(*args)
        validate_contract(unfiltered)
        checks += 1
        if unfiltered != rank_candidates(*args):
            raise ValueError("Repeated ranking differs")
        education = data.contexts[code]["preparation"]["education"]
        if education not in config["education_categories"]:
            raise ValueError("Review cohort lacks supported entry education")
        filtered = rank_candidates(
            *args,
            min_median_retention=1,
            allowed_education=[education],
            allowed_related_experience=["None"],
        )
        validate_contract(filtered)
        checks += 1
        if rank_candidates(*args, min_national_median=1e12)["candidates"]:
            raise ValueError("Impossible filters were padded")

        def summary(result):
            return {
                "request": result["request"],
                "eligible_after_filters": result["eligible_after_filters"],
                "filter_exclusions": result["filter_exclusions"],
                "candidates": [
                    {
                        "occupation_code": r["occupation_code"],
                        "title": r["title"],
                        "cosine_similarity": r["cosine_similarity"],
                        "median_annual_wage": r["labor_context"]["wage"][
                            "median_annual_wage"
                        ],
                        "mapped_wage_codes": [
                            x["target_code"]
                            for x in r["labor_context"]["wage"]["mapping_evidence"]
                        ],
                        "entry_education": r["labor_context"]["preparation"][
                            "education"
                        ],
                        "related_experience": r["labor_context"]["preparation"][
                            "related_experience"
                        ],
                        "licensing_and_accessibility": r["licensing_and_accessibility"],
                    }
                    for r in result["candidates"]
                ],
            }

        cases.append(
            {
                "source_code": code,
                "source_title": source["title"],
                "unfiltered": summary(unfiltered),
                "illustrative_source_context_filters": summary(filtered),
            }
        )
    engine = hashlib.sha256()
    for name in [
        "src/humanbridge/skill_transitions.py",
        "src/humanbridge/transition_data.py",
        "scripts/recommend_transitions.py",
        "scripts/audit_skill_transitions.py",
    ]:
        engine.update(name.encode())
        engine.update((ROOT / name).read_bytes())
    result = {
        "method_version": config["method_version"],
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "audit_engine_sha256": engine.hexdigest(),
        "coverage": data.audit,
        "case_studies": cases,
        "verified_case_study_contracts": checks,
        "detected_constraint_violations": 0,
        "deterministic_repeated_rankings": True,
        "impossible_filters_return_empty": True,
        "ranking_relevance_metrics": None,
        "human_feasibility_validation": "not_performed",
        "interpretation": "Engineering and coverage checks only. Filters use illustrative occupation context, not verified personal education, income or experience.",
        "source_notice": "Derived from O*NET 31.0 (USDOL/ETA, CC BY 4.0) and BLS data. HumanBridge selects/normalizes records; USDOL/ETA has not approved, endorsed or tested these modifications. See THIRD_PARTY_NOTICES.md.",
    }
    output = ROOT / "docs/reports/skill-transition-audit.json"
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "skill_profiles": len(data.profiles),
                "dimensions": len(data.features),
                "case_studies": len(cases),
                "verified_contracts": checks,
                "constraint_violations": 0,
                "ranking_quality_metrics": None,
            }
        )
    )


if __name__ == "__main__":
    main()
