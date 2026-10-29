# Core source data cards
Acquired 2026-10-29. Snapshot: core-2026-10-29-v1. Exact URLs, UTC times, bytes and full SHA-256 values are in the five [manifests](../../data/manifest). [Snapshot lock](../../config/core_snapshot.json) records the observed releases separately from preliminary acquisition labels.

## O*NET 31.0
- Publisher: USDOL/ETA, National Center for O*NET Development.
- Source and dictionary: [database](https://www.onetcenter.org/database.html), [31.0 dictionary](https://www.onetcenter.org/dictionary/31.0/excel/).
- Unit: occupation profile, occupation task, occupation-element/scale/category rating, alias, job zone or related-occupation edge.
- Release: 31.0 archive; individual survey and rating dates vary and are retained. The archive directory is db_31_0_excel.
- Observed import: 1,016 occupation profiles; 18,838 task statements for 923 occupations; 635,913 occupation-element ratings; 165,780 task ratings; 54,269 job-title aliases; 923 job zones; 18,460 related-occupation edges. Skill ratings cover 910 occupations.
- Collection/provenance: original Domain Source, Date, sampling N, uncertainty bounds, suppression and relevance fields are preserved where supplied. Occupation-element rows include 37,422 AI/Expert, 158,340 Analyst, 1,845 Analyst - Transition, 317,778 Incumbent and 120,528 Occupational Expert records. These are record counts, not counts of independent reviewers.
- Missingness: no assumption that every occupation has measured tasks or skills; preserve source suppression, null and Not Relevant flags. Task frequency category percentages and continuous level/importance values remain separate scales.
- Rights: [O*NET database CC BY 4.0 guidance](https://www.onetcenter.org/license_db.html). This project normalizes and selects records. USDOL/ETA has not approved, endorsed, or tested these modifications. See [notices](../../THIRD_PARTY_NOTICES.md).
- Appropriate use: occupation-level exploration and baseline research. Inappropriate: certifying a person's skills or using published AI/Expert ratings as independent human ground truth. Related occupations do not represent observed worker moves.
- Limitations: not all source workbooks are imported; task-level skill links and task-level human-dependency labels are not inferred. Rating dates are heterogeneous.

## BLS national OEWS, May 2025
- Publisher: U.S. Bureau of Labor Statistics. [Source](https://www.bls.gov/oes/tables.htm).
- Unit: detailed occupation at national area 99, cross-industry NAICS 000000, ownership 1235. Other summary groups are excluded, not counted as extra detailed occupations.
- Observed import: 830 detailed occupations; employment, annual mean and median wage, hourly median wage, and employment percent relative standard error. National ZIP only; state and metro files are not acquired.
- Missingness: source symbols including *, ** and # remain null plus their original marker. A top-coded wage is not converted into an exact wage. Through the current SOC mapping, 961 O*NET occupations have a detailed OEWS row; 956 have a usable annual median wage.
- Rights: [BLS copyright guidance](https://www.bls.gov/bls/linksite.htm); retain attribution and source exceptions.
- Appropriate use: national occupation context. Limitations: not individual earnings, not county estimates, and not directly comparable to NEM total employment including self-employed people. The 55 unmatched O*NET profiles remain explicit in the report; do not manufacture aggregate-code mappings.

## BLS employment projections, 2025–2035
- Publisher: U.S. Bureau of Labor Statistics. [Source](https://www.bls.gov/emp/data/occupational-data.htm).
- Unit: Table 1.2 Line item occupation, National Employment Matrix 2025 taxonomy. Summary rows are excluded.
- Observed import: 831 detailed occupations with base/projected employment, percent growth and annual average openings; 831 typed preparation records for entry education, related experience and on-the-job training.
- Units: employment and openings retain the source's thousands. They must be multiplied by 1,000 for an explicitly labeled count display. Growth is percent. Never sum summary and line-item rows.
- Parser detail: the source repeats the OOH-content heading; this one known duplicate is retained with an explicit suffix. Unrecognized duplicate headers fail.
- Rights: BLS guidance above. The workbook URL is mutable; the snapshot checksum fixes the bytes used here.
- Limitations: projections are not vacancies or guarantees. National preparation categories do not replace licensing checks or a person's education history. Source suppression tokens stay flagged.

## O*NET-SOC 2019 → SOC 2018 crosswalk
- Publisher: National Center for O*NET Development. [Source](https://www.onetcenter.org/crosswalks.html).
- Unit: official source/target code relationship, not an employment allocation.
- Observed import: 1,016 correspondences; every O*NET catalog code has a mapping, but not all target codes appear as detailed rows in this OEWS release.
- Rights: [Resource Center CC BY 4.0 content guidance](https://www.onetcenter.org/license.html); retain source credit and indicate normalization. The manifest preserves the preliminary review note; current review is documented here.
- Limitations: 76 target codes are shared by multiple source profiles. Allocation weights remain null. Do not duplicate aggregate employment when calculating totals.

## O*NET → National Employment Matrix crosswalk
- Publisher: U.S. Bureau of Labor Statistics. [Source](https://www.bls.gov/emp/data/occupational-data.htm).
- Observed vintage: source sheet says As of 08/27/2026.
- Unit: O*NET-SOC code to NEM code correspondence.
- Observed import: 996 correspondences, all with a projection line item in this snapshot. Twenty catalog profiles remain unmapped, listed in the report. Eighty-four NEM targets are shared by multiple source profiles.
- Rights: BLS guidance above. Preserve original workbook; all allocation weights remain null.
- Limitations: the source/target taxonomies have different resolutions. Do not treat NEM codes as automatic substitutes for OEWS SOC codes.

## Validation and allowed claims
The build passes archive CRC, SHA-256 identity, required-header, natural-key, foreign-key, scale-range and database integrity checks. These establish structural validity for this snapshot, not statistical validity of HumanBridge's proposed indices. Independent task annotation and transition review have not started.
