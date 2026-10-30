# Research hypotheses, methods and evaluation
## Definitions
AI exposure measures potential relevance of a specified AI capability set to a task, at a stated date. It is not adoption, successful automation, or replacement probability. Human Value Index (HVI) is a provisional name for task dependence on human capabilities; it is not a measure of a worker's worth. Public UI should explain it as human-dependency characteristics.

## Hypotheses and falsifiable tests
| Hypothesis | Test | Baseline / comparison | Failure interpretation |
|---|---|---|---|
| H1: task evidence improves exposure interpretation | Held-out occupation review of task explanations | Single occupation-level benchmark | Do not claim improvement if reviewers or metrics disagree |
| H2: human-dependency dimensions distinguish augmentation from automation candidates | Independently annotated workflow suitability | Exposure alone vs exposure plus dimensions | Revise dimensions if no added value |
| H3: skill similarity plus feasibility improves transition relevance | Independent review of top five candidates | Skill-only cosine ranking | Similarity alone may be sufficient |
| H4: adaptation capacity changes regional rankings | Sensitivity and external descriptive comparison | Exposure-only ranking | Avoid ATVI branding if unstable or unsupported |
| H5: consented interviews recover useful tacit knowledge | Participant review and independent utility review | Existing procedure documents | Do not assert cultural preservation from text extraction alone |

## Exposure baseline
Define a dated capability rubric covering information transformation, language, code, structured analysis, perception, physical execution and interpersonal context. Start with transparent task rules and evidence citations. A scalar may be a weighted sum of normalized rubric dimensions; weights are research choices, versioned before evaluation. Initially publish dimensions and missingness before a headline score.

O*NET task importance is not task time share. Any occupation aggregate must state its weighting rule and report unweighted sensitivity. No claim about percentage of working hours without actual time evidence. Do not calibrate confidence from a model's self-reported certainty.

## Human dependency
Start with separate judgment, interpersonal, physical/contextual and creative dimensions; add cultural context only when defensible evidence exists. Occupation-level work context can contextualize a task but cannot be presented as directly observed task-level truth. Do not infer task-specific empathy or cultural knowledge from the occupation title alone.

Normalize source rating scales from their dictionaries, not per-batch minima/maxima. Keep importance and level separate. Establish a human review rubric; compare equal weights with plausible alternatives. Publish score ranges/rank stability across weight sets. No validated HVI exists at initialization.

## Workflow classification
A provisional quadrant uses x=AI exposure increasing right and y=human dependency increasing up:
high/high → augmentation; high/low → automation candidate; low/high → human-led.
Low/low means limited evidence of either measured dimension, not low-value work.
Thresholds are not yet selected. Safety-critical accountability, licensing, workflow constraints and uncertain evidence can override a numeric quadrant. Automation candidate is a research label, not permission to automate work.

## Transition baseline
1. Build occupation vectors from release-consistent skill importance; maintain level separately.
2. Rank by cosine similarity as the first baseline. Exclude the current occupation.
3. Apply explicit education, relocation and other declared hard constraints before final ranking.
4. Add salary retention, outlook and training-gap components only after join coverage is known.
5. Publish individual components, missingness and assumption flags; do not fill unknown cost/time with zero.
6. Compare skill-only ranking with feasibility-aware ranking. Return fewer than five when evidence or constraints require it.

Occupation requirements are proxies for a worker's skills. Only user-confirmed skills are personal evidence. Licensing and degrees are feasibility gates; short training roadmaps cannot promise access to regulated professions. National openings are projections, not local vacancies or current hiring.

## Annotation protocol
Proposed pilot: 200 tasks across at least 20 diverse occupations, each independently labeled by two reviewers using the same dated rubric, with adjudication notes. Pilot sample size is a planning target, not a completed study or power calculation. Include routine cognitive, physical, interpersonal and accountable tasks.

Separate rule-development tasks from the final test set by occupation; deduplicate near-identical tasks across splits. Store annotator pseudonym, rubric version, timestamp, capability assumptions, label, rationale and adjudication. Ask participants for consent where needed. Model-generated labels remain separate from human labels.

## Metrics and review
- Agreement: Cohen's kappa for two categorical reviewers plus confusion matrix; weighted agreement for ordinal dimensions.
- Classification: macro-F1 and class precision/recall on occupation-held-out tasks; compare baselines.
- Calibration: only when a model emits probabilities supported by reference labels.
- Ranking: Precision@5 and NDCG@5 with independently assigned relevance; also report fewer-than-five coverage.
- Feasibility: hard-constraint violations, licensing barriers and unavailable-data rate.
- Robustness: weight sensitivity, missing-feature ablation and crosswalk ambiguity.
- Fairness/accessibility: stratified plausibility and coverage for rural, lower-income, older and non-degree worker scenarios. Protected attributes are not individual ranking inputs.
- Geographic research: blocked spatial validation where an actual supervised outcome exists; uncertainty and rank stability for descriptive composites.

Predeclare operational acceptance thresholds after the annotation pilot and before final evaluation. Never select thresholds on the held-out test set. Expert review is planned, not assumed to have occurred.

## Leakage and reproducibility
Freeze release IDs, acquisition dates, schema mappings, random seeds and split membership. Split by occupation for task models; use temporal cutoffs for outlook research. Do not evaluate against the same LLM labels used to train a model. External exposure benchmarks are comparisons, not displacement outcomes.

Each experiment records ID, date, data hashes, features, method, parameters, split, metrics, artifacts and failure notes. Append results; never overwrite prior runs. No experiments or results are claimed at Phase 0.

## Phase 2 implementation boundary
The [task rubric](task-rubric.md) and [annotation guide](task-annotation-guide.md) implement a purposive 200-task pilot and a lexical evidence baseline. Exact spans are machine-generated cues, not exposure labels. Creative/cultural judgments remain manual-only. All scalar scores and performance metrics remain unset. The committed [pilot report](reports/task-pilot.json) records preparation counts only; independent review, adjudication and final confirmatory evaluation are pending.

## Implemented skill-transition baseline
The [candidate baseline](skill-transitions.md) compares complete source-normalized occupation skill-importance vectors using cosine. Context is joined through official mappings, remains outside the ranking formula, and can supply explicit filters. Importance differences and separately shown level differences compare occupations, not a worker's verified abilities. Unknown AI/HVI and training costs are not imputed. The published [audit](reports/skill-transition-audit.json) checks structure and source coverage only; independent transition-pair relevance/feasibility evaluation remains pending.
