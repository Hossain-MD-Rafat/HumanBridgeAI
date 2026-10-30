# ADR 007: skill-only candidate ranking with explicit context filters
Status: proposed on feature/skill-transition-baseline, 2026-10-29.

## Context
Task exposure and HVI need independent evidence. Meanwhile the validated core already supports occupation-level skills, wages and preparation facts. The worker MVP can advance without inventing missing scores.

## Options
Block all career work on task labels; invent a weighted score with unknown HVI/training cost; or implement a transparent skill-only baseline with explicit source-context constraints.

## Decision
Pin 35 essential/transferable skill dimensions, require complete usable importance profiles, normalize by fixed source anchors and rank cosine. Exclude self, return at most five and break ties by code. Explain additive shared-skill contributions and occupation requirement differences. Do not interpret them as verified personal skill gaps.

Use official crosswalks for source context; preserve ambiguity, suppression, units and unknowns. Wage, entry-education and related-experience filters are opt-in exact source-data screens. They never change the cosine formula or certify licensing, accessibility or feasibility. HVI, exposure, salary growth and personal attributes are not ranking inputs. No arbitrary branded composite index is introduced.

## Reason
The baseline is reproducible and falsifiable, moves a core MVP flow forward, and supports later comparisons without circular use of unvalidated task labels. Source preparation barriers remain visible rather than being hidden by a high salary or similarity score.

## Tradeoffs
General skills alone can rank implausible domain transitions highly. Complete-case filtering excludes 106 catalog profiles and can affect coverage. National source context is not local opportunity. Independent transition review and verified licensing/training/accessibility data are needed before stronger claims.

## Branch dependency
The first two pull requests remain open. This branch starts from feature/review-workbench-evaluation and targets it in a stacked pull request. Main and the earlier branches are not automatically merged or rewritten.
