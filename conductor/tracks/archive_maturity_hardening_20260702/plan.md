# Implementation Plan: Archive Maturity Hardening

## Phase 1: Publication Evidence Overlay

- [x] Task: Build archive maturity from the monthly artifact directory.
    - [x] Merge Hugging Face publication evidence.
    - [x] Merge Zenodo draft evidence.
    - [x] Merge GitHub release evidence.
    - [x] Fall back to sibling metadata manifests when needed.
    - Evidence: `src/corpus_cases_medilegal_nz/archive_intelligence.py` now merges publication overlays from the artifact directory and still supports sibling metadata-manifest fallback.
- [x] Task: Add unit tests for partial and fully proven maturity reports.
    - Evidence: `tests/test_archive_intelligence.py` covers metadata fallback, artifact-dir maturity scoring, and strict-mode rejection of partial reports.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Publication Evidence Overlay' (Protocol in workflow.md)
    - Evidence: `phase1_publication_overlay_evidence.md` records the local verification commands and the synthetic artifact-dir `100`-score report.

## Phase 2: Workflow Attachment And Strict Gate

- [x] Task: Attach the maturity report in the monthly publication workflow.
    - [x] Upload it as a workflow artifact.
    - [x] Upload it as a GitHub release asset.
    - [x] Generate it after live publication evidence exists.
    - Evidence: `.github/workflows/monthly_dynamic_archive_publication.yml` now builds the GitHub release overlay, generates the maturity report after HF/Zenodo evidence exists, uploads `generated/archive-intelligence/**`, and attaches `archive_maturity.json` as a release asset.
- [x] Task: Add strict mode so canonical publication fails below `100`.
    - Evidence: `scripts/build_archive_intelligence.py`, `src/corpus_cases_medilegal_nz/cli.py`, and `archive_intelligence.py` now share strict validation helpers that fail closed when the score is below `100` or the severity is not `leading`.
- [x] Task: Add workflow and CLI tests for strict and non-strict modes.
    - Evidence: `tests/test_archive_intelligence.py` and `tests/test_monthly_publication_workflow.py` cover strict-mode rejection, artifact-dir scoring, and the publication gating workflow conditions.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Workflow Attachment And Strict Gate' (Protocol in workflow.md)
    - Evidence: `phase2_workflow_gate_evidence.md` records the workflow assertions and local validation results.

## Phase 3: Source Observability And Anomaly Detection

- [x] Task: Add source-level observability and drift warnings.
    - Evidence: `src/corpus_cases_medilegal_nz/archive_intelligence.py` now emits source crawlability, parser completion, fetch/parse timestamps, drift, rights, and document-class observability for all registry sources.
- [x] Task: Add anomaly detection for counts, schema, and remote manifests.
    - Evidence: `build_archive_anomaly_report` flags record-count drops, source URL drift, schema drift, failed remote manifest verification, and metadata inconsistencies.
- [x] Task: Add tests for warning and failure thresholds.
    - Evidence: `tests/test_archive_intelligence.py` covers drift warnings, anomaly blockers, privacy scores, claims generation, federation compatibility, and bundle artifact writes.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Source Observability And Anomaly Detection' (Protocol in workflow.md)
    - Evidence: `phase3_observability_anomaly_evidence.md` records the focused validation commands and `16 passed` result.

## Phase 4: Claims, Privacy, And Federation

- [x] Task: Generate public claims from ledgers for docs and release notes.
    - Evidence: `build_public_claims` emits README, dataset-card, release-notes, and GitHub-project-summary markdown derived from release evidence.
- [x] Task: Add privacy and rights scoring to archive intelligence.
    - Evidence: `build_privacy_rights_scoring` scores active sources from observability ledgers and feeds the claims bundle.
- [x] Task: Add cross-repo compatibility checks for sibling archive ledgers.
    - Evidence: `build_federation_compatibility_report` validates the shared archive-family contract and records target sibling repositories.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Claims, Privacy, And Federation' (Protocol in workflow.md)
    - Evidence: `phase4_claims_privacy_federation_evidence.md` records the focused validation commands and `16 passed` result.
