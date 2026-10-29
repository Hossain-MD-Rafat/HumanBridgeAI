# ADR 003: interpretable, provisional measures
Status: accepted for Phase 0, 2026-10-29.

## Context
The vision proposes HVI, complementarity and vulnerability indices. These are research constructs with no validated HumanBridge measurements yet.

## Options
Publish branded scalar scores immediately; use external exposure measures as ground truth; develop interpretable components with independent review.

## Decision
Develop task-level evidence and simple baselines first. Label every HumanBridge score experimental, with source/method versions, coverage and uncertainty. Keep external benchmarks separate. Defer final weights and thresholds until rubric and sensitivity work. Do not convert an exposure index to a replacement probability.

## Reason
Clear components and missingness are more defensible than arbitrary precision. Occupation work-context data alone do not establish task-level cultural knowledge.

## Tradeoffs
Early demos may show insufficient evidence. Independent annotation costs reviewer time. Findings may invalidate a proposed index, in which case revise or remove it.
