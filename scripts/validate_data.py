"""Check the locally built database against its frozen inputs and published report."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.acquisition import verify_manifest
from humanbridge.pipeline import COUNT_TABLES, logical_hash


def main() -> None:
    report = json.loads((ROOT / "docs/reports/core-data.json").read_text(encoding="utf-8"))
    snapshot = json.loads((ROOT / "config/core_snapshot.json").read_text(encoding="utf-8"))
    if report["inputs"] != snapshot["assets"]:
        raise ValueError("Report does not describe the current snapshot")
    for asset in snapshot["assets"]:
        manifest, _ = verify_manifest(ROOT, ROOT / asset["manifest_path"])
        if manifest["sha256"] != asset["sha256"]:
            raise ValueError("Manifest and snapshot checksums differ")
    database = ROOT / "data/processed/core.sqlite3"
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as db:
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Orphaned records")
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Database integrity failure")
        for table in COUNT_TABLES:
            count = db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            if count != report["counts"][table]:
                raise ValueError(f"Report count differs for {table}")
        if logical_hash(db) != report["logical_sha256"]:
            raise ValueError("Logical data fingerprint differs from report")
        expected = {asset["sha256"] for asset in snapshot["assets"]}
        if {row[0] for row in db.execute("SELECT sha256 FROM dataset_release")} != expected:
            raise ValueError("Database source snapshots differ from lock")
        quality = {
            "snapshot_id": snapshot["snapshot_id"],
            "occupations_with_tasks": db.execute(
                "SELECT COUNT(DISTINCT occupation_code) FROM task").fetchone()[0],
            "occupations_with_skill_ratings": db.execute(
                "SELECT COUNT(DISTINCT occupation_code) FROM occupation_element_rating "
                "WHERE element_id LIKE '2.A.%' OR element_id LIKE '2.B.%'").fetchone()[0],
            "occupations_with_usable_mapped_median_wage": db.execute(
                "SELECT COUNT(DISTINCT c.source_code) FROM occupation_crosswalk c "
                "JOIN labor_statistic s ON c.target_code=s.occupation_code "
                "AND c.target_taxonomy=s.taxonomy WHERE s.metric='A_MEDIAN' "
                "AND s.value IS NOT NULL AND s.quality_flag IS NULL").fetchone()[0],
            "foreign_key_violations": 0,
            "logical_sha256": report["logical_sha256"],
            "note": "Source integrity and coverage checks; no empirical model validation.",
        }
    output = ROOT / "docs/reports/data-quality.json"
    output.write_text(json.dumps(quality, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(quality, indent=2))


if __name__ == "__main__":
    main()
