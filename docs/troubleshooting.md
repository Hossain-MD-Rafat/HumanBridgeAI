# Troubleshooting
- Run commands from the repository root with Python 3.11 or later. On Windows, use py instead of python if needed.
- Foundation checks use only Python's standard library. Missing source data is expected in Phase 0.
- If a source download link redirects or fails, return to its official landing page. Record the actual resolved URL and checksum; do not silently substitute a different release.
- BLS and Census can block automated requests. Download manually using the official page where permitted; do not bypass access controls.
- The web research tool could read source pages but could not inspect ZIP/XLSX binary downloads. Links in the catalog are discoveries, not proof of a successfully downloaded file.
- Census API requests currently require a personal API key according to its developer documentation. Keep CENSUS_API_KEY outside Git; bulk/download portal alternatives are documented in the acquisition guide.
- A legacy ingestion tutorial may expect Skills.xlsx or Technology Skills.xlsx. O*NET 31.0 uses the release-specific table names in its dictionary; inspect headers before writing adapters.
- SQLite foreign key enforcement must be enabled for each connection. The schema and tests enable it explicitly.
- Suppressed wages, top-coded values, ACS special values and missing ratings are not numeric zero.
