# Specification: Bleeding-Edge Archive Intelligence

## Overview

Add a forward-looking archive intelligence layer that turns publication, collection, source coverage, quality, privacy, and public-surface evidence into actionable observability and planning signals.

This track captures additional improvements beyond the immediate GitHub/RIOPA synchronization and governance hardening work.

## Requirements

- Generate a machine-readable archive maturity score from release evidence, source coverage, quality, metadata, public surface, security, and remote proof ledgers.
- Add source-level collection observability for each configured or planned source:
  - crawlability
  - parser completeness
  - rights review state
  - expected document classes
  - last successful fetch
  - last successful parsed record
  - record-count drift
  - known exclusions
- Add collection/scraping progress dashboards or summary artifacts that distinguish:
  - configured
  - reachable
  - fetched
  - parsed
  - validated
  - published
  - DOI-snapshotted
- Add anomaly detection for record-count drops, source URL drift, schema drift, failed remote manifest verification, and metadata inconsistencies.
- Add public claims generation from ledgers so README, dataset cards, release notes, and GitHub project summaries do not drift from evidence.
- Add privacy and rights risk scoring suitable for public medical-legal corpora.
- Add optional OpenTelemetry-style structured events for archive workflows.
- Add cross-repo dashboard compatibility with `corpus-law-nz`, `corpus-nz-hansard`, `fyi-archive`, and future corpus repositories.

## Non-Functional Requirements

- Evidence and scoring must be reproducible from committed artifacts and workflow outputs.
- Risk scores must be explainable and source-linked.
- Public claims must be generated from ledgers, not hand-maintained prose.
- The system must avoid overclaiming collection completeness while parsers remain stubbed or delegated.

## Acceptance Criteria

- A generated archive maturity report is produced locally and in CI.
- Source-level collection status clearly reports zero-record and parser-stub states.
- README/dataset-card/release summary claims can be generated from evidence ledgers.
- Anomaly checks fail or warn according to configured severity.
- The output can be consumed by GitHub project sync, release evidence, and sibling archive dashboards.

## Out Of Scope

- Building a hosted dashboard service.
- Completing all parsers.
- Changing source redistribution policy without legal/provenance review.
- Publishing experimental analytics as canonical dataset artifacts before release-ladder promotion.
