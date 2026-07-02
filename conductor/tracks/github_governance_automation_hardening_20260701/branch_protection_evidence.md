# Phase 3 Branch Protection Evidence

Captured: 2026-07-02

## Master Branch Protection

Live command:

```powershell
gh api --method PUT repos/edithatogo/corpus-cases-medilegal-nz/branches/master/protection --input .tmp/branch-protection.json
gh api repos/edithatogo/corpus-cases-medilegal-nz/branches/master/protection
```

Result:

- Branch: `master`
- Required status checks strict mode: `true`
- Required checks:
  - `tests (3.12)`
  - `tests (3.14)`
  - `Python, Evidence, And Workflow Checks`
  - `Analyze Python`
  - `OSV Scanner`
  - `Astro docs`
- Enforce admins: `false`
- Allow force pushes: `false`
- Allow deletions: `false`

## Check Selection Rationale

- `tests (3.12)` and `tests (3.14)` protect the supported Python matrix.
- `Python, Evidence, And Workflow Checks` gates Ruff, release evidence, metadata
  checks, public surface audit, publication readiness, actionlint, and
  report-only Zizmor evidence.
- `Analyze Python` gates CodeQL.
- `OSV Scanner` gates dependency vulnerability scanning.
- `Astro docs` gates documentation builds.

`mirror` is intentionally not required because mirror transport is not part of
source, evidence, or release correctness and can be independently retried.

## Dependency-Update Publication Guard

The monthly publication workflow and code quality workflow retain explicit
dependency-update actor guards:

- `github.actor != 'dependabot[bot]'`
- `github.actor != 'renovate[bot]'`
- `Dependency Update Publication Guard`

Publication remains disallowed from dependency-update actors.
