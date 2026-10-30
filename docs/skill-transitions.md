# Transferable-skill candidate baseline
Status: occupation-skill-cosine-v0.1.0, unvalidated research baseline. This increment progresses the worker MVP while independent task-exposure review remains pending. It does not depend on guessed AI exposure or HVI values.

## Run it
First build the [pinned core database](running-pipeline.md). Search a title with explore_occupation.py, then use its full O*NET-SOC code:

```bash
python scripts/recommend_transitions.py 43-3031.00
```

Expected: up to five other occupations, raw cosine similarity, leading shared-skill contributions, priority occupation-importance differences and mapped national wage/outlook/preparation context. This is a command-line candidate explorer, not a validated career adviser or the complete worker-facing product.

For an illustrative constrained bookkeeping case:

```bash
python scripts/recommend_transitions.py 43-3031.00 --allowed-education "High school diploma or equivalent" --allowed-related-experience None --min-median-retention 1
```

For a direct national wage floor or saved reproducible output:

```bash
python scripts/recommend_transitions.py 43-3031.00 --min-national-median 55000 --top-k 3 --output-dir artifacts/skill-transitions
```

--allowed-education and --allowed-related-experience can be repeated. They are exact membership filters over published BLS categories, not a guessed hierarchy or a claim about the worker's actual education/experience. Omitting a filter means no constraint is applied. --min-median-retention compares target and source occupational national medians, not the worker's current or future personal income. It requires a usable source median. Missing required target context excludes a candidate; it is never filled with zero.

--top-k accepts 1 through 5. There is no self recommendation, duplicate candidate or padding to five. Impossible filters return an empty list. Unknown source codes or profiles without complete usable skill data fail with an explicit explanation. --database may select a local copy, but it must match the frozen core fingerprint.

## Fixed feature construction
[Method config](../config/skill_transition.json) pins 35 essential/transferable skill element IDs and the source snapshot. Each profile uses unsuppressed importance ratings on the IM source scale, whose fixed anchors are 1 and 5. Normalize each feature as (value − 1) / 4. This makes the source's lowest importance anchor zero without treating missing data as zero.

All 35 usable ratings are required. Exclude incomplete, suppressed or zero-vector profiles rather than filling gaps. Current coverage: 910 complete skill profiles from 1,016 catalog occupations. Full exclusions and context availability appear in the [audit](reports/skill-transition-audit.json). Software examples, domain knowledge, abilities, education and work-style measures are not ranking dimensions in this baseline.

Importance and level are distinct constructs. Level (LV, source 0–7) is displayed separately where both source and target measurements are usable. Missing, suppressed or Not Relevant levels remain unknown. A level difference between occupations is not an observed deficit in a worker.

## Ranking and explanation
The ranking value is cosine(x,y) = sum(xᵢyᵢ) / (norm(x) × norm(y)). It is unitless, not a percentage of shared skills, a success probability or an AI-resilience measure. Ties are broken by occupation code; no salary preference is hidden in tie-breaking.

Each skill's additive contribution is xᵢyᵢ divided by the same denominator. The five largest positive contributions are displayed; the remaining contribution is retained so explanations sum to the actual similarity. Skill differences are ordered by positive target-minus-source importance, then target importance and element ID. They identify requirements to inspect, not verified personal missing skills. No invented training duration, cost or course recommendation is supplied.

## Context and constraints
Official O*NET→SOC mappings connect national OEWS median wages; official O*NET→NEM mappings connect projection and preparation facts. No title matching, unconditional code truncation or inferred allocation is used. Multiple targets stay ambiguous even if values match. Suppressed/top-coded wages stay unknown, and every context retains source release IDs and mapping evidence.

Annual openings are converted from source thousands to openings/year for display, with original values and units retained in mapping evidence. Employment growth is national long-term projection context, not current local hiring. A mapped SOC/NEM aggregate may cover multiple O*NET specializations; it is not a specialization-specific estimate and must not be double-counted as separate workforce totals.

Entry education and related experience are source-data screens only. Every candidate retains unverified licensing/accessibility status. The baseline has no local demand, relocation, course access, training cost, licensing verification or confirmed personal skill data. It cannot certify a realistic transition. For example, an unfiltered bookkeeping result can include Financial Managers because general skill shapes are similar, despite the published additional preparation/experience requirements.

## Reproduction and validation
```bash
python scripts/audit_skill_transitions.py
python -m unittest discover -s tests -v
python scripts/check_foundation.py
```

The real-data audit checks the eight existing case-study occupations with unfiltered and explicit filtered requests: 16 ranking-contract checks. It verifies no self/duplicate output, score/contribution consistency, deterministic repeated ranking, hard-filter compliance and empty output for impossible filters. Its illustrative education filter uses each source occupation's typical category, not a worker profile.

The CLI includes source fingerprint, config and engine hashes. Saved result directories are content-identified and conflicting existing results are not overwritten. Source SQLite tables, the frozen task pilot and human labels are unchanged.

These tests are structural checks, not Precision@5, NDCG, accessibility validation or transition outcome research. Independent transition-pair judgments remain necessary. Similarity is often high because these are broad general skills; the [model card](model-cards/skill-transitions.md) describes the limits.

## Modules
| File | Purpose / inputs / outputs | Failure cases |
|---|---|---|
| transition_data.py | Frozen SQLite + config → complete profiles and mapped source context | Stale fingerprint, changed scale/schema, missing skill dictionary |
| skill_transitions.py | Profiles + explicit constraints → cosine-ranked candidates and explanations | Missing source vector, invalid filters, zero vectors, unsupported categories |
| recommend_transitions.py | Full source code + CLI filters → JSON report and optional immutable artifact | Unsupported code or incompatible source copy |
| audit_skill_transitions.py | Frozen data + case cohort → aggregate coverage/contract report | Inconsistent explanations, violated filters or nondeterministic results |

The next product step can expose these candidates and source differences in the worker interface. Human-reviewed career relevance and licensing/accessibility checks remain separate research requirements; HVI/exposure should join ranking only after their own evidence gates are met.
