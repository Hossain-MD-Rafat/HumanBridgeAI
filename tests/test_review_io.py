"""Fail closed on damaged manifests, duplicate identities and reviewer mixing."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.review_io import load_run, read_pair, read_queue
from humanbridge.task_screening import load_rubric
from review_run_fixture import create_run, completed, write_rows


class ReviewIOTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.rubric = load_rubric(ROOT / "config/task_rubric.json")
        self.run, self.tasks = create_run(self.root, self.rubric)

    def test_blank_pair_validates_without_claiming_completion(self) -> None:
        _, tasks, first, second = read_pair(
            self.run,
            self.run / "reviewer-A.blind.jsonl",
            self.run / "reviewer-B.blind.jsonl",
            self.rubric,
        )
        self.assertEqual(len(tasks), 2)
        self.assertTrue(
            all(
                row["review_status"] == "unreviewed"
                for row in [*first.values(), *second.values()]
            )
        )

    def test_manifest_cannot_omit_an_artifact_to_skip_its_hash_check(self) -> None:
        path = self.run / "artifact-hashes.json"
        hashes = json.loads(path.read_text())
        hashes.pop("selected-tasks.jsonl")
        path.write_text(json.dumps(hashes))
        with self.assertRaisesRegex(ValueError, "missing or unexpected"):
            load_run(self.run, self.rubric)

    def test_changed_original_task_is_detected(self) -> None:
        (self.run / "selected-tasks.jsonl").write_text('{"changed":true}\n')
        with self.assertRaisesRegex(ValueError, "differs"):
            load_run(self.run, self.rubric)

    def test_returned_queue_cannot_duplicate_or_drop_task_keys(self) -> None:
        _, tasks = load_run(self.run, self.rubric)
        path = self.root / "A.jsonl"
        row = completed(self.tasks[0], self.rubric, "A")
        write_rows(path, [row, row])
        with self.assertRaisesRegex(ValueError, "duplicate, missing"):
            read_queue(path, tasks, self.rubric, "A")

    def test_each_slot_uses_one_identity(self) -> None:
        _, tasks = load_run(self.run, self.rubric)
        path = self.root / "A.jsonl"
        rows = [completed(task, self.rubric, "A") for task in self.tasks]
        rows[1]["reviewer_id"] = "different-reviewer"
        write_rows(path, rows)
        with self.assertRaisesRegex(ValueError, "consistent pseudonym"):
            read_queue(path, tasks, self.rubric, "A")

    def test_same_reviewer_cannot_occupy_both_slots(self) -> None:
        first = self.root / "A.jsonl"
        second = self.root / "B.jsonl"
        write_rows(first, [completed(task, self.rubric, "A") for task in self.tasks])
        rows = [completed(task, self.rubric, "B") for task in self.tasks]
        for row in rows:
            row["reviewer_id"] = "SYNTHETIC-A"
        write_rows(second, rows)
        with self.assertRaisesRegex(ValueError, "different people"):
            read_pair(self.run, first, second, self.rubric, True)
