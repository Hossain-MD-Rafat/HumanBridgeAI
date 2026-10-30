# Occupation skill cosine v0.1.0
## Purpose and status
An interpretable baseline for exploring transferable occupation requirements. No learned weights or LLM labels are used. Status: unvalidated occupation-profile candidates, not personalized career recommendations or ranking of human worth.

## Inputs
Pinned O*NET 31.0 importance ratings for 35 fixed essential/transferable skills; complete unsuppressed profiles only. Normalize by source anchors 1–5, then compare cosine. Source levels are separate context. Optional wage/education/experience filters use official mapped BLS facts. Personal or protected attributes are not ranking inputs.

## Outputs
Up to five occupations other than the source, deterministic ranks, raw cosine values, additive leading skill contributions, positive occupation-importance differences and source-backed wage/outlook/preparation context. Licensing/accessibility are explicitly not_verified. AI exposure, HVI and ranking-quality metrics remain unset.

## Evaluation
Synthetic tests cover known cosine values, component sums, source normalization, no imputation, unknown/ambiguous mapping, self exclusion, tie order, filters, missing wages, unknown source income, impossible requests and nonmutation. A small actual-schema SQLite fixture tests quality flags, Not Relevant levels, opening units and stale fingerprints. The real-data [audit](../reports/skill-transition-audit.json) checks 910 profiles and 16 case-study contracts. No human relevance, transition feasibility, Precision@5, NDCG or employment outcome validation has been performed.

## Limitations
Broad general skill vectors are correlated, so high similarity can occur across occupations with very different domain, licensing or preparation requirements. Skill shape similarity is not percentage overlap or personal qualification. Unknown context stays unknown; filters provide source compatibility only. Source occupational medians are neither personal pay forecasts nor specialization-specific estimates. Real career transitions can require qualifications and resources absent from these data.

## Appropriate use and promotion gates
Use for research comparisons and inspecting candidate requirements. Do not use it to make hiring rejection, termination, wage-reduction or individual employment decisions. Before making a validated transition recommendation, obtain independent career-pair judgments, verify licensing/accessibility and evaluate recommendations for non-degree/rural/resource-constrained worker scenarios. Compare later feature additions against this baseline rather than assuming more complexity improves outcomes.

## Reproduction
Follow [run instructions](../skill-transitions.md). Inputs, config and code are fingerprinted. Raw source data, private profiles and reviewer responses are not included in saved public audit metadata. Third-party attribution is in [notices](../../THIRD_PARTY_NOTICES.md); USDOL/ETA has not approved, endorsed or tested these transformations.
