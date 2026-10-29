# Task review rubric v0.1.0
Date: 2026-10-29. Status: experimental, prepared for independent review.
Current objective: turn source tasks into auditable review evidence before computing headline exposure or human-dependency scores.

## Research question and assumptions
For the specific task, what assistance might a human-reviewed text/code/data system provide, under what conditions, and what would still require human participation? Assume lawful access to necessary digital inputs. Do not assume autonomous physical execution, professional authority, reliable completion, or measured time savings.

The date identifies this research scenario, not a certified benchmark of every AI system available that day. No named model has been tested in this phase. Occupation title, wages and stereotypes are not evidence of task feasibility.

Methodological references: [Eloundou et al. (2023)](https://arxiv.org/abs/2303.10130v5) uses a task-based exposure rubric; [ILO Working Paper 140 (2025)](https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure) combines task evidence with worker/expert-informed assessment. These motivate explicit assumptions and review; their published labels, scores and numerical thresholds are not imported. This baseline is not a replication or a validated update of either study.

## Dimensions
| Dimension | Reviewer asks | Lexical screen can establish |
|---|---|---|
| Information processing | Are documented records/information transformed or retrieved? | A configured action/object phrase occurs |
| Language generation | Is a language artifact created or revised? | A configured drafting/editing phrase occurs |
| Coding | Is source code or software created/maintained? | A configured coding phrase occurs |
| Analytical support | Is quantitative information analyzed? | A configured analytical phrase occurs |
| Interpersonal context | Does execution depend on direct interaction, trust or negotiation? | Interaction wording only; no measured empathy or trust |
| Physical context | Is acting in a physical environment necessary? | A physical action/object phrase occurs |
| Accountability | Does the text invoke consequential judgment, safety or regulated responsibility? | Relevant wording only; authority and risk still need context |
| Creative judgment | Is human creative judgment specifically supported? | Nothing automatically: manual review only |
| Cultural context | Is contextual/cultural knowledge supported by evidence? | Nothing automatically: manual review only |

Every human dimension label is one of not_supported, supporting, central, or insufficient_evidence. Here not_supported means the reviewer did not find sufficient support in the evidence they cite; it is not a claim that a worker lacks the capability. Missing context should produce insufficient_evidence, not a confident negative.

## Exposure labels for human review
- **not_supported:** cited evidence does not establish relevant assistance under the stated scenario.
- **assistive_candidate:** evidence supports a bounded supporting substep; the task's core execution remains dependent on unresolved context or other work.
- **substantial_candidate:** evidence supports assistance with a core task operation, conditional on documented quality, access, review and workflow assumptions. This is qualitative; it is not a measured percentage of time saved or probability of automation.
- **insufficient_evidence:** inputs, execution environment, quality standard or capability evidence do not support a defensible judgment.

Reviewers must identify the operation, needed inputs, expected output, quality standard, failure consequences and missing context. An experiment or source about a specific capability is stronger evidence than the appearance of a verb. If actual performance has not been observed, explicitly mark that in the rationale.

## Optional workflow hypothesis
After independently reviewing the dimensions and exposure evidence, choose automation_candidate, augmentation_candidate, human_led or insufficient_evidence. These are research hypotheses about a workflow; they authorize no employment action or autonomous execution. Automation_candidate requires evidence that the complete bounded operation, necessary inputs, quality checks and oversight can be specified. A lexical match alone never meets that requirement. Legal/clinical authority, safety and accountability remain explicit review requirements.

## What the machine baseline outputs
[Versioned config](../config/task_rubric.json) → [lexical screen](../src/humanbridge/task_screening.py).
Each rule is a project-owned regex over the original task statement. A match records its rule ID, exact text quote and character offsets. Status is cue_found; no match is not_assessed. Negation/qualification guard matches downgrade matching dimensions to ambiguous_cue. A safety/regulated-context guard routes the entire statement to manual_context_review. Guards are deliberately conservative; they are not a complete risk detector.

Routing categories: digital_assistance_review, digital_and_context_review, human_context_review, manual_context_review, insufficient_evidence. These categories are review organization aids, not human exposure labels, workflow labels or ordinal rankings. Numeric ai_exposure and human_dependency, and the final workflow_label, always remain null.

Examples using synthetic text:
- Draft reports and discuss findings with clients → digital and context cues, with exact matched spans.
- Do not write reports without permission → manual review; the positive-looking drafting cue is ambiguous.
- Write reports about clinical patient examinations → manual contextual review even though drafting wording appears.
- Consider unusual circumstances → insufficient evidence; unmatched dimensions remain unknown.

## Limitations and promotion gates
Rules miss synonyms, task decomposition, implied social/physical context and negation scope. A quoted phrase is evidence of wording, not measured capability. Cultural or creative judgment is not inferred from a title. Source occupational context and AI/Expert work-style ratings are not independent human task labels.

Before publishing task exposure scores: independently label the pilot, adjudicate disagreements, inspect false positives/negatives, freeze acceptance criteria before a new confirmatory test, and compare the transparent baseline with any proposed learned method. Report agreement and appropriate task metrics only after genuine labels exist. Do not evaluate a method against its own suggestions.
