# Specification: Source Collection And Parser Completion

## Overview

Move the corpus from configured source scaffolding to evidence-backed collection output with real harvested records, parser completion status, and source-by-source quality gates.

The current archive publication tooling is strong, and the local evidence now reports 13 processed records with no remaining planned placeholders. This track closes the last gap.

## Current State

- `dataset_quality.json` reports `record_count: 13`.
- `data/processed/jsonl/records.jsonl` is present.
- Source coverage reports 13 validated sources and no planned sources.
- HDC, HPDT, MoJ Tribunals, ERA, Teachers, Privacy Commissioner, Human Rights Commission/Tribunal, Ombudsman Reports, IPCA, Law Commission, Royal Commissions & Waitangi Tribunal, Coronial Decisions, and Ministry of Justice Court Cases now produce validated local parsed record output.

## Requirements

- Define a source adapter completion ladder:
  - configured
  - reachable
  - fetched
  - parsed
  - normalized
  - validated
  - published
- Implement or integrate parsing for HDC, HPDT, MoJ Tribunals, ERA, and Teachers.
- Define the contract between this repo and `nlp-policy-nz` for shared parser logic.
- Add fixture-based parser tests for each source.
- Add smoke-fetch tests that are rate-limited and safe for CI.
- Add deterministic export to JSONL, JSON, Markdown, text, and Parquet where applicable.
- Add minimum-record and zero-record gates that fail only when a source claims parser-complete status.
- Update source coverage evidence to distinguish "reachable but parser incomplete" from "no collection attempted".
- Add tombstone and changed-record handling for source removals or corrected decisions.

## Non-Functional Requirements

- Collection must be polite, resumable, and cache-aware.
- Parser failures must be source-scoped and diagnosable.
- Source output must preserve raw-source provenance.
- Tests must avoid brittle dependence on live site layout where fixtures are available.
- The implementation must align with sibling archive/corpus patterns.

## Acceptance Criteria

- At least one source produces non-zero validated local records.
- Each source has an explicit parser status and evidence.
- The archive release evidence records real collection state instead of ambiguous zero-record output.
- CI catches regressions where a parser-complete source unexpectedly drops to zero records.
- The `nlp-policy-nz` dependency boundary is documented and tested.

## Out Of Scope

- Completing OCR for scanned PDFs.
- Legal conclusions about redistribution rights.
- Production publication of records to Hugging Face or Zenodo.
- Hosted search UI or end-user analytics.
