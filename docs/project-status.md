# Project status
Date: 2026-10-29. Current milestone: source-backed skill-transition candidate baseline implemented on a stacked feature branch; task/HVI and career relevance validation pending.

## Completed foundations
- Phase 0: requirements, architecture, MVP gates, data guide, methodology, schema, risks and roadmap.
- Phase 1: five official assets acquired and pinned; source-linked SQLite pipeline and occupation explorer verified.
- Source coverage remains 1,016 occupations, 18,838 tasks, 635,913 occupation-element ratings and 165,780 task ratings. Of the profiles, 923 have tasks, 910 have skill ratings, and 956 have a usable mapped annual median wage.

## Phase 2 implementation
- Versioned nine-dimension task review rubric and dated capability scenario.
- Deterministic lexical baseline with exact evidence spans, conservative negation/safety guards, unknown states and no scalar exposure/HVI claims.
- Frozen 200-task pilot from 20 occupations across 17 major groups, with known case studies restricted to development.
- Occupation-group split and selected-text exact/near-duplicate audit: 160 development tasks and 40 pilot holdout tasks; zero detected duplicate links across splits. Semantic leakage review remains pending.
- Two independent blind queues, 200 records each, with all human fields empty. No reviewer is assigned and no invitation has been sent.
- Development-only machine suggestions; no holdout suggestions. The strict baseline routes 112 development tasks to insufficient_evidence, a lexical noncoverage count rather than an exposure estimate.
- Immutable run artifacts, source attribution, code/config/source hashes, JSON interchange schema and returned-review integrity/completion gates.
- Local tests and real-data pilot checks cover exact spans, abstention, deterministic artifacts, grouped splitting and rejection of unsupported completion claims.

## Reviewable work
Branch: feature/phase-2-task-exposure. Target: main. Phase 2 is proposed through a pull request; it is not merged automatically.

Start with the [task rubric](task-rubric.md), [annotation guide](task-annotation-guide.md), [model card](model-cards/lexical-screen.md) and [pilot report](reports/task-pilot.json). The [core pipeline instructions](running-pipeline.md) reproduce prerequisite data. Artifacts and returned reviews stay outside Git; aggregate run metadata is committed.

## Pending research and next work
1. Review the Phase 2 pull request and rubric assumptions.
2. Assign two independent reviewers; perform semantic leakage review before first-pass labeling.
3. Complete the blind pilot, preserve original reviews and adjudicate disagreements separately.
4. Establish acceptance criteria and an independent confirmatory split before performance claims; compare exposure-only vs human-context features where justified.
5. Develop human-dependency feature mappings after evidence review; do not treat occupational AI/Expert source fields as independent human labels.

No completed human reviews, agreement metrics, task-model accuracy, 0–100 exposure/HVI scores, career recommendations, worker UI or county map exist. The Phase 2 research foundation is implemented; validated exposure modeling is not complete.

## Work log
- 2026-10-29: initialized project foundations and source discovery.
- 2026-10-29: acquired, normalized and validated the core data pipeline.
- 2026-10-29: prepared the lexical evidence baseline and frozen independent-review pilot on a feature branch. See Git history and the pull request for proposed changes.

## Offline review workbench increment
- Branch: feature/review-workbench-evaluation, based on the open Phase 2 PR and targeting feature/phase-2-task-exposure. No automatic merge into main.
- Added a self-contained offline review form per reviewer slot with local draft backup/resume and completed-only response export. Unfinished drafts remain blank in response files.
- Added shared frozen-run/response verification, consistent reviewer-slot identity checks, gated nominal agreement diagnostics and pending adjudication output.
- All assessment inputs start empty. No model suggestions, completed human labels or real study agreement statistics are supplied.
- Python tests cover known-answer kappa, unknown/undefined handling, evidence gates, frozen-run integrity and safe blind HTML bundling. The synthetic Chromium round-trip test passed in GitHub Actions, including Python validation of the browser export. Desktop/mobile CI screenshots were inspected; source strings remain text and no horizontal overflow was detected. Check the PR checks for the latest commit result.
- Local Chromium could not launch because this execution environment denies a required socket operation. No local browser visual verification is claimed; the GitHub browser job is the verification path.

Next: review the stacked changes, assign the two independent reviewers, use the workbench to label tasks, validate returned files, then inspect agreement/disagreements before developing validated exposure/HVI scores.

## Transferable-skill candidate increment
- Branch: feature/skill-transition-baseline, based on and targeting feature/review-workbench-evaluation. Earlier branches and main are not automatically merged.
- Added complete-case source-normalized 35-skill cosine ranking for 910 occupation profiles. The other 106 catalog profiles remain explicitly excluded rather than imputed.
- Added top-five candidate explanations with additive shared-skill contributions and positive occupation-importance differences. Differences are not verified personal skill gaps.
- Added official-mapping national median wage, projection and preparation context, plus opt-in wage/retention, exact entry-education and related-experience filters. Missing required context fails the filter. Licensing/accessibility remain unverified.
- Added source fingerprint/config/code provenance, deterministic ties, self exclusion and empty outputs for impossible filters. No arbitrary HVI/exposure or composite transition score is introduced.
- The real-data audit verifies 16 ranking/filter contracts across the eight case-study occupations. It does not establish candidate relevance, accessibility or employment outcomes.

See [skill-transition instructions](skill-transitions.md), [model card](model-cards/skill-transitions.md) and [audit](reports/skill-transition-audit.json). Next product work can connect occupation exploration, task evidence and skill candidates in a worker interface while independent task/career review proceeds.
