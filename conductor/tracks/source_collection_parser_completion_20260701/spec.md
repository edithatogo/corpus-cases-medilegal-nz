# Specification: Source Collection And Parser Completion

## Overview

Move the corpus from configured source scaffolding to evidence-backed collection output with real harvested records, parser completion status, and source-by-source quality gates.

The current archive publication tooling is strong, but the local evidence still reports zero processed records and multiple source adapters are stubs or delegate real parsing elsewhere. This track closes that gap.

## Current State

- `dataset_quality.json` reports `record_count: 0`.
- `data/processed/jsonl/records.jsonl` is absent.
- Source coverage reports one active source, four configured sources, and eight stub/planned sources.
- HDC, HPDT, MoJ Tribunals, ERA, and Teachers adapters are wired but do not yet produce local parsed record output.
- Some parsing is intended to be delegated to `nlp-policy-nz`, but the repo does not yet have a hard contract proving that delegation produces records.

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
- Each core configured source has an explicit parser status and evidence.
- The archive release evidence records real collection state instead of ambiguous zero-record output.
- CI catches regressions where a parser-complete source unexpectedly drops to zero records.
- The `nlp-policy-nz` dependency boundary is documented and tested.

## Out Of Scope

- Completing OCR for scanned PDFs.
- Legal conclusions about redistribution rights.
- Production publication of records to Hugging Face or Zenodo.
- Hosted search UI or end-user analytics.
