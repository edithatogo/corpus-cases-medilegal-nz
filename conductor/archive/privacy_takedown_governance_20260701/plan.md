# Implementation Plan: Privacy, Takedown, And Redaction Governance

## Phase 1: Governance Baseline

- [x] Task: Audit current legal/provenance and privacy evidence fields.
- [x] Task: Define privacy risk taxonomy.
    - [x] Medical sensitivity.
    - [x] De-anonymisation likelihood.
    - [x] Named-party handling.
    - [x] Suppression or non-publication indicators.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Governance Baseline' (Protocol in workflow.md)

## Phase 2: Takedown And Correction Workflow

- [x] Task: Draft public takedown and correction policy.
- [x] Task: Define intake, triage, decision, and release-reissue workflow.
- [x] Task: Add private-safe public evidence fields for takedown state.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Takedown And Correction Workflow' (Protocol in workflow.md)

## Phase 3: Redaction And Exclusion Ledgers

- [x] Task: Add exclusion ledger schema.
- [x] Task: Add tombstone and correction evidence schema.
- [x] Task: Add tests for redacted, excluded, tombstoned, and corrected records.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Redaction And Exclusion Ledgers' (Protocol in workflow.md)

## Phase 4: Publication Gates

- [x] Task: Add publication-readiness checks for unresolved privacy blockers.
- [x] Task: Add release evidence fields for privacy state.
- [x] Task: Add Hugging Face, GitHub release, and Zenodo metadata warnings where needed.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Publication Gates' (Protocol in workflow.md)

## Phase 5: Simulated Takedown Proof

- [x] Task: Create a synthetic takedown/correction fixture.
- [x] Task: Run the workflow through new-version evidence generation.
- [x] Task: Verify public artifacts avoid sensitive requester details.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Simulated Takedown Proof' (Protocol in workflow.md)
