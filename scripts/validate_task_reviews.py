"""Validate returned blind review files without reporting model accuracy."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.review_io import read_pair
from humanbridge.task_screening import load_rubric


def validate(
    run: Path,
    first_path: Path,
    second_path: Path,
    rubric: dict,
    require_complete: bool = False,
) -> dict:
    report, expected, first, second = read_pair(
        run, first_path, second_path, rubric, require_complete
    )
    complete = sum(
        row["review_status"] == "completed"
        for queue in (first, second)
        for row in queue.values()
    )
    return {
        "run_id": report["run_id"],
        "expected_tasks": len(expected),
        "review_records": len(expected) * 2,
        "completed_review_records": complete,
        "performance_metrics": None,
        "note": "Record integrity only. Independent review and adjudication are separate requirements.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--reviewer-a", type=Path)
    parser.add_argument("--reviewer-b", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    rubric = load_rubric(ROOT / "config/task_rubric.json")
    result = validate(
        args.run_directory,
        args.reviewer_a or args.run_directory / "reviewer-A.blind.jsonl",
        args.reviewer_b or args.run_directory / "reviewer-B.blind.jsonl",
        rubric,
        args.require_complete,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
