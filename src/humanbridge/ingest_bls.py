"""Import observed BLS workbook contracts and official mappings without title joins."""
from __future__ import annotations

import sqlite3
import zipfile
from pathlib import Path

from humanbridge.excel import records
from humanbridge.ingest_common import code, number


def wages(db: sqlite3.Connection, asset: Path, release: str) -> int:
    """Retain detailed national cross-industry/all-ownership OEWS facts."""
    with zipfile.ZipFile(asset) as archive:
        members = [name for name in archive.namelist() if name.endswith(".xlsx")]
    if len(members) != 1:
        raise ValueError("Unexpected OEWS archive layout")
    count = 0
    for row in records(asset, members[0], required=("OCC_CODE", "O_GROUP", "A_MEDIAN", "TOT_EMP")):
        if row["O_GROUP"] != "detailed":
            continue
        if (str(row["AREA"]), str(row["NAICS"]), str(row["OWN_CODE"])) != ("99", "000000", "1235"):
            raise ValueError("Unexpected national OEWS universe")
        occupation = code(row["OCC_CODE"])
        db.execute("INSERT INTO source_occupation VALUES (?, ?, ?, ?)",
                   (release, occupation, "SOC 2018", row["OCC_TITLE"]))
        metrics = {"TOT_EMP": "jobs", "A_MEDIAN": "USD/year", "A_MEAN": "USD/year",
                   "H_MEDIAN": "USD/hour", "EMP_PRSE": "percent relative standard error"}
        for metric, unit in metrics.items():
            value, flag = number(row[metric])
            db.execute("INSERT INTO labor_statistic VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (release, "SOC 2018", occupation, "US", "national",
                        "OEWS cross-industry; ownership 1235", metric, "2025-05",
                        unit, value, flag))
        count += 1
    return count


def projections(db: sqlite3.Connection, asset: Path, release: str) -> int:
    """Keep projection employment/openings in source thousands, with typed preparation."""
    title = "2025 National Employment Matrix title"
    identifier = "2025 National Employment Matrix code"
    metrics = {
        "Employment, 2025": ("employment_base", "2025", "thousand jobs"),
        "Employment, 2035": ("employment_projected", "2035", "thousand jobs"),
        "Employment change, percent, 2025–35": ("growth_percent", "2025-2035", "percent"),
        "Occupational openings, 2025–35 annual average": ("annual_openings", "2025-2035", "thousand openings/year"),
    }
    count = 0
    for row in records(asset, sheet="Table 1.2", required=(identifier, title, "Occupation type", *metrics),
                       allowed_duplicates=("Related Occupational Outlook Handbook (OOH) content",)):
        if row["Occupation type"] != "Line item":
            continue
        occupation = code(row[identifier])
        db.execute("INSERT INTO source_occupation VALUES (?, ?, ?, ?)",
                   (release, occupation, "NEM 2025", row[title].strip()))
        for column, (metric, period, unit) in metrics.items():
            value, flag = number(row[column])
            db.execute("INSERT INTO labor_statistic VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (release, "NEM 2025", occupation, "US", "national",
                        "NEM total employment including self-employed", metric,
                        period, unit, value, flag))
        db.execute("INSERT INTO preparation_requirement VALUES (?, ?, ?, ?, ?)",
                   (release, occupation, row["Typical education needed for entry"],
                    row["Work experience in a related occupation"],
                    row["Typical on-the-job training needed to attain competency in the occupation"]))
        count += 1
    return count


def crosswalk(db: sqlite3.Connection, asset: Path, release: str, nem: bool = False) -> int:
    """Import every official correspondence, leaving allocation weights unknown."""
    source = "O*NET-SOC code" if nem else "O*NET-SOC 2019 Code"
    target = "NEM Code" if nem else "2018 SOC Code"
    count = 0
    for row in records(asset, required=(source, target)):
        # Missing-target rows are retained in the source; not fabricated as mappings.
        if row[source] is None or row[target] is None:
            raise ValueError("Missing code in crosswalk; review source before proceeding")
        db.execute("INSERT INTO occupation_crosswalk VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (release, "O*NET-SOC 2019", code(row[source], True),
                    "NEM 2025" if nem else "SOC 2018", code(row[target]),
                    "official_correspondence", None))
        count += 1
    return count
