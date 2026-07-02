# Implementation Plan: GitHub RIOPA Project Synchronisation

## Phase 1: Project Schema Audit

- [x] Task: Capture live RIOPA and repo project field schemas.
    - [x] Record project IDs, field IDs, option IDs, and current item IDs.
    - [x] Compare medilegal project fields against sibling roadmap boards.
    - [x] Identify fields that can be created through available GitHub APIs.
    - Evidence: `phase1_project_schema_audit.md` records live RIOPA project #4 and repo roadmap project #7 IDs, field IDs/options, issue #1 item IDs, and sibling board comparisons.
- [x] Task: Define the medilegal project field contract.
    - [x] Specify field names, allowed values, and mapping to Conductor track status.
    - [x] Document fallback behavior for unsupported field mutations.
    - Evidence: `phase1_project_schema_audit.md` defines the medilegal project field contract and fallback behavior for missing project fields and missing dedicated RIOPA mirror-source options.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Project Schema Audit' (Protocol in workflow.md)
    - Evidence: live `gh project view`, `gh project field-list`, `gh project item-list`, and `gh issue view` readbacks completed; no project or issue writes were made in Phase 1.

## Phase 2: RIOPA Mirror Alignment

- [x] Task: Add or document the `corpus-cases-medilegal-nz` RIOPA mirror source option.
    - [x] Prefer a dedicated mirror-source option.
    - [x] If unavailable through the API, document the manual project-field change.
    - Evidence: `phase2_riopa_mirror_alignment.md` records that RIOPA has `Mirror source` but no dedicated medilegal option; the installed `gh` supports creating new fields, not adding an option to an existing single-select field, so Phase 2 uses `other` as the API-safe fallback and documents the dedicated option as a manual/project-admin follow-up.
- [x] Task: Set issue #1 RIOPA item fields.
    - [x] Set status, repository, mirror source, and conductor-track metadata.
    - [x] Verify item appears in filtered RIOPA views.
    - Evidence: issue #1 RIOPA item `PVTI_lAHOAOYc4M4BcJFFzgxZYg0` now reads back with `mirror source: other`, `status: Done`, repository URL `https://github.com/edithatogo/corpus-cases-medilegal-nz`, and the hidden `monthly_dynamic_archive_publication_20260701` marker.
- [x] Task: Conductor - User Manual Verification 'Phase 2: RIOPA Mirror Alignment' (Protocol in workflow.md)
    - Evidence: live `gh project item-edit`, `gh project item-list`, `gh issue view`, and `gh project field-list` verification completed and is recorded in `phase2_riopa_mirror_alignment.md`.

## Phase 3: Sub-Issue Work Breakdown

- [ ] Task: Create sub-issues under issue #1.
    - [ ] Hugging Face remote proof.
    - [ ] Zenodo draft/new-version proof.
    - [ ] Protected Zenodo production handoff.
    - [ ] GitHub release assets and attestations.
    - [ ] Public-surface and metadata evidence.
    - [ ] Collection/parser completion.
    - [ ] RIOPA/project sync automation.
- [ ] Task: Add all sub-issues to repo project #7 and RIOPA.
- [ ] Task: Populate project fields for each sub-issue.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Sub-Issue Work Breakdown' (Protocol in workflow.md)

## Phase 4: Sync Automation

- [ ] Task: Add an idempotent GitHub project sync script.
    - [ ] Read Conductor track entries and hidden issue markers.
    - [ ] Reconcile issues, sub-issues, labels, and project items.
    - [ ] Support dry-run and apply modes.
- [ ] Task: Add a scheduled/manual sync workflow.
    - [ ] Use least-privilege permissions.
    - [ ] Guard writes against dependency-update actors.
    - [ ] Emit project-sync evidence artifacts.
- [ ] Task: Add tests for marker parsing, duplicate avoidance, and field mapping.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Sync Automation' (Protocol in workflow.md)

## Phase 5: Documentation And Evidence

- [ ] Task: Document repo-to-RIOPA synchronization rules.
- [ ] Task: Update issue/project operating notes.
- [ ] Task: Run sync verification and attach evidence to the track.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Documentation And Evidence' (Protocol in workflow.md)
