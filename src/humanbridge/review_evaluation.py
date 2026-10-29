"""Human-review agreement only; no machine-accuracy or employment-effect estimates."""

from __future__ import annotations

from collections import Counter


def agreement(first: list[str], second: list[str], labels: list[str]) -> dict:
    """Nominal Cohen's kappa, with explicit undefined constant-marginal handling."""
    if len(first) != len(second) or not first:
        raise ValueError("Agreement needs equally sized, nonempty paired labels")
    if len(labels) != len(set(labels)) or any(
        value not in labels for value in first + second
    ):
        raise ValueError("Unknown or duplicate agreement categories")
    size = len(first)
    counts_a, counts_b = Counter(first), Counter(second)
    confusion = {a: {b: 0 for b in labels} for a in labels}
    for a, b in zip(first, second):
        confusion[a][b] += 1
    observed = sum(a == b for a, b in zip(first, second)) / size
    expected = sum(counts_a[label] * counts_b[label] for label in labels) / size**2
    denominator = 1 - expected
    kappa = (observed - expected) / denominator if denominator > 1e-12 else None
    substantive = [
        (a, b)
        for a, b in zip(first, second)
        if a != "insufficient_evidence" and b != "insufficient_evidence"
    ]
    return {
        "paired_records": size,
        "exact_agreement_fraction": observed,
        "cohen_kappa_nominal": kappa,
        "kappa_note": "undefined_constant_marginals" if kappa is None else None,
        "confusion_matrix_A_rows_B_columns": confusion,
        "reviewer_A_counts": {label: counts_a[label] for label in labels},
        "reviewer_B_counts": {label: counts_b[label] for label in labels},
        "insufficient_evidence_A": counts_a["insufficient_evidence"],
        "insufficient_evidence_B": counts_b["insufficient_evidence"],
        "both_substantive_pairs": len(substantive),
        "both_substantive_agreement_fraction": (
            sum(a == b for a, b in substantive) / len(substantive)
            if substantive
            else None
        ),
        "note": "Insufficient evidence is a separate nominal category, never numeric zero. Substantive-only agreement is a selected subset, not an overall accuracy metric.",
    }


def analyze_reviews(
    tasks: dict[str, dict],
    first: dict[str, dict],
    second: dict[str, dict],
    rubric: dict,
    split: str,
) -> tuple[dict, list[dict]]:
    """Require complete pairs for the selected split; keep adjudication fields empty."""
    if split not in ("development", "holdout"):
        raise ValueError("Choose development or holdout explicitly")
    selected = sorted(key for key, task in tasks.items() if task["split"] == split)
    if not selected:
        raise ValueError("Selected split has no tasks")
    if any(
        queue[key]["review_status"] != "completed"
        for key in selected
        for queue in (first, second)
    ):
        raise ValueError(
            "Every selected-split task needs two completed reviews before agreement is computed"
        )
    metrics = {}
    disagreements = []
    aspects = [
        ("exposure_label", rubric["human_exposure_labels"]),
        ("workflow_label", rubric["human_workflow_labels"]),
    ]
    aspects += [
        ("dimension:" + item["id"], rubric["human_dimension_labels"])
        for item in rubric["dimensions"]
    ]
    for aspect, labels in aspects:

        def value(row: dict) -> str:
            return (
                row["dimension_ratings"][aspect.split(":", 1)[1]]
                if aspect.startswith("dimension:")
                else row[aspect]
            )

        a = [value(first[key]) for key in selected]
        b = [value(second[key]) for key in selected]
        metrics[aspect] = agreement(a, b, labels)
        for key, left, right in zip(selected, a, b):
            if left != right:
                disagreements.append(
                    {
                        "task_key": key,
                        "split": split,
                        "aspect": aspect,
                        "reviewer_A_label": left,
                        "reviewer_B_label": right,
                        "adjudicated_label": None,
                        "adjudicator_id": None,
                        "adjudication_rationale": None,
                        "status": "pending_adjudication",
                    }
                )
    return {
        "scope": "human_review_agreement_only",
        "split": split,
        "paired_tasks": len(selected),
        "aspect_agreement": metrics,
        "disagreement_items": len(disagreements),
        "predictive_performance_metrics": None,
        "causal_employment_effects": None,
        "limitations": [
            "Agreement does not establish correctness, worker outcomes or AI capability.",
            "This purposive pilot is not population representative.",
            "No automatic adjudication or consensus label is created.",
        ],
    }, disagreements
