"""Explore occupation skill-profile candidates with explicit source-context filters."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.skill_transitions import rank_candidates
from humanbridge.transition_data import load_transition_data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("occupation_code", help="Full O*NET-SOC code, e.g. 43-3031.00")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-national-median", type=float)
    parser.add_argument("--min-median-retention", type=float)
    parser.add_argument(
        "--allowed-education",
        action="append",
        help="Repeat exact BLS entry-education categories",
    )
    parser.add_argument(
        "--allowed-related-experience",
        action="append",
        help="Repeat exact BLS related-work-experience categories",
    )
    parser.add_argument(
        "--database", type=Path, default=ROOT / "data/processed/core.sqlite3"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optionally save an immutable content-identified result",
    )
    args = parser.parse_args()
    config_path = ROOT / "config/skill_transition.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    try:
        data = load_transition_data(ROOT, args.database, config)
        result = rank_candidates(
            args.occupation_code,
            data.profiles,
            data.features,
            data.names,
            data.contexts,
            config,
            args.top_k,
            args.min_national_median,
            args.min_median_retention,
            args.allowed_education,
            args.allowed_related_experience,
        )
    except ValueError as error:
        parser.exit(2, f"Candidate analysis not produced: {error}\n")
    engine = hashlib.sha256()
    for name in (
        "src/humanbridge/skill_transitions.py",
        "src/humanbridge/transition_data.py",
        "scripts/recommend_transitions.py",
    ):
        engine.update(name.encode())
        engine.update((ROOT / name).read_bytes())
    result.update(
        {
            "method_version": config["method_version"],
            "source_snapshot": config["source_snapshot"],
            "core_logical_sha256": data.audit["core_logical_sha256"],
            "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
            "engine_sha256": engine.hexdigest(),
            "status": "unvalidated_occupation_profile_baseline",
        }
    )
    content = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output_dir:
        output = (
            args.output_dir
            / hashlib.sha256(content.encode()).hexdigest()[:20]
            / "candidates.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() and output.read_text(encoding="utf-8") != content:
            raise ValueError("Existing result differs; refusing to overwrite")
        if not output.exists():
            output.write_text(content, encoding="utf-8")
    print(content, end="")


if __name__ == "__main__":
    main()
