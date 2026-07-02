# Plan - Monthly Dynamic Archive Publication

## Phase 1: Archive-Family Contract And Current-State Audit

- [x] Task: Compare medilegal publication conventions against corpus-law, Hansard, and fyi-archive archive patterns.
- [x] Task: Record required compatibility decisions for GitHub, Hugging Face, Zenodo, OSF, release evidence, and protected publication.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Archive-Family Contract And Current-State Audit' (Protocol in workflow.md)

## Phase 2: Versioning, Schema, And Release Ladder

- [x] Task: Add dataset archive version derivation and release tag helpers.
- [x] Task: Add schema export and schema-version evidence for release manifests.
- [x] Task: Add release ladder and dataset diff/changelog fields to release evidence.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Versioning, Schema, And Release Ladder' (Protocol in workflow.md)

## Phase 3: Archive Packaging, Coverage, And Quality Gates

- [x] Task: Add deterministic archive packaging helpers and checksum manifest generation.
- [x] Task: Add source coverage, completeness reconciliation, tombstone, and quality regression evidence.
- [x] Task: Add legal/privacy/provenance ledger generation.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Archive Packaging, Coverage, And Quality Gates' (Protocol in workflow.md)

## Phase 4: Metadata And Discovery Surfaces

- [x] Task: Generate Croissant, RO-Crate, Frictionless, DCAT, PROV-O, DataCite, schema.org Dataset JSON-LD, and Hugging Face dataset-card metadata.
- [x] Task: Add metadata package manifest checksums.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Metadata And Discovery Surfaces' (Protocol in workflow.md)

## Phase 5: Public Surface, Legal, And Privacy Governance

- [x] Task: Add public surface audit evidence for GitHub, Hugging Face, Zenodo, OSF, and future metadata endpoints.
- [x] Task: Add citation, DOI, takedown, rollback, retry, privacy, and de-anonymisation caveat documentation.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Public Surface, Legal, And Privacy Governance' (Protocol in workflow.md)

## Phase 6: Security, Supply Chain, And Provenance

- [x] Task: Add security and quality workflow scaffolding for CodeQL, Scorecard, OSV scanning, workflow linting, and release checks.
- [x] Task: Add SBOM generation, artifact attestation wiring, and no-publish dependency-update guards.
- [x] Task: Tighten Renovate publication-path automerge rules.
- [x] Task: Conductor - User Manual Verification 'Phase 6: Security, Supply Chain, And Provenance' (Protocol in workflow.md)

## Phase 7: Monthly Publication Workflow

- [x] Task: Add monthly/manual GitHub Actions workflow for Hugging Face publication, Zenodo draft/new-version upload, GitHub release artifact creation, remote manifest verification, and observability artifacts.
- [x] Task: Keep Zenodo production publication as protected handoff-only.
- [x] Task: Conductor - User Manual Verification 'Phase 7: Monthly Publication Workflow' (Protocol in workflow.md)

## Phase 8: Verification And First Release Proof

- [x] Task: Run the complete local validation suite after implementation.
- [x] Task: Execute a GitHub Actions dry run and capture no-secret failure behavior.
    - Evidence: corrected dry-run `https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/runs/28557667012` succeeded in `dry-run` mode with `quality.record_count=5`, `collection_quality_gates.status=pass`, HF dry-run evidence, Zenodo dry-run evidence, artifact upload, and attestation. Initial run `28557593684` exposed a zero-record release-evidence ordering defect, fixed by commit `21968e6`. GitHub issue evidence: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861228232`.
- [ ] Task: Execute approved Hugging Face publication and verify the remote manifest from a fresh snapshot.
- [ ] Task: Execute approved Zenodo draft/new-version upload and capture draft evidence.
- [ ] Task: Route production Zenodo publication through the protected environment after human approval.
- [ ] Task: Conductor - User Manual Verification 'Phase 8: Verification And First Release Proof' (Protocol in workflow.md)
