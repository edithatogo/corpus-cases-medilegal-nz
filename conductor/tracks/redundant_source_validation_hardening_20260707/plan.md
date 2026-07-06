# Implementation Plan: Redundant Source Validation And Reconciliation Hardening

## Phase 1: Validation Source Inventory And Classification

- [ ] Task: Catalog redundant public sources for medicolegal validation.
    - [ ] NZLII subsections and search surfaces.
    - [ ] Court of New Zealand case summaries and judgments.
    - [ ] Council mirror pages for Medical, Dental, Pharmacy, and Teaching.
    - [ ] Older ACCDCR and ACC appeal pages.
    - [ ] Ministry of Justice tribunal index and summary pages.
- [ ] Task: Define validation-source classes and evidence roles.
    - [ ] Primary.
    - [ ] Redundant witness.
    - [ ] Summary index.
    - [ ] Mirror.
    - [ ] Candidate only.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Validation Source Inventory And Classification' (Protocol in workflow.md)

## Phase 2: Equivalence Rules And Duplicate Detection

- [ ] Task: Add source-equivalence rules.
    - [ ] Case identifiers.
    - [ ] Titles.
    - [ ] Decision dates.
    - [ ] Canonical and alternate URLs.
- [ ] Task: Add duplicate detection across canonical and validation sources.
- [ ] Task: Add tests for positive and negative equivalence cases.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Equivalence Rules And Duplicate Detection' (Protocol in workflow.md)

## Phase 3: Redundant Ledger And Coverage Reporting

- [ ] Task: Build a redundant-source ledger for active sources.
    - [ ] Record which witness supports which source family.
    - [ ] Record where no redundant witness exists.
    - [ ] Record candidate-only families separately.
- [ ] Task: Add coverage-gap reports derived from the redundant ledger.
- [ ] Task: Add tests for coverage-gap summaries and no-witness blockers.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Redundant Ledger And Coverage Reporting' (Protocol in workflow.md)

## Phase 4: Release Claims And Evidence Integration

- [ ] Task: Integrate the redundant-source ledger into release evidence.
    - [ ] Public claims.
    - [ ] README claims.
    - [ ] Dataset-card claims.
    - [ ] Release-notes claims.
- [ ] Task: Add issue and project evidence for validation coverage.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Release Claims And Evidence Integration' (Protocol in workflow.md)
