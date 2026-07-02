# Monthly Dynamic Archive Publication

This repository follows the same publication contract used by the parallel New
Zealand legal archive repositories:

- GitHub is the code, workflow, and lightweight release-evidence surface.
- Hugging Face Datasets is the live mutable operational dataset surface.
- Zenodo is the immutable DOI snapshot surface.
- OSF is inactive until a dedicated mirror activation track defines its policy.

The active Conductor track is
`monthly_dynamic_archive_publication_20260701`.

## Versioning

Dataset/archive versions use `YYYY.MM.0`. GitHub release tags use
`dataset-vYYYY.MM.0`. The Python package version remains independent from the
dataset/archive version.

Example:

```text
Archive version: 2026.07.0
GitHub tag:      dataset-v2026.07.0
HF path:         releases/2026.07.0/
```

## Required Secrets And Variables

Use the same names as the sibling archive family where practical:

- `HF_TOKEN`: Hugging Face token with write access to the dataset repository.
- `HF_REPO_ID`: Hugging Face dataset repository id. Defaults to
  `edithatogo/corpus-cases-medilegal-nz`.
- `ZENODO_ACCESS_TOKEN`: Zenodo production API token.
- `ZENODO_SANDBOX_ACCESS_TOKEN`: Zenodo sandbox API token for rehearsal.
- `ZENODO_API_URL`: production API URL. Defaults to `https://zenodo.org/api`.
- `ZENODO_SANDBOX_API_URL`: sandbox API URL.
- `ARCHIVE_CREATORS_JSON`: Zenodo creators JSON array.
- `ZENODO_PROTECTED_ENVIRONMENT`: optional GitHub environment name for the
  protected publish handoff. Defaults to `zenodo-production`.

If this repository uses a local alias such as `zenodo-production-publish`, set
`ZENODO_PROTECTED_ENVIRONMENT` to that name and keep the protection rules on
that environment.

During migration, this repository also accepts the legacy secret aliases
`ZENODO_TOKEN` and `ZENODO_SANDBOX_TOKEN` as fallbacks for the canonical
`ZENODO_ACCESS_TOKEN` and `ZENODO_SANDBOX_ACCESS_TOKEN` names. New repositories
should use the canonical names.

`publication-readiness` can also consume live GitHub governance evidence through
comma-separated environment variables:

- `GITHUB_ENVIRONMENT_NAMES`: observed GitHub environment names.
- `GITHUB_PROTECTED_ENVIRONMENT_NAMES`: observed environments with reviewer or
  equivalent protection.

When these are supplied, the readiness report fails closed if the configured
Zenodo protected environment is missing or unprotected.

## Release Evidence

Each release build writes deterministic artifacts under
`generated/monthly-publication/`:

- `manifests/release_evidence.json`
- `manifests/source_coverage.json`
- `manifests/dataset_quality.json`
- `manifests/dataset_diff.json`
- `manifests/public_surface_audit.json`
- `manifests/legal_provenance.json`
- `manifests/release_ladder.json`
- `manifests/attestation_verification.json`
- `manifests/checksum_manifest.json`
- `manifests/zenodo-metadata.json`
- `metadata/metadata_packages_manifest.json`
- `sbom/sbom.cyclonedx.json`
- `sbom/sbom.spdx.json`
- `SHA256SUMS`

The publication workflow also writes the archive-intelligence bundle under
`generated/archive-intelligence/`:

- `archive_maturity.json`
- `source_observability.json`
- `privacy_rights_score.json`
- `anomaly_report.json`
- `public_claims.json`
- `federation_compatibility.json`
- `README.claims.md`
- `dataset-card.claims.md`
- `release-notes.claims.md`
- `github-project-summary.claims.md`

The public claims in README files, release notes, and dataset cards must be
derived from these generated ledgers. Do not hand-maintain stronger coverage,
rights, privacy, DOI, or mirror claims than the evidence supports.

`release_evidence.json` also records the expected artifact-attestation
verification contract. The attestation evidence names the GitHub artifact
attestation provider, the SHA-pinned `actions/attest-build-provenance` action,
the attested artifact globs, the expected GitHub release assets, and the
`gh attestation verify` commands to run after GitHub has created attestations
for uploaded assets.

## Governance Gates

The publication path is protected by repository governance as well as workflow
checks:

- `master` requires strict status checks for the Python test matrix, code
  quality/evidence checks, CodeQL, OSV scanning, and docs.
- Force pushes and branch deletion are disabled for `master`.
- The monthly publication workflow uses least-privilege permissions, explicit
  dependency-update actor guards, SHA-pinned third-party actions on the
  publication path, and GitHub artifact attestations.
- `zenodo-production` is the default protected environment for production DOI
  handoff. It must require reviewer approval and must not allow admin bypass.
- Dependency Review runs on pull requests, while Renovate GitHub Actions updates
  require human review and Dependency Dashboard approval.

The live governance proof for this repository is recorded in
`conductor/tracks/github_governance_automation_hardening_20260701/`.

## Publication Workflow

`.github/workflows/monthly_dynamic_archive_publication.yml` runs monthly and by
manual dispatch. It supports these modes:

- `dry-run`: build and validate local release artifacts without network writes.
- `huggingface`: publish versioned artifacts to Hugging Face and verify the
  uploaded manifest from a fresh snapshot.
- `zenodo-draft`: create or update a Zenodo draft/new-version, upload release
  files, and record draft evidence without publishing.
- `full`: run Hugging Face publication, Zenodo draft upload, GitHub release
  asset upload, and protected Zenodo publish handoff.

Scheduled runs default to the draft-first path. Production Zenodo DOI
publication is not automatic. It must pass through the configured protected
GitHub environment and human review before any Zenodo publish action is taken.
The `zenodo-production` environment should require reviewer approval and should
not allow admin bypass for production DOI handoff runs.

The monthly publication workflow pins third-party GitHub Actions to immutable
commit SHAs. Renovate may propose action updates, but GitHub Actions updates
require human review and must not automerge.

## Local Commands

Build release artifacts:

```bash
python scripts/build_release_evidence.py --output-dir generated/monthly-publication
```

Build the archive-intelligence bundle:

```bash
python scripts/build_archive_intelligence_bundle.py \
  --artifact-dir generated/monthly-publication \
  --output-dir generated/archive-intelligence
```

Run readiness checks:

```bash
python -m corpus_cases_medilegal_nz.cli publication-readiness
python -m corpus_cases_medilegal_nz.cli publication-readiness --strict
python scripts/check_release_evidence.py --require-file
python scripts/check_metadata_packages.py --require-file
python scripts/check_public_surface_audit.py --require-file
```

Create dry-run publication evidence:

```bash
python scripts/publish_huggingface_release.py \
  --artifact-dir generated/monthly-publication \
  --archive-version 2026.07.0 \
  --dry-run
```

```bash
python scripts/publish_zenodo_draft.py \
  --artifact-dir generated/monthly-publication \
  --bundle generated/monthly-publication-bundles/corpus-cases-medilegal-nz-2026.07.0.tar.gz \
  --archive-version 2026.07.0 \
  --dry-run
```

## Rollback And Retry

- Hugging Face writes are versioned under `releases/<archive_version>/`.
  Re-running the same version overwrites that versioned path with a new commit
  and then verifies the uploaded manifest hash.
- Zenodo writes are draft-only from automation. If upload validation fails,
  delete or correct the draft in Zenodo, then re-run `zenodo-draft`.
- GitHub release asset upload is idempotent with `--clobber`.
- Never publish a Zenodo production DOI from a dependency-update run or an
  unreviewed workflow change.

## Legal And Privacy Boundary

The source material is public-facing, but redistribution, privacy, and
de-anonymisation claims are source-specific. Release evidence therefore records:

- source terms and redistribution review status;
- attribution and known exclusions;
- takedown contact route;
- de-anonymisation caveats;
- public surface status for GitHub, Hugging Face, Zenodo, and OSF.

Any correction request should be handled by opening a tracked issue, updating
the source coverage or legal provenance ledger, and issuing a new monthly
archive version if published artifacts need to change.
