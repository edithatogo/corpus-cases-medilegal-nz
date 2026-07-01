# Implementation Plan: GitHub RIOPA Project Synchronisation

## Phase 1: Project Schema Audit

- [ ] Task: Capture live RIOPA and repo project field schemas.
    - [ ] Record project IDs, field IDs, option IDs, and current item IDs.
    - [ ] Compare medilegal project fields against sibling roadmap boards.
    - [ ] Identify fields that can be created through available GitHub APIs.
- [ ] Task: Define the medilegal project field contract.
    - [ ] Specify field names, allowed values, and mapping to Conductor track status.
    - [ ] Document fallback behavior for unsupported field mutations.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Project Schema Audit' (Protocol in workflow.md)

## Phase 2: RIOPA Mirror Alignment

- [ ] Task: Add or document the `corpus-cases-medilegal-nz` RIOPA mirror source option.
    - [ ] Prefer a dedicated mirror-source option.
    - [ ] If unavailable through the API, document the manual project-field change.
- [ ] Task: Set issue #1 RIOPA item fields.
    - [ ] Set status, repository, mirror source, and conductor-track metadata.
    - [ ] Verify item appears in filtered RIOPA views.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: RIOPA Mirror Alignment' (Protocol in workflow.md)

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
