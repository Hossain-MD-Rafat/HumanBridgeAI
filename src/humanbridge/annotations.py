"""Blind review templates and strict validation of returned human-label records."""
from __future__ import annotations

from datetime import datetime, timezone

IDENTITY_FIELDS = ("task_key", "release_id", "occupation_code", "occupation_title",
                   "task_id", "task_text", "split", "rubric_version", "capability_assumption_date")


def blank_review(task: dict, rubric: dict, slot: str) -> dict:
    """Create an unreviewed record with no machine suggestions or inferred labels."""
    if slot not in ("A", "B"):
        raise ValueError("Reviewer slot must be A or B")
    return {
        **{field: task[field] for field in IDENTITY_FIELDS if field in task},
        "rubric_version": rubric["rubric_version"],
        "capability_assumption_date": rubric["capability_assumption_date"],
        "reviewer_slot": slot, "reviewer_id": None, "review_status": "unreviewed",
        "dimension_ratings": {item["id"]: None for item in rubric["dimensions"]},
        "exposure_label": None, "workflow_label": None, "rationale": None,
        "evidence_references": [], "context_notes": None, "reviewed_at_utc": None,
    }


def validate_review(record: dict, task: dict, rubric: dict, slot: str,
                    require_complete: bool = False) -> None:
    """Reject changed task identities, unblinded fields and unsupported completion claims."""
    expected = blank_review(task, rubric, slot)
    if set(record) != set(expected):
        raise ValueError("Review fields differ from the blind template")
    for field in (*IDENTITY_FIELDS, "reviewer_slot"):
        if record[field] != expected[field]:
            raise ValueError(f"Changed review identity: {field}")
    dimensions = record["dimension_ratings"]
    if not isinstance(dimensions, dict) or set(dimensions) != set(expected["dimension_ratings"]):
        raise ValueError("Dimension keys differ from the rubric")
    if any(value is not None and value not in rubric["human_dimension_labels"]
           for value in dimensions.values()):
        raise ValueError("Invalid human dimension label")
    for field, labels in (("exposure_label", rubric["human_exposure_labels"]),
                          ("workflow_label", rubric["human_workflow_labels"])):
        if record[field] is not None and record[field] not in labels:
            raise ValueError(f"Invalid {field}")
    if record["review_status"] not in ("unreviewed", "completed"):
        raise ValueError("Invalid review status")
    complete = record["review_status"] == "completed"
    if require_complete and not complete:
        raise ValueError("Review has not been completed")
    if not complete:
        mutable = set(record) - set(IDENTITY_FIELDS) - {"reviewer_slot"}
        if any(record[field] != expected[field] for field in mutable):
            raise ValueError("Unreviewed record contains partial labels; finish it or restore the template")
        return
    if any(value is None for value in dimensions.values()) or record["exposure_label"] is None or record["workflow_label"] is None:
        raise ValueError("Completed review must label every field, including explicit insufficient evidence")
    if not isinstance(record["reviewer_id"], str) or not record["reviewer_id"].strip():
        raise ValueError("Completed review needs a reviewer pseudonym")
    if not isinstance(record["rationale"], str) or len(record["rationale"].strip()) < 20:
        raise ValueError("Completed review needs a substantive rationale")
    references = record["evidence_references"]
    if not isinstance(references, list) or not references or any(
            not isinstance(value, str) or not value.strip() for value in references):
        raise ValueError("Completed review needs evidence references")
    if record["context_notes"] is not None and not isinstance(record["context_notes"], str):
        raise ValueError("Context notes must be text or null")
    try:
        timestamp = datetime.fromisoformat(record["reviewed_at_utc"].replace("Z", "+00:00"))
        if timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
            raise ValueError("Review timestamp must be UTC")
    except (AttributeError, TypeError, ValueError) as error:
        raise ValueError("Completed review needs an ISO UTC timestamp") from error


def validate_pair(first: dict, second: dict) -> None:
    """Independence is a review protocol; at minimum reject reuse of one identity."""
    if first["task_key"] != second["task_key"] or {first["reviewer_slot"], second["reviewer_slot"]} != {"A", "B"}:
        raise ValueError("Expected two slots for the same task")
    if first["review_status"] == second["review_status"] == "completed":
        if first["reviewer_id"].strip().casefold() == second["reviewer_id"].strip().casefold():
            raise ValueError("Two independent reviewers cannot use the same identity")
