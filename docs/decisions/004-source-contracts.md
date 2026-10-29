# ADR 004: source contracts and quality provenance
Status: accepted for Phase 1, 2026-10-29.

## Context
Actual Excel downloads contain preambles, release-specific headers, category ratings, a repeated projection link heading, varying source populations, and suppressed measurements. The initial schema did not preserve every rating quality field or typed preparation fact.

## Options
Use a generic spreadsheet merge; discard fields that do not fit the first schema; add release-specific adapters and a schema migration.

## Decision
Use pinned openpyxl 3.1.5 streaming readers, required-header contracts and an explicitly allowed duplicate OOH heading. Add schema/002_source_detail.sql for source metadata, BLS source occupations and preparation, O*NET aliases/job zones/relatedness. Store original rating N, SE, CI, suppression, relevance, date and Domain Source metadata.

Download to temporary files, validate containers and publish checksum-addressed assets. Build SQLite in a temporary directory and replace an existing derived DB only with --replace after checks pass. Commit manifests/locks and aggregate reports; raw assets and SQLite files are reconstructed outside Git.

## Reason
All five core sources are available directly from their official publishers. Strict release contracts make errors visible. Full O*NET codes and official mapping edges avoid inferred title joins and double-counted employment. The published AI/Expert work-style source must stay visible in later validation design.

## Tradeoffs
The build is an intentional source slice, not import of every O*NET workbook. New releases require adapter and lock review. Users need network access or permitted manual files to reconstruct raw inputs. Published report coverage does not resolve every aggregated BLS occupation gap.
