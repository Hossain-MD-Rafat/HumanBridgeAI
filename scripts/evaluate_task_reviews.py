"""Evaluate paired human review agreement only after explicit research attestations."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.review_evaluation import analyze_reviews
from humanbridge.review_io import read_pair
from humanbridge.task_screening import load_rubric


def evaluate(
    root: Path,
    run: Path,
    first: Path,
    second: Path,
    split: str,
    attest_independent: bool,
    attest_semantic: bool,
    output_parent: Path,
) -> Path:
    """Attestations document protocol responsibility; software cannot prove independence."""
    if not attest_independent:
        raise ValueError(
            "Independent human review must be explicitly attested; empty or synthetic labels are not study evidence"
        )
    if split == "holdout" and not attest_semantic:
        raise ValueError("Holdout use requires semantic leakage review attestation")
    rubric = load_rubric(root / "config/task_rubric.json")
    run_report, tasks, a, b = read_pair(run, first, second, rubric)
    result, disagreements = analyze_reviews(tasks, a, b, rubric, split)
    result.update(
        {
            "evaluation_version": "human-agreement-v0.1.0",
            "source_run_id": run_report["run_id"],
            "rubric_sha256": rubric["config_sha256"],
            "response_A_sha256": hashlib.sha256(first.read_bytes()).hexdigest(),
            "response_B_sha256": hashlib.sha256(second.read_bytes()).hexdigest(),
            "independent_human_review_attested": True,
            "semantic_leakage_review_attested": attest_semantic,
            "attestation_note": "These declarations are the researcher's responsibility, not software verification of reviewer authenticity or independence.",
        }
    )
    engine = hashlib.sha256()
    for name in (
        "src/humanbridge/review_evaluation.py",
        "src/humanbridge/review_io.py",
        "src/humanbridge/annotations.py",
        "scripts/evaluate_task_reviews.py",
    ):
        engine.update(name.encode())
        engine.update((root / name).read_bytes())
    result["evaluator_sha256"] = engine.hexdigest()
    content = json.dumps(result, indent=2, sort_keys=True) + "\n"
    evaluation_id = hashlib.sha256(content.encode()).hexdigest()[:20]
    output = output_parent / evaluation_id
    output_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output_parent) as directory:
        stage = Path(directory) / "evaluation"
        stage.mkdir()
        (stage / "agreement.json").write_text(content, encoding="utf-8")
        (stage / "adjudication-queue.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in disagreements),
            encoding="utf-8",
        )
        if output.exists():
            if {p.name for p in output.iterdir()} != {
                p.name for p in stage.iterdir()
            } or any(
                (output / p.name).read_bytes() != p.read_bytes()
                for p in stage.iterdir()
            ):
                raise ValueError("Existing immutable evaluation differs")
        else:
            stage.replace(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument(
        "--split", choices=("development", "holdout"), default="development"
    )
    parser.add_argument("--attest-independent-human-review", action="store_true")
    parser.add_argument("--attest-semantic-leakage-reviewed", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/review-evaluation"
    )
    args = parser.parse_args()
    try:
        output = evaluate(
            ROOT,
            args.run_directory,
            args.reviewer_a,
            args.reviewer_b,
            args.split,
            args.attest_independent_human_review,
            args.attest_semantic_leakage_reviewed,
            args.output,
        )
    except ValueError as error:
        parser.exit(2, f"Evaluation not produced: {error}\n")
    print(output)


if __name__ == "__main__":
    main()
