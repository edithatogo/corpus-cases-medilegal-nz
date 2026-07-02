# Implementation Plan: GitHub Governance And Automation Hardening

## Phase 1: Governance Baseline

- [x] Task: Capture current repository security and governance settings.
    - [x] Branch protection and rulesets.
    - [x] Actions permissions and allowed actions.
    - [x] Environments and protected reviewers.
    - [x] Vulnerability alerts and dependency graph state.
    - [x] Secret and variable presence.
    - Evidence: `governance_baseline_evidence.md` records live `gh api` results for repository visibility, default branch, branch protection, rulesets, Actions policy, environments, vulnerability alerts, Dependabot alerts, secrets, variables, and workflow surface.
- [x] Task: Document gaps against the archive-family publication contract.
    - Evidence: `governance_baseline_evidence.md` identifies missing master protection/rulesets, missing environment reviewer protection, disabled vulnerability/Dependabot alerts, unpinned/all-allowed Actions policy, canonical secret/variable gaps, and the need to triage one recent failed workflow before strict gating.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Governance Baseline' (Protocol in workflow.md)
    - Evidence: live audit commands completed and produced a durable Phase 1 baseline; no repository settings were changed in Phase 1.

## Phase 2: Protected Publication Controls

- [x] Task: Configure or document creation of `zenodo-production`.
    - [x] Require reviewer approval.
    - [x] Confirm workflow handoff uses the protected environment.
    - [x] Add readiness detection for missing environment.
    - Evidence: GitHub environment `zenodo-production` now requires reviewer `edithatogo`, disables admin bypass, and the full publication workflow has already exercised `Protected Zenodo Publish Handoff`. `publication_readiness` now detects supplied GitHub environment/protection observations via `GITHUB_ENVIRONMENT_NAMES` and `GITHUB_PROTECTED_ENVIRONMENT_NAMES`.
- [x] Task: Align publication secrets and variables.
    - [x] Add readiness checks for canonical names.
    - [x] Document migration from legacy names.
    - [x] Avoid printing secret values.
    - Evidence: readiness checks preserve canonical names, accept documented `ZENODO_TOKEN`/`ZENODO_SANDBOX_TOKEN` aliases, expose only configured names rather than values, and docs explain the alias migration path.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Protected Publication Controls' (Protocol in workflow.md)
    - Evidence: focused tests cover protected environment readiness states and Zenodo secret aliases; docs now state protected-environment and alias policy.

## Phase 3: Branch And Ruleset Protection

- [ ] Task: Add branch protection or ruleset requirements for `master`.
    - [ ] Require Tests.
    - [ ] Require Code Quality And Workflow Hardening.
    - [ ] Require CodeQL.
    - [ ] Require OSV Scan.
    - [ ] Require Docs where relevant.
- [ ] Task: Confirm dependency-update actors cannot publish.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Branch And Ruleset Protection' (Protocol in workflow.md)

## Phase 4: Supply Chain Enforcement

- [ ] Task: Add Dependency Review workflow for pull requests.
- [ ] Task: Decide and implement action pinning policy.
    - [ ] Prefer SHA pinning for publication workflows.
    - [ ] Document Renovate update review requirements.
- [ ] Task: Move report-only checks to gating where baseline debt allows.
    - [ ] Typos.
    - [ ] Taplo.
    - [ ] Zizmor.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Supply Chain Enforcement' (Protocol in workflow.md)

## Phase 5: Attestation Verification

- [ ] Task: Add artifact attestation verification to release-readiness checks.
- [ ] Task: Record attestation verification evidence in release evidence.
- [ ] Task: Add tests for missing/invalid attestation metadata.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Attestation Verification' (Protocol in workflow.md)

## Phase 6: Documentation And First Governance Proof

- [ ] Task: Update governance documentation.
- [ ] Task: Run publication-readiness/doctor checks against live GitHub settings.
- [ ] Task: Attach governance proof to the GitHub issue/project.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Documentation And First Governance Proof' (Protocol in workflow.md)
