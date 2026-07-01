# Specification: GitHub Governance And Automation Hardening

## Overview

Harden GitHub repository governance and automation so the monthly archive publication system is protected by modern GitHub security, release, and policy controls rather than relying only on workflow-level checks.

## Current State

- Workflows are active for tests, docs, mirror sync, multi-source sync, monthly publication, CodeQL, OSV, Scorecard, and quality hardening.
- The monthly publication workflow uses artifact attestations and protected-environment references.
- No `zenodo-production` environment was visible from the API.
- `master` is not branch-protected.
- Repository Actions allow all actions and do not require SHA pinning.
- Vulnerability alerts are disabled.
- Publication secret names are not fully aligned with the hardened contract.

## Requirements

- Configure a protected `zenodo-production` environment or documented repo-specific alias.
- Require approval before any production DOI publication handoff.
- Add branch protection or repository rulesets for `master`.
- Require current CI checks before merge or protected updates.
- Enable Dependabot alerts and vulnerability visibility.
- Add Dependency Review for pull requests where available.
- Align repository secrets and variables with the archive-family contract:
  - `HF_TOKEN`
  - `HF_REPO_ID`
  - `ZENODO_ACCESS_TOKEN`
  - `ZENODO_SANDBOX_ACCESS_TOKEN`
  - `ZENODO_API_URL`
  - `ZENODO_SANDBOX_API_URL`
  - `ARCHIVE_CREATORS_JSON`
  - `ZENODO_PROTECTED_ENVIRONMENT`
- Preserve compatibility with legacy secret names only through documented migration or fallback behavior.
- Restrict publication workflows from untrusted events and dependency-update actors.
- Move report-only checks to gating once baseline debt is resolved.
- Add evidence that artifact attestations are created and verifiable.

## Non-Functional Requirements

- Governance changes must be auditable and reversible.
- Protected publication must fail closed when required secrets, variables, or environments are absent.
- Workflows must use least-privilege permissions.
- Security hardening must remain compatible with sibling repository conventions.

## Acceptance Criteria

- `zenodo-production` or the configured alias exists and has required reviewers.
- `master` has protection or a ruleset requiring green checks.
- Vulnerability alerts are enabled or a documented account/plan limitation exists.
- Publication readiness checks detect missing repo secrets, vars, environments, and branch protections.
- Dependency Review, CodeQL, OSV, Scorecard, actionlint, Zizmor, typos, and Taplo are represented in CI with explicit gating/reporting status.
- Release artifacts have attestation verification documented and tested.

## Out Of Scope

- Publishing a production DOI.
- Rotating actual secret values unless explicitly requested.
- Migrating away from `uv.lock`.
- Enforcing organization-wide policies outside this repository.
