# Specification - Monthly Dynamic Archive Publication

## Overview

Implement monthly dynamically versioned archive publication for
`corpus-cases-medilegal-nz`, aligned with the parallel archive patterns used by
`corpus-nz-hansard`, `corpus-law-nz`, and `fyi-archive`.

GitHub remains the code and evidence surface, Hugging Face remains the mutable
live dataset surface, and Zenodo becomes the immutable DOI snapshot surface.
Publication must be manifest-first, draft-first for Zenodo, evidence-backed,
protected for production DOI publication, and verified after remote upload.

## Requirements

- Use dataset/archive versions in the form `YYYY.MM.0`, with GitHub release tags
  named `dataset-vYYYY.MM.0`.
- Keep package version, dataset version, schema version, Hugging Face revision,
  Zenodo DOI/version DOI, GitHub release tag, manifest hash, and release
  evidence hash as separate checked authorities.
- Add monthly and manual GitHub Actions automation for archive rebuilds,
  Hugging Face publication, Zenodo draft/new-version upload, GitHub release
  artifact publication, remote manifest verification, and protected Zenodo
  publish handoff.
- Generate machine-readable release evidence, source coverage, public surface
  audit, metadata package, schema, SBOM, legal/provenance, and dataset quality
  artifacts.
- Keep OSF inactive unless a later dedicated mirror policy activates it.
- Ensure dependency-update contexts and untrusted pull requests cannot publish to
  Hugging Face, Zenodo, or GitHub Releases.

## Archive-Family Alignment

- Follow the corpus-law ADR convention: GitHub for source and lightweight
  release assets, Hugging Face/Xet for live operational data, Zenodo for
  immutable DOI snapshots, OSF optional only.
- Follow the Hansard monthly workflow convention: monthly/manual archive rebuild,
  staged Hugging Face upload, Zenodo draft/new-version upload, protected Zenodo
  publish handoff, release evidence manifest, and artifact attestation.
- Follow fyi-archive's mirror-verification convention: publish adapters emit
  remote artifact evidence and verify the uploaded manifest from the remote
  surface after publication.
- Prefer shared names for secrets and variables: `HF_TOKEN`, `HF_REPO_ID`,
  `ZENODO_ACCESS_TOKEN`, `ZENODO_SANDBOX_ACCESS_TOKEN`, `ZENODO_API_URL`,
  `ZENODO_SANDBOX_API_URL`, and `ARCHIVE_CREATORS_JSON`.

## Acceptance Criteria

- New Conductor track artifacts exist and the track is registered.
- Release tooling can generate release evidence, metadata packages, source
  coverage, quality gates, public-surface audit, SBOM, and Zenodo metadata
  locally without external credentials.
- Monthly publication workflow exists, has least-privilege permissions, includes
  artifact attestation permissions, and blocks dependency-update publication.
- Code quality/security workflows exist for tests, Ruff, workflow linting,
  CodeQL, OpenSSF Scorecard, and OSV scanning.
- Renovate cannot automerge changes to publication workflows, release scripts,
  schemas, or metadata generators.
- Focused tests validate the versioning, evidence, metadata, workflow, and
  publication-safety contracts.
- Live proof remains pending until the required GitHub, Hugging Face, and Zenodo
  credentials/environments are configured and explicitly approved.

## Out Of Scope

- Activating secondary Git remotes; that remains in
  `multi_git_archive_mirroring_20260614`.
- Publishing production Zenodo DOI records without protected approval.
- Claiming complete New Zealand medicolegal coverage before source-specific
  reconciliation evidence exists.
- Publishing experimental endpoint artifacts as canonical releases before a
  later promotion track.
