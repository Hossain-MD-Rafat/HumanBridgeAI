# Data acquisition runbook
## What to download first
Download from official links in [the dataset guide](datasets.md); do not rename or edit the original bytes. Suggested destinations:

| Order | Asset | Destination |
|---|---|---|
| 1 | O*NET 31.0 complete Excel ZIP | data/raw/onet/31.0/db_31_0_excel.zip |
| 2 | O*NET 31.0 dictionary and license references | Record URLs in manifest; save a dated documentation copy if permitted |
| 3 | May 2025 OEWS national ZIP | data/raw/bls_oews/2025-05/oesm25nat.zip |
| 4 | BLS 2025–2035 occupation workbook | data/raw/bls_projections/2025-2035/occupation.xlsx |
| 5 | O*NET-to-SOC crosswalk | data/raw/crosswalks/2026-10-29/2019_to_SOC_Crosswalk.xlsx |
| 6 | O*NET-to-NEM crosswalk | data/raw/crosswalks/2026-10-29/nem-onet-to-soc-crosswalk.xlsx |

The crosswalk folder date is the acquisition snapshot label, not a claimed publisher release. BLS workbook links can change contents without changing filenames. Confirm their internal base and target years.

## Acquisition procedure
1. Open the official landing page and confirm the listed vintage and terms.
2. Download the asset to its destination; create parent folders as needed.
3. Confirm the payload is the expected ZIP/XLSX, not an HTML block or error page.
4. Calculate a SHA-256; record size and UTC retrieval time.
5. Create an immutable manifest under data/manifest/ with the required fields in data/README.md. Keep credentials out of URLs and metadata.
6. Extract ZIPs to a separate directory. Validate member paths and file sizes before any scripted extraction.
7. Inspect actual workbook sheet names, headers, scale definitions, unique keys, missing-value markers and row counts.
8. Update catalog acquisition_status only after validation, with a manifest reference.
9. Create a dataset card covering source, release, unit of observation, collection, license, missingness, allowed uses and limitations.

Portable checksum command (replace the path with the actual asset):
```bash
python -c "import hashlib,pathlib; p=pathlib.Path('data/raw/onet/31.0/db_31_0_excel.zip'); print(hashlib.file_digest(p.open('rb'),'sha256').hexdigest())"
```

This reads a local file only. It does not download or validate its contents. A file-not-found error means the path or acquisition is incomplete.

## Initial validation gates
- O*NET occupation IDs retained as full strings; all related tasks/skills reference a known release/code.
- Task ID scope and rating keys verified against the release dictionary.
- Skill importance and level scales kept separate; categories and suppression flags preserved.
- BLS aggregate/group rows separated from detailed occupations; source units preserved.
- Wage symbols, ACS annotations and missing values mapped with documented rules.
- Crosswalk reports include matched/unmatched codes, ambiguous mappings and any aggregates.
- Do not duplicate employment across one-to-many crosswalk edges.
- Report observed row counts after acquisition, never from an assumption or old tutorial.

## ACS example for the regional phase
Read the [Census developer guide](https://www.census.gov/data/developers/data-sets/acs-5year.html) and request a key. Store it as CENSUS_API_KEY outside the repository.

Request county estimates and MOEs for income using this URL template, substituting the key locally:
```text
https://api.census.gov/data/2024/acs/acs5?get=NAME,B19013_001E,B19013_001M&for=county:*&in=state:*&key=YOUR_KEY
```

This template has not been executed in this session. Query other tables in documented batches and retain annotations/special-value flags. Filter to the study geography and retain FIPS leading zeros. Bulk downloads through official Census tools are an alternative; record the extraction selection and vintage.

## Download status and limitations
No dataset payloads have been downloaded in Phase 0. Research tooling could inspect official source pages, but ZIP/XLSX binaries were not readable through that tool. Resolve failures via official landing pages or permitted manual downloads. Do not bypass blocks or silently substitute a newer vintage.
