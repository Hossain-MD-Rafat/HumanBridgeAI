# Project status
Date: 2026-10-29. Current milestone: Phase 1 core data pipeline completed.

## Completed
- Phase 0: requirements, architecture, MVP gates, dataset guide, methodology, schema, risks and 16-week roadmap.
- Phase 1: five public source assets acquired, CRC-validated and SHA-256-pinned; immutable manifests committed.
- Actual workbook contracts inspected; source-specific O*NET and BLS adapters implemented.
- Atomic local SQLite build with 1,016 occupation profiles, 18,838 tasks, 635,913 occupation-element ratings and 165,780 task ratings.
- Official crosswalk audit: 961 profiles connect to detailed national wage rows; 956 have a usable annual median wage; 996 connect to projection line items.
- Coverage limits explicit: 923 profiles have tasks; 910 have skill ratings. No missing profile is silently assigned a zero score.
- Sampling/quality metadata, source dates and Domain Source retained, including AI/Expert work-style provenance.
- Real-data integrity and logical-fingerprint checks passed. Synthetic acquisition, schema and source-format tests pass locally.
- Command-line occupation search/exploration demonstrated for bookkeepers; no product API/UI is claimed.
- Initial eight-occupation case-study cohort recorded with exact source codes and task counts.

## Files and results
[Run instructions](running-pipeline.md), [coverage report](reports/core-data.json), [quality report](reports/data-quality.json), [source cards](data-cards/core-sources.md), [review cohort](../config/review_cohort.json) and [source snapshot](../config/core_snapshot.json).

Raw assets and the generated SQLite database stay outside Git. The committed lock/manifests permit reproduction with official downloads. Regional/optional datasets are not yet acquired. Not every workbook in the O*NET archive is imported.

## Next: Phase 2 evidence and task rubric
Objective: define dated AI-capability dimensions, an annotation rubric and a transparent task baseline before generating headline scores.
Inputs: validated source tasks, skill/context dimensions, provenance and an independent review plan.
Files to create: docs/task-rubric.md, a versioned rubric config, a candidate annotation dataset/schema, baseline scoring module and focused tests.
Expected output: auditable dimensions, evidence references and insufficient-evidence behavior, with a separated annotation review queue.
Definition of done: rubric documented; leakage-safe review/development split selected; baseline behavior tested; every task label states its method and evidence status.

Independent reviewers are not yet assigned. The eight case studies are illustrative coverage choices, not a representative validation sample or the planned 20-occupation evaluation set. No human validation, AI exposure/HVI scores, career recommendations, worker UI, county map or empirical model evaluation has been completed.

## Work log
- 2026-10-29: initialized project foundation and dataset discovery.
- 2026-10-29: acquired five official source assets; built and checked the core data pipeline; documented source coverage and provenance limitations. See Git history for published changes.
