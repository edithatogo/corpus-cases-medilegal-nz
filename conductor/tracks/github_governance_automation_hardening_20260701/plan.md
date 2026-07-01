# Implementation Plan: GitHub Governance And Automation Hardening

## Phase 1: Governance Baseline

- [ ] Task: Capture current repository security and governance settings.
    - [ ] Branch protection and rulesets.
    - [ ] Actions permissions and allowed actions.
    - [ ] Environments and protected reviewers.
    - [ ] Vulnerability alerts and dependency graph state.
    - [ ] Secret and variable presence.
- [ ] Task: Document gaps against the archive-family publication contract.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Governance Baseline' (Protocol in workflow.md)

## Phase 2: Protected Publication Controls

- [ ] Task: Configure or document creation of `zenodo-production`.
    - [ ] Require reviewer approval.
    - [ ] Confirm workflow handoff uses the protected environment.
    - [ ] Add readiness detection for missing environment.
- [ ] Task: Align publication secrets and variables.
    - [ ] Add readiness checks for canonical names.
    - [ ] Document migration from legacy names.
    - [ ] Avoid printing secret values.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Protected Publication Controls' (Protocol in workflow.md)

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
