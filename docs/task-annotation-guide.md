# Prepare and review the Phase 2 pilot
## Generate the frozen research artifacts
First follow [core pipeline instructions](running-pipeline.md). Then run:

```bash
python scripts/prepare_task_pilot.py
```

Expected: a content-identified directory under artifacts/task-pilot with 200 selected source tasks, 160 development suggestions, two 200-record blind queues and no holdout suggestions for the current snapshot. The script verifies the core database's logical fingerprint. Run identity incorporates source snapshot, rubric bytes, cohort bytes, engine source code and selected task/split membership.

Re-running identical inputs verifies byte-identical artifacts and reuses the directory. It never overwrites modified review work. A changed rubric, source, cohort or engine creates a new run ID. Artifacts, returned labels and reviewer identities remain outside public Git by default; the committed aggregate report contains no completed reviews.

## Sampling and leakage controls
The existing eight public case-study occupations are development-only. Additional occupations are deterministically selected from eligible occupations with at least ten distinct task texts, prioritizing additional two-digit occupation groups. Ten tasks per selected occupation are chosen by a seeded hash. This purposive pilot is not representative of the U.S. workforce.

Before splitting, link occupations when selected task statements have identical case/punctuation-normalized text, or at least 0.85 token-set Jaccard similarity with at least five unique tokens per text. Connected occupation groups stay in one split. A group touching a public development example cannot enter the holdout. Select at least four remaining occupations for the pilot holdout; fail rather than break groups if this is impossible.

The audit covers selected pilot texts. It cannot rule out semantic paraphrases, shared concepts or unselected source-text overlap. Independent semantic leakage review remains pending. The current 40-task holdout is a pilot holdout, not a final confirmatory test. If feedback changes the rubric, freeze a new confirmatory sample before making generalization claims.

## Artifacts
| File | Purpose | Intended audience |
|---|---|---|
| selected-tasks.jsonl | Source identity, original task, occupation and split | Research coordinator |
| split-manifest.json | Sampling choices and detected duplicate links | Research coordinator; reviewer split metadata is also visible |
| machine-suggestions.development.jsonl | Exact lexical evidence for development tasks only | Method developer after the independent first pass |
| reviewer-A.blind.jsonl / reviewer-B.blind.jsonl | Empty independent-label records without machine suggestions | One copy per assigned reviewer |
| run-report.json | Inputs, version hashes, counts and explicit no-validation status | Research coordinator |
| artifact-hashes.json | Content fingerprints for generated files | Integrity checks |
| SOURCE_NOTICE.md | O*NET attribution, CC BY 4.0 link and modifications notice | Preserve when sharing review materials |

Blinding means machine suggestions are omitted; occupation identity and split remain visible. This is procedural separation, not an access-control system. Do not share the development suggestions or another reviewer's responses before first-pass labeling. Reviewers are not yet assigned, and no invitations have been sent.

## Review process
1. Read the [rubric](task-rubric.md) and agree on the stated capability scenario.
2. Assign two independent reviewers with different pseudonyms. Keep any real identity mapping private.
3. Copy the appropriate blind queue to a response directory outside the immutable generated run.
4. For each record, preserve task identity/text, rubric version, split and reviewer slot. Fill every dimension label, exposure label, workflow hypothesis, rationale, evidence references and UTC review time. Mark review_status completed only when the record is finished. Use explicit insufficient_evidence where context is unavailable.
5. Submit the two response files to the validator. Do not put names, personal histories, company secrets or identifiable worker examples in responses.
6. Review disagreement patterns and adjudicate separately while preserving both independent originals. Domain experts should review safety-critical cases. Participant involvement or interviews require the separate consent protocol.

[Annotation JSON Schema](../schema/task_annotation.schema.json) defines the interchange record. Runtime validation additionally checks immutable source identity, substantive rationale, UTC timestamp and distinct reviewer identities. It cannot prove that a reviewer is human, qualified or independent; the review protocol must establish that.

```bash
python scripts/validate_task_reviews.py artifacts/task-pilot/RUN_ID
```

Expected for generated templates: 400 structurally valid review records, **zero completed reviews**, and null performance metrics. The completion gate must reject those same empty templates:

```bash
python scripts/validate_task_reviews.py artifacts/task-pilot/RUN_ID --require-complete
```

For actual returned responses:

```bash
python scripts/validate_task_reviews.py artifacts/task-pilot/RUN_ID --reviewer-a artifacts/responses/A.jsonl --reviewer-b artifacts/responses/B.jsonl --require-complete
```

Missing/duplicate tasks, changed source text, unexpected machine fields, partial labels, absent evidence, stale rubrics or the same identity in both completed reviewer slots cause a failure. The validator reports record integrity, not model accuracy. No agreement or predictive metric is computed in this phase.

## Modules and failure cases
- task_screening.py exists to produce auditable review cues; no match remains unknown. Run through the pilot script or unit tests.
- pilot_sampling.py exists to select and group tasks deterministically; insufficient eligible occupations or inseparable holdout groups fail.
- annotations.py exists to separate blank queues from completed human evidence; it rejects schema/identity/label inconsistencies.
- prepare_task_pilot.py orchestrates the frozen source, sampling and artifact flow; stale databases or modified existing runs fail.
- validate_task_reviews.py validates returned records against the immutable run; it requires the original run and matching rubric.

These modules do not change the source SQLite schema or fill its task_score table. The next evaluation phase requires actual independent labels, adjudication and a preregistered comparison protocol.

## Offline review and subsequent agreement
The [offline workbench](review-workbench.md) replaces manual JSON editing with an independent review form. It exports completed records plus original blanks for unfinished drafts; use its draft backup for in-progress work. Shared run/response validation now requires a complete artifact hash set and a consistent pseudonym per slot. After genuine paired reviews, the gated agreement tool produces agreement diagnostics and empty adjudication items. No completed study labels or agreement results exist yet.
