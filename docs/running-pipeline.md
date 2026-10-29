# Run the Phase 1 core data pipeline
Python 3.11+ is required. Commands work from the repository root; Windows users may use py in place of python.

```bash
python -m pip install -r requirements.txt
python scripts/acquire_data.py --locked
python scripts/build_data.py
python scripts/validate_data.py
python scripts/explore_occupation.py 43-3031.00
```

The first command installs pinned openpyxl. Acquisition downloads five public assets, approximately 49 MB combined, or verifies the local cache. It requires their committed checksums; changed publisher bytes fail rather than silently updating the research snapshot. Raw files and the generated SQLite database stay outside Git. The committed manifests and snapshot lock allow reconstruction. There is no API key or GPU requirement.

The build streams inspected workbooks into data/processed/core.sqlite3, validates source ranges and relationships, and writes docs/reports/core-data.json. The integrity check compares actual rows, source hashes and the logical data fingerprint with that report. Exploration prints a JSON occupation profile with sample tasks, skill importance ratings and mapped labor context. This is a command-line data demonstration, not the worker MVP.

For an existing derived database, explicitly rebuild it with:

```bash
python scripts/build_data.py --replace
```

The old database remains available until a complete replacement passes checks. Temporary build directories are removed on failure. Reproducibility is defined by logical records, not SQLite file-byte identity. Build reports use fixed manifest provenance; they do not invent new acquisition timestamps.

## Modules and their roles
| File | Purpose / inputs / outputs | Connection and failure cases |
|---|---|---|
| src/humanbridge/acquisition.py | Catalog + public download/manual bytes → validated archive and immutable manifest | First pipeline stage; rejects HTML, corruption, unsafe archive members and lock mismatches |
| src/humanbridge/excel.py | Source workbook/member → streamed dictionaries | Used by importers; fails on unexpected headers and unapproved duplicate column names |
| src/humanbridge/ingest_common.py | Raw codes/values → typed values and quality metadata | Strict identifiers; suppression remains null plus a source flag |
| src/humanbridge/ingest_onet.py | Pinned O*NET archive → occupation/task/skill and contextual records | Rejects duplicate keys, foreign-key failures, unexpected domains and out-of-scale values |
| src/humanbridge/ingest_bls.py | Wages/projection/crosswalk workbooks → labor facts and official edges | Keeps universes and units separate; never infers weights from a mapping |
| src/humanbridge/pipeline.py | Pinned snapshot + DDL → atomic SQLite database and coverage report | Fails on changed bytes, empty source tables, schema drift or broken integrity |
| scripts/explore_occupation.py | Search text or code → up to ten matching occupation profiles | Read-only DB access; no match returns an empty matches list |
| scripts/validate_data.py | Raw bytes + DB + report → integrity/coverage summary | Requires the default local DB; missing data or differing fingerprints fail |

## If a download fails
Use the official source landing page and download manually where permitted. Register the file without changing the lock:

```bash
python scripts/acquire_data.py --locked --dataset onet_31_0 --local-file /path/to/db_31_0_excel.zip
```

If the publisher changed a mutable workbook, the checksum will fail. Keep the old snapshot, review the new release, and create an explicit new lock/manifest. Do not edit checksums merely to make the build pass. Checksums establish identity, not evidence that a dataset is unbiased or a model is valid.

## Tests and limitations
```bash
python -m unittest discover -s tests -v
python scripts/check_foundation.py
```

CI uses synthetic local fixtures and does not download 49 MB or rebuild third-party data on every commit. Real-data checks were run separately on the pinned snapshot. [Coverage report](reports/core-data.json), [quality report](reports/data-quality.json) and [source cards](data-cards/core-sources.md) describe the actual local build.

Imports deliberately exclude Software Skills, education frequency tables, emerging tasks, task/activity link tables and other workbooks not yet needed for this core slice. BLS Table 1.2 supplies typed entry-preparation facts. No task exposure labels, HVI, recommendation ranking, county estimates or scores are generated.
