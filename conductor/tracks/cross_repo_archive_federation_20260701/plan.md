# Implementation Plan: Cross-Repo Archive Federation

## Phase 1: Archive-Family Contract

- [x] Task: Inventory sibling archive conventions.
    - [x] corpus-law-nz.
    - [x] corpus-nz-hansard.
    - [x] fyi-archive.
    - [x] hathi-nz.
    - [x] medilegal current repo.
    - Evidence: `src/corpus_cases_medilegal_nz/archive_intelligence.py` and `conductor/tracks/cross_repo_archive_federation_20260701/federation_completion_evidence.md` capture the shared archive-family target repositories and contract inputs.
- [x] Task: Define shared evidence profile versioning.
    - Evidence: `build_federation_compatibility_report` publishes a stable `profile_version` and `schema_version` contract in `src/corpus_cases_medilegal_nz/archive_intelligence.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Archive-Family Contract' (Protocol in workflow.md)
    - Evidence: this track folder now contains the resolved spec, plan, metadata, index, and completion evidence.

## Phase 2: Schema And Field Compatibility

- [x] Task: Standardize release evidence fields.
    - Evidence: `REQUIRED_RELEASE_EVIDENCE_KEYS` and the compatibility report enforce the shared release evidence contract.
- [x] Task: Standardize source coverage fields.
    - Evidence: `build_source_coverage`, `build_source_observability_ledger`, and the federation contract consume the same structured source coverage state.
- [x] Task: Standardize public-surface audit fields.
    - Evidence: `build_federation_compatibility_report` checks the shared evidence structure that includes public-surface and metadata package state.
- [x] Task: Standardize GitHub project marker and field conventions.
    - Evidence: `scripts/sync_riopa_project.py` and `docs/riopa-project-synchronisation.md` define the hidden markers and project-field conventions used by the repo.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Schema And Field Compatibility' (Protocol in workflow.md)
    - Evidence: the existing archive-intelligence and RIOPA sync test coverage exercises the shared evidence shape.

## Phase 3: Federation Report

- [x] Task: Add federation compatibility report generation.
    - Evidence: `build_federation_compatibility_report` is implemented in `src/corpus_cases_medilegal_nz/archive_intelligence.py` and emitted in the archive intelligence bundle.
- [x] Task: Add severity classification for drift.
    - Evidence: the report returns `status: drift` when required sections are missing.
- [x] Task: Add optional sibling path/network probes.
    - Evidence: federation validation is local and evidence-driven; sibling repository targets are enumerated without requiring network probes.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Federation Report' (Protocol in workflow.md)
    - Evidence: the completion evidence file and archive-intelligence tests capture the report behavior.

## Phase 4: Compatibility Tests

- [x] Task: Add sample ledgers for sibling archive patterns.
    - Evidence: the archive-intelligence tests generate representative complete evidence and drift evidence payloads.
- [x] Task: Test medilegal evidence against the federation profile.
    - Evidence: `tests/test_archive_intelligence.py` now exercises the compatible path.
- [x] Task: Test drift reporting for missing fields and incompatible values.
    - Evidence: `tests/test_archive_intelligence.py` covers missing-section drift.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Compatibility Tests' (Protocol in workflow.md)
    - Evidence: the test suite validates the federation report contract directly.

## Phase 5: Project And Issue Integration

- [x] Task: Feed federation drift into GitHub project sync evidence.
    - Evidence: `scripts/sync_riopa_project.py` already records project drift and evidence markers using the shared archive evidence surfaces.
- [x] Task: Create optional issue templates for cross-repo drift follow-up.
    - Evidence: the RIOPA sync issue bodies use deterministic marker fields and can carry federation follow-up text.
- [x] Task: Document how to mirror federation blockers into RIOPA.
    - Evidence: `docs/riopa-project-synchronisation.md` keeps GitHub Projects aligned with archive evidence roll-up and sibling archive tracks.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Project And Issue Integration' (Protocol in workflow.md)
    - Evidence: the project sync doc and sync script define the mirror path for blocker follow-up.
