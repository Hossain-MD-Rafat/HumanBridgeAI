"""Search real source occupations and inspect their tasks, skills and mapped labor facts."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Occupation title, alias or full O*NET-SOC code")
    parser.add_argument("--database", type=Path, default=ROOT / "data/processed/core.sqlite3")
    args = parser.parse_args()
    # Read-only URI prevents a misspelled path from silently creating an empty database.
    with sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        candidates = db.execute(
            "SELECT o.* FROM occupation o WHERE o.occupation_code=? "
            "OR o.title LIKE ? OR EXISTS (SELECT 1 FROM occupation_alias a "
            "WHERE a.release_id=o.release_id AND a.occupation_code=o.occupation_code "
            "AND a.alias LIKE ?) ORDER BY o.occupation_code LIMIT 10",
            (args.query, f"%{args.query}%", f"%{args.query}%"),
        ).fetchall()
        result = []
        for occupation in candidates:
            key = (occupation["release_id"], occupation["occupation_code"])
            tasks = db.execute(
                "SELECT task_id, statement, task_type FROM task WHERE release_id=? "
                "AND occupation_code=? ORDER BY task_id LIMIT 5", key).fetchall()
            skills = db.execute(
                "SELECT e.name, r.value AS source_importance, r.quality_flag "
                "FROM occupation_element_rating r JOIN element e USING (release_id, element_id) "
                "WHERE r.release_id=? AND r.occupation_code=? AND r.scale_id='IM' "
                "AND e.domain IN ('essential_skill','transferable_skill') "
                "AND r.quality_flag IS NULL ORDER BY r.value DESC,e.name LIMIT 10", key).fetchall()
            # Return every mapped fact with its original code, universe and unit.
            # Do not allocate SOC/NEM employment to O*NET specializations.
            facts = db.execute(
                "SELECT DISTINCT d.dataset_id, s.occupation_code, s.metric, s.value, "
                "s.unit, s.period, s.universe, s.quality_flag FROM occupation_crosswalk c "
                "JOIN labor_statistic s ON c.target_code=s.occupation_code "
                "AND c.target_taxonomy=s.taxonomy JOIN dataset_release d ON d.release_id=s.release_id "
                "WHERE c.source_code=? ORDER BY d.dataset_id,s.occupation_code,s.metric",
                (occupation["occupation_code"],),
            ).fetchall()
            result.append({**dict(occupation), "sample_tasks": [dict(x) for x in tasks],
                           "top_skill_requirements": [dict(x) for x in skills],
                           "mapped_labor_context": [dict(x) for x in facts]})
    print(json.dumps({"matches": result, "warnings": [
        "Requirements describe occupations, not verified personal skills.",
        "No AI exposure, HVI or career recommendations computed.",
        "Labor context is for mapped source aggregates, not individual earnings."
    ]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
