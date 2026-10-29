# ADR 001: local relational foundation
Status: accepted for Phase 0, 2026-10-29.

## Context
A single owner must reproduce the first pipeline on a laptop. The project later needs an API, skill graph and geographic analysis.

## Options
SQLite local store; PostgreSQL from day one; Neo4j as primary store.

## Decision
Use a versioned relational schema and SQLite for local MVP work. Plan PostgreSQL migration for deployment/concurrency and an optional Neo4j export after the skill baseline is evaluated. Python pipelines, a planned FastAPI service and Streamlit research demo keep the first implementation small.

## Reason
No service setup or GPU is required. Foreign keys and unique constraints make early data errors visible. One canonical representation avoids inconsistent graph and relational copies.

## Tradeoffs
SQLite SQL is not a deployable PostgreSQL migration. Concurrent writes and multiuser hosting require a later migration. The initial schema is a starting contract, not every future platform table.
