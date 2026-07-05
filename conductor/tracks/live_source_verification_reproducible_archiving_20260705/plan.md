# Implementation Plan: Live Source Verification And Reproducible Evidence Archiving

## Phase 1: Feasibility Audit And Verification Input Inventory

- [ ] Task: Define the source verification feasibility schema
    - [ ] Add statuses for immediately available, partially available, blocked, manual review required, and excluded sources.
    - [ ] Add evidence-type, archiving-policy, rights, blocker, and next-action fields.
    - [ ] Add fixture examples for all configured sources.
- [ ] Task: Discover immediately available verification inputs
    - [ ] Inspect source indexes, sitemaps, public APIs, feeds, downloadable exports, and static listing pages for every configured source.
    - [ ] Record whether each source can be verified from public official evidence without browser login or manual intervention.
    - [ ] Identify alternate datasets that can be downloaded and archived for reproducible verification.
- [ ] Task: Classify blockers and exclusions
    - [ ] Record technical blockers such as JavaScript-only search, anti-bot challenges, pagination gaps, source outages, and rate limits.
    - [ ] Record legal/privacy blockers such as terms uncertainty, redistribution limits, sensitive personal information, and redaction caveats.
    - [ ] Distinguish temporary blockers from sources that should be excluded with rationale.
- [ ] Task: Emit the first feasibility report
    - [ ] Generate `source_verification_feasibility.json`.
    - [ ] Generate a public-safe markdown summary for Conductor and release evidence.
    - [ ] Ensure every configured source has a feasibility classification.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Feasibility Audit And Verification Input Inventory' (Protocol in workflow.md)

## Phase 2: Evidence Downloading And Archive Bundle Design

- [ ] Task: Design deterministic verification evidence storage
    - [ ] Define raw evidence, normalized ledger, manifest, and replay directories.
    - [ ] Define checksum, retrieval timestamp, HTTP metadata, rights note, and parser provenance fields.
    - [ ] Separate small Git-safe ledgers from larger release/Hugging Face/Zenodo evidence archives.
- [ ] Task: Implement verification input fetchers
    - [ ] Download immediately available official indexes and alternate verification datasets.
    - [ ] Apply polite rate limits, retries, content-size limits, and deterministic filenames.
    - [ ] Capture retrieval failures as evidence instead of silently skipping them.
- [ ] Task: Implement evidence archive manifests
    - [ ] Write `verification_input_manifest.json`.
    - [ ] Write SHA256 checksums for raw and normalized verification inputs.
    - [ ] Record when a source is metadata-only because raw archiving is blocked.
- [ ] Task: Add archived-input replay mode
    - [ ] Allow verification to run offline from archived evidence bundles.
    - [ ] Fail if a replayed input hash does not match its manifest.
    - [ ] Add tests that prove replay mode does not use network access.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Evidence Downloading And Archive Bundle Design' (Protocol in workflow.md)

## Phase 3: Source-Specific Verification Adapters

- [ ] Task: Build common verification adapter contracts
    - [ ] Normalize expected records with source, identifier, title, date, canonical URL, alternate URLs, content hash when available, and evidence input references.
    - [ ] Add adapter validation for missing identifiers, malformed dates, duplicate URLs, and ambiguous titles.
- [ ] Task: Implement adapters for immediately available official sources
    - [ ] Implement adapters for sources with public static indexes or APIs discovered in Phase 1.
    - [ ] Add fixture-backed tests for each implemented adapter.
    - [ ] Keep blocked sources represented by blocker records instead of false zero counts.
- [ ] Task: Implement alternate-dataset adapters where justified
    - [ ] Normalize alternate datasets only after their raw inputs are archived or metadata-only blockers are recorded.
    - [ ] Keep alternate-source confidence below official-source confidence unless the alternate source is authoritative.
    - [ ] Record provenance links between alternate expected records and official source records.
- [ ] Task: Generate expected-record ledgers
    - [ ] Emit per-source `expected_records.jsonl`.
    - [ ] Emit aggregate `source_expected_records.jsonl`.
    - [ ] Emit source target confidence updates for source maturity.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Source-Specific Verification Adapters' (Protocol in workflow.md)

## Phase 4: Completeness Reconciliation And Gap Classification

- [ ] Task: Implement expected-versus-processed reconciliation
    - [ ] Match on stable identifier, canonical URL, alternate URLs, title/date fingerprints, and source-specific aliases.
    - [ ] Classify matched, missing, extra, duplicate, ambiguous, excluded, blocked, and manual-review records.
    - [ ] Preserve source-specific match rationale for auditability.
- [ ] Task: Add verified target promotion rules
    - [ ] Promote to `source_index_count` or `official_count` only from archived evidence-backed inputs.
    - [ ] Prevent baseline fixture minima from claiming historical completion.
    - [ ] Recompute source maturity using verification ledgers.
- [ ] Task: Generate source completeness reports
    - [ ] Write per-source gap reports.
    - [ ] Write aggregate completeness summaries.
    - [ ] Write public-safe claims data for README, dataset cards, and release notes.
- [ ] Task: Add regression and anomaly checks
    - [ ] Detect sudden expected-count drift.
    - [ ] Detect disappearance of official source index inputs.
    - [ ] Detect remote-manifest or archived-input hash mismatch.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Completeness Reconciliation And Gap Classification' (Protocol in workflow.md)

## Phase 5: Publication And Archive Integration

- [ ] Task: Integrate verification artifacts into monthly publication
    - [ ] Attach feasibility report, verification input manifest, expected-record ledgers, completeness reports, and blocker summaries.
    - [ ] Include verification artifact checksums in release evidence.
    - [ ] Include verification status in archive maturity scoring.
- [ ] Task: Publish reproducible evidence to archive surfaces
    - [ ] Add Hugging Face upload/readback for verification ledgers and permitted evidence inputs.
    - [ ] Add Zenodo bundle inclusion for immutable verification evidence.
    - [ ] Keep GitHub release assets lightweight but sufficient to locate and verify all evidence bundles.
- [ ] Task: Align public claims with evidence ledgers
    - [ ] Generate README and dataset-card claims from completeness reports.
    - [ ] Include explicit caveats for blocked, partially available, and metadata-only sources.
    - [ ] Fail strict release readiness if claims drift from ledgers.
- [ ] Task: Add release readiness gates
    - [ ] Report verified complete, verified incomplete, blocked by source access, and not yet verified separately.
    - [ ] Allow canonical publication only when unresolved verification blockers are declared and evidence-backed.
    - [ ] Keep Codeberg/GitLab mirror health integrated with the release evidence summary.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Publication And Archive Integration' (Protocol in workflow.md)

## Phase 6: Review, Documentation, And First Verification Proof

- [ ] Task: Add operator documentation
    - [ ] Document how to run live verification, archived replay verification, and publication-integrated verification.
    - [ ] Document source-specific blockers and how to update them.
    - [ ] Document how alternate datasets are archived and cited.
- [ ] Task: Run first feasibility and archived replay proof
    - [ ] Generate first feasibility report from live discovery.
    - [ ] Download and archive immediately available verification inputs.
    - [ ] Replay verification from archived inputs and compare results.
- [ ] Task: Run automated validation
    - [ ] Run unit tests for schemas, fetchers, manifests, adapters, reconciliation, claims, and release gates.
    - [ ] Run integration tests for archived replay and monthly publication artifact inclusion.
    - [ ] Run lint, format, and CI-equivalent pytest coverage.
- [ ] Task: Run Conductor review and archive evidence
    - [ ] Run `$conductor-review` against the track.
    - [ ] Apply review fixes.
    - [ ] Archive the track only after verification artifacts and blockers are evidence-backed.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Review, Documentation, And First Verification Proof' (Protocol in workflow.md)
