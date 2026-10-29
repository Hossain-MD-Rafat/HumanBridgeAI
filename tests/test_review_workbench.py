"""Verify blinding and safe offline bundling; browser behavior has an optional smoke check."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.workbench import render, script_json
from workbench_fixture import fixture_payload


class WorkbenchTests(unittest.TestCase):
    def test_embedded_source_cannot_close_the_payload_script(self) -> None:
        payload = fixture_payload()
        encoded = script_json(payload)
        self.assertNotIn("</script>", encoded)
        self.assertEqual(json.loads(encoded), payload)
        document = render(payload, ROOT / "src/humanbridge")
        embedded = document.split(
            '<script id="hb-payload" type="application/json">', 1
        )[1].split("</script>", 1)[0]
        self.assertEqual(json.loads(embedded), payload)

    def test_payload_is_blind_and_single_reviewer_only(self) -> None:
        payload = fixture_payload()
        self.assertNotIn("rules", payload)
        self.assertNotIn("guards", payload)
        self.assertNotIn("machine_suggestions", payload)
        self.assertTrue(
            all(
                row["reviewer_slot"] == "A"
                and row["review_status"] == "unreviewed"
                and row["exposure_label"] is None
                for row in payload["records"]
            )
        )

    def test_template_has_network_disabled_and_no_external_assets(self) -> None:
        document = render(fixture_payload(), ROOT / "src/humanbridge")
        self.assertIn("connect-src 'none'", document)
        self.assertNotIn("<script src=", document)
        self.assertNotIn('<link rel="stylesheet"', document)
        self.assertNotIn("fetch(", document)
        self.assertNotIn("localStorage", document)
