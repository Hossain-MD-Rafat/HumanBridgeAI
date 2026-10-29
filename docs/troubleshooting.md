# Troubleshooting
- Run commands from the repository root with Python 3.11 or later. On Windows, use py instead of python if needed.
- The catalog/link/schema check uses Python's standard library. Ingestion and source-format tests need openpyxl: install requirements.txt first. Missing raw data in a fresh clone is expected; run acquire_data.py --locked.
- If a source download link redirects or fails, return to its official landing page. Record the actual resolved URL and checksum; do not silently substitute a different release.
- BLS and Census can block automated requests. Download manually using the official page where permitted; do not bypass access controls.
- The web research tool could read source pages but could not inspect ZIP/XLSX binary downloads. Links in the catalog are discoveries, not proof of a successfully downloaded file.
- Census API requests currently require a personal API key according to its developer documentation. Keep CENSUS_API_KEY outside Git; bulk/download portal alternatives are documented in the acquisition guide.
- A legacy ingestion tutorial may expect Skills.xlsx or Technology Skills.xlsx. O*NET 31.0 uses the release-specific table names in its dictionary; inspect headers before writing adapters.
- SQLite foreign key enforcement must be enabled for each connection. The schema and tests enable it explicitly.
- Suppressed wages, top-coded values, ACS special values and missing ratings are not numeric zero.

## Phase 1 source details
- BLS Table 1.2 has two OOH-content headings. The adapter permits this known duplication and preserves both; other duplicate headings fail.
- O*NET Work Styles uses element prefix 1.D and includes AI/Expert provenance. The release-specific adapter checks element domains; do not infer them from older diagrams.
- Mutable publisher URLs may serve changed bytes. A locked download must fail rather than promote a new snapshot automatically.
- A failed import does not replace the existing database. Review the traceback and source headers, apply the smallest adapter/schema fix, then rebuild with --replace.
- Different OEWS and NEM employment totals can reflect different universes. Keep source units and self-employment coverage visible.

## Phase 2 review pilot
- Build the pinned core database before running prepare_task_pilot.py. A logical fingerprint mismatch means the source DB differs from the published report.
- Run identities change when generator code, rubric, cohort or selected inputs change. Existing immutable artifacts must not be edited; copy blind queues to a separate response directory.
- A completion validation failure on fresh blind queues is expected: their human labels are deliberately empty.
- Lexical insufficient_evidence is not a low exposure result. Do not replace unknowns with zeros.
- If grouped sampling cannot create a holdout, review the sampling design and create a new version; do not split duplicate-linked occupations to force the requested count.

## Offline workbench and agreement
- Open the generated HTML directly; it needs no server. Draft edits are tab memory, so download a draft backup before closing. JSONL response export intentionally leaves unfinished tasks blank.
- Draft import checks the run and slot. Source identity and labels must match the frozen queue; changing task text is rejected.
- A single reviewer slot must use one pseudonym consistently, and slots A/B must use different identities. This is a protocol check, not proof of independent human participation.
- Agreement remains blocked without explicit research attestation and complete pairs for the selected split. Constant-marginal kappa is undefined and reported as null, never silently changed to one.
- Node and Playwright are optional browser-test dependencies only. Install them with npm ci; use the pinned browser install from the review-workbench guide. If the runtime prohibits Chromium sockets, run the browser smoke check in the repository GitHub Actions environment. Do not interpret a failed browser launch as an application pass.
