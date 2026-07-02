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

- [x] Task: Add branch protection or ruleset requirements for `master`.
    - [x] Require Tests.
    - [x] Require Code Quality And Workflow Hardening.
    - [x] Require CodeQL.
    - [x] Require OSV Scan.
    - [x] Require Docs where relevant.
    - Evidence: `branch_protection_evidence.md` records live `master` branch protection with strict required checks for `tests (3.12)`, `tests (3.14)`, `Python, Evidence, And Workflow Checks`, `Analyze Python`, `OSV Scanner`, and `Astro docs`; force pushes and deletions are disabled.
- [x] Task: Confirm dependency-update actors cannot publish.
    - Evidence: monthly publication workflow retains dependency actor guards for Dependabot and Renovate; `Dependency Update Publication Guard` remains represented in the code quality workflow.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Branch And Ruleset Protection' (Protocol in workflow.md)
    - Evidence: latest candidate checks were green before protection was applied; live branch protection readback confirms required contexts.

## Phase 4: Supply Chain Enforcement

- [x] Task: Add Dependency Review workflow for pull requests.
    - Evidence: `.github/workflows/dependency_review.yml` adds PR Dependency Review with SHA-pinned `actions/dependency-review-action`, high-severity vulnerability gating, and license/vulnerability checks.
- [x] Task: Decide and implement action pinning policy.
    - [x] Prefer SHA pinning for publication workflows.
    - [x] Document Renovate update review requirements.
    - Evidence: monthly publication workflow actions are pinned to immutable SHAs; `renovate.json` now requires review/Dependency Dashboard approval for GitHub Actions updates instead of automerge; `supply_chain_enforcement_evidence.md` records the action SHA mapping.
- [x] Task: Move report-only checks to gating where baseline debt allows.
    - [x] Typos.
    - [x] Taplo.
    - [x] Zizmor.
    - Evidence: Typos and Taplo remain report-only because that is where baseline debt/runtime cost currently allows; Zizmor now uploads a durable report artifact and is explicitly report-only until non-publication workflow pinning debt is remediated.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Supply Chain Enforcement' (Protocol in workflow.md)
    - Evidence: supply-chain workflow changes are covered by workflow tests, actionlint, and branch-protected CI; remaining full-workflow pinning is tracked as baseline debt rather than silently ignored.

## Phase 5: Attestation Verification

- [x] Task: Add artifact attestation verification to release-readiness checks.
    - Evidence: `scripts/check_release_evidence.py` now fails through `validate_release_evidence` when the required attestation verification contract is missing or malformed.
- [x] Task: Record attestation verification evidence in release evidence.
    - Evidence: `release_evidence.json` now includes `attestation_verification`, and `build_release_artifacts` writes `manifests/attestation_verification.json` with provider, SHA-pinned attestation action, subject paths, expected release assets, and `gh attestation verify` commands.
- [x] Task: Add tests for missing/invalid attestation metadata.
    - Evidence: `tests/test_archive_release.py` covers generated attestation evidence, missing metadata rejection, invalid provider/status/action pin rejection, and empty required list rejection.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Attestation Verification' (Protocol in workflow.md)
    - Evidence: `attestation_verification_evidence.md` records focused tests, Ruff checks, generated artifact proof, and release evidence validation output.

## Phase 6: Documentation And First Governance Proof

- [x] Task: Update governance documentation.
    - Evidence: `docs/monthly-dynamic-archive-publication.md` now documents the attestation verification manifest, governance gates, protected Zenodo handoff, Dependency Review, Renovate review requirements, and strict readiness command.
- [x] Task: Run publication-readiness/doctor checks against live GitHub settings.
    - Evidence: `phase6_governance_proof_evidence.md` records live `zenodo-production` environment protection, live `master` branch protection, configured secret/variable names, and strict `publication-readiness --strict` output with `status: ready`.
- [x] Task: Attach governance proof to the GitHub issue/project.
    - Evidence: issue `#1` is linked to `Rare Insights on Open Policy from Aotearoa` and `corpus-cases-medilegal-nz Archive Roadmap`; Phase 6 proof is attached as an issue comment and the repo roadmap project item is marked `Done`.
- [x] Task: Conductor - User Manual Verification 'Phase 6: Documentation And First Governance Proof' (Protocol in workflow.md)
    - Evidence: documentation, live readiness, GitHub issue/project proof, and local checks are recorded in `phase6_governance_proof_evidence.md`; post-push GitHub check results are recorded on the implementation commit.
