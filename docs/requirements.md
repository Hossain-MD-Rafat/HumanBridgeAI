# Requirements and MVP specification
Date: 2026-10-29. Owner: MD Rafat Hossain. Phase: 0.

## Problem and users
Workers need actionable ways to adapt as AI changes individual tasks. Employers and policymakers need aggregate evidence about adaptation, not unsupported predictions of individual displacement. Researchers need reproducible, traceable methods.

The first release serves a worker exploring an occupation without an account. Employer redesign, community mapping, and consented knowledge preservation are later work.

## Functional requirements
| ID | Requirement | Acceptance evidence |
|---|---|---|
| F01 | Search titles, aliases, and occupation codes | Bookkeeper query resolves to a source occupation; no-match state works |
| F02 | Display task statements with source ratings | Every displayed task links to a versioned source record |
| F03 | Show experimental AI exposure | Method, dimensions, evidence, date, coverage, and uncertainty visible |
| F04 | Show experimental human-dependency/HVI components | Components and limitations visible; never described as human worth |
| F05 | Classify task workflows | Automate candidate, augment, human-led; explicit insufficient-evidence fallback |
| F06 | Rank up to five other occupations | No self recommendation, duplicates, or hidden hard-constraint violations |
| F07 | Explain skill overlap and gaps | Shared/missing skills and source importance visible; personal assumptions stated |
| F08 | Provide a learning-priority plan | Evidence-backed skill order; no invented training hours or costs |
| F09 | Compare wages and outlook | Unit, geography, year, source, suppression and projection caveats visible |
| F10 | Export reproducible research output | Source release IDs, method version and run ID retained |

Four-category research workflow labels may distinguish AI assist and human+AI collaboration; the MVP groups them under augment. Ambiguous tasks stay unclassified. Never force a label because a chart needs a point.

## Nonfunctional requirements
- Local foundation and baseline pipeline must run on a consumer laptop without a GPU.
- Reprocessing a frozen input produces the same row keys and deterministic baseline outputs.
- Pipeline rejects duplicate natural keys, broken foreign keys and unknown scale IDs.
- Every score and recommendation traces to an input snapshot and method version.
- Null, suppressed and unavailable data remain distinct from numeric zero.
- Personal profiles remain session-local for MVP; logging must not capture free text or secrets.
- User-facing explanations use plain language, readable contrast and keyboard-accessible controls.
- Proposed performance target: occupation detail response p95 under 2 seconds on documented local hardware after precomputation; measure before claiming it.

## MVP scope
Occupation search, task exploration, prototype AI exposure, prototype HVI, workflow labels, transition ranking, skill gaps, and explanations. Use a fixed initial release and an explicitly reviewed occupation cohort; report nationwide source coverage separately from validated score coverage.

Initial case studies: bookkeeping, customer service, software development, nursing, teaching, electrician work and construction supervision, mapped to exact source codes during ingestion. Labels such as data analyst may be ambiguous; present candidates rather than inventing a SOC code.

## Explicitly later
- Phase 2: state/metro context, county vulnerability prototype, map, aggregate employer analysis.
- Research extension: learned ranking, graph models, spatial validation, culturally informed HVI review.
- Future product: accounts, verified training marketplace, institutional integrations, production monitoring.
- Consent-based pilot: tacit knowledge interviews and participant-reviewed knowledge records.

## MVP definition of done
- [ ] Frozen core source files registered with checksums, dates, licenses and dictionaries.
- [ ] Canonical occupation, task and skill tables loaded; zero orphan keys and duplicate natural keys.
- [ ] Crosswalk coverage reported with unmatched and one-to-many mappings reviewed.
- [ ] All F01–F10 demonstrated end to end for the reviewed cohort.
- [ ] Every numerical output identifies whether it is observed, derived, model-produced or illustrative.
- [ ] Annotation and ranking evaluation completed on held-out data; limitations reported even when results disappoint.
- [ ] Recommendations exclude the source occupation; hard-constraint violations are zero in the test cohort.
- [ ] Empty, missing, suppressed, unsupported and ambiguous cases tested in API and UI.
- [ ] One-command local pipeline and demo instructions verified from a clean checkout.
- [ ] Dataset cards, model cards, ethics note and reproducible evaluation report included.
- [ ] No invented wages, scores, transition duration, training cost or displacement probabilities.
- [ ] Owner can reproduce the bookkeeper flow and two contrasting occupation stories.

Phase 0 completion is not MVP completion.
