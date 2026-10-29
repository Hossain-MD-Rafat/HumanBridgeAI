# HumanBridge AI
**AI is changing work. HumanBridge helps people change with it.**

HumanBridge AI is a research and engineering project that helps workers understand task-level AI exposure, recognize human capabilities, explore transferable skills, and plan realistic career transitions across the United States.

**Status: Phase 0 foundation. No trained models, production API, dashboard, downloaded datasets, or validated scores yet.** Numbers in the original concept are illustrative, not research results.

## Start here
1. [Requirements and MVP](docs/requirements.md)
2. [System and technical architecture](docs/architecture.md)
3. [Dataset guide and download order](docs/datasets.md)
4. [Data acquisition checklist](docs/data-acquisition.md)
5. [Research methodology](docs/methodology.md)
6. [16-week roadmap](docs/roadmap.md)
7. [Phase 0 checklist and next session](docs/project-status.md)

The [original master brain](docs/master-brain.md) records the owner's vision. Implementation decisions and current status live in the documents above.

## First MVP
Search an occupation → inspect tasks → see experimental AI exposure and human-dependency measures → compare task workflow categories → explore up to five feasible transitions → inspect skill gaps and explanations.

Every result must retain its data vintage, evidence, limitations, and method version. AI exposure is not a probability of job loss. The proposed Human Value Index describes task dependencies; it does not measure a person's worth.

## Architecture
Versioned source files → validation and identifier crosswalks → relational occupation/task/skill store → baseline scoring and recommendations → API → worker-facing interface. See [architecture](docs/architecture.md) for the detailed diagram.

## Local setup
Python 3.11 or later; no paid service or GPU is required for the foundation checks.

```bash
git clone https://github.com/Hossain-MD-Rafat/HumanBridgeAI.git
cd HumanBridgeAI
python -m unittest discover -s tests -v
python scripts/check_foundation.py
```

Expected: schema tests and foundation checks pass. These commands do not download data or run a product demo. [Troubleshooting](docs/troubleshooting.md) covers common issues.

## Data and attribution
Begin with O*NET 31.0, May 2025 BLS OEWS national estimates, BLS 2025–2035 employment projections, and official occupation crosswalks. Regional extensions use ACS and Census boundaries. Exact sources, access conditions, and gaps are in the [dataset guide](docs/datasets.md) and [machine-readable catalog](config/datasets.json).

This repository does not bundle third-party datasets. O*NET data require versioned attribution under CC BY 4.0; see [third-party notices](THIRD_PARTY_NOTICES.md). Repository code has no open-source license assigned yet; public visibility alone does not grant reuse rights.

## Planned evaluation
Task annotation agreement, occupation-held-out classification, ranking relevance, constraint violations, sensitivity analysis, and subgroup/accessibility review. [Methodology](docs/methodology.md) defines the protocol. **No evaluation results exist yet.**

## Scope and limitations
Nationwide vulnerability mapping follows the worker MVP. Tacit and cultural knowledge preservation requires a separate, consent-based pilot. National wages are context, not an individual's earnings forecast. O*NET occupation profiles are not verified personal skill profiles. Course duration, licensing, and transition costs remain unknown unless independently sourced.

Screenshots, a hosted demo, and a research paper will be added only when they exist. For now cite the source datasets and their authors; there is no published HumanBridge AI research claim.

## Repository map
- `config/`: source inventory and experimental settings
- `schema/`: executable initial relational schema
- `src/humanbridge/`: future ingestion and analysis modules
- `scripts/`: foundation checks
- `tests/`: schema integrity checks
- `docs/`: requirements, data, methodology, decisions, and roadmap
- `data/`: local raw/interim/processed files, excluded from Git
