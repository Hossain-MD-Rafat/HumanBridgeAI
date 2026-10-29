# Initial database contract
The executable [SQLite DDL](../schema/001_initial.sql) defines a local research store. It is a foundation, not a claim that sources are already loaded.

| Entity | Unit / key | Purpose |
|---|---|---|
| dataset_release | Snapshot ID; dataset+version+hash | Provenance for original bytes |
| occupation | Release + full source code | Titles, taxonomy and descriptions |
| task | Release + occupation + task ID | Occupation-specific task statement |
| scale | Release + scale ID | Source scale definitions |
| element | Release + element ID | Skills, knowledge, abilities and context dimensions |
| occupation_element_rating | Occupation + element + scale + category | Keep importance/level and categorical frequencies separate |
| task_rating | Task + scale + category | Source task evidence |
| occupation_crosswalk | Mapping release + source/target taxonomy codes | Preserve mappings, ambiguity and optional validated weights |
| geography | ID + boundary vintage | Separate national, state, metro and county geography |
| labor_statistic | Source + code + geography + universe + metric + period | Tidy wages, employment, outlook and entry-requirement extensions |
| county_observation | Source + county + boundary + variable | ACS estimates, MOEs and flags |
| analysis_run | Run ID | Method, capability date and parameters |
| analysis_run_input | Run + release | Reproducible snapshot membership |
| task_score | Run + source task | Experimental dimensions, workflow and evidence |
| transition | Run + source/target | Ranked recommendations, constraints and explanation |

## Design boundaries
- labor_statistic numeric values do not hold textual education or training categories. Add typed categorical source tables in Phase 1 once actual workbook headers are inspected.
- Source taxonomy codes in crosswalk/labor tables deliberately need not exist in the O*NET occupation table. Validate their own source code sets during ingestion.
- Importers must select or aggregate source rating populations explicitly; the current rating keys assume one selected source row per category. Extend the key if the dictionary requires additional dimensions.
- Crosswalk weight sums, scale-specific value ranges, JSON structure, county geography types and rating quality rules require ingestion checks beyond these SQL constraints.
- Derived task scores reference a run's registered source snapshot. Evidence references in JSON need application validation.
- A transition score has no fixed range until its baseline formula is defined. It is not a probability.
- Task–activity edges, resource catalogs, annotations, experiment artifacts and consented knowledge records are later migrations. Do not force them into untyped personal free-text columns.
- Full schema revisions must preserve source release identity and produce explicit migrations.
