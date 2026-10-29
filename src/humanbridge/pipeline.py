"""Build an atomic, validated local database from a pinned core snapshot."""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import tempfile
from pathlib import Path

from humanbridge import ingest_bls, ingest_onet
from humanbridge.acquisition import CORE_IDS, verify_manifest
from humanbridge.ingest_common import count_table

LOGGER = logging.getLogger(__name__)
COUNT_TABLES = (
    "dataset_release", "occupation", "task", "scale", "element",
    "occupation_element_rating", "task_rating", "occupation_job_zone",
    "occupation_alias", "related_occupation", "source_occupation",
    "preparation_requirement", "labor_statistic", "occupation_crosswalk",
)


def mapping_coverage(db: sqlite3.Connection, target_taxonomy: str,
                     mapping_release: str, target_release: str) -> dict:
    """Report source and target availability separately, including unmapped codes."""
    source_codes = {row[0] for row in db.execute("SELECT occupation_code FROM occupation")}
    targets = {row[0] for row in db.execute(
        "SELECT code FROM source_occupation WHERE release_id=?", (target_release,))}
    relationships: dict[str, set[str]] = {}
    reverse: dict[str, set[str]] = {}
    for source, target in db.execute(
        "SELECT source_code, target_code FROM occupation_crosswalk "
        "WHERE mapping_release_id=? AND target_taxonomy=?", (mapping_release, target_taxonomy)
    ):
        relationships.setdefault(source, set()).add(target)
        reverse.setdefault(target, set()).add(source)
    mapped = source_codes & relationships.keys()
    available = {source for source in mapped if relationships[source] & targets}
    return {
        "source_occupations": len(source_codes), "mapped_occupations": len(mapped),
        "with_target_data": len(available),
        "unmapped_source_codes": sorted(source_codes - mapped),
        "mapped_without_target_data": sorted(mapped - available),
        "crosswalk_sources_outside_catalog": sorted(relationships.keys() - source_codes),
        "one_source_to_multiple_targets": {
            key: sorted(value) for key, value in sorted(relationships.items())
            if key in source_codes and len(value) > 1
        },
        "targets_shared_by_multiple_source_occupations": sum(
            len(value & source_codes) > 1 for value in reverse.values()),
        "note": "No employment allocation across specializations is inferred.",
    }


def logical_hash(db: sqlite3.Connection) -> str:
    """Fingerprint ordered logical rows, independent of SQLite file layout."""
    checksum = hashlib.sha256()
    for table in COUNT_TABLES:
        columns = len(db.execute(f'PRAGMA table_info("{table}")').fetchall())
        order = ", ".join(str(i + 1) for i in range(columns))
        checksum.update(table.encode())
        for row in db.execute(f'SELECT * FROM "{table}" ORDER BY {order}'):
            checksum.update((json.dumps(row, ensure_ascii=False) + "\n").encode())
    return checksum.hexdigest()


def build(root: Path, output: Path, replace: bool = False) -> dict:
    """Publish the database only if imports, ranges, keys and mapping audits pass."""
    if output.exists() and not replace:
        raise FileExistsError("Derived database exists; use --replace to rebuild it")
    snapshot = json.loads((root / "config/core_snapshot.json").read_text(encoding="utf-8"))
    ids = [item["dataset_id"] for item in snapshot["assets"]]
    if sorted(ids) != sorted(CORE_IDS):
        raise ValueError("Snapshot must contain exactly the five core assets")
    assets = {}
    for item in snapshot["assets"]:
        manifest, asset = verify_manifest(root, root / item["manifest_path"])
        if manifest["dataset_id"] != item["dataset_id"] or manifest["sha256"] != item["sha256"]:
            raise ValueError("Snapshot and manifest identity mismatch")
        assets[item["dataset_id"]] = (manifest, asset, item)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as directory:
        temporary = Path(directory) / "core.sqlite3"
        db = sqlite3.connect(temporary)
        try:
            for migration in sorted((root / "schema").glob("*.sql")):
                db.executescript(migration.read_text(encoding="utf-8"))
            release_ids = {}
            for dataset_id, (manifest, asset, item) in assets.items():
                release = dataset_id + "-" + manifest["sha256"][:16]
                release_ids[dataset_id] = release
                db.execute("INSERT INTO dataset_release VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (release, dataset_id, item["observed_release"],
                            manifest["resolved_download_url"], manifest["retrieved_at_utc"],
                            manifest["sha256"], manifest["license_review_status"]))
            db.execute("INSERT INTO geography VALUES ('US', 'national', 'national', 'United States')")
            source_counts = ingest_onet.load(db, assets["onet_31_0"][1], release_ids["onet_31_0"])
            wages_count = ingest_bls.wages(db, assets["bls_oews_2025"][1], release_ids["bls_oews_2025"])
            projections_count = ingest_bls.projections(
                db, assets["bls_projections_2025_2035"][1], release_ids["bls_projections_2025_2035"])
            for dataset, nem in (("onet_soc_crosswalk", False), ("onet_nem_crosswalk", True)):
                ingest_bls.crosswalk(db, assets[dataset][1], release_ids[dataset], nem)
            if db.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("Broken source foreign keys")
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("SQLite integrity check failed")
            # Empty or unexpectedly partial imports must never be promoted as a usable snapshot.
            counts = {table: count_table(db, table) for table in COUNT_TABLES}
            if any(count == 0 for count in counts.values()):
                raise ValueError("Unexpected empty source table")
            coverage = {
                "OEWS": mapping_coverage(db, "SOC 2018", release_ids["onet_soc_crosswalk"],
                                         release_ids["bls_oews_2025"]),
                "projections": mapping_coverage(db, "NEM 2025", release_ids["onet_nem_crosswalk"],
                                                release_ids["bls_projections_2025_2035"]),
            }
            report = {
                "snapshot_id": snapshot["snapshot_id"], "inputs": snapshot["assets"],
                "counts": counts, "source_rating_rows": source_counts,
                "element_rating_domain_sources": dict(db.execute(
                    "SELECT json_extract(source_metadata_json, '$.\"Domain Source\"'), COUNT(*) "
                    "FROM occupation_element_rating GROUP BY 1 ORDER BY 1").fetchall()),
                "oews_detailed_occupations": wages_count,
                "projection_detailed_occupations": projections_count,
                "coverage": coverage, "foreign_key_violations": 0,
                "logical_sha256": logical_hash(db),
                "limits": ["No validated AI exposure or HVI scores",
                           "Occupation skills are not personal skills",
                           "Related occupations are not observed worker transitions",
                           "Not all downloaded O*NET workbooks are imported"],
            }
            db.commit()
        finally:
            db.close()
        temporary.replace(output)
    LOGGER.info("Published %s", output)
    return report
