# ADR 002: preserve occupation and geography identifiers
Status: accepted for Phase 0, 2026-10-29.

## Context
O*NET, BLS and ACS classify occupations at different levels. Source code similarity does not establish a valid join.

## Options
Truncate O*NET extensions; join by title; maintain versioned official crosswalk relationships.

## Decision
Use full O*NET-SOC strings as occupation identifiers within a source release. Preserve SOC 2018 and National Employment Matrix codes as separate strings with taxonomy metadata. Store official crosswalk edges, relation type and optional validated weights. No automatic title join or unconditional decimal truncation.

Keep county FIPS as five-character strings and state FIPS as two-character strings. Record boundary year. Restrict the first nationwide county study to 50 states plus DC and list territories excluded. Reconcile county-equivalent changes before joins.

## Reason
One SOC aggregate can map to several O*NET occupations; copying its employment to each would double-count workers. County and metro geographies are not interchangeable.

## Tradeoffs
Crosswalk tables and coverage review add work. If employment-allocation weights are unavailable, retain the broader SOC level or publish a bounded/proxy analysis rather than inventing weights.

## Sources
[O*NET crosswalks](https://www.onetcenter.org/crosswalks.html) and [BLS directories/crosswalks](https://www.bls.gov/emp/data/occupational-data.htm).
