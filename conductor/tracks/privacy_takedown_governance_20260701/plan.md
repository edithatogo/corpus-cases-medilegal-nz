# Implementation Plan: Privacy, Takedown, And Redaction Governance

## Phase 1: Governance Baseline

- [ ] Task: Audit current legal/provenance and privacy evidence fields.
- [ ] Task: Define privacy risk taxonomy.
    - [ ] Medical sensitivity.
    - [ ] De-anonymisation likelihood.
    - [ ] Named-party handling.
    - [ ] Suppression or non-publication indicators.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Governance Baseline' (Protocol in workflow.md)

## Phase 2: Takedown And Correction Workflow

- [ ] Task: Draft public takedown and correction policy.
- [ ] Task: Define intake, triage, decision, and release-reissue workflow.
- [ ] Task: Add private-safe public evidence fields for takedown state.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Takedown And Correction Workflow' (Protocol in workflow.md)

## Phase 3: Redaction And Exclusion Ledgers

- [ ] Task: Add exclusion ledger schema.
- [ ] Task: Add tombstone and correction evidence schema.
- [ ] Task: Add tests for redacted, excluded, tombstoned, and corrected records.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Redaction And Exclusion Ledgers' (Protocol in workflow.md)

## Phase 4: Publication Gates

- [ ] Task: Add publication-readiness checks for unresolved privacy blockers.
- [ ] Task: Add release evidence fields for privacy state.
- [ ] Task: Add Hugging Face, GitHub release, and Zenodo metadata warnings where needed.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Publication Gates' (Protocol in workflow.md)

## Phase 5: Simulated Takedown Proof

- [ ] Task: Create a synthetic takedown/correction fixture.
- [ ] Task: Run the workflow through new-version evidence generation.
- [ ] Task: Verify public artifacts avoid sensitive requester details.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Simulated Takedown Proof' (Protocol in workflow.md)
