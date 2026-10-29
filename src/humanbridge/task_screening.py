"""Explainable lexical review cues; not a validated capability or employment model."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def load_rubric(path: Path) -> dict:
    """Validate identifiers and compile only a trusted project-owned rule config."""
    raw = path.read_bytes()
    rubric = json.loads(raw)
    dimensions = {item["id"]: item for item in rubric["dimensions"]}
    if len(dimensions) != len(rubric["dimensions"]):
        raise ValueError("Duplicate dimension IDs")
    rule_ids = [item["id"] for item in rubric["rules"] + rubric["guards"]]
    if len(rule_ids) != len(set(rule_ids)):
        raise ValueError("Duplicate rule/guard IDs")
    for item in rubric["rules"]:
        if item["dimension"] not in dimensions:
            raise ValueError("Rule references an unknown dimension")
        if dimensions[item["dimension"]]["family"] == "manual_only":
            raise ValueError("Manual-only dimensions cannot have lexical rules")
    for item in rubric["rules"] + rubric["guards"]:
        re.compile(item["pattern"], re.IGNORECASE)
    if not 0 < rubric["near_duplicate_jaccard"] <= 1:
        raise ValueError("Invalid similarity threshold")
    rubric["config_sha256"] = hashlib.sha256(raw).hexdigest()
    return rubric


def screen_task(text: str, rubric: dict) -> dict:
    """Return exact text spans, unknown dimensions and conservative review routing.

    A match supports only that a lexical cue occurs, not actual AI feasibility.
    Negation/qualification causes abstention even when positive-looking cues occur.
    Safety/regulated cues always require manual contextual review.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Task text must be a nonempty string")
    guard_hits = []
    for guard in rubric["guards"]:
        for match in re.finditer(guard["pattern"], text, re.IGNORECASE):
            guard_hits.append({"rule_id": guard["id"], "reason": guard["reason"],
                               "span": [match.start(), match.end()], "quote": match.group()})
    qualified = any(hit["reason"] == "negation_or_qualification" for hit in guard_hits)
    dimensions = {item["id"]: {"status": "not_assessed", "evidence": []}
                  for item in rubric["dimensions"]}
    for rule in rubric["rules"]:
        for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
            evidence = {"rule_id": rule["id"], "span": [match.start(), match.end()],
                        "quote": match.group(), "type": "task_text_lexical_cue"}
            item = dimensions[rule["dimension"]]
            item["status"] = "ambiguous_cue" if qualified else "cue_found"
            item["evidence"].append(evidence)
    families = {item["family"] for item in rubric["dimensions"]
                if dimensions[item["id"]]["status"] == "cue_found"}
    if guard_hits:
        route = "manual_context_review"
    elif families == {"digital", "context"}:
        route = "digital_and_context_review"
    elif "digital" in families:
        route = "digital_assistance_review"
    elif "context" in families:
        route = "human_context_review"
    else:
        route = "insufficient_evidence"
    return {
        "method_version": rubric["method_version"],
        "rubric_version": rubric["rubric_version"],
        "config_sha256": rubric["config_sha256"],
        "capability_assumption_date": rubric["capability_assumption_date"],
        "evidence_status": "machine_generated_unreviewed",
        "review_route": route, "dimensions": dimensions, "guard_hits": guard_hits,
        "ai_exposure": None, "human_dependency": None, "workflow_label": None,
        "limitations": ["Lexical cues do not establish actual AI capability or time savings.",
                        "No match means not assessed, not zero exposure or low human worth.",
                        "No occupation or person-level replacement probability is estimated."],
    }
