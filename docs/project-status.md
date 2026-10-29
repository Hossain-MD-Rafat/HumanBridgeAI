# Project status
Date: 2026-10-29. Current milestone: Phase 2 baseline and annotation pilot prepared on a feature branch; independent validation pending.

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
