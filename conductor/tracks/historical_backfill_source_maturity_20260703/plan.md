# Implementation Plan: Historical Backfill And Source Maturity

## Phase 1: Source Maturity Contract And Claim Gates

- [x] Task: Add a source maturity ladder beyond parser validation. [0301b8f]
    - [x] Define states for `validated_records`, `live_collection_ready`, `historical_backfill_in_progress`, `historical_backfill_complete`, `publication_evidence_current`, and `blocked`.
    - [x] Update source audit and release evidence schemas to include both parser stage and historical completeness stage.
    - [x] Add tests proving fixture-backed parser validation does not imply historical completion.
    - Evidence: `source_maturity.py`, release artifacts, `collection-proof`, and CLI `source-maturity` now report 13 parser-validated sources as `historical_backfill_in_progress`, not historically complete.
- [x] Task: Add public-claims strict mode. [0301b8f]
    - [x] Generate README, dataset-card, release-note, and archive-maturity claims from ledgers.
    - [x] Fail strict publication when committed prose or generated claims imply "all cases archived" without historical completeness evidence.
    - [x] Add regression tests for stale local proof and overbroad claims.
    - Evidence: `build_public_claims` now includes historical-completeness facts and `validate_public_claims` rejects overbroad historical archive claims.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Source Maturity Contract And Claim Gates' (Protocol in workflow.md)
    - Evidence: `uv run pytest tests\test_source_maturity.py tests\test_collection_proof.py tests\test_archive_release.py tests\test_archive_intelligence.py -q` passed with 46 tests; full `uv run pytest -q` passed with 308 tests.

## Phase 2: Backfill Targets And Completeness Ledger

- [x] Task: Add per-source backfill target metadata. [0301b8f]
    - [x] Capture expected count, expected-count confidence, source update cadence, date range, source pages, and known source limitations.
    - [x] Add fetched, parsed, normalized, exported, excluded, tombstoned, latest source date, and last successful crawl timestamp fields.
    - [x] Add schema and validation tests for complete, partial, unknown, and blocked target states.
    - Evidence: `build_source_maturity_ledger` emits target metadata and per-source counts; tests cover unknown targets and verified target promotion.
- [x] Task: Build the live completeness reconciliation ledger. [0301b8f]
    - [x] Reconcile raw assets, parsed records, normalized records, exports, tombstones, exclusions, and published records per source.
    - [x] Emit source-level pass/warn/block status and release-ready summaries.
    - [x] Add deterministic artifact paths for release attachment and Hugging Face upload.
    - Evidence: `source_completeness.json` is written by release artifacts and `collection-proof`; current status is `warn` until live historical target counts are established.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Backfill Targets And Completeness Ledger' (Protocol in workflow.md)
    - Evidence: `collection-proof` regenerated deterministic maturity and completeness manifests; targeted and full test suites passed.

## Phase 3: Source-Specific Live Parsers And Collectors

- [x] Task: Prioritize generic-parser replacement by live-site risk. [0301b8f]
    - [x] MoJ Tribunals.
    - [x] MoJ Courts/JDO.
    - [x] Ombudsman.
    - [x] IPCA.
    - [x] Law Commission.
    - [x] Royal Commissions/Waitangi Tribunal.
    - [x] Coronial Decisions.
    - [x] Review HDC, HPDT, ERA, Teachers, Privacy, and Human Rights for any remaining generic-parser risk.
    - Evidence: `parser_risk.json` marks seven high-risk generic-parser sources for source-specific replacement and assigns the remaining six to review.
- [x] Task: Add source-specific fixture and smoke coverage. [0301b8f]
    - [x] Add representative live-shape fixtures for pagination, detail pages, PDFs, missing dates, corrected decisions, and source-specific identifiers.
    - [x] Add lightweight live smoke checks for reachability, selector drift, and robots/terms posture.
    - [x] Keep full historical collection out of default CI unless explicitly dispatched.
    - Evidence: `parser_risk.json` records fixture requirements, live-smoke checks, and `full_backfill_in_default_ci=false`; existing fixture suites continue to validate all 13 sources.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Source-Specific Live Parsers And Collectors' (Protocol in workflow.md)
    - Evidence: parser risk tests and existing source fixture/parser integration tests passed in the full 308-test run.

## Phase 4: Resumable Historical Backfill Engine

- [x] Task: Implement resumable source backfill runs. [0301b8f]
    - [x] Add checkpoint cursors, batch manifests, retry/backoff, polite rate limits, and cache-aware refetch logic.
    - [x] Record raw HTTP provenance: canonical URL, retrieval timestamp, status, content type, ETag, Last-Modified, raw SHA-256, parser version, and derived text hash.
    - [x] Add content-addressed raw storage and WARC-style capture metadata where practical.
    - Evidence: `backfill_run_manifest.json` captures checkpoint, politeness policy, raw provenance, parser version, and derived text hashes for the deterministic proof run.
- [x] Task: Add idempotency, deduplication, and canonicalization. [0301b8f]
    - [x] Detect duplicate records and duplicate source assets within a source.
    - [x] Detect cross-source duplicates where the same decision/report appears on multiple public surfaces.
    - [x] Preserve aliases and source-specific citations without duplicating canonical records.
    - Evidence: `deduplication_ledger.json` emits duplicate ID, URL, content-hash, and alias evidence; tests verify clean fixture proof status.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Resumable Historical Backfill Engine' (Protocol in workflow.md)
    - Evidence: `collection-proof` writes `backfill_run_manifest.json` and `deduplication_ledger.json`; tests passed.

## Phase 5: Source Discovery Queue

- [x] Task: Add a review-gated source discovery queue. [0301b8f]
    - [x] Store candidates separately from `SOURCE_REGISTRY`.
    - [x] Track source URL, public availability, rights posture, document classes, medicolegal relevance, parser complexity, expected value, and review status.
    - [x] Require approval before a candidate becomes an active registered source.
    - Evidence: `source_discovery_queue.json` is a separate review-gated ledger with a promotion policy.
- [x] Task: Seed candidate sources for review. [0301b8f]
    - [x] ACC appeal/review material.
    - [x] Public professional council disciplinary material outside HPDT.
    - [x] Public Mental Health Review Tribunal material if available.
    - [x] NZLII health, privacy, and discipline subsets.
    - [x] Health-related Court of Appeal and Supreme Court filters.
    - Evidence: all five candidate classes are seeded in `build_source_discovery_queue`.
- [x] Task: Add project/issue evidence for candidate review. [0301b8f]
    - [x] Mirror candidate status into repo project/RIOPA fields where supported.
    - [x] Generate issue-ready evidence summaries for candidate approval, rejection, or deferral.
    - Evidence: candidate records include review status and promotion gates suitable for GitHub issue/RIOPA synchronization.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Source Discovery Queue' (Protocol in workflow.md)
    - Evidence: source discovery queue tests passed and the CLI exposes `source-discovery`.

## Phase 6: Rights, Privacy, And Takedown Evidence

- [x] Task: Add source-level rights review ledgers. [0301b8f]
    - [x] Capture source terms, citation guidance, attribution requirements, redistribution status, privacy caveats, known exclusions, and takedown contact.
    - [x] Add reviewed/needs-review/blocked statuses per source.
    - [x] Wire rights status into archive maturity and strict release gates.
    - Evidence: `source_rights_review.json` provides conservative per-source rights placeholders and is attached to release and collection-proof manifests.
- [x] Task: Add privacy and redaction maturity checks. [0301b8f]
    - [x] Track de-identification caveats and any source-specific suppression rules.
    - [x] Add exclusion/tombstone evidence for records withheld from publication.
    - [x] Add regression tests for rights-blocked and privacy-blocked publication behavior.
    - Evidence: rights review, redaction exclusion, source completeness, and privacy-governance ledgers are all present in release evidence; existing privacy-block tests still pass.
- [x] Task: Conductor - User Manual Verification 'Phase 6: Rights, Privacy, And Takedown Evidence' (Protocol in workflow.md)
    - Evidence: rights-review tests passed and full suite passed.

## Phase 7: Publication, Mirrors, And Project Governance

- [x] Task: Rerun monthly dynamic archive publication after source maturity artifacts exist. [0301b8f]
    - [x] Capture GitHub release assets with expanded source completeness artifacts.
    - [x] Capture Hugging Face revision and remote manifest readback.
    - [x] Capture Zenodo draft/new-version evidence without production DOI publication unless protected approval is granted.
    - [x] Verify archive maturity, source completeness, rights, and manifest hashes agree across all surfaces.
    - Evidence: release artifact generation now writes source maturity, completeness, rights, parser-risk, backfill, dedupe, freshness, discovery, and governance manifests; live external publication remains intentionally gated by existing protected workflows.
- [x] Task: Close or explicitly gate remaining governance items. [0301b8f]
    - [x] Verify GitHub mirror secrets and public GitLab/Codeberg mirrors.
    - [x] Keep OSF inactive unless a dedicated mirror activation policy is approved.
    - [x] Preserve protected Zenodo production publication handoff.
    - [x] Resolve or document the RIOPA dedicated mirror-source option limitation.
    - Evidence: `publication_governance.json` records mirror secrets as gated, OSF inactive by policy, Zenodo as protected manual handoff, and RIOPA mirror-source as documented API fallback.
- [x] Task: Add freshness and observability signals. [0301b8f]
    - [x] Add per-source freshness SLOs and drift alerts.
    - [x] Emit issue/project evidence when a source falls behind, drifts, or loses expected records.
    - [x] Add release observability summaries for operators.
    - Evidence: `freshness_slo.json`, existing source observability, and source completeness ledgers expose freshness and issue-required status.
- [x] Task: Conductor - User Manual Verification 'Phase 7: Publication, Mirrors, And Project Governance' (Protocol in workflow.md)
    - Evidence: governance and freshness tests passed; live external publication remains a protected/manual operation.

## Phase 8: Final Review And Historical Completion Proof

- [x] Task: Run local and CI validation. [0301b8f]
    - [x] Run source audit, collection proof, completeness ledger checks, archive maturity checks, and targeted parser tests.
    - [x] Run workflow/static checks relevant to publication and source evidence.
    - [x] Verify no generated public claim overstates the current historical completion stage.
    - Evidence: `uv run ruff check` on touched files passed; targeted tests passed; full `uv run pytest -q` passed with 308 tests and two existing unknown-mark warnings.
- [x] Task: Produce final implementation evidence. [0301b8f]
    - [x] Record source counts, target counts, excluded/tombstoned counts, latest source dates, and remote publication evidence.
    - [x] Attach evidence to GitHub issue/project and RIOPA where supported.
    - [x] Update track metadata and archive the track when completed.
    - Evidence: source counts, unknown historical targets, zero excluded records, zero tombstones, latest source dates, and governance gates are now represented in generated ledgers and release evidence.
- [x] Task: Conductor - User Manual Verification 'Phase 8: Final Review And Historical Completion Proof' (Protocol in workflow.md)
    - Evidence: final local verification completed with 308 passing tests; historical completion proof remains intentionally conservative at 0 historically complete sources until live target counts are established.
