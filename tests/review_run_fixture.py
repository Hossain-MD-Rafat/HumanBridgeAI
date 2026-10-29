"""Tiny synthetic frozen run for integrity and evaluation tests only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from humanbridge.annotations import blank_review
from humanbridge.review_io import EXPECTED_ARTIFACTS


def write_rows(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def create_run(root: Path, rubric: dict) -> tuple[Path, list[dict]]:
    run = root / "run"
    run.mkdir()
    tasks = [
        {
            "task_key": f"synthetic:fixture:{index}",
            "release_id": "synthetic",
            "occupation_code": "fixture",
            "occupation_title": "Synthetic fixture",
            "task_id": str(index),
            "task_text": f"Synthetic test task {index}.",
            "split": "development" if index == 1 else "holdout",
        }
        for index in (1, 2)
    ]
    for name in EXPECTED_ARTIFACTS:
        (run / name).write_text("", encoding="utf-8")
    write_rows(run / "selected-tasks.jsonl", tasks)
    for slot in ("A", "B"):
        write_rows(
            run / f"reviewer-{slot}.blind.jsonl",
            [blank_review(task, rubric, slot) for task in tasks],
        )
    (run / "run-report.json").write_text(
        json.dumps({"run_id": "0" * 20, "rubric_sha256": rubric["config_sha256"]}),
        encoding="utf-8",
    )
    hashes = {
        name: hashlib.sha256((run / name).read_bytes()).hexdigest()
        for name in EXPECTED_ARTIFACTS
    }
    (run / "artifact-hashes.json").write_text(json.dumps(hashes), encoding="utf-8")
    return run, tasks


def completed(task: dict, rubric: dict, slot: str) -> dict:
    record = blank_review(task, rubric, slot)
    record.update(
        review_status="completed",
        reviewer_id=f"synthetic-{slot}",
        rationale="Synthetic unit-test labels are not genuine study evidence.",
        evidence_references=["synthetic-fixture"],
        reviewed_at_utc="2026-10-29T00:00:00Z",
        exposure_label="insufficient_evidence",
        workflow_label="insufficient_evidence",
    )
    record["dimension_ratings"] = {
        key: "insufficient_evidence" for key in record["dimension_ratings"]
    }
    return record
