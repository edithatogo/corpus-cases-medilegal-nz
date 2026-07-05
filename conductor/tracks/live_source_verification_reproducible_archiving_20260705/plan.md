# Implementation Plan: Live Source Verification And Reproducible Evidence Archiving

## Phase 1: Feasibility Audit And Verification Input Inventory

- [x] Task: Define the source verification feasibility schema
    - [x] Add statuses for immediately available, partially available, blocked, manual review required, and excluded sources.
    - [x] Add evidence-type, archiving-policy, rights, blocker, and next-action fields.
    - [x] Add fixture examples for all configured sources.
- [x] Task: Discover immediately available verification inputs
    - [x] Inspect source indexes, sitemaps, public APIs, feeds, downloadable exports, and static listing pages for every configured source.
    - [x] Record whether each source can be verified from public official evidence without browser login or manual intervention.
    - [x] Identify alternate datasets that can be downloaded and archived for reproducible verification.
- [x] Task: Classify blockers and exclusions
    - [x] Record technical blockers such as JavaScript-only search, anti-bot challenges, pagination gaps, source outages, and rate limits.
    - [x] Record legal/privacy blockers such as terms uncertainty, redistribution limits, sensitive personal information, and redaction caveats.
    - [x] Distinguish temporary blockers from sources that should be excluded with rationale.
- [x] Task: Emit the first feasibility report
    - [x] Generate `source_verification_feasibility.json`.
    - [x] Generate a public-safe markdown summary for Conductor and release evidence.
    - [x] Ensure every configured source has a feasibility classification.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Feasibility Audit And Verification Input Inventory' (Protocol in workflow.md)

## Phase 2: Evidence Downloading And Archive Bundle Design

- [x] Task: Design deterministic verification evidence storage
    - [x] Define raw evidence, normalized ledger, manifest, and replay directories.
    - [x] Define checksum, retrieval timestamp, HTTP metadata, rights note, and parser provenance fields.
    - [x] Separate small Git-safe ledgers from larger release/Hugging Face/Zenodo evidence archives.
- [x] Task: Implement verification input fetchers
    - [x] Download immediately available official indexes and alternate verification datasets.
    - [x] Apply polite rate limits, retries, content-size limits, and deterministic filenames.
    - [x] Capture retrieval failures as evidence instead of silently skipping them.
- [x] Task: Implement evidence archive manifests
    - [x] Write `verification_input_manifest.json`.
    - [x] Write SHA256 checksums for raw and normalized verification inputs.
    - [x] Record when a source is metadata-only because raw archiving is blocked.
- [x] Task: Add archived-input replay mode
    - [x] Allow verification to run offline from archived evidence bundles.
    - [x] Fail if a replayed input hash does not match its manifest.
    - [x] Add tests that prove replay mode does not use network access.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Evidence Downloading And Archive Bundle Design' (Protocol in workflow.md)

## Phase 3: Source-Specific Verification Adapters

- [x] Task: Build common verification adapter contracts
    - [x] Normalize expected records with source, identifier, title, date, canonical URL, alternate URLs, content hash when available, and evidence input references.
    - [x] Add adapter validation for missing identifiers, malformed dates, duplicate URLs, and ambiguous titles.
- [x] Task: Implement adapters for immediately available official sources
    - [x] Implement adapters for sources with public static indexes or APIs discovered in Phase 1.
    - [x] Add fixture-backed tests for each implemented adapter.
    - [x] Keep blocked sources represented by blocker records instead of false zero counts.
- [x] Task: Implement alternate-dataset adapters where justified
    - [x] Normalize alternate datasets only after their raw inputs are archived or metadata-only blockers are recorded.
    - [x] Keep alternate-source confidence below official-source confidence unless the alternate source is authoritative.
    - [x] Record provenance links between alternate expected records and official source records.
- [x] Task: Generate expected-record ledgers
    - [x] Emit per-source `expected_records.jsonl`.
    - [x] Emit aggregate `source_expected_records.jsonl`.
    - [x] Emit source target confidence updates for source maturity.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Source-Specific Verification Adapters' (Protocol in workflow.md)

## Phase 4: Completeness Reconciliation And Gap Classification

- [x] Task: Implement expected-versus-processed reconciliation
    - [x] Match on stable identifier, canonical URL, alternate URLs, title/date fingerprints, and source-specific aliases.
    - [x] Classify matched, missing, extra, duplicate, ambiguous, excluded, blocked, and manual-review records.
    - [x] Preserve source-specific match rationale for auditability.
- [x] Task: Add verified target promotion rules
    - [x] Promote to `source_index_count` or `official_count` only from archived evidence-backed inputs.
    - [x] Prevent baseline fixture minima from claiming historical completion.
    - [x] Recompute source maturity using verification ledgers.
- [x] Task: Generate source completeness reports
    - [x] Write per-source gap reports.
    - [x] Write aggregate completeness summaries.
    - [x] Write public-safe claims data for README, dataset cards, and release notes.
- [x] Task: Add regression and anomaly checks
    - [x] Detect sudden expected-count drift.
    - [x] Detect disappearance of official source index inputs.
    - [x] Detect remote-manifest or archived-input hash mismatch.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Completeness Reconciliation And Gap Classification' (Protocol in workflow.md)

## Phase 5: Publication And Archive Integration

- [x] Task: Integrate verification artifacts into monthly publication
    - [x] Attach feasibility report, verification input manifest, expected-record ledgers, completeness reports, and blocker summaries.
    - [x] Include verification artifact checksums in release evidence.
    - [x] Include verification status in archive maturity scoring.
- [x] Task: Publish reproducible evidence to archive surfaces
    - [x] Add Hugging Face upload/readback for verification ledgers and permitted evidence inputs.
    - [x] Add Zenodo bundle inclusion for immutable verification evidence.
    - [x] Keep GitHub release assets lightweight but sufficient to locate and verify all evidence bundles.
- [x] Task: Align public claims with evidence ledgers
    - [x] Generate README and dataset-card claims from completeness reports.
    - [x] Include explicit caveats for blocked, partially available, and metadata-only sources.
    - [x] Fail strict release readiness if claims drift from ledgers.
- [x] Task: Add release readiness gates
    - [x] Report verified complete, verified incomplete, blocked by source access, and not yet verified separately.
    - [x] Allow canonical publication only when unresolved verification blockers are declared and evidence-backed.
    - [x] Keep Codeberg/GitLab mirror health integrated with the release evidence summary.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Publication And Archive Integration' (Protocol in workflow.md)

## Phase 6: Review, Documentation, And First Verification Proof

- [x] Task: Add operator documentation
    - [x] Document how to run live verification, archived replay verification, and publication-integrated verification.
    - [x] Document source-specific blockers and how to update them.
    - [x] Document how alternate datasets are archived and cited.
- [x] Task: Run first feasibility and archived replay proof
    - [x] Generate first feasibility report from live discovery.
    - [x] Download and archive immediately available verification inputs.
    - [x] Replay verification from archived inputs and compare results.
- [x] Task: Run automated validation
    - [x] Run unit tests for schemas, fetchers, manifests, adapters, reconciliation, claims, and release gates.
    - [x] Run integration tests for archived replay and monthly publication artifact inclusion.
    - [x] Run lint, format, and CI-equivalent pytest coverage.
- [x] Task: Run Conductor review and archive evidence
    - [x] Run `$conductor-review` against the track.
    - [x] Apply review fixes.
    - [x] Archive the track only after verification artifacts and blockers are evidence-backed.
- [x] Task: Conductor - User Manual Verification 'Phase 6: Review, Documentation, And First Verification Proof' (Protocol in workflow.md)
