# Phase 4 Supply Chain Enforcement Evidence

Captured: 2026-07-02

## Dependency Review

Added workflow:

- `.github/workflows/dependency_review.yml`
- Trigger: `pull_request`
- Required permissions:
  - `contents: read`
  - `pull-requests: read`
- Action:
  - `actions/dependency-review-action@a1d282b36b6f3519aa1f3fc636f609c47dddb294`
  - Release tag: `v5.0.0`
- Policy:
  - Fails on high-severity vulnerabilities.
  - Enables vulnerability and license checks.

## Publication Workflow Action Pinning

Pinned monthly publication workflow actions to immutable SHAs:

- `actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10` (`v6`)
- `astral-sh/setup-uv@94527f2e458b27549849d47d273a16bec83a01e9` (`v7`)
- `actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1` (`v6`)
- `actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4` (`v5`)
- `actions/attest-build-provenance@43d14bc2b83dec42d39ecae14e916627a18bb661` (`v3`)

Scope:

- Publication workflow is SHA-pinned first because it has write permissions,
  external publication side effects, artifact attestations, and release upload
  authority.
- Remaining non-publication workflows keep Zizmor report-only evidence until
  their pinning debt is remediated.

## Renovate Policy

Updated `renovate.json` so GitHub Actions updates require review:

- GitHub Actions updates no longer automerge.
- Dependency Dashboard approval is required.
- Publication/release evidence paths already required human review.

## Report-Only Baseline

Code quality workflow now uploads `zizmor-report` as an artifact and exits the
Zizmor step successfully. This preserves evidence while preventing known
baseline pinning debt from blocking unrelated governance fixes.

Typos and Taplo remain report-only until baseline debt and runtime cost are
separately reviewed.
