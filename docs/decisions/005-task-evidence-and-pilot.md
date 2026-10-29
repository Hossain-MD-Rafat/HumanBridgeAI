# ADR 005: lexical evidence before scalar exposure scores
Status: proposed on the Phase 2 feature branch, 2026-10-29.

## Context
The source database contains occupation/task facts but no independently validated HumanBridge task-exposure labels. Task verbs alone cannot establish capability, replacement probability, cultural judgment or measured time savings.

## Options
Generate 0–100 scores from keyword weights; use an LLM's labels as both predictions and ground truth; or build explicit lexical review cues and independent annotation infrastructure first.

## Decision
Build a dated, versioned nine-dimension review rubric. Seven dimensions have limited lexical rules; creative and cultural judgment remain manual-only. Preserve exact spans and route negation and safety contexts conservatively. Leave scalar scores and final workflow labels null.

Prepare a 200-task/20-occupation purposive pilot. Keep the eight known case studies in development. Group occupations connected by detected selected-text duplicates before assigning the holdout. Generate two blind queues with empty human fields, and machine suggestions only for development tasks. Freeze run inputs and content hashes, including code/config versions.

## Reason
This produces a reproducible, inspectable baseline while preserving the distinction between machine suggestions and independent evidence. It implements the planned Phase 2 foundation without inventing empirical validation or ranking human worth.

## Tradeoffs
Lexical cues have limited semantic coverage. Unknowns and manual review are frequent and intentional. The pilot is not representative; semantic leakage review, reviewer assignment, adjudication and performance evaluation remain pending. No result is promoted to a validated public score.

## Branch workflow
Phase 2 is published through feature/phase-2-task-exposure and a pull request targeting main. Review and merge are separate from implementation; future phase work should follow the same reviewable branch workflow.
