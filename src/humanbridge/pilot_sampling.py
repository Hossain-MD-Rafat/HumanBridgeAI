"""Deterministic occupation sampling and grouped pilot holdout selection."""
from __future__ import annotations

import hashlib
import itertools
import re
from collections import defaultdict


def stable_key(seed: str, value: str) -> str:
    return hashlib.sha256((seed + "|" + value).encode()).hexdigest()


def normalized(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.casefold()))


def task_key(task: dict) -> str:
    return ":".join(str(task[field]) for field in ("release_id", "occupation_code", "task_id"))


def similar(left: str, right: str, threshold: float) -> bool:
    """Conservative lexical duplicate rule; semantic paraphrases need human review."""
    a, b = normalized(left), normalized(right)
    if a == b:
        return True
    first, second = set(a.split()), set(b.split())
    if min(len(first), len(second)) < 5:
        return False
    return len(first & second) / len(first | second) >= threshold


def sample_pilot(tasks: list[dict], rubric: dict, development_codes: list[str]) -> tuple[list[dict], dict]:
    """Choose a diverse pilot and keep linked occupations in the same split.

    The existing public case studies are always development-only. The leakage
    check covers all selected pilot task texts, not every unselected source task.
    """
    if len(development_codes) != len(set(development_codes)):
        raise ValueError("Duplicate development occupation codes")
    by_occupation: dict[str, list[dict]] = defaultdict(list)
    for task in sorted(tasks, key=task_key):
        by_occupation[task["occupation_code"]].append(task)
    unique = {}
    for occupation, rows in by_occupation.items():
        texts = {}
        for row in rows:
            texts.setdefault(normalized(row["task_text"]), row)
        unique[occupation] = list(texts.values())
    per_occupation = rubric["tasks_per_occupation"]
    desired = rubric["pilot_occupations"]
    if per_occupation < 1 or desired <= len(development_codes):
        raise ValueError("Invalid pilot size or insufficient room for holdout occupations")
    eligible = {code for code, rows in unique.items() if len(rows) >= per_occupation}
    if not set(development_codes).issubset(eligible) or len(eligible) < desired:
        raise ValueError("Insufficient eligible occupations/tasks for this pilot")
    seed = rubric["seed"]
    selected = sorted(development_codes)
    represented = {code[:2] for code in selected}
    majors = sorted({code[:2] for code in eligible} - represented,
                    key=lambda value: stable_key(seed, "major:" + value))
    for major in majors:
        candidates = sorted((code for code in eligible if code[:2] == major),
                            key=lambda code: stable_key(seed, "occupation:" + code))
        if len(selected) < desired:
            selected.append(candidates[0])
    for code in sorted(eligible - set(selected), key=lambda value: stable_key(seed, "fill:" + value)):
        if len(selected) < desired:
            selected.append(code)
    sampled = []
    for code in sorted(selected):
        chosen = sorted(unique[code], key=lambda row: stable_key(seed, "task:" + task_key(row)))
        sampled.extend(dict(row) for row in chosen[:per_occupation])

    parent = {code: code for code in selected}

    def find(code: str) -> str:
        while parent[code] != code:
            parent[code] = parent[parent[code]]
            code = parent[code]
        return code

    links = []
    for left, right in itertools.combinations(sampled, 2):
        if left["occupation_code"] == right["occupation_code"]:
            continue
        if similar(left["task_text"], right["task_text"], rubric["near_duplicate_jaccard"]):
            a, b = sorted((find(left["occupation_code"]), find(right["occupation_code"])))
            parent[b] = a
            links.append([task_key(left), task_key(right)])
    groups: dict[str, list[str]] = defaultdict(list)
    for code in sorted(selected):
        groups[find(code)].append(code)
    candidates = [sorted(group) for group in groups.values()
                  if not set(group) & set(development_codes)]
    candidates.sort(key=lambda group: stable_key(seed, "group:" + ",".join(group)))
    minimum = rubric["minimum_holdout_occupations"]
    if minimum < 1:
        raise ValueError("A nonempty holdout is required")
    options = []
    for count in range(1, len(candidates) + 1):
        for choice in itertools.combinations(candidates, count):
            codes = sorted(itertools.chain.from_iterable(choice))
            if minimum <= len(codes) < len(selected):
                options.append((len(codes), stable_key(seed, "holdout:" + ",".join(codes)), codes))
    if not options:
        raise ValueError("Cannot create a grouped holdout without leaking development examples")
    holdout = set(min(options)[2])
    for row in sampled:
        row["task_key"] = task_key(row)
        row["split"] = "holdout" if row["occupation_code"] in holdout else "development"
    split_by_key = {row["task_key"]: row["split"] for row in sampled}
    leaks = [pair for pair in links if split_by_key[pair[0]] != split_by_key[pair[1]]]
    if leaks:
        raise ValueError("Detected lexical duplicate crossing splits")
    return sorted(sampled, key=lambda row: row["task_key"]), {
        "sampling_version": "occupation-grouped-pilot-v0.1.0", "seed": seed,
        "eligible_occupations": len(eligible), "selected_occupations": len(selected),
        "selected_major_groups": len({code[:2] for code in selected}),
        "tasks_per_occupation": per_occupation, "selected_tasks": len(sampled),
        "development_occupations": sorted(set(selected) - holdout),
        "holdout_occupations": sorted(holdout),
        "occupation_groups": sorted(sorted(group) for group in groups.values()),
        "detected_duplicate_links": links, "detected_cross_split_duplicate_links": 0,
        "near_duplicate_jaccard": rubric["near_duplicate_jaccard"],
        "limitations": ["Purposive pilot, not a population-representative sample.",
                        "Duplicate audit covers selected texts; semantic leakage review remains pending.",
                        "This is a pilot holdout, not the final confirmatory test set."],
    }
