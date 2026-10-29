"""Exercise lexical evidence, abstention and unvalidated-output boundaries."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.task_screening import load_rubric, screen_task


class ScreeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rubric = load_rubric(ROOT / "config/task_rubric.json")

    def test_preserves_exact_source_spans_and_unknown_manual_dimensions(self) -> None:
        text = "  Draft reports and discuss findings with clients."
        output = screen_task(text, self.rubric)
        self.assertEqual(output["review_route"], "digital_and_context_review")
        for dimension in output["dimensions"].values():
            for evidence in dimension["evidence"]:
                start, end = evidence["span"]
                self.assertEqual(text[start:end], evidence["quote"])
        self.assertEqual(output["dimensions"]["cultural_context"]["status"], "not_assessed")
        self.assertEqual(output["dimensions"]["creative_judgment"]["status"], "not_assessed")

    def test_negation_abstains_instead_of_asserting_capability(self) -> None:
        output = screen_task("Do not write reports without permission.", self.rubric)
        self.assertEqual(output["review_route"], "manual_context_review")
        self.assertEqual(output["dimensions"]["language_generation"]["status"], "ambiguous_cue")

    def test_patient_context_overrides_digital_cues(self) -> None:
        output = screen_task("Write reports about clinical patient examinations.", self.rubric)
        self.assertEqual(output["review_route"], "manual_context_review")
        self.assertTrue(any(hit["reason"] == "safety_or_regulated_context" for hit in output["guard_hits"]))

    def test_no_cue_is_unknown_and_never_zero_exposure(self) -> None:
        output = screen_task("Consider unusual circumstances.", self.rubric)
        self.assertEqual(output["review_route"], "insufficient_evidence")
        self.assertTrue(all(item["status"] == "not_assessed" for item in output["dimensions"].values()))
        self.assertIsNone(output["ai_exposure"])
        self.assertIsNone(output["human_dependency"])
        self.assertIsNone(output["workflow_label"])

    def test_distinguishes_physical_objects_from_report_repair(self) -> None:
        physical = screen_task("Repair electrical equipment.", self.rubric)
        textual = screen_task("Repair reports.", self.rubric)
        self.assertEqual(physical["dimensions"]["physical_context"]["status"], "cue_found")
        self.assertEqual(textual["dimensions"]["physical_context"]["status"], "not_assessed")

    def test_outputs_are_deterministic_and_explicitly_unreviewed(self) -> None:
        first = screen_task("Develop software applications.", self.rubric)
        self.assertEqual(first, screen_task("Develop software applications.", self.rubric))
        self.assertEqual(first["evidence_status"], "machine_generated_unreviewed")
        self.assertEqual(first["dimensions"]["coding"]["status"], "cue_found")

    def test_rejects_missing_task_instead_of_inventing_a_label(self) -> None:
        for text in ("", "   ", None):
            with self.assertRaises(ValueError):
                screen_task(text, self.rubric)
