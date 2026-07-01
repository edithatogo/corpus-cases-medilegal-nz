# Implementation Plan: Bleeding-Edge Archive Intelligence

## Phase 1: Intelligence Model

- [ ] Task: Define archive maturity scoring dimensions.
    - [ ] Release evidence completeness.
    - [ ] Source coverage completeness.
    - [ ] Collection and parsing progress.
    - [ ] Metadata package completeness.
    - [ ] Public-surface consistency.
    - [ ] Security and provenance posture.
    - [ ] Remote publication proof.
- [ ] Task: Define severity levels and score explanations.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Intelligence Model' (Protocol in workflow.md)

## Phase 2: Source Observability Ledger

- [ ] Task: Add source-level observability fields.
    - [ ] Crawlability.
    - [ ] Parser completeness.
    - [ ] Fetch timestamp.
    - [ ] Parse timestamp.
    - [ ] Record-count drift.
    - [ ] Rights/privacy review status.
- [ ] Task: Add tests for zero-record, stub-parser, and failed-fetch states.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Source Observability Ledger' (Protocol in workflow.md)

## Phase 3: Claims Generation

- [ ] Task: Generate public claims from ledgers.
    - [ ] README summary.
    - [ ] Hugging Face dataset card claims.
    - [ ] Release notes summary.
    - [ ] GitHub project issue summary.
- [ ] Task: Add drift checks that compare generated claims to committed prose.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Claims Generation' (Protocol in workflow.md)

## Phase 4: Anomaly Detection

- [ ] Task: Add record-count and source URL drift detection.
- [ ] Task: Add schema and metadata drift detection.
- [ ] Task: Add remote manifest verification drift detection.
- [ ] Task: Configure warn/fail thresholds.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Anomaly Detection' (Protocol in workflow.md)

## Phase 5: Workflow Telemetry

- [ ] Task: Emit structured workflow observability events.
- [ ] Task: Attach archive intelligence reports to workflow artifacts.
- [ ] Task: Feed intelligence summaries into project sync evidence.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Workflow Telemetry' (Protocol in workflow.md)

## Phase 6: Cross-Repo Compatibility

- [ ] Task: Align report schema with sibling archive repositories.
- [ ] Task: Document shared dashboard ingestion contract.
- [ ] Task: Add compatibility tests using sample ledgers.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Cross-Repo Compatibility' (Protocol in workflow.md)
