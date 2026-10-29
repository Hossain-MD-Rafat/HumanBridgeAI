"""Validate the browser export against the same Python contract used for real reviews.

Only a synthetic browser fixture is accepted here; this script creates no study evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.annotations import validate_review
from humanbridge.task_screening import load_rubric
from workbench_fixture import fixture_payload


if __name__ == "__main__":
    rows = [
        json.loads(line)
        for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    ]
    originals = fixture_payload()["records"]
    if len(rows) != len(originals):
        raise ValueError("Unexpected browser fixture record count")
    rubric = load_rubric(ROOT / "config/task_rubric.json")
    for row, task in zip(rows, originals):
        validate_review(row, task, rubric, "A")
    if sum(row["review_status"] == "completed" for row in rows) != 1:
        raise ValueError("Expected exactly one synthetic completed browser test record")
    print(
        "Synthetic browser export passes the Python review contract; not study evidence."
    )
