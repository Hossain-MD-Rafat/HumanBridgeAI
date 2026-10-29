"""Build one offline review workbench; open the resulting HTML in a local browser."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.workbench import build_workbench


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--slot", choices=("A", "B"), required=True)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/review-workbench"
    )
    args = parser.parse_args()
    output = build_workbench(
        ROOT, args.run_directory.resolve(), args.slot, args.output.resolve()
    )
    print(output)


if __name__ == "__main__":
    main()
