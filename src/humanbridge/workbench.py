"""Bundle one verified blind queue into a self-contained offline review file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from humanbridge.review_io import load_run, read_queue
from humanbridge.task_screening import load_rubric


def script_json(value: dict) -> str:
    """Encode embedded JSON without allowing a task string to terminate its script tag."""
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render(payload: dict, asset_directory: Path) -> str:
    """Use trusted repo assets; task data is never interpreted as markup."""
    template = (asset_directory / "review_workbench.html").read_text(encoding="utf-8")
    parts = {
        "__HB_CSS__": (asset_directory / "review_workbench.css").read_text(
            encoding="utf-8"
        ),
        "__HB_JS__": (asset_directory / "review_workbench.js").read_text(
            encoding="utf-8"
        ),
        "__HB_PAYLOAD__": script_json(payload),
    }
    for marker in parts:
        if template.count(marker) != 1:
            raise ValueError("Unexpected workbench template marker")
    # One substitution pass avoids interpreting marker-looking source task text.
    import re

    return re.sub(
        r"__HB_(?:CSS|JS|PAYLOAD)__", lambda match: parts[match.group()], template
    )


def build_workbench(root: Path, run: Path, slot: str, output_parent: Path) -> Path:
    if slot not in ("A", "B"):
        raise ValueError("Reviewer slot must be A or B")
    rubric = load_rubric(root / "config/task_rubric.json")
    report, tasks = load_run(run, rubric)
    queue = read_queue(run / f"reviewer-{slot}.blind.jsonl", tasks, rubric, slot)
    if any(row["review_status"] != "unreviewed" for row in queue.values()):
        raise ValueError("Workbench must start from an untouched blind queue")
    payload = {
        "format": "humanbridge-offline-workbench-v1",
        "run_id": report["run_id"],
        "slot": slot,
        "rubric_version": rubric["rubric_version"],
        "rubric_sha256": rubric["config_sha256"],
        "capability_scope": rubric["capability_scope"],
        "dimensions": rubric["dimensions"],
        "dimension_labels": rubric["human_dimension_labels"],
        "exposure_labels": rubric["human_exposure_labels"],
        "workflow_labels": rubric["human_workflow_labels"],
        "records": list(queue.values()),
        "source_notice": (run / "SOURCE_NOTICE.md").read_text(encoding="utf-8"),
    }
    # No rules, guards, machine suggestions, other reviewer files or labels are bundled.
    document = render(payload, root / "src/humanbridge")
    renderer_id = hashlib.sha256(document.encode()).hexdigest()[:16]
    output = output_parent / report["run_id"] / renderer_id / f"reviewer-{slot}.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.read_text(encoding="utf-8") != document:
        raise ValueError("Existing workbench differs; do not overwrite local work")
    output.write_text(document, encoding="utf-8")
    return output
