"""Strict source conversions shared by release-specific importers."""
from __future__ import annotations

import json
import math
import re
import sqlite3


def code(value: object, extended: bool = False) -> str:
    """Validate occupation strings without truncating or guessing mappings."""
    text = str(value).strip()
    pattern = r"\d{2}-\d{4}\.\d{2}" if extended else r"\d{2}-\d{4}"
    if not re.fullmatch(pattern, text):
        raise ValueError(f"Unexpected occupation code: {text!r}")
    return text


def number(value: object) -> tuple[float | None, str | None]:
    """Retain missing/suppression tokens; reject unrecognized text instead of zeroing."""
    if value is None or value == "":
        return None, "missing"
    if value in ("*", "**", "#", "—", "–", "-", "N/A"):
        return None, f"source_marker:{value}"
    if isinstance(value, bool):
        raise ValueError("Boolean is not a source measurement")
    result = float(str(value).replace(",", ""))
    if not math.isfinite(result):
        raise ValueError("Nonfinite source measurement")
    return result, None


def metadata(row: dict) -> str:
    """Preserve original quality and sampling fields outside the logical value."""
    names = ("N", "Standard Error", "Lower CI Bound", "Upper CI Bound",
             "Recommend Suppress", "Not Relevant", "Date", "Domain Source",
             "Incumbents Responding")
    return json.dumps({key: row[key] for key in names if key in row}, sort_keys=True)


def count_table(db: sqlite3.Connection, table: str) -> int:
    """Count an internal schema table; user input must never supply the name."""
    return db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
