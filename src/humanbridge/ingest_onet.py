"""Normalize the inspected O*NET 31.0 Excel contract into source-linked tables."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from humanbridge.excel import member_name, records
from humanbridge.ingest_common import code, metadata, number

LOGGER = logging.getLogger(__name__)
RATING_FILES = {
    "Essential Skills.xlsx": "essential_skill",
    "Transferable Skills.xlsx": "transferable_skill",
    "Abilities.xlsx": "ability",
    "Knowledge.xlsx": "knowledge",
    "Work Activities.xlsx": "activity",
    "Work Context.xlsx": "context",
    "Work Styles.xlsx": "work_style",
}


def domain(element_id: str) -> str:
    for prefix, label in (("2.A", "essential_skill"), ("2.B", "transferable_skill"),
                          ("1.A", "ability"), ("2.C", "knowledge"),
                          ("4.A", "activity"), ("4.C", "context"),
                          ("1.D", "work_style")):
        if element_id == prefix or element_id.startswith(prefix + "."):
            return label
    return "reference"


def load(db: sqlite3.Connection, asset: Path, release: str) -> dict:
    """Import source facts only; create no exposure or personal-skill estimates."""
    def table(filename: str, required: tuple[str, ...]):
        return records(asset, member_name(asset, filename), required=required)

    for row in table("Occupation Data.xlsx", ("O*NET-SOC Code", "Title", "Description")):
        db.execute("INSERT INTO occupation VALUES (?, ?, ?, ?, ?)",
                   (release, code(row["O*NET-SOC Code"], True), "O*NET-SOC 2019",
                    row["Title"], row["Description"]))
    for row in table("Scales Reference.xlsx", ("Scale ID", "Scale Name", "Minimum", "Maximum")):
        db.execute("INSERT INTO scale VALUES (?, ?, ?, ?, ?)",
                   (release, row["Scale ID"], row["Scale Name"], row["Minimum"], row["Maximum"]))
    for row in table("Content Model Reference.xlsx", ("Element ID", "Element Name", "Description")):
        db.execute("INSERT INTO element VALUES (?, ?, ?, ?, ?)",
                   (release, row["Element ID"], domain(row["Element ID"]),
                    row["Element Name"], row["Description"]))
    for row in table("Task Statements.xlsx", ("O*NET-SOC Code", "Task ID", "Task", "Task Type")):
        db.execute("INSERT INTO task VALUES (?, ?, ?, ?, ?, ?)",
                   (release, code(row["O*NET-SOC Code"], True), str(row["Task ID"]),
                    row["Task"], row["Task Type"], metadata(row)))

    source_counts = {}
    for filename in ("Task Ratings.xlsx", *RATING_FILES):
        task_level = filename == "Task Ratings.xlsx"
        entity = "Task ID" if task_level else "Element ID"
        count = 0
        for row in table(filename, ("O*NET-SOC Code", entity, "Scale ID", "Data Value")):
            if not task_level and domain(row[entity]) != RATING_FILES[filename]:
                raise ValueError(f"Unexpected element domain in {filename}: {row[entity]}")
            value, flag = number(row["Data Value"])
            category = "" if row.get("Category") is None else str(row["Category"])
            suppressed = row.get("Recommend Suppress") == "Y"
            quality = "suppress" if suppressed else flag
            target = "task_rating" if task_level else "occupation_element_rating"
            db.execute(f"INSERT INTO {target} VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (release, code(row["O*NET-SOC Code"], True), str(row[entity]),
                        row["Scale ID"], category, value, quality, metadata(row)))
            count += 1
        source_counts[filename] = count
        LOGGER.info("Imported %s: %d rows", filename, count)

    for row in table("Job Zones.xlsx", ("O*NET-SOC Code", "Job Zone")):
        db.execute("INSERT INTO occupation_job_zone VALUES (?, ?, ?, ?)",
                   (release, code(row["O*NET-SOC Code"], True), row["Job Zone"], metadata(row)))
    for row in table("Related Occupations.xlsx", ("O*NET-SOC Code", "Related O*NET-SOC Code")):
        db.execute("INSERT INTO related_occupation VALUES (?, ?, ?, ?, ?)",
                   (release, code(row["O*NET-SOC Code"], True),
                    code(row["Related O*NET-SOC Code"], True),
                    row["Relatedness Tier"], row["Index"]))
    for row in table("Job Titles.xlsx", ("O*NET-SOC Code", "Job Title", "Source(s)")):
        db.execute("INSERT INTO occupation_alias VALUES (?, ?, ?, ?)",
                   (release, code(row["O*NET-SOC Code"], True), row["Job Title"], row["Source(s)"]))

    # Percentage scales and level scales use different bounds from the source dictionary.
    for target in ("task_rating", "occupation_element_rating"):
        invalid = db.execute(
            f"SELECT COUNT(*) FROM {target} r JOIN scale s "
            "ON r.release_id=s.release_id AND r.scale_id=s.scale_id "
            "WHERE r.value IS NOT NULL AND "
            "(r.value < s.minimum - 0.001 OR r.value > s.maximum + 0.001)"
        ).fetchone()[0]
        if invalid:
            raise ValueError(f"{target}: {invalid} values outside source scale bounds")
    return source_counts
