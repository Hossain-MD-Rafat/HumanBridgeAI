# Project status and Phase 0 checklist
Date: 2026-10-29. Current phase: 0.
Current objective: establish the repository and a defensible dataset acquisition plan.
Input: owner's master brain and an initially empty GitHub repository.
Expected output: planning, sources, schema and reproducibility checks.

## Completed foundation
- [x] Project requirements and MVP acceptance criteria
- [x] System and technical architecture
- [x] Dataset inventory and acquisition order
- [x] Research hypotheses and evaluation design
- [x] Initial database schema and repository structure
- [x] 16-week roadmap
- [x] Risks, ethics and mitigation plan
- [x] Initial architecture decisions and third-party notices
- [x] Executable foundation and schema checks

## Pending Phase 0 closure
- [ ] Owner reviews the scope and documents any material changes.
- [ ] Select an initial occupation review cohort with exact source codes.
- [ ] Confirm independent reviewer availability for the annotation pilot.

## Not completed
No source datasets have been downloaded or ingested. Download links were discovered from source landing pages; archive contents, checksums, row counts and actual join coverage remain unverified. No scores, models, API, UI, graph database, county map or empirical results exist.

## Next session: Phase 1 acquisition
Files to modify: config/datasets.json, data/manifest entries, dataset cards, and new ingestion modules with tests.
1. Download the pinned O*NET archive and dictionaries; record SHA-256 and raw headers.
2. Download BLS national wages, projections and both required occupation crosswalks.
3. Register immutable manifests before transformations.
4. Normalize occupation/task/skill records and report crosswalk coverage.
5. Review exact occupation codes for the initial case studies.

Definition of done: reproducible core data snapshot with provenance, validated keys and a mapping coverage report. Do not begin scalar score generation before the evidence rubric is defined.

## Work log
2026-10-29: foundation prepared; sources researched; schema and documentation checks run locally. See Git history for published file changes. Planned tests are not evidence that an empirical model has been validated.
