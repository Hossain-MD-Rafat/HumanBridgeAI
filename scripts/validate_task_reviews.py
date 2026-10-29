"""Validate returned blind review files without reporting model accuracy."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.annotations import validate_pair, validate_review
from humanbridge.task_screening import load_rubric


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate(run: Path, first_path: Path, second_path: Path, rubric: dict,
             require_complete: bool = False) -> dict:
    hashes = json.loads((run / "artifact-hashes.json").read_text(encoding="utf-8"))
    for name, checksum in hashes.items():
        if Path(name).name != name or hashlib.sha256((run / name).read_bytes()).hexdigest() != checksum:
            raise ValueError("Frozen run artifact differs from its manifest")
    report = json.loads((run / "run-report.json").read_text(encoding="utf-8"))
    if report["rubric_sha256"] != rubric["config_sha256"]:
        raise ValueError("Review must be validated with the frozen run's rubric")
    tasks = read_jsonl(run / "selected-tasks.jsonl")
    expected = {task["task_key"]: task for task in tasks}
    files = []
    for path, slot in ((first_path, "A"), (second_path, "B")):
        rows = read_jsonl(path)
        by_key = {row["task_key"]: row for row in rows}
        if len(by_key) != len(rows) or set(by_key) != set(expected):
            raise ValueError("Returned queue has duplicate, missing or unknown task keys")
        for key, row in by_key.items():
            validate_review(row, expected[key], rubric, slot, require_complete)
        files.append(by_key)
    for key in expected:
        validate_pair(files[0][key], files[1][key])
    complete = sum(row["review_status"] == "completed" for queue in files for row in queue.values())
    return {"run_id": report["run_id"], "expected_tasks": len(expected),
            "review_records": len(expected) * 2, "completed_review_records": complete,
            "performance_metrics": None,
            "note": "Record integrity only. Independent review and adjudication are separate requirements."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--reviewer-a", type=Path)
    parser.add_argument("--reviewer-b", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    rubric = load_rubric(ROOT / "config/task_rubric.json")
    result = validate(args.run_directory,
                      args.reviewer_a or args.run_directory / "reviewer-A.blind.jsonl",
                      args.reviewer_b or args.run_directory / "reviewer-B.blind.jsonl",
                      rubric, args.require_complete)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
