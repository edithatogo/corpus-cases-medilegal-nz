# Implementation Plan: Redundant Source Validation And Reconciliation Hardening

## Phase 1: Validation Source Inventory And Classification

- [x] Task: Catalog redundant public sources for medicolegal validation.
    - [x] NZLII subsections and search surfaces.
    - [x] Court of New Zealand case summaries and judgments.
    - [x] Council mirror pages for Medical, Dental, Pharmacy, and Teaching.
    - [x] Older ACCDCR and ACC appeal pages.
    - [x] Ministry of Justice tribunal index and summary pages.
- [x] Task: Define validation-source classes and evidence roles.
    - [x] Primary.
    - [x] Redundant witness.
    - [x] Summary index.
    - [x] Mirror.
    - [x] Candidate only.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Validation Source Inventory And Classification' (Protocol in workflow.md)

## Phase 2: Equivalence Rules And Duplicate Detection

- [x] Task: Add source-equivalence rules.
    - [x] Case identifiers.
    - [x] Titles.
    - [x] Decision dates.
    - [x] Canonical and alternate URLs.
- [x] Task: Add duplicate detection across canonical and validation sources.
- [x] Task: Add tests for positive and negative equivalence cases.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Equivalence Rules And Duplicate Detection' (Protocol in workflow.md)

## Phase 3: Redundant Ledger And Coverage Reporting

- [x] Task: Build a redundant-source ledger for active sources.
    - [x] Record which witness supports which source family.
    - [x] Record where no redundant witness exists.
    - [x] Record candidate-only families separately.
- [x] Task: Add coverage-gap reports derived from the redundant ledger.
- [x] Task: Add tests for coverage-gap summaries and no-witness blockers.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Redundant Ledger And Coverage Reporting' (Protocol in workflow.md)

## Phase 4: Release Claims And Evidence Integration

- [x] Task: Integrate the redundant-source ledger into release evidence.
    - [x] Public claims.
    - [x] README claims.
    - [x] Dataset-card claims.
    - [x] Release-notes claims.
- [x] Task: Add issue and project evidence for validation coverage.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Release Claims And Evidence Integration' (Protocol in workflow.md)
