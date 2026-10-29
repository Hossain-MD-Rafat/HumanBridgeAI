# Offline review workbench
The next research step needs independent human judgments. This tool makes the frozen pilot reviewable without showing machine suggestions or requiring a hosted service. No actual reviewer has been assigned, contacted or simulated.

## Build and open
From this feature branch, first follow the [core pipeline](running-pipeline.md) and [pilot preparation guide](task-annotation-guide.md). For the current frozen run:

```bash
python scripts/build_review_workbench.py artifacts/task-pilot/2f50657777212dcae013 --slot A
python scripts/build_review_workbench.py artifacts/task-pilot/2f50657777212dcae013 --slot B
```

Each command prints a local HTML path under artifacts/review-workbench. Open that file in a current desktop browser. The renderer fingerprint in the path changes when document content changes. The files are reproducible outputs outside Git; they do not modify the original pilot run.

Reviewers need only the generated HTML and the [rubric](task-rubric.md). Node, a server, an API account and an internet connection are not needed to use the generated file. Each file includes one reviewer's blank queue, the rubric questions, label choices and source attribution. It does not include lexical rules, guards, machine suggestions or the other reviewer's responses.

## Complete a review
1. Use task search, the queue or Previous/Next to navigate. All assessment fields start empty.
2. Select all nine dimension judgments, an exposure hypothesis and a workflow hypothesis. Use insufficient evidence when the available context does not justify a judgment.
3. Add a rationale of at least 20 characters and at least one evidence reference. Record assumptions or missing context in the optional notes.
4. Enter a reviewer pseudonym and mark the task completed. Use one consistent pseudonym throughout the file. Completed records become read-only until explicitly reopened.
5. Download a draft backup regularly and before closing the tab. Drafts are held in memory; there is no browser-storage or server autosave. Resume a draft or response through the local file selector.
6. Export review responses for the coordinator. Completed tasks are exported in the original JSONL contract. Unfinished drafts are exported as unchanged blank records, never as completed evidence. A draft backup is needed to preserve unfinished edits.

Draft imports require the same run and slot. JSONL imports verify task identity/text, rubric version and slot; original coordinator assignment and version discipline still matter because that legacy record format does not independently authenticate a response's originating run. The response filename includes the run ID for organization, not as a security proof.

The file makes no network requests and has a restrictive connection policy. Imported source strings are displayed as text, not executable markup. A local file is not an access-control system: keep reviewer materials separate, preserve attribution, and avoid personal/company secrets. Do not share another reviewer's labels or development suggestions before the first independent pass.

## Validate returned responses
Copy downloads into an ignored response directory and run:

```bash
python scripts/validate_task_reviews.py artifacts/task-pilot/2f50657777212dcae013 --reviewer-a artifacts/responses/A.jsonl --reviewer-b artifacts/responses/B.jsonl
```

This checks frozen run integrity, complete task coverage, record identities, allowed labels, rationale/evidence, timestamps and reviewer-slot consistency. It reports how many records are completed. Add --require-complete only when all 400 records should be finished. Partial drafts should be resumed in the workbench, not edited into fake completed records.

## Human-review agreement and adjudication preparation
The agreement command is inactive by default. It requires an explicit declaration that the selected responses are genuine independent human reviews. Software cannot verify authenticity, qualifications or independence; that remains the research coordinator's responsibility.

After all development tasks have two completed, validated reviews:

```bash
python scripts/evaluate_task_reviews.py artifacts/task-pilot/2f50657777212dcae013 --reviewer-a artifacts/responses/A.jsonl --reviewer-b artifacts/responses/B.jsonl --split development --attest-independent-human-review
```

Expected outputs under artifacts/review-evaluation: an immutable agreement.json and an adjudication-queue.jsonl. The report retains source run, response checksums, rubric and evaluator fingerprints. Re-running unchanged inputs checks/reuses the same output; conflicting existing files are not overwritten.

For each dimension, exposure and workflow label, the report includes nominal exact agreement, nominal Cohen's kappa, a labeled confusion matrix and insufficient-evidence counts. Insufficient evidence is its own category, not zero. It also reports substantive-only pair coverage and agreement, explicitly identified as a selected subset. When constant marginals make kappa undefined, the result is null with a reason.

Disagreement items retain each reviewer's original label and empty adjudicator, rationale and consensus fields. No majority vote, automatic adjudication or inferred truth label is created. Original responses remain unchanged. Separate adjudication and task-model evaluation are later steps.

Selecting --split holdout additionally requires --attest-semantic-leakage-reviewed. The 40-task holdout is a pilot holdout, not a final confirmatory test. Development responses may be evaluated while holdout records remain blank, but every task in the selected split must have both completed reviews. No partial-subset agreement is silently reported.

These outputs measure agreement between reviewers. They are not model accuracy, measured AI productivity, employment effects or HVI validation. No genuine review-agreement result exists yet.

## Implementation and tests
| Component | Role | Important failures |
|---|---|---|
| review_io.py | Shared frozen-run and response validation | Missing artifact hashes, altered source text, missing tasks, mixed reviewer identities |
| workbench.py and review_workbench assets | Build a self-contained, single-slot offline interface | Stale rubric, changed run, unsafe template markers, edited existing outputs |
| review_evaluation.py | Nominal paired-label agreement and empty adjudication items | Missing paired labels, unknown categories, unsupported split |
| build_review_workbench.py | Generate HTML from the verified pilot | Run/slot mismatch or unavailable artifacts |
| evaluate_task_reviews.py | Apply protocol gates and publish immutable reports | No attestation, incomplete selected split, unreconciled output conflict |

Python tests use explicit synthetic fixtures. The optional browser smoke check creates synthetic tasks only, verifies draft/response round trips, rejects changed task text, checks mobile overflow and validates the downloaded JSONL with the production Python contract. It must never be treated as study data.

```bash
python -m unittest discover -s tests -v
python scripts/check_foundation.py
npm ci
npx playwright install --with-deps chromium
python tests/workbench_fixture.py artifacts/ui-smoke/fixture.html
npm run test:browser
python tests/check_browser_response.py artifacts/ui-smoke/output/synthetic-responses.jsonl
```

Node/Playwright are development-only browser test dependencies, pinned in package-lock.json. GitHub Actions runs the browser smoke check and retains synthetic exports/screenshots briefly as a test artifact. It does not upload real reviewer files. The workbench itself needs no installed JavaScript packages.
