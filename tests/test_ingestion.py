"""Test actual source-format failure cases without network or third-party data."""
from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.excel import records
from humanbridge.ingest_common import code, number
from humanbridge.ingest_onet import domain
from humanbridge.pipeline import mapping_coverage


class SourceFormatTests(unittest.TestCase):
    def test_code_validation_never_truncates(self) -> None:
        self.assertEqual(code("13-2011.00", True), "13-2011.00")
        with self.assertRaises(ValueError):
            code("13-2011.00")

    def test_suppressed_and_missing_values_are_not_zero(self) -> None:
        for raw in (None, "", "*", "**", "#", "—"):
            value, flag = number(raw)
            self.assertIsNone(value)
            self.assertIsNotNone(flag)
        self.assertEqual(number(0), (0.0, None))
        self.assertEqual(number("12,300"), (12300.0, None))
        for raw in ("unrecognized", "NaN", "inf", True):
            with self.assertRaises(ValueError):
                number(raw)

    def test_explicit_duplicate_heading_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.xlsx"
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["Release-specific preamble"])
            sheet.append(["Code", "Link", "Link"])
            sheet.append(["A", "visible", "html"])
            workbook.save(path)
            workbook.close()
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                list(records(path, required=("Code",)))
            data = list(records(path, required=("Code",), allowed_duplicates=("Link",)))
            self.assertEqual(data, [{"Code": "A", "Link": "visible", "Link__2": "html"}])

    def test_missing_required_header_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changed.xlsx"
            workbook = openpyxl.Workbook()
            workbook.active.append(["Renamed source column"])
            workbook.save(path)
            workbook.close()
            with self.assertRaisesRegex(ValueError, "No expected header"):
                list(records(path, required=("Original column",)))

    def test_work_style_domain_uses_actual_content_model_prefix(self) -> None:
        self.assertEqual(domain("1.D.1.a"), "work_style")
        self.assertEqual(domain("1.C.1.a"), "reference")

    def test_mapping_reports_gaps_and_shared_aggregates(self) -> None:
        with sqlite3.connect(":memory:") as db:
            db.executescript(
                "CREATE TABLE occupation(occupation_code TEXT);"
                "CREATE TABLE source_occupation(release_id TEXT, code TEXT);"
                "CREATE TABLE occupation_crosswalk(mapping_release_id TEXT, "
                "source_code TEXT, target_code TEXT, target_taxonomy TEXT);"
            )
            db.executemany("INSERT INTO occupation VALUES (?)", [("A",), ("B",), ("C",), ("D",)])
            db.execute("INSERT INTO source_occupation VALUES ('wages','X')")
            db.executemany("INSERT INTO occupation_crosswalk VALUES ('mapping',?,?,'SOC')",
                           [("A", "X"), ("B", "X"), ("C", "missing")])
            report = mapping_coverage(db, "SOC", "mapping", "wages")
            self.assertEqual(report["with_target_data"], 2)
            self.assertEqual(report["unmapped_source_codes"], ["D"])
            self.assertEqual(report["mapped_without_target_data"], ["C"])
            self.assertEqual(report["targets_shared_by_multiple_source_occupations"], 1)
