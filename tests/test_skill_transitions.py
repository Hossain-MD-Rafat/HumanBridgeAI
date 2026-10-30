"""Known-answer similarity and hard-filter checks using synthetic occupation profiles."""

from __future__ import annotations

import copy
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from humanbridge.skill_transitions import (
    SkillProfile,
    scaled_importance,
    cosine_components,
    explain_pair,
    rank_candidates,
)
from humanbridge.transition_data import mapped_record


class SkillMathTests(unittest.TestCase):
    def test_fixed_source_anchor_scaling_not_batch_minmax(self) -> None:
        self.assertEqual(
            scaled_importance({"a": 1, "b": 3, "c": 5}, ["a", "b", "c"], 1, 5),
            [0, 0.5, 1],
        )
        self.assertEqual(
            scaled_importance({"a": 3, "b": 3, "c": 3}, ["a", "b", "c"], 1, 5),
            [0.5, 0.5, 0.5],
        )

    def test_missing_nonfinite_or_out_of_scale_is_not_imputed(self) -> None:
        for values in [
            {"a": 3},
            {"a": 3, "b": None},
            {"a": 3, "b": float("nan")},
            {"a": 3, "b": 6},
        ]:
            with self.assertRaises(ValueError):
                scaled_importance(values, ["a", "b"], 1, 5)

    def test_known_cosine_and_exact_additive_explanation(self) -> None:
        similarity, parts = cosine_components([1, 0], [1, 1])
        self.assertAlmostEqual(similarity, 1 / math.sqrt(2))
        self.assertAlmostEqual(sum(parts), similarity)
        self.assertEqual(parts[1], 0)
        self.assertEqual(cosine_components([1, 0], [0, 1])[0], 0)

    def test_zero_or_incompatible_vectors_fail(self) -> None:
        for first, second in [
            ([0, 0], [1, 0]),
            ([1], [1, 2]),
            ([1, -1], [1, 1]),
            ([math.inf], [1]),
        ]:
            with self.assertRaises(ValueError):
                cosine_components(first, second)

    def test_ambiguous_mapping_is_unknown_even_if_values_match(self) -> None:
        mapped = mapped_record({"A", "B"}, {"A": {"value": 100}, "B": {"value": 100}})
        self.assertEqual(mapped["status"], "ambiguous_mapping")
        self.assertIsNone(mapped["record"])
        self.assertEqual(len(mapped["mapping_evidence"]), 2)

    def test_unmapped_and_missing_target_data_are_distinct(self) -> None:
        self.assertEqual(mapped_record(set(), {})["status"], "unmapped")
        self.assertEqual(mapped_record({"A"}, {})["status"], "missing_target_data")


class RankingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.features = ["a", "b", "c"]
        self.names = {"a": "First skill", "b": "Second skill", "c": "Third skill"}
        self.config = {
            "importance_minimum": 1,
            "importance_maximum": 5,
            "maximum_results": 5,
            "explanation_skills": 1,
            "education_categories": ["high-school", "bachelor"],
            "related_experience_categories": ["None", "5 years or more"],
            "limitations": ["Synthetic fixture only"],
        }
        self.profiles = {
            "source": SkillProfile(
                "source",
                "Source",
                {"a": 5, "b": 1, "c": 1},
                {"a": 2, "b": None, "c": 0},
            ),
            "B": SkillProfile("B", "Identical profile", {"a": 5, "b": 1, "c": 1}),
            "C": SkillProfile("C", "Orthogonal profile", {"a": 1, "b": 5, "c": 1}),
            "D": SkillProfile(
                "D",
                "Diagonal profile",
                {"a": 5, "b": 5, "c": 1},
                {"a": 2, "b": 3, "c": 1},
            ),
            "E": SkillProfile("E", "Zero vector", {"a": 1, "b": 1, "c": 1}),
            "F": SkillProfile("F", "Incomplete", {"a": 5, "b": 1}),
        }
        self.contexts = {
            code: {
                "wage": {"median_annual_wage": 100},
                "preparation": {
                    "education": "high-school",
                    "related_experience": "None",
                },
            }
            for code in self.profiles
        }
        self.contexts["B"]["wage"]["median_annual_wage"] = 110
        self.contexts["B"]["preparation"]["education"] = "bachelor"
        self.contexts["B"]["preparation"]["related_experience"] = "5 years or more"
        self.contexts["C"]["wage"]["median_annual_wage"] = None
        self.contexts["C"]["preparation"]["education"] = None
        self.contexts["D"]["wage"]["median_annual_wage"] = 90

    def rank(self, **kwargs):
        return rank_candidates(
            "source",
            self.profiles,
            self.features,
            self.names,
            self.contexts,
            self.config,
            **kwargs,
        )

    def test_self_exclusion_order_and_no_padding(self) -> None:
        result = self.rank()
        self.assertEqual(
            [r["occupation_code"] for r in result["candidates"]], ["B", "D", "C"]
        )
        self.assertEqual([r["rank"] for r in result["candidates"]], [1, 2, 3])
        self.assertEqual(result["filter_exclusions"]["incomparable_skill_profile"], 2)
        self.assertIsNone(result["ai_exposure"])
        self.assertIsNone(result["human_dependency"])
        self.assertIsNone(result["ranking_quality_metrics"])

    def test_no_wage_or_education_effect_without_requested_filters(self) -> None:
        before = [r["occupation_code"] for r in self.rank()["candidates"]]
        self.contexts["B"]["wage"]["median_annual_wage"] = 1
        self.contexts["D"]["wage"]["median_annual_wage"] = 1000000
        self.contexts["B"]["preparation"]["education"] = None
        self.assertEqual(
            before, [r["occupation_code"] for r in self.rank()["candidates"]]
        )

    def test_ties_are_broken_by_source_code(self) -> None:
        self.profiles["A"] = SkillProfile(
            "A", "Tied", dict(self.profiles["B"].importance)
        )
        self.contexts["A"] = copy.deepcopy(self.contexts["B"])
        self.assertEqual(
            [r["occupation_code"] for r in self.rank()["candidates"]][:2], ["A", "B"]
        )

    def test_wage_filter_excludes_missing_targets_even_at_zero_threshold(self) -> None:
        result = self.rank(min_national_median=100)
        self.assertEqual([r["occupation_code"] for r in result["candidates"]], ["B"])
        self.assertNotIn(
            "C",
            [
                r["occupation_code"]
                for r in self.rank(min_national_median=0)["candidates"]
            ],
        )

    def test_retention_uses_source_median_and_rejects_unknown_source(self) -> None:
        result = self.rank(min_median_retention=1)
        self.assertEqual([r["occupation_code"] for r in result["candidates"]], ["B"])
        self.assertEqual(
            result["candidates"][0]["national_median_retention_ratio"], 1.1
        )
        self.contexts["source"]["wage"]["median_annual_wage"] = None
        with self.assertRaisesRegex(ValueError, "source national median"):
            self.rank(min_median_retention=0)

    def test_education_and_experience_are_explicit_membership_filters(self) -> None:
        result = self.rank(
            allowed_education=["high-school"], allowed_related_experience=["None"]
        )
        self.assertEqual([r["occupation_code"] for r in result["candidates"]], ["D"])
        with self.assertRaisesRegex(ValueError, "Education"):
            self.rank(allowed_education=["guessed-degree"])

    def test_unknown_experience_is_not_none(self) -> None:
        self.contexts["D"]["preparation"]["related_experience"] = None
        result = self.rank(allowed_related_experience=["None"])
        self.assertNotIn("D", [r["occupation_code"] for r in result["candidates"]])

    def test_difference_is_importance_not_missing_personal_skill(self) -> None:
        result = explain_pair(
            self.profiles["source"],
            self.profiles["D"],
            self.features,
            self.names,
            self.config,
        )
        gap = result["priority_importance_differences"][0]
        self.assertEqual(gap["element_id"], "b")
        self.assertEqual(gap["importance_difference"], 4)
        self.assertIsNone(gap["occupation_level_difference"])
        total = (
            sum(
                row["cosine_contribution"]
                for row in result["shared_skill_contributions"]
            )
            + result["remaining_skill_contribution"]
        )
        self.assertAlmostEqual(total, result["cosine_similarity"])

    def test_invalid_requests_fail_before_returning_candidates(self) -> None:
        for args in [
            {"top_k": 0},
            {"top_k": 6},
            {"top_k": True},
            {"min_national_median": float("nan")},
            {"min_median_retention": -1},
            {"allowed_education": []},
            {"allowed_related_experience": ["unknown"]},
        ]:
            with self.assertRaises(ValueError):
                self.rank(**args)

    def test_impossible_filters_return_empty_results(self) -> None:
        result = self.rank(min_national_median=100000000)
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["eligible_after_filters"], 0)

    def test_inputs_are_not_mutated(self) -> None:
        before = copy.deepcopy((self.profiles, self.contexts))
        self.rank()
        self.assertEqual(before, (self.profiles, self.contexts))
