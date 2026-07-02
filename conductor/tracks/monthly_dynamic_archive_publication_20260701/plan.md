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
- [x] Task: Execute approved Hugging Face publication and verify the remote manifest from a fresh snapshot.
    - Evidence: live workflow run `https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/runs/28557778268` succeeded in `huggingface` mode. Downloaded artifact evidence reports `dry_run=false`, HF repo `edithatogo/corpus-cases-medilegal-nz`, revision `73b7b10889bc43ce013ffe1d5e3ba66a0cb352c2`, path `releases/2026.07.0`, `remote_manifest_verified=true`, `quality.record_count=5`, and `collection_quality_gates.status=pass`. GitHub release `https://github.com/edithatogo/corpus-cases-medilegal-nz/releases/tag/dataset-v2026.07.0` was created with expected assets. GitHub issue evidence: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861246629`.
- [x] Task: Execute approved Zenodo draft/new-version upload and capture draft evidence.
    - Evidence: live workflow run `https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/runs/28557891130` succeeded in `zenodo-draft` mode. Downloaded artifact evidence reports `dry_run=false`, `uploaded=true`, deposition id `21119990`, record URL `https://zenodo.org/deposit/21119990`, 9 upload files, 9 uploaded files, `publish_handoff_only=true`, `quality.record_count=5`, and `collection_quality_gates.status=pass`. DOI and concept DOI remain empty because production publication has not been approved or executed. GitHub issue evidence: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861258383`.
- [x] Task: Route production Zenodo publication through the protected environment after human approval.
    - Evidence: full workflow run `https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/runs/28558066846` succeeded in `full` mode and executed the `Protected Zenodo Publish Handoff` job. The job logs state that the Zenodo draft upload is complete, production DOI publication remains a human-approved protected-environment action, and `zenodo_draft_evidence.json` must be reviewed before publishing from Zenodo. Downloaded evidence reports HF revision `154f2e06336b4a77839eb3ec23252d86cfa53e2b`, remote manifest verification `true`, Zenodo deposition `21119990`, 9 uploaded files, `publish_handoff_only=true`, and empty DOI/concept DOI fields. GitHub issue evidence: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861278867`.
- [x] Task: Conductor - User Manual Verification 'Phase 8: Verification And First Release Proof' (Protocol in workflow.md)
    - Evidence: final review verified local tests (`18 passed`), Ruff checks, corrected dry-run proof, live Hugging Face publication/readback proof, Zenodo draft upload proof, GitHub release assets, artifact attestations, and protected Zenodo handoff evidence. Production DOI publication remains intentionally manual after Zenodo draft review.
