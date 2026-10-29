# 16-week execution roadmap
This is an effort-based sequence, not a guaranteed delivery date. Revisit estimates after actual ingestion. Nationwide mapping and knowledge preservation cannot delay the worker MVP.

| Week | Phase / objective | Deliverable | Exit gate |
|---|---|---|---|
| 1 | 0: foundation | Requirements, architecture, source inventory, schema, decisions | Foundation checks pass; review scope |
| 2 | 1: acquire core data | Frozen O*NET, BLS and crosswalk files, manifests and data cards | Checksums, dictionaries and permissions recorded |
| 3 | 1: normalize | Occupation/task/skill tables; mapping coverage report | No duplicate natural keys or orphan rows |
| 4 | 2: exposure baseline | Dated task rubric, transparent rules, annotation pilot | Reviewer disagreements documented |
| 5 | 3: human dependency | Dimension mapping and baseline components | Sensitivity and missingness report |
| 6 | 4: complementarity | Workflow categories, evidence and unknown states | Occupation-held-out review ready |
| 7 | 5: skill relationships | Relational graph edges and cosine similarity | Source-consistent vectors; no invented edges |
| 8 | 6: transitions | Feasibility-aware top-five baseline | Self exclusion, constraints and missing data tested |
| 9 | 7: gaps and explanations | Shared/missing skills, priority plan and case studies | No unsupported duration/cost claims |
| 10 | 10/11: service and demo | API contracts and worker exploration interface | Bookkeeper flow plus contrasting cases run |
| 11 | MVP validation | Held-out annotation and ranking evaluation | Publish results, failures and limitations |
| 12 | MVP reproducibility | Dependency lock, pipeline command, data/model cards | Clean-checkout demo and MVP DoD review |
| 13 | 8: regional prototype | ACS county context and consistent boundary joins | Vintage alignment and MOE handling documented |
| 14 | 8/9: regional evaluation | Descriptive vulnerability prototype and map | Spatial/missingness/sensitivity review |
| 15 | 9: knowledge pilot + 12: operations | Consent workflow prototype; packaging and logging | No private interview material in public Git |
| 16 | 13: research synthesis | Paper outline, reproducibility report and demo narrative | Claims supported by actual completed evidence |

Dependencies: normalization precedes scoring; independent labels precede evaluation; crosswalk coverage precedes regional aggregation. Neo4j and advanced ML require a documented advantage over the baseline. Weeks 13–16 may move to a separate milestone if the MVP gates are not met.
