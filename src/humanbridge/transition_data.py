"""Read fixed skill profiles and conservative mapped context from the frozen core."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from humanbridge.pipeline import logical_hash
from humanbridge.skill_transitions import (
    SkillProfile,
    cosine_components,
    scaled_importance,
)


@dataclass(frozen=True)
class TransitionData:
    profiles: dict[str, SkillProfile]
    features: list[str]
    names: dict[str, str]
    contexts: dict[str, dict]
    audit: dict


def mapped_record(targets: set[str], records: dict[str, dict]) -> dict:
    """Preserve ambiguity and absent targets; never choose the first mapping silently."""
    evidence = [
        {"target_code": code, "record": records.get(code)} for code in sorted(targets)
    ]
    if not targets:
        return {"status": "unmapped", "record": None, "mapping_evidence": evidence}
    if len(targets) != 1:
        return {
            "status": "ambiguous_mapping",
            "record": None,
            "mapping_evidence": evidence,
        }
    record = records.get(next(iter(targets)))
    return {
        "status": "available" if record is not None else "missing_target_data",
        "record": record,
        "mapping_evidence": evidence,
    }


def load_transition_data(root: Path, database: Path, config: dict) -> TransitionData:
    """Read one verified snapshot; exclude incomplete vectors, not missing context."""
    report = json.loads(
        (root / "docs/reports/core-data.json").read_text(encoding="utf-8")
    )
    if config["source_snapshot"] != report["snapshot_id"]:
        raise ValueError("Transition config and core snapshot differ")
    features = config["feature_ids"]
    if len(features) != config["expected_skill_dimensions"] or len(features) != len(
        set(features)
    ):
        raise ValueError("Invalid fixed feature schema")
    with sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.execute("BEGIN")
        if logical_hash(db) != report["logical_sha256"]:
            raise ValueError(
                "Core database differs from its validated logical fingerprint"
            )
        db.row_factory = sqlite3.Row
        releases = {
            row["dataset_id"]: row["release_id"]
            for row in db.execute("SELECT * FROM dataset_release")
        }
        onet = releases["onet_31_0"]
        scale = db.execute(
            "SELECT minimum,maximum FROM scale WHERE release_id=? AND scale_id=?",
            (onet, config["importance_scale_id"]),
        ).fetchone()
        if scale is None or tuple(scale) != (
            config["importance_minimum"],
            config["importance_maximum"],
        ):
            raise ValueError("Source importance anchors differ from the method config")
        catalog = {
            row["occupation_code"]: row["title"]
            for row in db.execute(
                "SELECT occupation_code,title FROM occupation WHERE release_id=?",
                (onet,),
            )
        }
        names = {
            row["element_id"]: row["name"]
            for row in db.execute(
                "SELECT element_id,name FROM element WHERE release_id=?", (onet,)
            )
        }
        if not set(features).issubset(names):
            raise ValueError(
                "Configured skill IDs are absent from the source dictionary"
            )
        importance = defaultdict(dict)
        levels = defaultdict(dict)
        quality = defaultdict(list)
        for row in db.execute(
            "SELECT r.* FROM occupation_element_rating r JOIN element e USING(release_id,element_id) "
            "WHERE r.release_id=? AND e.domain IN ('essential_skill','transferable_skill') "
            "AND r.scale_id IN ('IM','LV') AND r.category='' ORDER BY r.occupation_code,r.element_id,r.scale_id",
            (onet,),
        ):
            code = row["occupation_code"]
            feature = row["element_id"]
            metadata = json.loads(row["source_metadata_json"])
            usable = (
                row["value"] is not None
                and row["quality_flag"] is None
                and metadata.get("Not Relevant") != "Y"
            )
            if row["scale_id"] == "IM":
                if feature not in features:
                    raise ValueError(
                        "Unexpected skill dimension; review the fixed schema"
                    )
                if usable:
                    importance[code][feature] = row["value"]
                else:
                    quality[code].append(feature)
            else:
                levels[code][feature] = row["value"] if usable else None
        profiles = {}
        excluded = {}
        for code, title in sorted(catalog.items()):
            try:
                vector = scaled_importance(
                    importance[code],
                    features,
                    config["importance_minimum"],
                    config["importance_maximum"],
                )
                cosine_components(vector, vector)
            except ValueError as error:
                excluded[code] = {
                    "title": title,
                    "reason": str(error),
                    "usable_importance_count": len(importance[code]),
                    "unusable_importance_elements": quality[code],
                }
            else:
                profiles[code] = SkillProfile(
                    code, title, importance[code], levels[code]
                )

        soc = defaultdict(set)
        nem = defaultdict(set)
        for dataset, target, taxonomy in (
            ("onet_soc_crosswalk", soc, "SOC 2018"),
            ("onet_nem_crosswalk", nem, "NEM 2025"),
        ):
            for row in db.execute(
                "SELECT source_code,target_code FROM occupation_crosswalk "
                "WHERE mapping_release_id=? AND source_taxonomy='O*NET-SOC 2019' AND target_taxonomy=?",
                (releases[dataset], taxonomy),
            ):
                target[row["source_code"]].add(row["target_code"])
        wages = {
            row["occupation_code"]: dict(row)
            for row in db.execute(
                "SELECT occupation_code,value,quality_flag,period,unit,universe FROM labor_statistic "
                "WHERE release_id=? AND metric='A_MEDIAN' AND geography_id='US' AND boundary_vintage='national' "
                "AND period='2025-05' AND unit='USD/year'",
                (releases["bls_oews_2025"],),
            )
        }
        preparation = {
            row["occupation_code"]: dict(row)
            for row in db.execute(
                "SELECT occupation_code,education,related_experience,on_job_training FROM preparation_requirement WHERE release_id=?",
                (releases["bls_projections_2025_2035"],),
            )
        }
        outlook = defaultdict(dict)
        for row in db.execute(
            "SELECT occupation_code,metric,value,quality_flag,period,unit FROM labor_statistic "
            "WHERE release_id=? AND metric IN ('growth_percent','annual_openings')",
            (releases["bls_projections_2025_2035"],),
        ):
            outlook[row["occupation_code"]][row["metric"]] = dict(row)
        contexts = {}
        for code in profiles:
            wage = mapped_record(soc[code], wages)
            raw = wage.pop("record")
            median = None
            if raw is not None:
                if (
                    raw["value"] is not None
                    and raw["quality_flag"] is None
                    and raw["value"] > 0
                ):
                    median = raw["value"]
                    wage["status"] = "observed"
                else:
                    wage["status"] = "suppressed_or_unavailable"
            wage.update(
                {
                    "median_annual_wage": median,
                    "unit": "USD/year",
                    "period": "2025-05",
                    "source_release_id": releases["bls_oews_2025"],
                    "aggregation_warning": "Mapped source occupation aggregate; not an individual's salary or specialization-specific estimate.",
                }
            )
            prep = mapped_record(nem[code], preparation)
            raw_prep = prep.pop("record")
            prep.update(
                {
                    "education": raw_prep["education"] if raw_prep else None,
                    "related_experience": (
                        raw_prep["related_experience"] if raw_prep else None
                    ),
                    "on_job_training": (
                        raw_prep["on_job_training"] if raw_prep else None
                    ),
                    "source_release_id": releases["bls_projections_2025_2035"],
                    "licensing": "not_verified",
                }
            )
            outlook_mapping = mapped_record(nem[code], dict(outlook))
            outlook_raw = outlook_mapping.pop("record")
            growth = None
            openings = None
            if outlook_raw:
                g = outlook_raw.get("growth_percent")
                o = outlook_raw.get("annual_openings")
                if g and g["quality_flag"] is None:
                    growth = g["value"]
                if o and o["quality_flag"] is None and o["value"] is not None:
                    if o["unit"] != "thousand openings/year":
                        raise ValueError("Unexpected openings unit")
                    openings = o["value"] * 1000
            contexts[code] = {
                "wage": wage,
                "preparation": prep,
                "outlook": {
                    **outlook_mapping,
                    "growth_percent": growth,
                    "annual_openings": openings,
                    "annual_openings_unit": "openings/year",
                    "source_release_id": releases["bls_projections_2025_2035"],
                    "note": "National long-term projections; not current local vacancies.",
                },
            }
    audit = {
        "source_snapshot": report["snapshot_id"],
        "core_logical_sha256": report["logical_sha256"],
        "catalog_occupations": len(catalog),
        "complete_skill_profiles": len(profiles),
        "skill_dimensions": len(features),
        "excluded_profiles": excluded,
        "wage_status_counts": dict(
            sorted(Counter(c["wage"]["status"] for c in contexts.values()).items())
        ),
        "preparation_status_counts": dict(
            sorted(
                Counter(c["preparation"]["status"] for c in contexts.values()).items()
            )
        ),
        "note": "Coverage/integrity audit, not recommendation relevance or feasibility validation.",
    }
    return TransitionData(profiles, features, names, contexts, audit)
