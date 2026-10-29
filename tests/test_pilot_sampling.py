"""Guard against split leakage and source-order-dependent pilot selection."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.pilot_sampling import sample_pilot, similar


class SamplingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.codes = ["11-1011.00", "13-2011.00", "15-1252.00", "29-1141.00"]
        self.rubric = {"seed": "fixture", "pilot_occupations": 4,
                       "tasks_per_occupation": 2, "minimum_holdout_occupations": 1,
                       "near_duplicate_jaccard": 0.85}
        self.tasks = [
            {"release_id": "fixture", "occupation_code": code,
             "occupation_title": code, "task_id": str(index),
             "task_text": f"Special marker{position} activity{index} object{position}."}
            for position, code in enumerate(self.codes) for index in range(2)
        ]

    def test_order_invariant_selection_and_no_input_mutation(self) -> None:
        original = copy.deepcopy(self.tasks)
        first = sample_pilot(self.tasks, self.rubric, [self.codes[0]])
        second = sample_pilot(list(reversed(self.tasks)), self.rubric, [self.codes[0]])
        self.assertEqual(first, second)
        self.assertEqual(self.tasks, original)

    def test_shared_task_forces_linked_occupations_into_development(self) -> None:
        shared = "Provide specialized professional assistance to clients in difficult situations."
        self.tasks[0]["task_text"] = shared
        self.tasks[2]["task_text"] = shared.upper()
        rows, report = sample_pilot(self.tasks, self.rubric, [self.codes[0]])
        splits = {row["occupation_code"]: row["split"] for row in rows}
        self.assertEqual(splits[self.codes[0]], "development")
        self.assertEqual(splits[self.codes[1]], "development")
        self.assertEqual(report["detected_cross_split_duplicate_links"], 0)
        self.assertTrue(report["detected_duplicate_links"])

    def test_fails_when_duplicate_group_leaves_no_independent_holdout(self) -> None:
        for index in range(0, len(self.tasks), 2):
            self.tasks[index]["task_text"] = "Shared common task."
        with self.assertRaisesRegex(ValueError, "holdout"):
            sample_pilot(self.tasks, self.rubric, [self.codes[0]])

    def test_fails_if_requested_occupation_has_too_few_unique_tasks(self) -> None:
        self.tasks[1]["task_text"] = self.tasks[0]["task_text"]
        with self.assertRaisesRegex(ValueError, "eligible"):
            sample_pilot(self.tasks, self.rubric, [self.codes[0]])

    def test_near_duplicate_policy_handles_case_punctuation_and_small_edits(self) -> None:
        self.assertTrue(similar("Maintain records.", "MAINTAIN records!", 0.85))
        self.assertTrue(similar("Prepare detailed reports about monthly financial records for clients",
                                "Prepare reports about monthly financial records for clients", 0.85))
        self.assertFalse(similar("Operate machinery", "Operate software", 0.85))
