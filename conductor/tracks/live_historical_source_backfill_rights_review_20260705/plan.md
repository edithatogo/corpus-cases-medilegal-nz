# Implementation Plan: Live Historical Corpus Completion And Rights Review

## Phase 1: Track, Issue, And Project Evidence Setup

- [x] Task: Create Conductor track artifacts.
    - [x] Add specification, implementation plan, metadata, and index files.
    - [x] Register the track in `conductor/tracks.md`.
- [x] Task: Create GitHub issue hierarchy.
    - [x] Create parent issue `#10` for live historical corpus completion.
    - [x] Create seven subissues aligned with verification, rights, parser, candidate, backfill, release, and project-sync workstreams.
    - [x] Add deterministic issue markers for project-sync readback.
- [x] Task: Extend RIOPA project sync evidence.
    - [x] Add content-completion subissues to sync desired state.
    - [x] Preserve existing monthly archive issue sync behavior.
    - [x] Add tests for multi-parent issue markers and sync planning.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Track, Issue, And Project Evidence Setup' (Protocol in workflow.md)

## Phase 2: Live Source Verification And Archived Replay

- [x] Task: Implement live source-index fetchers for all active sources.
    - [x] Fetch official index or listing evidence for the 13 active sources.
    - [x] Archive raw inputs with checksums, timestamps, URL metadata, and rights notes.
    - [x] Record failed fetches as explicit blockers.
- [x] Task: Preserve offline replay.
    - [x] Verify archived input hashes before replay.
    - [x] Rebuild expected-record ledgers from archived inputs without network access.
    - [x] Fail replay when manifest and raw evidence disagree.
- [x] Task: Reconcile live expected records against processed records.
    - [x] Match by source identifier, canonical URL, alternate URL, title/date fingerprint, and source-specific aliases.
    - [x] Classify matched, missing, extra, duplicate, ambiguous, excluded, blocked, and manual-review records.
    - [x] Emit source-level gap reports and aggregate completeness summaries.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Live Source Verification And Archived Replay' (Protocol in workflow.md)

## Phase 3: Rights, Terms, Privacy, And Claims Governance

- [x] Task: Complete source rights ledger for all active sources.
    - [x] Populate source terms URL, attribution, redistribution status, citation guidance, known exclusions, privacy caveats, and takedown contact.
    - [x] Keep unresolved sources as blockers with source-specific next action.
    - [x] Add validation for rights ledger completeness.
- [x] Task: Add release-claim gates.
    - [x] Block complete-corpus claims when rights, privacy, parser, live verification, or reconciliation status is unresolved.
    - [x] Keep dry-run publication allowed with explicit caveats.
    - [x] Generate README, dataset-card, release-note, and project-summary claims from ledgers.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Rights, Terms, Privacy, And Claims Governance' (Protocol in workflow.md)

## Phase 4: Parser Replacement And Live Drift Proof

- [x] Task: Replace high-risk generic parser paths.
    - [x] Implement source-specific parser proof for `moj_tribunals`, `royal_commissions`, `coronial`, `ombudsman`, `moj_courts`, `ipca`, and `law_commission`.
    - [x] Add fixture and live-smoke contracts for pagination, detail pages, document assets, dates, and source identifiers.
    - [x] Keep blockers explicit where live site shape prevents deterministic parser proof.
- [x] Task: Promote review-level parser sources only after drift checks.
    - [x] Run selector-drift checks for `hdc`, `hpdt`, `era`, `teachers`, `privacy`, and `human_rights`.
    - [x] Record whether generic parser behavior remains acceptable or needs replacement.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Parser Replacement And Live Drift Proof' (Protocol in workflow.md)

## Phase 5: Candidate Source Triage And Promotion

- [x] Task: Triage remaining candidate sources.
    - [x] Classify ACC appeals/reviews, other professional councils, Mental Health Review Tribunal, NZLII health/privacy/discipline subsets, and health appellate court filters as `approved`, `deferred`, or `excluded`.
    - [x] Record rights, public availability, duplication, scope, parser complexity, and promotion rationale.
- [x] Task: Promote approved candidates.
    - [x] Add source config and fixture contract for approved candidates.
    - [x] Add live verification, rights ledger, parser-risk status, and release-evidence integration.
    - [x] Keep deferred or excluded candidates visible in public-safe discovery ledgers.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Candidate Source Triage And Promotion' (Protocol in workflow.md)

## Phase 6: Historical Backfill, Publication, And Completion Proof

- [x] Task: Run historical backfill after verification gates pass.
    - [x] Generate processed records, manifests, source coverage ledgers, and dataset diff evidence from live-backed inputs.
    - [x] Reconcile processed records against expected live source records.
    - [x] Preserve unresolved source gaps as blockers rather than false completion.
- [ ] Task: Publish verified release evidence.
    - [x] Attach source verification, rights, parser, candidate-source, and completeness evidence to GitHub release assets.
    - [ ] Upload live-backed evidence to Hugging Face and verify remote manifests.
    - [ ] Upload Zenodo draft/new-version evidence and preserve protected production handoff.
- [ ] Task: Complete review and archive.
    - [ ] Run `uv run pytest -q` and targeted workflow/project-sync tests.
    - [ ] Run Conductor review, apply fixes, and archive the track after evidence is complete.
    - [ ] Close or update the parent issue and subissues based on verified outcomes.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Historical Backfill, Publication, And Completion Proof' (Protocol in workflow.md)
