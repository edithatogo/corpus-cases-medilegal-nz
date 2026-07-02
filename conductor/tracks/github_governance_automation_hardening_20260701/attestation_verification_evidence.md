# Phase 5 Attestation Verification Evidence

Date: 2026-07-02

## Implemented Contract

- Release evidence now includes required `attestation_verification` metadata.
- A standalone `manifests/attestation_verification.json` sidecar is generated with release artifacts.
- The contract records:
  - GitHub artifact attestation provider.
  - SHA-pinned `actions/attest-build-provenance` action reference.
  - Publication workflow path.
  - Attested subject globs.
  - Required GitHub release asset names.
  - `gh attestation verify` commands for each expected release asset.
- Release evidence validation fails when attestation metadata is missing, uses a non-GitHub provider, uses an unpinned action reference, or omits subject paths, required release assets, or verification commands.

## Validation Evidence

- `uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_release.py -q`
  - Result: `15 passed`
- `uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_release.py tests/test_monthly_publication_workflow.py tests/test_publication_adapters.py -q`
  - Result: `19 passed`
- `uv run --frozen --python 3.12 --extra dev ruff format --check src\corpus_cases_medilegal_nz\archive.py tests\test_archive_release.py`
  - Result: `2 files already formatted`
- `uv run --frozen --python 3.12 --extra dev ruff check src\corpus_cases_medilegal_nz\archive.py tests\test_archive_release.py`
  - Result: `All checks passed`
- `uv run --frozen --python 3.12 --extra dev python scripts\build_release_evidence.py --output-dir generated\monthly-publication --archive-version 2026.07.0`
  - Result: generated `manifests/attestation_verification.json` and included it in the checksum manifest.
- `uv run --frozen --python 3.12 --extra dev python scripts\check_release_evidence.py --require-file`
  - Result: `Release evidence checks passed.`

## Boundary

This phase records and validates the expected attestation verification contract before publication. Live `gh attestation verify` readback requires GitHub-created attestations for uploaded release assets and remains part of the first governance proof/live publication verification phase.
