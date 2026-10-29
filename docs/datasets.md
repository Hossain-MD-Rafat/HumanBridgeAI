# Dataset inventory and source guide
Research date: 2026-10-29. These are source recommendations, not downloaded assets. Release labels were checked against publisher pages; binary payloads, row counts and join coverage remain unverified.

## Start with these four source groups
| Priority | Source / release | Why HumanBridge needs it | Access and join |
|---|---|---|---|
| 1 — MVP | [O*NET 31.0 database](https://www.onetcenter.org/database.html), August 2026 | Occupation, task and skill foundation | Free downloadable archive; full O*NET-SOC code and release |
| 2 — MVP | [BLS OEWS](https://www.bls.gov/oes/tables.htm), May 2025 | Wage and employment context | Free ZIP/XLSX; SOC, geography, ownership/industry and year |
| 3 — MVP | [BLS employment projections](https://www.bls.gov/emp/data/occupational-data.htm), 2025–2035 | Outlook, openings and typical entry requirements | Free XLSX; National Employment Matrix code and base/target year |
| 4 — MVP | [O*NET crosswalks](https://www.onetcenter.org/crosswalks.html) and BLS crosswalks | Connect classification systems without title guessing | Download official mappings; preserve taxonomy and mapping multiplicity |

### 1. Occupation and task foundation
Get the [O*NET 31.0 Excel archive](https://www.onetcenter.org/dl_files/database/db_31_0_excel.zip) and [version-specific dictionary](https://www.onetcenter.org/dictionary/31.0/excel/).

Prioritize these logical tables: Occupation Data; Task Statements; Task Ratings; Essential Skills; Transferable Skills; Abilities; Knowledge; Work Activities; Work Context; Education; Training and Experience; Job Zones; Related Occupations; Software Skills; Content Model Reference; Scales Reference; Level Scale Anchors. Task/activity link tables can support later evidence mapping.

Inspect actual filenames and headers after download. Avoid assuming older tutorials' skill filenames match release 31.0.

**Limits:** occupation requirements are not measured individual skills; task ratings are not direct time allocations. Profiles do not supply validated HumanBridge HVI or AI exposure labels. Some dimensions or occupations may lack comparable ratings.

**Rights:** [CC BY 4.0 with attribution and change notices](https://www.onetcenter.org/license_db.html). Retain release-specific attribution; do not imply USDOL endorsement.

### 2. Wages and employment
Download [May 2025 national OEWS](https://www.bls.gov/oes/special-requests/oesm25nat.zip) first. Add [state](https://www.bls.gov/oes/special-requests/oesm25st.zip) and [metro/nonmetro](https://www.bls.gov/oes/special-requests/oesm25ma.zip) files when regional comparisons start.

Candidate fields to verify: OCC_CODE, OCC_TITLE, O_GROUP, TOT_EMP, A_MEDIAN, A_MEAN, H_MEDIAN and geography/industry/ownership fields where supplied. Filter to detailed occupations and the intended area and ownership universe before comparisons.

Treat suppressed, unavailable and top-coded cells according to the release notes; do not parse every nonnumeric symbol as zero. Retain source units and estimation uncertainty fields where supplied.

**Limits:** standard published OEWS geography is not detailed occupation-by-every-county. Estimates describe jobs in establishments, whereas ACS occupation measures describe residents. Do not mix the populations silently. Wages are occupation context, not an individual's salary offer.

**Rights:** see [BLS copyright information](https://www.bls.gov/bls/linksite.htm); record program/table attribution.

### 3. Outlook and typical preparation
Download [all occupational projection tables](https://www.bls.gov/emp/ind-occ-matrix/occupation.xlsx). Start with Table 1.2 and verify its exact worksheet and column labels; use Table 1.10 for separations/openings where relevant.

Needed concepts: base/projected employment, percent growth, annual openings, typical entry education, related work experience and on-the-job training.

**Limits:** national long-term projections are neither real-time vacancies nor county forecasts. Typical entry requirements do not substitute for state licensing rules or personalized training duration. This URL is not versioned: freeze retrieved bytes, workbook vintage and SHA-256.

### 4. Identifier crosswalks
- [O*NET-SOC 2019 to 2018 SOC](https://www.onetcenter.org/taxonomy/2019/soc/2019_to_SOC_Crosswalk.xlsx?fmt=xlsx)
- [O*NET to BLS National Employment Matrix](https://www.bls.gov/emp/classifications-crosswalks/nem-onet-to-soc-crosswalk.xlsx)
- BLS National Employment Matrix/SOC to ACS crosswalk, linked on the [BLS projections page](https://www.bls.gov/emp/data/occupational-data.htm), for later ACS work.

Crosswalk release dates may differ from data release dates. Save originals and verify code coverage against both endpoint datasets. A one-to-many correspondence is not a validated allocation weight. Never sum duplicated SOC employment across O*NET specializations.

## Regional extension: after the worker MVP
| Source | Required variables or tables | Geography / join | What it cannot establish |
|---|---|---|---|
| [ACS 2024 5-year](https://www.census.gov/data/developers/data-sets/acs-5year.html), covering 2020–2024 | B24010 occupation; B15003 education; B19013 median household income; B17001 poverty; B23025 employment status; B28002 internet subscription | County, state+county FIPS; retain estimate and margin of error | Not a detailed SOC employment census or physical broadband availability survey |
| [2024 Census county boundaries](https://www.census.gov/geographies/mapping-files/2024/geo/carto-boundary-file.html) | County identifiers and simplified polygons | GEOID string; reconcile to ACS vintage | A map boundary is not economic evidence |
| [NCES IPEDS](https://nces.ed.gov/ipeds/use-the-data) | Institution directory, coordinates, programs/completions, cost context | UNITID; CIP and official CIP–SOC mappings | Nearby institution does not prove a worker can access or complete a course |

Choose 2024 boundaries for the ACS 2024 baseline even though newer boundaries exist. Check county-equivalent changes and ACS geography documentation. First study covers 50 states and DC; document territorial exclusions.

ACS API access currently requires a personal key according to the publisher documentation. [Variable groups](https://api.census.gov/data/2024/acs/acs5/groups.html) define the table concepts. Retain MOEs and special-value annotations. B24010 categories are coarser than detailed SOC; sum male/female estimates only for matching, nonoverlapping occupation categories. Do not sum nested subtotals, and propagate uncertainty using documented Census guidance.

B28002 measures household internet subscription, not infrastructure supply or an individual's digital proficiency. Use aggregate measures solely for regional analysis. ACS county resident composition and OEWS work-location composition must stay separate.

A county exposure estimate requires an explicit coarse occupation aggregation or a separately validated small-area model. Do not copy a metro score to every member county and call it measured county exposure.

## Research comparators: optional
| Source | Use | Caveats and terms |
|---|---|---|
| [Felten, Raj & Seamans AIOE](https://github.com/AIOE-Data/AIOE) | Compare occupation-level exposure rankings; inspect generative AI variants | Historical capability construct; no replacement labels. Explicit redistribution terms not established here: do not vendor files until resolved |
| [GPTs-are-GPTs](https://github.com/openai/GPTs-are-GPTs) | Compare published occupation-level human/model ratings | Historical LLM assumptions; not current ground truth. Repository MIT license; verify underlying asset notices and preserve attribution |

Pin any benchmark to a commit and evaluate taxonomy compatibility before comparisons. Keep benchmark development and HumanBridge test labels independent.

## Necessary data we must create
1. **Reviewed task annotation set:** capability date, rubric, dimensions, workflow label, evidence, independent reviewer IDs and adjudication. Public datasets above do not complete this.
2. **Transition relevance set:** reviewed candidate career pairs with skill compatibility, education/licensing barriers and accessibility judgments.
3. **Consented tacit-knowledge pilot:** interviews, participant-reviewed extracts, permissions and verification status. No open dataset here can replace informed participation.
4. **Verified learning resource catalog:** skill links, provider, eligibility, date, location/online access and published cost/duration. Unknown values stay unknown.

Do not treat O*NET Related Occupations as observed real worker transitions. Do not scrape LinkedIn, Indeed or licensed job-posting corpora as the MVP default. Real vacancy data and course outcomes are separate later acquisition decisions.

## Minimal acquisition recommendation
Download the O*NET ZIP, BLS national OEWS ZIP, projection workbook, and two occupation crosswalks first. That is sufficient to start the occupation/task/skill pipeline. Research labels and validation remain necessary before credible scores. Add ACS, boundaries and IPEDS only after the worker flow works.

For exact destinations, checksum commands and readiness gates see [data acquisition](data-acquisition.md). The [JSON catalog](../config/datasets.json) records source IDs, release selections, access, permissions status and links. None of these sources requires a GPU; initial core work requires no paid dataset.
