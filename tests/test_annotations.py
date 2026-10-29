"""Prevent machine suggestions, stale identities and incomplete human-label claims."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.annotations import blank_review, validate_pair, validate_review
from humanbridge.task_screening import load_rubric


class AnnotationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rubric = load_rubric(ROOT / "config/task_rubric.json")
        self.task = {"task_key": "fixture:11-1011.00:1", "release_id": "fixture",
                     "occupation_code": "11-1011.00", "occupation_title": "Fixture",
                     "task_id": "1", "task_text": "Fixture task.", "split": "development"}

    def completed(self, slot: str, reviewer: str) -> dict:
        record = blank_review(self.task, self.rubric, slot)
        record.update(review_status="completed", reviewer_id=reviewer,
                      exposure_label="insufficient_evidence", workflow_label="insufficient_evidence",
                      rationale="Synthetic fixture: the task lacks execution context.",
                      evidence_references=["synthetic-fixture-task"],
                      reviewed_at_utc="2026-10-29T00:00:00Z")
        record["dimension_ratings"] = {key: "insufficient_evidence" for key in record["dimension_ratings"]}
        return record

    def test_blank_records_are_blind_and_not_completed(self) -> None:
        record = blank_review(self.task, self.rubric, "A")
        validate_review(record, self.task, self.rubric, "A")
        self.assertTrue(all(value is None for value in record["dimension_ratings"].values()))
        with self.assertRaisesRegex(ValueError, "not been completed"):
            validate_review(record, self.task, self.rubric, "A", require_complete=True)

    def test_rejects_added_machine_suggestion_and_changed_source_text(self) -> None:
        record = blank_review(self.task, self.rubric, "A")
        unblinded = {**record, "machine_suggestion": "augment"}
        with self.assertRaisesRegex(ValueError, "fields"):
            validate_review(unblinded, self.task, self.rubric, "A")
        record["task_text"] = "Altered source text"
        with self.assertRaisesRegex(ValueError, "identity"):
            validate_review(record, self.task, self.rubric, "A")

    def test_completed_review_needs_evidence_and_explicit_dimension_labels(self) -> None:
        record = self.completed("A", "fixture-a")
        validate_review(record, self.task, self.rubric, "A", require_complete=True)
        missing = copy.deepcopy(record)
        missing["evidence_references"] = []
        with self.assertRaisesRegex(ValueError, "evidence"):
            validate_review(missing, self.task, self.rubric, "A")
        missing = copy.deepcopy(record)
        missing["dimension_ratings"]["coding"] = None
        with self.assertRaisesRegex(ValueError, "every field"):
            validate_review(missing, self.task, self.rubric, "A")

    def test_rejects_reuse_of_same_reviewer_identity(self) -> None:
        with self.assertRaisesRegex(ValueError, "independent"):
            validate_pair(self.completed("A", "Fixture-A"), self.completed("B", " fixture-a "))
        validate_pair(self.completed("A", "fixture-a"), self.completed("B", "fixture-b"))

    def test_rejects_partial_labels_masquerading_as_unreviewed(self) -> None:
        record = blank_review(self.task, self.rubric, "A")
        record["exposure_label"] = "assistive_candidate"
        with self.assertRaisesRegex(ValueError, "partial"):
            validate_review(record, self.task, self.rubric, "A")
