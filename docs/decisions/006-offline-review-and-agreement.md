# ADR 006: offline human review and gated agreement analysis
Status: proposed on feature/review-workbench-evaluation, 2026-10-29.

## Context
Phase 2 prepares blind JSONL queues but asks reviewers to edit a structured format manually. Independent labels do not yet exist. A usable review interface and trustworthy analysis gates can be built without inventing those labels.

## Options
Ask reviewers to edit JSON directly; introduce a hosted multiuser app; or generate a self-contained offline review file for each slot.

## Decision
Build offline HTML from a verified frozen run. Bundle only one blind queue, human rubric questions/choices and source attribution. Drafts remain in tab memory and can be downloaded/imported locally. Response exports contain completed records plus untouched blanks for unfinished tasks. No network, browser-storage autosave, model hints or server account is needed.

Share run/response validation across commands and enforce one consistent pseudonym per slot with distinct reviewer identities. Compute only paired human-review agreement after explicit research attestation and completion of every selected-split task. Retain insufficient evidence as a category, undefined kappa as null, and disagreements as pending adjudication. Preserve originals and fingerprint outputs.

## Reason
This removes the JSON-editing burden while preserving the current annotation contract and separation from machine suggestions. It produces usable next-step tooling without paid services or false performance claims.

## Tradeoffs
Offline memory is not autosave: reviewers must export draft backups. Browser download/resume behavior needs testing. Identity and independence cannot be authenticated by a pseudonym or checkbox. The legacy response format does not independently carry a run hash, so coordinator provenance and rubric version discipline remain required. Agreement alone does not establish truth or justify a validated exposure score.

## Branch dependency
PR #1 remains open. This branch starts at its Phase 2 head and targets feature/phase-2-task-exposure in a stacked pull request, so its diff includes only the workbench/evaluation additions. No merge into main is performed by this work.
