"""Verify integrity rules that protect later ingestion and analysis."""
from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.executescript(
            (ROOT / "schema/001_initial.sql").read_text(encoding="utf-8")
        )
        self.db.execute(
            "INSERT INTO dataset_release VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("r1", "fixture", "test", "https://example.test", "2026-10-29",
             "a" * 64, "Synthetic test fixture, not source data"),
        )
        self.db.executemany(
            "INSERT INTO occupation VALUES (?, ?, ?, ?, ?)",
            [("r1", code, "fixture", code, None) for code in ("A", "B", "C")],
        )
        self.db.execute("INSERT INTO task VALUES ('r1', 'A', 't1', 'Fixture', NULL)")
        self.db.execute(
            "INSERT INTO analysis_run VALUES ('run1', 'test', '2026-10-29', "
            "'2026-10-29', '{}')"
        )
        self.db.execute("INSERT INTO analysis_run_input VALUES ('run1', 'r1')")

    def test_rejects_orphan_task(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO task VALUES ('r1', 'missing', 't2', 'x', NULL)")

    def test_rejects_duplicate_task(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO task VALUES ('r1', 'A', 't1', 'x', NULL)")

    def test_score_range_and_unknown_state(self) -> None:
        sql = "INSERT INTO task_score VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(sql, ("run1", "r1", "A", "t1", 101, 50,
                                 "augment", "{}", "[]", "Fixture"))
        self.db.execute(sql, ("run1", "r1", "A", "t1", None, None,
                              "insufficient_evidence", "{}", "[]", "Not measured"))
        self.assertIsNone(self.db.execute("SELECT ai_exposure FROM task_score").fetchone()[0])

    def test_rejects_self_transition_and_duplicate_rank(self) -> None:
        sql = "INSERT INTO transition VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(sql, ("run1", "r1", "A", "A", 1, None, "{}", "[]", "{}"))
        self.db.execute(sql, ("run1", "r1", "A", "B", 1, None, "{}", "[]", "{}"))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(sql, ("run1", "r1", "A", "C", 1, None, "{}", "[]", "{}"))

    def test_county_codes_retain_leading_zero(self) -> None:
        self.db.execute("INSERT INTO geography VALUES ('01001', '2024', 'county', 'Fixture')")
        sql = "INSERT INTO county_observation VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        self.db.execute(sql, ("r1", "01001", "2024", "test", "fixture", None, None, "missing"))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(sql, ("r1", "1001", "2024", "test", "fixture", None, None, "missing"))

    def test_rejects_score_from_unregistered_snapshot(self) -> None:
        self.db.execute(
            "INSERT INTO analysis_run VALUES ('run2', 'test', '2026-10-29', "
            "'2026-10-29', '{}')"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO task_score VALUES ('run2', 'r1', 'A', 't1', "
                "NULL, NULL, 'insufficient_evidence', '{}', '[]', 'Fixture')"
            )

    def test_rejects_unknown_scale(self) -> None:
        self.db.execute("INSERT INTO element VALUES ('r1', 'e1', 'skill', 'Fixture', NULL)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO occupation_element_rating VALUES "
                "('r1', 'A', 'e1', 'unknown', '', 1, NULL)"
            )


if __name__ == "__main__":
    unittest.main()
