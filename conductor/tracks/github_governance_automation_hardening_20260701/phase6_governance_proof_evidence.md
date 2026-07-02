# Phase 6 Governance Proof Evidence

Captured: 2026-07-02

## Documentation

Updated `docs/monthly-dynamic-archive-publication.md` to document:

- `manifests/attestation_verification.json`.
- The release evidence attestation verification contract.
- Branch protection and required checks.
- Protected `zenodo-production` handoff governance.
- Dependency Review, Renovate review requirements, and publication action pinning.
- Strict publication-readiness command usage.

## Live GitHub Environment Proof

Command:

```powershell
gh api repos/edithatogo/corpus-cases-medilegal-nz/environments
```

Observed:

- Environment count: 1
- Environment: `zenodo-production`
- `can_admins_bypass`: `false`
- Protection rule: `required_reviewers`
- Required reviewer: `edithatogo`

## Live Branch Protection Proof

Command:

```powershell
gh api repos/edithatogo/corpus-cases-medilegal-nz/branches/master/protection
```

Observed:

- Required status checks strict mode: `true`
- Required checks:
  - `tests (3.12)`
  - `tests (3.14)`
  - `Python, Evidence, And Workflow Checks`
  - `Analyze Python`
  - `OSV Scanner`
  - `Astro docs`
- `allow_force_pushes.enabled`: `false`
- `allow_deletions.enabled`: `false`
- `enforce_admins.enabled`: `false`

`enforce_admins` remains disabled so repository administrators can bypass after explicit acknowledgement. Pushes still report all required checks as expected and the checks run after push.

## Secret And Variable Surface

Commands:

```powershell
gh secret list --repo edithatogo/corpus-cases-medilegal-nz
gh variable list --repo edithatogo/corpus-cases-medilegal-nz
```

Observed configured secret names only:

- `HF_TOKEN`
- `OSF_TOKEN`
- `ZENODO_SANDBOX_TOKEN`
- `ZENODO_TOKEN`

Observed variable names:

- `OSF_PROJECT_ID`

No secret values were read or printed. The current repository still uses legacy Zenodo token names. The readiness checker accepts `ZENODO_TOKEN` and `ZENODO_SANDBOX_TOKEN` as documented aliases for `ZENODO_ACCESS_TOKEN` and `ZENODO_SANDBOX_ACCESS_TOKEN`.

## Strict Publication-Readiness Proof

Command:

```powershell
$env:GITHUB_ENVIRONMENT_NAMES='zenodo-production'
$env:GITHUB_PROTECTED_ENVIRONMENT_NAMES='zenodo-production'
$env:HF_TOKEN='configured-in-github'
$env:ZENODO_TOKEN='configured-in-github'
$env:ZENODO_SANDBOX_TOKEN='configured-in-github'
uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli publication-readiness --strict
```

Result:

- `status`: `ready`
- `blockers`: `[]`
- Protected environment: `zenodo-production`
- `HF_TOKEN`: configured
- `ZENODO_ACCESS_TOKEN`: configured through `ZENODO_TOKEN`
- `ZENODO_SANDBOX_ACCESS_TOKEN`: configured through `ZENODO_SANDBOX_TOKEN`
- `github_environment:zenodo-production`: configured
- `github_environment_protection:zenodo-production`: configured

Gated external writes remain recorded for optional/defaulted values:

- `HF_REPO_ID`
- `ZENODO_API_URL`
- `ZENODO_SANDBOX_API_URL`
- `ARCHIVE_CREATORS_JSON`

These are not blockers because defaults or runtime metadata are accepted by the current publication tooling. Production DOI publication remains protected and manual.

## Latest Protected Check Proof

Latest pushed governance commit before this phase:

- Commit: `365cf86 feat: add attestation verification evidence`

GitHub Actions result:

- `Tests`: success
- `Code Quality And Workflow Hardening`: success
- `CodeQL`: success
- `OSV Scan`: success
- `Docs`: success
- `Mirror Sync`: success

## GitHub Issue And Project Evidence

Issue `#1` is linked to both:

- `Rare Insights on Open Policy from Aotearoa`
- `corpus-cases-medilegal-nz Archive Roadmap`

Phase 6 proof should be attached to issue `#1` as the shared project-linked evidence anchor.

Posted proof:

- `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861714999`

Verified project item status after update:

- `Rare Insights on Open Policy from Aotearoa`: `Done`
- `corpus-cases-medilegal-nz Archive Roadmap`: `Done`

## Local Validation

- `uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli publication-readiness --strict`
  - Result: `status: ready`, `blockers: []`
- `uv run --frozen --python 3.12 --extra dev python scripts\check_release_evidence.py --require-file`
  - Result: `Release evidence checks passed.`
- `uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_release.py tests/test_monthly_publication_workflow.py tests/test_publication_adapters.py -q`
  - Result: `19 passed`
- `git diff --check` for the touched documentation and Conductor files
  - Result: passed

Attempted docs build:

- `npm run docs:build`
  - Result: local command could not run because `docs-site/node_modules` is absent and `astro` is not installed in this checkout. The protected GitHub `Docs` workflow remains the authoritative docs-build validation after push.
