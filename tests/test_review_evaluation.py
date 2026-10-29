"""Known-answer agreement calculations; all labels here are synthetic fixtures."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from humanbridge.review_evaluation import agreement, analyze_reviews
from humanbridge.annotations import blank_review
from humanbridge.task_screening import load_rubric
from evaluate_task_reviews import evaluate
from review_run_fixture import create_run, completed


class AgreementTests(unittest.TestCase):
    def test_known_kappa_and_confusion_matrix(self) -> None:
        result = agreement(["a", "a", "a", "b"], ["a", "a", "b", "b"], ["a", "b"])
        self.assertEqual(result["exact_agreement_fraction"], 0.75)
        self.assertEqual(result["cohen_kappa_nominal"], 0.5)
        self.assertEqual(
            result["confusion_matrix_A_rows_B_columns"],
            {"a": {"a": 2, "b": 1}, "b": {"a": 0, "b": 1}},
        )

    def test_constant_marginals_do_not_become_perfect_kappa(self) -> None:
        result = agreement(
            ["insufficient_evidence"] * 3,
            ["insufficient_evidence"] * 3,
            ["yes", "insufficient_evidence"],
        )
        self.assertIsNone(result["cohen_kappa_nominal"])
        self.assertEqual(result["kappa_note"], "undefined_constant_marginals")
        self.assertIsNone(result["both_substantive_agreement_fraction"])
        self.assertEqual(result["insufficient_evidence_A"], 3)

    def test_chance_level_agreement_is_zero_kappa(self) -> None:
        self.assertEqual(
            agreement(["a", "a", "b", "b"], ["a", "b", "a", "b"], ["a", "b"])[
                "cohen_kappa_nominal"
            ],
            0,
        )

    def test_unknown_is_separate_from_substantive_judgments(self) -> None:
        result = agreement(
            ["not_supported", "insufficient_evidence"],
            ["not_supported", "insufficient_evidence"],
            ["not_supported", "insufficient_evidence"],
        )
        self.assertEqual(result["both_substantive_pairs"], 1)
        self.assertEqual(result["both_substantive_agreement_fraction"], 1)

    def test_empty_mismatched_or_unknown_categories_fail(self) -> None:
        for first, second in [([], []), (["a"], []), (["invalid"], ["a"])]:
            with self.assertRaises(ValueError):
                agreement(first, second, ["a", "b"])


class EvaluationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rubric = load_rubric(ROOT / "config/task_rubric.json")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run, self.tasks = create_run(self.root, self.rubric)

    def test_incomplete_labels_never_produce_agreement(self) -> None:
        tasks = {task["task_key"]: task for task in self.tasks}
        first = {
            key: blank_review(task, self.rubric, "A") for key, task in tasks.items()
        }
        second = {
            key: blank_review(task, self.rubric, "B") for key, task in tasks.items()
        }
        with self.assertRaisesRegex(ValueError, "two completed reviews"):
            analyze_reviews(tasks, first, second, self.rubric, "development")

    def test_disagreements_remain_unadjudicated(self) -> None:
        tasks = {task["task_key"]: task for task in self.tasks}
        first = {key: completed(task, self.rubric, "A") for key, task in tasks.items()}
        second = {key: completed(task, self.rubric, "B") for key, task in tasks.items()}
        second[self.tasks[0]["task_key"]]["exposure_label"] = "assistive_candidate"
        result, queue = analyze_reviews(
            tasks, first, second, self.rubric, "development"
        )
        self.assertEqual(result["paired_tasks"], 1)
        self.assertEqual(len(queue), 1)
        self.assertIsNone(queue[0]["adjudicated_label"])
        self.assertEqual(queue[0]["status"], "pending_adjudication")
        self.assertIsNone(result["predictive_performance_metrics"])

    def test_attestation_and_empty_labels_fail_without_outputs(self) -> None:
        output = self.root / "evaluation"
        with self.assertRaisesRegex(ValueError, "explicitly attested"):
            evaluate(
                ROOT,
                self.run,
                self.run / "reviewer-A.blind.jsonl",
                self.run / "reviewer-B.blind.jsonl",
                "development",
                False,
                False,
                output,
            )
        with self.assertRaisesRegex(ValueError, "two completed reviews"):
            evaluate(
                ROOT,
                self.run,
                self.run / "reviewer-A.blind.jsonl",
                self.run / "reviewer-B.blind.jsonl",
                "development",
                True,
                False,
                output,
            )
        self.assertFalse(output.exists())

    def test_holdout_requires_semantic_review_attestation(self) -> None:
        with self.assertRaisesRegex(ValueError, "semantic leakage"):
            evaluate(
                ROOT,
                self.run,
                self.run / "reviewer-A.blind.jsonl",
                self.run / "reviewer-B.blind.jsonl",
                "holdout",
                True,
                False,
                self.root / "evaluation",
            )
