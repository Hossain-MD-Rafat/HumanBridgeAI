"""Build the pinned local occupation/task/skill database and its coverage report."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.pipeline import build


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/core.sqlite3")
    parser.add_argument("--report", type=Path, default=ROOT / "docs/reports/core-data.json")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    report = build(ROOT, args.output.resolve(), replace=args.replace)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    logging.info("Counts: %s", report["counts"])
    logging.info("Coverage report: %s", args.report)


if __name__ == "__main__":
    main()
