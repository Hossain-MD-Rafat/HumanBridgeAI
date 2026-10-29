"""Synthetic UI fixture. These records must never be used as study evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.annotations import blank_review
from humanbridge.task_screening import load_rubric
from humanbridge.workbench import render


def fixture_payload() -> dict:
    rubric = load_rubric(ROOT / "config/task_rubric.json")
    tasks = [
        {
            "task_key": "synthetic:fixture:1",
            "release_id": "synthetic",
            "occupation_code": "fixture",
            "occupation_title": "Synthetic browser fixture",
            "task_id": "1",
            "split": "development",
            "task_text": "Synthetic task: review a fictional document. </script><img src=x onerror=alert(1)>",
        },
        {
            "task_key": "synthetic:fixture:2",
            "release_id": "synthetic",
            "occupation_code": "fixture",
            "occupation_title": "Synthetic browser fixture",
            "task_id": "2",
            "split": "holdout",
            "task_text": "Synthetic task: inspect a fictional object.",
        },
    ]
    return {
        "format": "humanbridge-offline-workbench-v1",
        "run_id": "synthetic-ui-fixture-v1",
        "slot": "A",
        "rubric_version": rubric["rubric_version"],
        "rubric_sha256": rubric["config_sha256"],
        "capability_scope": rubric["capability_scope"],
        "dimensions": rubric["dimensions"],
        "dimension_labels": rubric["human_dimension_labels"],
        "exposure_labels": rubric["human_exposure_labels"],
        "workflow_labels": rubric["human_workflow_labels"],
        "records": [blank_review(task, rubric, "A") for task in tasks],
        "source_notice": "Synthetic test data only. Not source tasks or genuine human reviews.",
    }


if __name__ == "__main__":
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render(fixture_payload(), ROOT / "src/humanbridge"), encoding="utf-8"
    )
    print(output)
