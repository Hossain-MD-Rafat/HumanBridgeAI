"""Verified frozen runs and returned review queues, shared by review tools."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from humanbridge.annotations import validate_pair, validate_review

EXPECTED_ARTIFACTS = {
    "SOURCE_NOTICE.md",
    "machine-suggestions.development.jsonl",
    "selected-tasks.jsonl",
    "reviewer-A.blind.jsonl",
    "reviewer-B.blind.jsonl",
    "split-manifest.json",
    "run-report.json",
}


def read_jsonl(path: Path) -> list[dict]:
    """Read newline-delimited objects; reject nonobjects and duplicate file records later."""
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("Expected JSON objects in the review file")
    return rows


def load_run(run: Path, rubric: dict) -> tuple[dict, dict[str, dict]]:
    """Verify the full artifact set and rubric before exposing tasks to any consumer."""
    hashes = json.loads((run / "artifact-hashes.json").read_text(encoding="utf-8"))
    if set(hashes) != EXPECTED_ARTIFACTS:
        raise ValueError("Frozen run manifest has missing or unexpected artifacts")
    for name, checksum in hashes.items():
        if (
            Path(name).name != name
            or hashlib.sha256((run / name).read_bytes()).hexdigest() != checksum
        ):
            raise ValueError("Frozen run artifact differs from its manifest")
    report = json.loads((run / "run-report.json").read_text(encoding="utf-8"))
    if not isinstance(report.get("run_id"), str) or not re.fullmatch(
        r"[0-9a-f]{20}", report["run_id"]
    ):
        raise ValueError("Invalid frozen run identifier")
    if report["rubric_sha256"] != rubric["config_sha256"]:
        raise ValueError("Review must use the frozen run's rubric")
    tasks = read_jsonl(run / "selected-tasks.jsonl")
    expected = {task["task_key"]: task for task in tasks}
    if not expected or len(expected) != len(tasks):
        raise ValueError("Frozen run has empty or duplicate task identities")
    return report, expected


def read_queue(
    path: Path,
    expected: dict[str, dict],
    rubric: dict,
    slot: str,
    require_complete: bool = False,
) -> dict[str, dict]:
    """Validate all task records and one consistent reviewer identity per slot."""
    rows = read_jsonl(path)
    by_key = {row["task_key"]: row for row in rows}
    if len(by_key) != len(rows) or set(by_key) != set(expected):
        raise ValueError("Returned queue has duplicate, missing or unknown task keys")
    identities = set()
    for key, row in by_key.items():
        validate_review(row, expected[key], rubric, slot, require_complete)
        if row["review_status"] == "completed":
            identities.add(row["reviewer_id"].strip().casefold())
    if len(identities) > 1:
        raise ValueError("One reviewer slot must use one consistent pseudonym")
    return by_key


def read_pair(
    run: Path,
    first_path: Path,
    second_path: Path,
    rubric: dict,
    require_complete: bool = False,
) -> tuple[dict, dict, dict, dict]:
    report, expected = load_run(run, rubric)
    first = read_queue(first_path, expected, rubric, "A", require_complete)
    second = read_queue(second_path, expected, rubric, "B", require_complete)
    first_ids = {
        row["reviewer_id"].strip().casefold()
        for row in first.values()
        if row["review_status"] == "completed"
    }
    second_ids = {
        row["reviewer_id"].strip().casefold()
        for row in second.values()
        if row["review_status"] == "completed"
    }
    if first_ids & second_ids:
        raise ValueError("Reviewer A and B must be different people/pseudonyms")
    for key in expected:
        validate_pair(first[key], second[key])
    return report, expected, first, second
