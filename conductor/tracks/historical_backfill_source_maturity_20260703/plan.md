# Implementation Plan: Historical Backfill And Source Maturity

## Phase 1: Source Maturity Contract And Claim Gates

- [ ] Task: Add a source maturity ladder beyond parser validation.
    - [ ] Define states for `validated_records`, `live_collection_ready`, `historical_backfill_in_progress`, `historical_backfill_complete`, `publication_evidence_current`, and `blocked`.
    - [ ] Update source audit and release evidence schemas to include both parser stage and historical completeness stage.
    - [ ] Add tests proving fixture-backed parser validation does not imply historical completion.
- [ ] Task: Add public-claims strict mode.
    - [ ] Generate README, dataset-card, release-note, and archive-maturity claims from ledgers.
    - [ ] Fail strict publication when committed prose or generated claims imply "all cases archived" without historical completeness evidence.
    - [ ] Add regression tests for stale local proof and overbroad claims.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Source Maturity Contract And Claim Gates' (Protocol in workflow.md)

## Phase 2: Backfill Targets And Completeness Ledger

- [ ] Task: Add per-source backfill target metadata.
    - [ ] Capture expected count, expected-count confidence, source update cadence, date range, source pages, and known source limitations.
    - [ ] Add fetched, parsed, normalized, exported, excluded, tombstoned, latest source date, and last successful crawl timestamp fields.
    - [ ] Add schema and validation tests for complete, partial, unknown, and blocked target states.
- [ ] Task: Build the live completeness reconciliation ledger.
    - [ ] Reconcile raw assets, parsed records, normalized records, exports, tombstones, exclusions, and published records per source.
    - [ ] Emit source-level pass/warn/block status and release-ready summaries.
    - [ ] Add deterministic artifact paths for release attachment and Hugging Face upload.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Backfill Targets And Completeness Ledger' (Protocol in workflow.md)

## Phase 3: Source-Specific Live Parsers And Collectors

- [ ] Task: Prioritize generic-parser replacement by live-site risk.
    - [ ] MoJ Tribunals.
    - [ ] MoJ Courts/JDO.
    - [ ] Ombudsman.
    - [ ] IPCA.
    - [ ] Law Commission.
    - [ ] Royal Commissions/Waitangi Tribunal.
    - [ ] Coronial Decisions.
    - [ ] Review HDC, HPDT, ERA, Teachers, Privacy, and Human Rights for any remaining generic-parser risk.
- [ ] Task: Add source-specific fixture and smoke coverage.
    - [ ] Add representative live-shape fixtures for pagination, detail pages, PDFs, missing dates, corrected decisions, and source-specific identifiers.
    - [ ] Add lightweight live smoke checks for reachability, selector drift, and robots/terms posture.
    - [ ] Keep full historical collection out of default CI unless explicitly dispatched.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Source-Specific Live Parsers And Collectors' (Protocol in workflow.md)

## Phase 4: Resumable Historical Backfill Engine

- [ ] Task: Implement resumable source backfill runs.
    - [ ] Add checkpoint cursors, batch manifests, retry/backoff, polite rate limits, and cache-aware refetch logic.
    - [ ] Record raw HTTP provenance: canonical URL, retrieval timestamp, status, content type, ETag, Last-Modified, raw SHA-256, parser version, and derived text hash.
    - [ ] Add content-addressed raw storage and WARC-style capture metadata where practical.
- [ ] Task: Add idempotency, deduplication, and canonicalization.
    - [ ] Detect duplicate records and duplicate source assets within a source.
    - [ ] Detect cross-source duplicates where the same decision/report appears on multiple public surfaces.
    - [ ] Preserve aliases and source-specific citations without duplicating canonical records.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Resumable Historical Backfill Engine' (Protocol in workflow.md)

## Phase 5: Source Discovery Queue

- [ ] Task: Add a review-gated source discovery queue.
    - [ ] Store candidates separately from `SOURCE_REGISTRY`.
    - [ ] Track source URL, public availability, rights posture, document classes, medicolegal relevance, parser complexity, expected value, and review status.
    - [ ] Require approval before a candidate becomes an active registered source.
- [ ] Task: Seed candidate sources for review.
    - [ ] ACC appeal/review material.
    - [ ] Public professional council disciplinary material outside HPDT.
    - [ ] Public Mental Health Review Tribunal material if available.
    - [ ] NZLII health, privacy, and discipline subsets.
    - [ ] Health-related Court of Appeal and Supreme Court filters.
- [ ] Task: Add project/issue evidence for candidate review.
    - [ ] Mirror candidate status into repo project/RIOPA fields where supported.
    - [ ] Generate issue-ready evidence summaries for candidate approval, rejection, or deferral.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Source Discovery Queue' (Protocol in workflow.md)

## Phase 6: Rights, Privacy, And Takedown Evidence

- [ ] Task: Add source-level rights review ledgers.
    - [ ] Capture source terms, citation guidance, attribution requirements, redistribution status, privacy caveats, known exclusions, and takedown contact.
    - [ ] Add reviewed/needs-review/blocked statuses per source.
    - [ ] Wire rights status into archive maturity and strict release gates.
- [ ] Task: Add privacy and redaction maturity checks.
    - [ ] Track de-identification caveats and any source-specific suppression rules.
    - [ ] Add exclusion/tombstone evidence for records withheld from publication.
    - [ ] Add regression tests for rights-blocked and privacy-blocked publication behavior.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Rights, Privacy, And Takedown Evidence' (Protocol in workflow.md)

## Phase 7: Publication, Mirrors, And Project Governance

- [ ] Task: Rerun monthly dynamic archive publication after source maturity artifacts exist.
    - [ ] Capture GitHub release assets with expanded source completeness artifacts.
    - [ ] Capture Hugging Face revision and remote manifest readback.
    - [ ] Capture Zenodo draft/new-version evidence without production DOI publication unless protected approval is granted.
    - [ ] Verify archive maturity, source completeness, rights, and manifest hashes agree across all surfaces.
- [ ] Task: Close or explicitly gate remaining governance items.
    - [ ] Verify GitHub mirror secrets and public GitLab/Codeberg mirrors.
    - [ ] Keep OSF inactive unless a dedicated mirror activation policy is approved.
    - [ ] Preserve protected Zenodo production publication handoff.
    - [ ] Resolve or document the RIOPA dedicated mirror-source option limitation.
- [ ] Task: Add freshness and observability signals.
    - [ ] Add per-source freshness SLOs and drift alerts.
    - [ ] Emit issue/project evidence when a source falls behind, drifts, or loses expected records.
    - [ ] Add release observability summaries for operators.
- [ ] Task: Conductor - User Manual Verification 'Phase 7: Publication, Mirrors, And Project Governance' (Protocol in workflow.md)

## Phase 8: Final Review And Historical Completion Proof

- [ ] Task: Run local and CI validation.
    - [ ] Run source audit, collection proof, completeness ledger checks, archive maturity checks, and targeted parser tests.
    - [ ] Run workflow/static checks relevant to publication and source evidence.
    - [ ] Verify no generated public claim overstates the current historical completion stage.
- [ ] Task: Produce final implementation evidence.
    - [ ] Record source counts, target counts, excluded/tombstoned counts, latest source dates, and remote publication evidence.
    - [ ] Attach evidence to GitHub issue/project and RIOPA where supported.
    - [ ] Update track metadata and archive the track when completed.
- [ ] Task: Conductor - User Manual Verification 'Phase 8: Final Review And Historical Completion Proof' (Protocol in workflow.md)
