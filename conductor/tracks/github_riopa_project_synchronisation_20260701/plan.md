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

- [x] Task: Create sub-issues under issue #1.
    - [x] Hugging Face remote proof.
    - [x] Zenodo draft/new-version proof.
    - [x] Protected Zenodo production handoff.
    - [x] GitHub release assets and attestations.
    - [x] Public-surface and metadata evidence.
    - [x] Collection/parser completion.
    - [x] RIOPA/project sync automation.
    - Evidence: issues `#2`-`#8` were created under parent issue `#1` with stable `riopa-subissue-id` markers.
- [x] Task: Add all sub-issues to repo project #7 and RIOPA.
    - Evidence: `phase3_subissue_work_breakdown.md` records readback showing all sub-issues are present in both `Rare Insights on Open Policy from Aotearoa` and `corpus-cases-medilegal-nz Archive Roadmap`.
- [x] Task: Populate project fields for each sub-issue.
    - Evidence: issues `#2`-`#7` read back as `Done` on both project boards, issue `#8` reads back as `In Progress`, and all RIOPA sub-issue items use `Mirror source: other`.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Sub-Issue Work Breakdown' (Protocol in workflow.md)
    - Evidence: live `gh issue view`, `gh issue list`, and `gh project item-list` verification is recorded in `phase3_subissue_work_breakdown.md`.

## Phase 4: Sync Automation

- [x] Task: Add an idempotent GitHub project sync script.
    - [x] Read Conductor track entries and hidden issue markers.
    - [x] Reconcile issues, sub-issues, labels, and project items.
    - [x] Support dry-run and apply modes.
    - Evidence: `scripts/sync_riopa_project.py` parses stable issue markers, detects duplicate markers, builds idempotent sync plans, supports dry-run and explicit `--apply`, and writes JSON evidence.
- [x] Task: Add a scheduled/manual sync workflow.
    - [x] Use least-privilege permissions.
    - [x] Guard writes against dependency-update actors.
    - [x] Emit project-sync evidence artifacts.
    - Evidence: `.github/workflows/riopa_project_sync.yml` runs weekly/manual sync, guards Dependabot/Renovate, prefers `RIOPA_PROJECT_TOKEN`, and uploads `riopa-project-sync-evidence`.
- [x] Task: Add tests for marker parsing, duplicate avoidance, and field mapping.
    - Evidence: `tests/test_riopa_project_sync.py` covers marker parsing, in-sync state, drift planning, and duplicate marker blocking; workflow assertions cover the RIOPA sync workflow guard and evidence artifact.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Sync Automation' (Protocol in workflow.md)
    - Evidence: `phase4_sync_automation_evidence.md` records local tests, Ruff checks, live apply-mode drift repair, and final dry-run `status: in_sync`.

## Phase 5: Documentation And Evidence

- [x] Task: Document repo-to-RIOPA synchronization rules.
    - Evidence: `docs/riopa-project-synchronisation.md` documents the RIOPA and repository project surfaces, hidden marker contract, `other` mirror-source fallback, dry-run/apply commands, workflow behavior, token expectations, generated evidence artifact, and operating notes.
- [x] Task: Update issue/project operating notes.
    - Evidence: issue `#8` now carries the sync-automation operating-note comment with the final dry-run command, evidence path, and RIOPA fallback boundary.
- [x] Task: Run sync verification and attach evidence to the track.
    - Evidence: `phase5_documentation_evidence.md` records the final sync dry-run result: `status: in_sync`, `actions: []`, `duplicate_markers: {}`, and seven desired subissues.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Documentation And Evidence' (Protocol in workflow.md)
    - Evidence: `phase5_documentation_evidence.md` records local sync verification, focused tests, Ruff checks, and Git whitespace validation.
