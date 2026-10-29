"""Generate a frozen task-review pilot with blind queues and development-only hints."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.annotations import blank_review, validate_review
from humanbridge.pipeline import logical_hash
from humanbridge.pilot_sampling import sample_pilot
from humanbridge.task_screening import load_rubric, screen_task


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n"
                            for row in rows), encoding="utf-8")


def prepare(root: Path, output_parent: Path) -> tuple[Path, dict]:
    rubric = load_rubric(root / "config/task_rubric.json")
    core_report = json.loads((root / "docs/reports/core-data.json").read_text(encoding="utf-8"))
    cohort = json.loads((root / "config/review_cohort.json").read_text(encoding="utf-8"))
    if cohort["source_snapshot"] != core_report["snapshot_id"]:
        raise ValueError("Review cohort belongs to another snapshot")
    database = root / "data/processed/core.sqlite3"
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as db:
        # Freeze one read transaction so a concurrent local update cannot mix snapshots.
        db.execute("BEGIN")
        if logical_hash(db) != core_report["logical_sha256"]:
            raise ValueError("Core database differs from its validated snapshot")
        db.row_factory = sqlite3.Row
        tasks = [dict(row) for row in db.execute(
            "SELECT t.release_id,t.occupation_code,o.title AS occupation_title,"
            "t.task_id,t.statement AS task_text FROM task t JOIN occupation o "
            "USING (release_id,occupation_code) ORDER BY t.occupation_code,t.task_id")]
    sampled, split_report = sample_pilot(
        tasks, rubric, [item["occupation_code"] for item in cohort["occupations"]])
    engine_files = ["src/humanbridge/task_screening.py", "src/humanbridge/pilot_sampling.py",
                    "src/humanbridge/annotations.py", "scripts/prepare_task_pilot.py"]
    engine_hash = hashlib.sha256()
    for name in engine_files:
        engine_hash.update(name.encode())
        engine_hash.update((root / name).read_bytes())
    identity = {"source_snapshot": core_report["snapshot_id"],
                "core_logical_sha256": core_report["logical_sha256"],
                "rubric_sha256": rubric["config_sha256"],
                "cohort_sha256": hashlib.sha256((root / "config/review_cohort.json").read_bytes()).hexdigest(),
                "engine_sha256": engine_hash.hexdigest(),
                "selected_tasks": [(row["task_key"], row["split"]) for row in sampled]}
    run_id = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]
    output_parent.mkdir(parents=True, exist_ok=True)
    destination = output_parent / run_id
    with tempfile.TemporaryDirectory(dir=output_parent) as directory:
        stage = Path(directory) / "pilot"
        stage.mkdir()
        (stage / "SOURCE_NOTICE.md").write_text(
            "# Source attribution\n\n"
            "This review pilot includes task information from the O*NET 31.0 Database "
            "by the U.S. Department of Labor, Employment and Training Administration "
            "(USDOL/ETA), used under CC BY 4.0. O*NET is a trademark of USDOL/ETA.\n\n"
            "Source: https://www.onetcenter.org/database.html\n"
            "License: https://creativecommons.org/licenses/by/4.0/\n\n"
            "HumanBridge AI selected records and added split metadata, blank review "
            "fields and unvalidated lexical suggestions. USDOL/ETA has not approved, "
            "endorsed, or tested these modifications. Preserve this notice when "
            "sharing pilot materials. Machine suggestions are not human labels.\n",
            encoding="utf-8")
        suggestions = []
        for task in sampled:
            if task["split"] == "development":
                suggestions.append({**task, **screen_task(task["task_text"], rubric)})
        write_jsonl(stage / "machine-suggestions.development.jsonl", suggestions)
        write_jsonl(stage / "selected-tasks.jsonl", sampled)
        for slot in ("A", "B"):
            reviews = [blank_review(task, rubric, slot) for task in sampled]
            for review, task in zip(reviews, sampled):
                validate_review(review, task, rubric, slot)
            write_jsonl(stage / f"reviewer-{slot}.blind.jsonl", reviews)
        (stage / "split-manifest.json").write_text(json.dumps(split_report, indent=2) + "\n", encoding="utf-8")
        report = {
            "run_id": run_id, "method_version": rubric["method_version"],
            "rubric_version": rubric["rubric_version"],
            **{key: value for key, value in identity.items() if key != "selected_tasks"},
            "capability_assumption_date": rubric["capability_assumption_date"],
            "pilot": split_report,
            "development_machine_suggestions": len(suggestions),
            "development_review_routes": dict(sorted(Counter(row["review_route"] for row in suggestions).items())),
            "holdout_machine_suggestions": 0,
            "blind_records_per_reviewer": len(sampled), "completed_human_reviews": 0,
            "ai_exposure_scores_computed": 0, "human_dependency_scores_computed": 0,
            "performance_metrics": None,
            "status": "prepared_for_independent_review_not_validated",
        }
        (stage / "run-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in sorted(stage.iterdir())}
        (stage / "artifact-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
        if destination.exists():
            expected_files = {path.name for path in stage.iterdir()}
            if {path.name for path in destination.iterdir()} != expected_files:
                raise ValueError("Existing run has unexpected/missing artifacts")
            if any((destination / path.name).read_bytes() != path.read_bytes() for path in stage.iterdir()):
                raise ValueError("Existing immutable run differs; do not overwrite review work")
        else:
            stage.replace(destination)
    return destination, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/task-pilot")
    args = parser.parse_args()
    destination, report = prepare(ROOT, args.output.resolve())
    print(json.dumps({"run_directory": str(destination), "run_id": report["run_id"],
                      "selected_tasks": report["pilot"]["selected_tasks"],
                      "development_suggestions": report["development_machine_suggestions"],
                      "holdout_suggestions": 0, "completed_human_reviews": 0}, indent=2))


if __name__ == "__main__":
    main()
