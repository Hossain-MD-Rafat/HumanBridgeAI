"""Check the Phase 0 catalog, local documentation links and SQLite schema.

Run from any directory with: python scripts/check_foundation.py
Uses no network, data downloads or third-party dependencies.
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Fail clearly when the committed foundation is internally inconsistent."""
    catalog = json.loads((ROOT / "config/datasets.json").read_text(encoding="utf-8"))
    datasets = catalog["datasets"]
    ids = [item["id"] for item in datasets]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate dataset IDs")
    required = {
        "id", "name", "phase", "release", "publisher", "landing_url",
        "dictionary_url", "license_review_status", "acquisition_status",
    }
    for item in datasets:
        missing = required - item.keys()
        if missing:
            raise ValueError(f"{item['id']}: missing fields {sorted(missing)}")
        for url in [item["landing_url"], *item["download_urls"]]:
            if not url.startswith("https://"):
                raise ValueError(f"{item['id']}: expected HTTPS source URL")
        if item["acquisition_status"] == "not_downloaded" and item["sha256"]:
            raise ValueError(f"{item['id']}: unexpected hash for unacquired asset")

    broken = []
    for document in [ROOT / "README.md", *(ROOT / "docs").rglob("*.md")]:
        if document.name == "master-brain.md":
            continue  # Owner's original concept is preserved verbatim.
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if path and not (document.parent / path).exists():
                broken.append(f"{document.relative_to(ROOT)} -> {target}")
    if broken:
        raise ValueError("Broken local documentation links: " + "; ".join(broken))

    with sqlite3.connect(":memory:") as connection:
        for migration in sorted((ROOT / "schema").glob("*.sql")):
            connection.executescript(migration.read_text(encoding="utf-8"))
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Schema foreign-key check failed")
    snapshot = json.loads((ROOT / "config/core_snapshot.json").read_text(encoding="utf-8"))
    for asset in snapshot["assets"]:
        manifest = json.loads((ROOT / asset["manifest_path"]).read_text(encoding="utf-8"))
        if manifest["dataset_id"] != asset["dataset_id"] or manifest["sha256"] != asset["sha256"]:
            raise ValueError("Snapshot/manifest identity mismatch")
    print(f"Foundation checks passed: {len(datasets)} catalog entries; "
          "local documentation links; executable SQLite schema. "
          "No network or empirical validation performed.")


if __name__ == "__main__":
    main()
