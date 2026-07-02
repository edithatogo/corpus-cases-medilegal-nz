# Phase 1 Governance Baseline Evidence

Captured: 2026-07-02

## Repository

- Repository: `edithatogo/corpus-cases-medilegal-nz`
- URL: `https://github.com/edithatogo/corpus-cases-medilegal-nz`
- Visibility: `PUBLIC`
- Default branch: `master`
- Current viewer permission: `ADMIN`

## Branch Protection And Rulesets

Live checks:

```powershell
gh api repos/edithatogo/corpus-cases-medilegal-nz/branches/master/protection
gh api repos/edithatogo/corpus-cases-medilegal-nz/rulesets
```

Result:

- `master` branch protection: not configured (`Branch not protected`, HTTP 404).
- Repository rulesets: empty list.

Gap:

- `master` is not protected by branch protection or repository rulesets.
- Required status checks are not enforced at the repository governance layer.

## Actions Permissions

Live check:

```powershell
gh api repos/edithatogo/corpus-cases-medilegal-nz/actions/permissions
```

Result:

- Actions enabled: `true`
- Allowed actions: `all`
- SHA pinning required: `false`

Gap:

- Actions are not restricted to pinned or explicitly allowed actions.
- This is acceptable as an audit baseline only; publication workflows still use
  local guards and least-privilege permissions, but repository policy does not
  enforce action pinning.

## Environments

Live check:

```powershell
gh api repos/edithatogo/corpus-cases-medilegal-nz/environments
```

Result:

- Environment exists: `zenodo-production`
- Created: `2026-07-02T01:02:35Z`
- Initial baseline protection rules: none
- Initial baseline admin bypass: `true`

Phase 2 update:

- Updated: `2026-07-02T01:10:19Z`
- Required reviewer: `edithatogo`
- Reviewer id: `15080672`
- Admin bypass: `false`
- Protection rule type: `required_reviewers`

Gap:

- The protected handoff environment existed without reviewer approval at the
  Phase 1 baseline.
- Phase 2 tightened the environment with required reviewer approval and no admin
  bypass.

## Vulnerability And Dependabot Alerts

Live checks:

```powershell
gh api repos/edithatogo/corpus-cases-medilegal-nz/vulnerability-alerts -i
gh api repos/edithatogo/corpus-cases-medilegal-nz/dependabot/alerts?per_page=1 -i
```

Result:

- Vulnerability alerts: disabled (`Vulnerability alerts are disabled`, HTTP 404).
- Dependabot alerts: disabled (`Dependabot alerts are disabled for this repository`, HTTP 403).

Gap:

- Vulnerability alerting and Dependabot alert visibility are not enabled.

## Secrets And Variables

Live checks:

```powershell
gh secret list --json name,updatedAt
gh variable list --json name,updatedAt,value
```

Configured secrets:

- `HF_TOKEN`
- `OSF_TOKEN`
- `ZENODO_SANDBOX_TOKEN`
- `ZENODO_TOKEN`

Configured variables:

- `OSF_PROJECT_ID`

Gaps against canonical archive-family names:

- Missing variable: `HF_REPO_ID`
- Missing secret or variable: `ZENODO_ACCESS_TOKEN`
- Missing secret or variable: `ZENODO_SANDBOX_ACCESS_TOKEN`
- Missing variable: `ZENODO_API_URL`
- Missing variable: `ZENODO_SANDBOX_API_URL`
- Missing secret: `ARCHIVE_CREATORS_JSON`
- Missing variable: `ZENODO_PROTECTED_ENVIRONMENT`

Compatibility note:

- The monthly workflow now accepts `ZENODO_TOKEN` as a legacy alias for
  `ZENODO_ACCESS_TOKEN`.
- The monthly workflow preserves canonical names for future alignment.

## Workflow Surface

Active workflows:

- `Code Quality And Workflow Hardening`
- `CodeQL`
- `Docs`
- `Mirror Sync`
- `Monthly Dynamic Archive Publication`
- `Multi-Source Daily Sync`
- `OSV Scan`
- `OpenSSF Scorecard`
- `Tests`
- `Dependency Graph`

Recent workflow state:

- Recent monthly publication dry-run, Hugging Face, Zenodo draft, and full
  protected-handoff runs completed successfully.
- One recent push workflow failure remains visible in the latest run list and
  should be triaged before enabling strict branch protection.

## Gap Summary

- Add branch protection or repository rulesets for `master`.
- Require selected CI checks before merge or protected updates.
- Add required reviewers to `zenodo-production`.
- Enable vulnerability alerts and Dependabot alerts.
- Decide action pinning policy and either enforce repository policy or document
  controlled exceptions.
- Align canonical publication secrets/variables while preserving documented
  legacy aliases during migration.
