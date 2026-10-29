"""Download/register core source assets without modifying existing snapshots."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.acquisition import CORE_IDS, acquire, verify_manifest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=(*CORE_IDS, "core"), default="core")
    parser.add_argument("--local-file", type=Path, help="Register an official manual download")
    parser.add_argument("--locked", action="store_true", help="Require the committed snapshot checksums")
    args = parser.parse_args()
    if args.local_file and args.dataset == "core":
        parser.error("--local-file requires one --dataset")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    locked = {}
    if args.locked:
        snapshot = json.loads((ROOT / "config/core_snapshot.json").read_text(encoding="utf-8"))
        locked = {item["dataset_id"]: item for item in snapshot["assets"]}
    failures = []
    for dataset in CORE_IDS if args.dataset == "core" else (args.dataset,):
        try:
            expected = locked.get(dataset, {}).get("sha256")
            if args.locked and expected is None:
                raise ValueError("Dataset is not pinned in the core snapshot")
            if args.locked and args.local_file is None:
                manifest_path = ROOT / locked[dataset]["manifest_path"]
                if manifest_path.exists():
                    try:
                        manifest, _ = verify_manifest(ROOT, manifest_path)
                        if manifest["sha256"] != expected:
                            raise ValueError("Manifest differs from lock")
                        logging.info("Verified cached %s", dataset)
                        continue
                    except FileNotFoundError:
                        pass  # A clone has metadata but must acquire the raw bytes.
            acquire(ROOT, dataset, args.local_file, expected_sha256=expected)
        except Exception as error:
            logging.error("%s: %s", dataset, error)
            failures.append(dataset)
    if failures:
        raise SystemExit("Not acquired: " + ", ".join(failures))


if __name__ == "__main__":
    main()
