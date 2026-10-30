"""Exercise source-quality and unit propagation through a tiny real SQLite schema."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.pipeline import logical_hash
from humanbridge.transition_data import load_transition_data


class TransitionDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "fixture.sqlite3"
        (self.root / "docs/reports").mkdir(parents=True)
        self.config = {
            "source_snapshot": "synthetic",
            "feature_ids": ["2.A.1.a", "2.B.1.a"],
            "expected_skill_dimensions": 2,
            "importance_scale_id": "IM",
            "importance_minimum": 1,
            "importance_maximum": 5,
        }
        with sqlite3.connect(self.db) as d:
            for migration in sorted((ROOT / "schema").glob("*.sql")):
                d.executescript(migration.read_text())
            ids = [
                "onet_31_0",
                "bls_oews_2025",
                "bls_projections_2025_2035",
                "onet_soc_crosswalk",
                "onet_nem_crosswalk",
            ]
            for dataset in ids:
                d.execute(
                    "INSERT INTO dataset_release VALUES (?,?,?,?,?,?,?)",
                    (
                        dataset,
                        dataset,
                        "synthetic",
                        "https://example.test",
                        "2026-10-29",
                        "a" * 64,
                        "Synthetic test only",
                    ),
                )
            d.execute(
                "INSERT INTO geography VALUES ('US','national','national','Synthetic')"
            )
            for scale, lo, hi in [("IM", 1, 5), ("LV", 0, 7)]:
                d.execute(
                    "INSERT INTO scale VALUES (?,?,?,?,?)",
                    ("onet_31_0", scale, scale, lo, hi),
                )
            for element, domain in [
                ("2.A.1.a", "essential_skill"),
                ("2.B.1.a", "transferable_skill"),
            ]:
                d.execute(
                    "INSERT INTO element VALUES (?,?,?,?,?)",
                    ("onet_31_0", element, domain, element, None),
                )
            for occupation in ["11-1011.00", "13-2011.00", "15-1252.00", "29-1141.00"]:
                d.execute(
                    "INSERT INTO occupation VALUES (?,?,?,?,?)",
                    ("onet_31_0", occupation, "O*NET-SOC 2019", occupation, None),
                )
                for element in self.config["feature_ids"]:
                    if occupation == "15-1252.00" and element == "2.B.1.a":
                        continue
                    suppressed = occupation == "29-1141.00" and element == "2.B.1.a"
                    d.execute(
                        "INSERT INTO occupation_element_rating VALUES (?,?,?,?,?,?,?,?)",
                        (
                            "onet_31_0",
                            occupation,
                            element,
                            "IM",
                            "",
                            3,
                            "suppress" if suppressed else None,
                            "{}",
                        ),
                    )
                d.execute(
                    "INSERT INTO occupation_element_rating VALUES (?,?,?,?,?,?,?,?)",
                    (
                        "onet_31_0",
                        occupation,
                        "2.A.1.a",
                        "LV",
                        "",
                        4,
                        None,
                        '{"Not Relevant":"Y"}',
                    ),
                )
            for occupation, target in [
                ("11-1011.00", "11-1011"),
                ("13-2011.00", "13-2011"),
            ]:
                for mapping, taxonomy in [
                    ("onet_soc_crosswalk", "SOC 2018"),
                    ("onet_nem_crosswalk", "NEM 2025"),
                ]:
                    d.execute(
                        "INSERT INTO occupation_crosswalk VALUES (?,?,?,?,?,?,?)",
                        (
                            mapping,
                            "O*NET-SOC 2019",
                            occupation,
                            taxonomy,
                            target,
                            "official_correspondence",
                            None,
                        ),
                    )
                for dataset, taxonomy in [
                    ("bls_oews_2025", "SOC 2018"),
                    ("bls_projections_2025_2035", "NEM 2025"),
                ]:
                    d.execute(
                        "INSERT INTO source_occupation VALUES (?,?,?,?)",
                        (dataset, target, taxonomy, target),
                    )
                d.execute(
                    "INSERT INTO preparation_requirement VALUES (?,?,?,?,?)",
                    (
                        "bls_projections_2025_2035",
                        target,
                        "High school diploma or equivalent",
                        "None",
                        "Short-term on-the-job training",
                    ),
                )
                wage = 100000 if target == "11-1011" else None
                d.execute(
                    "INSERT INTO labor_statistic VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        "bls_oews_2025",
                        "SOC 2018",
                        target,
                        "US",
                        "national",
                        "synthetic",
                        "A_MEDIAN",
                        "2025-05",
                        "USD/year",
                        wage,
                        None if wage else "source_marker:#",
                    ),
                )
                for metric, value, unit in [
                    ("growth_percent", 5, "percent"),
                    ("annual_openings", 2.5, "thousand openings/year"),
                ]:
                    d.execute(
                        "INSERT INTO labor_statistic VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (
                            "bls_projections_2025_2035",
                            "NEM 2025",
                            target,
                            "US",
                            "national",
                            "synthetic",
                            metric,
                            "2025-2035",
                            unit,
                            value,
                            None,
                        ),
                    )
            d.commit()
            fingerprint = logical_hash(d)
        (self.root / "docs/reports/core-data.json").write_text(
            json.dumps({"snapshot_id": "synthetic", "logical_sha256": fingerprint})
        )

    def test_incomplete_and_suppressed_profiles_are_excluded_not_zero_filled(
        self,
    ) -> None:
        data = load_transition_data(self.root, self.db, self.config)
        self.assertEqual(set(data.profiles), {"11-1011.00", "13-2011.00"})
        self.assertEqual(
            data.audit["excluded_profiles"]["15-1252.00"]["usable_importance_count"], 1
        )
        self.assertEqual(
            data.audit["excluded_profiles"]["29-1141.00"][
                "unusable_importance_elements"
            ],
            ["2.B.1.a"],
        )
        self.assertIsNone(data.profiles["11-1011.00"].levels["2.A.1.a"])

    def test_suppressed_wage_stays_unknown_and_openings_preserve_unit_conversion(
        self,
    ) -> None:
        data = load_transition_data(self.root, self.db, self.config)
        context = data.contexts["13-2011.00"]
        self.assertIsNone(context["wage"]["median_annual_wage"])
        self.assertEqual(context["wage"]["status"], "suppressed_or_unavailable")
        self.assertEqual(context["outlook"]["annual_openings"], 2500)
        self.assertEqual(context["outlook"]["annual_openings_unit"], "openings/year")
        self.assertEqual(
            context["outlook"]["mapping_evidence"][0]["record"]["annual_openings"][
                "value"
            ],
            2.5,
        )
        self.assertEqual(context["preparation"]["licensing"], "not_verified")

    def test_changed_snapshot_cannot_be_used_for_ranking(self) -> None:
        with sqlite3.connect(self.db) as d:
            d.execute(
                "UPDATE occupation SET title='Changed' WHERE occupation_code='11-1011.00'"
            )
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            load_transition_data(self.root, self.db, self.config)
