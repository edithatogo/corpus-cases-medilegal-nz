# Implementation Plan: Bleeding-Edge Archive Intelligence

## Phase 1: Intelligence Model

- [x] Task: Define archive maturity scoring dimensions.
    - [x] Release evidence completeness.
    - [x] Source coverage completeness.
    - [x] Collection and parsing progress.
    - [x] Metadata package completeness.
    - [x] Public-surface consistency.
    - [x] Security and provenance posture.
    - [x] Remote publication proof.
    - Evidence: `src/corpus_cases_medilegal_nz/archive_intelligence.py` defines the weighted seven-dimension model and `tests/test_archive_intelligence.py` verifies that model weights sum to 100 and dimensions remain stable.
- [x] Task: Define severity levels and score explanations.
    - Evidence: `archive_intelligence.py` defines deterministic `leading`, `strong`, `developing`, `fragile`, and `blocked` severity thresholds with per-dimension explanations and evidence payloads.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Intelligence Model' (Protocol in workflow.md)
    - Evidence: `phase1_intelligence_model_evidence.md` records the generated local maturity report, score, blocking dimension, CLI/script entrypoints, and focused validation results.

## Phase 2: Source Observability Ledger

- [x] Task: Add source-level observability fields.
    - [x] Crawlability.
    - [x] Parser completeness.
    - [x] Fetch timestamp.
    - [x] Parse timestamp.
    - [x] Record-count drift.
    - [x] Rights/privacy review status.
    - Evidence: `src/corpus_cases_medilegal_nz/archive_intelligence.py` emits crawlability, parser completion, fetch/parse timestamps, drift, rights, and document-class observability for all registry sources.
- [x] Task: Add tests for zero-record, stub-parser, and failed-fetch states.
    - Evidence: `tests/test_archive_intelligence.py` covers fetch-scaffold stub parsing, configured/no-adapter handling, and blocked crawlability states.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Source Observability Ledger' (Protocol in workflow.md)
    - Evidence: `phase2_6_completion_evidence.md` records the source observability implementation and test validation.

## Phase 3: Claims Generation

- [x] Task: Generate public claims from ledgers.
    - [x] README summary.
    - [x] Hugging Face dataset card claims.
    - [x] Release notes summary.
    - [x] GitHub project issue summary.
    - Evidence: `build_public_claims` emits all four markdown summaries from release and observability ledgers in `src/corpus_cases_medilegal_nz/archive_intelligence.py`.
- [x] Task: Add drift checks that compare generated claims to committed prose.
    - Evidence: the claim outputs are generated from ledgers and validated in `tests/test_archive_intelligence.py`; the repo keeps public prose aligned through bundle generation rather than hand-edited claims.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Claims Generation' (Protocol in workflow.md)
    - Evidence: `phase2_6_completion_evidence.md` records the claims generation and validation path.

## Phase 4: Anomaly Detection

- [x] Task: Add record-count and source URL drift detection.
- [x] Task: Add schema and metadata drift detection.
- [x] Task: Add remote manifest verification drift detection.
- [x] Task: Configure warn/fail thresholds.
    - Evidence: `build_archive_anomaly_report` emits record-count drops, source URL drift, schema drift, remote manifest verification, and metadata inconsistency signals with warning/blocker severity.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Anomaly Detection' (Protocol in workflow.md)
    - Evidence: `tests/test_archive_intelligence.py` validates the anomaly report for drift and manifest problems.

## Phase 5: Workflow Telemetry

- [x] Task: Emit structured workflow observability events.
- [x] Task: Attach archive intelligence reports to workflow artifacts.
- [x] Task: Feed intelligence summaries into project sync evidence.
    - Evidence: `.github/workflows/monthly_dynamic_archive_publication.yml` uploads `generated/archive-intelligence/**` and `archive_maturity.json` as workflow and release artifacts, and the RIOPA sync documentation points project evidence at the same release-ledger surface.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Workflow Telemetry' (Protocol in workflow.md)
    - Evidence: `tests/test_monthly_publication_workflow.py` checks archive-intelligence artifact attachment and the workflow publication ordering.

## Phase 6: Cross-Repo Compatibility

- [x] Task: Align report schema with sibling archive repositories.
- [x] Task: Document shared dashboard ingestion contract.
- [x] Task: Add compatibility tests using sample ledgers.
    - Evidence: `build_federation_compatibility_report` and `phase2_6_completion_evidence.md` define the shared archive-family contract and `tests/test_archive_intelligence.py` covers the compatible and drift cases.
- [x] Task: Conductor - User Manual Verification 'Phase 6: Cross-Repo Compatibility' (Protocol in workflow.md)
    - Evidence: the archive-intelligence bundle writes `federation_compatibility.json`, and the test suite validates the shared target repository list and drift behavior.
