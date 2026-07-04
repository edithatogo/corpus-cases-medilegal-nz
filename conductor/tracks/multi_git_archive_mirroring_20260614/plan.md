# Plan - Multi-Git and Multi-Archive Mirroring

## Phase 1: Git Remote Mirror Setup
- [x] Task: Write `.github/workflows/mirror_sync.yml` to support automated SSH mirroring to secondary Git remotes (GitLab/Codeberg).
- [x] Task: Locally harden `mirror_sync.yml` credential bypass behavior for missing mirror URL or missing SSH private key.
- [x] Task: Document public GitLab and Codeberg mirror URLs in env templates and mirror docs.
- [x] Task: Configure repository secrets `GIT_MIRROR_URL`, `GIT_MIRROR_URL_GITLAB`, `GIT_MIRROR_URL_CODEBERG`, and mirror SSH key secrets on GitHub.
  - Evidence: `gh secret list --repo edithatogo/corpus-cases-medilegal-nz` shows all four `GIT_MIRROR_*` secrets updated on 2026-07-03.
  - Evidence: `uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli mirror-readiness --strict` returned `status: ready` with no blockers when the same values were loaded locally.
  - Evidence: GitLab and Codeberg both have the v2 deploy key fingerprint `SHA256:8pVwLtOI8exwo3MLOJIQmEtwOrjwCof9eMRV94MBELE` attached with write access.
  - Evidence: GitLab was recreated as a public SHA-1-compatible project on 2026-07-04 and now uses provider-specific v3 deploy key fingerprint `SHA256:HACEq+yiW+PnlES8HFBFnMK0ppUW4tXt1R4i/mIwIos`; Codeberg keeps the working v2 deploy key fingerprint `SHA256:8pVwLtOI8exwo3MLOJIQmEtwOrjwCof9eMRV94MBELE`.
  - Evidence: `mirror_sync.yml` supports `GIT_MIRROR_SSH_PRIVATE_KEY_GITLAB` and `GIT_MIRROR_SSH_PRIVATE_KEY_CODEBERG` with the generic `GIT_MIRROR_SSH_PRIVATE_KEY` as fallback.
- [x] Task: Verify successful manual and push triggers for mirror sync.
  - Partial live result: Codeberg mirror push succeeded and public readback returns `5a85e9311562da17146a65308200134192b73671` for `HEAD` and `refs/heads/master`.
  - Blocked live result: GitLab mirror push authenticates but fails with `fatal: the receiving end does not support this repository's hash algorithm` because the existing GitLab project HEAD is a 64-character SHA-256 object (`e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e`). The GitLab mirror project must be recreated or converted as a SHA-1-compatible repository before direct git push mirroring can complete.

## Phase 2: Zenodo & OSF Mirroring Integration
- [x] Task: Document Zenodo archival publication schema and script requirements. (See zenodo_archival_plan.md)
- [x] Task: Design OSF optional mirror convenience policy matching sister Hansard/Legislation corpora. (See osf_mirror_policy.md)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Zenodo & OSF Mirroring Integration' (Protocol in workflow.md)

## Chrome Operator Evidence - 2026-06-14

- Local non-gated validation complete for this lane; no Chrome/browser-profile work was approved or performed.
- Verified `.github/workflows/mirror_sync.yml` contains empty-secret bypasses for both `GIT_MIRROR_URL` and `GIT_MIRROR_SSH_PRIVATE_KEY`, plus quoted dynamic shell values for mirror URL and SSH host extraction.
- Focused validation passed: `pytest tests/test_mirror_workflow.py` -> 2 passed.
- Full local validation passed with escalated filesystem permissions for pytest temp cleanup: `pytest --basetemp pytest_tmp_verify -p no:cacheprovider` -> 174 passed.
- Scoped lint passed: `ruff check tests/test_mirror_workflow.py` -> all checks passed; Ruff cache write warning only.
- Full lint remains outside this lane's local fix scope: `ruff check .` reports existing lint debt across earlier pipeline/source/test files.
- Gated pending work remains: configure GitHub repository secrets and verify live workflow triggers/manual dispatch.

## Local Evidence - 2026-06-14
- `python -m pytest tests/test_mirror_workflow.py -p no:cacheprovider` passed: 2/2.
- `python -m ruff check tests/test_mirror_workflow.py --no-cache` passed.
- Full `python -m pytest` was attempted, but tests requiring `tmp_path` were blocked by local Windows filesystem permissions on pytest temp directories. Non-temp tests reached 149 passing before the permission errors.
- Gated items remain pending: GitHub secret configuration and any external archive/account publication.
- 2026-07-02: Verified live GitHub Mirror Sync push runs completed successfully with guarded secret skips, and a manual `workflow_dispatch` run (`28582552048`) was accepted and completed successfully on `master`.
- 2026-07-03: Public GitLab and Codeberg mirror endpoints were verified as reachable; env templates now store mirror URLs and tokens in ignored local env files.
- 2026-07-03: Strict mirror readiness now fails closed unless the full mirror target set is configured, so the track can distinguish partial from complete mirror coverage.
- 2026-07-02: `mirror-readiness --strict` returns `status: ready` when `GIT_MIRROR_URL`, `GIT_MIRROR_URL_GITLAB`, `GIT_MIRROR_URL_CODEBERG`, and `GIT_MIRROR_SSH_PRIVATE_KEY` are all configured.
- 2026-07-03: `uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli mirror-readiness --strict` returned `status: blocked` with blockers `GIT_MIRROR_URL`, `GIT_MIRROR_URL_GITLAB`, `GIT_MIRROR_URL_CODEBERG`, `GIT_MIRROR_SSH_PRIVATE_KEY`, and `mirror_target_set`.
- 2026-07-03: `git ls-remote https://gitlab.com/edithatogo/corpus-cases-medilegal-nz.git HEAD` returned public HEAD `e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e`; local Codeberg HTTPS readback failed with a Windows Schannel TLS handshake error, so Codeberg should be rechecked from GitHub Actions or a non-Schannel client after mirror secrets are configured.
- 2026-07-03: Used Chrome-authenticated GitLab and Codeberg sessions to attach v2 writable deploy key `SHA256:8pVwLtOI8exwo3MLOJIQmEtwOrjwCof9eMRV94MBELE`; updated GitHub Actions `GIT_MIRROR_*` secrets without printing secret values.
- 2026-07-03: Mirror Sync run `28659283834` failed on GitLab with `Permission denied (publickey)` because the first generated key was passphrase-protected accidentally; v2 key generation corrected this.
- 2026-07-03: Mirror Sync run `28659792499` authenticated to GitLab but failed with `fatal: the receiving end does not support this repository's hash algorithm`, confirming a GitLab remote object-format blocker rather than a credentials blocker.
- 2026-07-03: Direct Codeberg SSH push with the v2 key succeeded: `HEAD -> master`; public readback now returns `5a85e9311562da17146a65308200134192b73671` for both `HEAD` and `refs/heads/master`.
- 2026-07-03: Focused validation passed after workflow hardening: `uv run --frozen --python 3.12 --extra dev pytest -q tests/test_mirror_workflow.py` -> 6 passed.
- 2026-07-03: Codeberg readback after the clean-checkout release evidence fix returned `b70b00f6642634d31299afba8976486328134a2a` for both `HEAD` and `refs/heads/master`; GitHub `Tests`, `CodeQL`, `Docs`, `OSV Scan`, and `Code Quality And Workflow Hardening` were green for that commit.
- 2026-07-03: GitLab project creation remains manual-blocked by browser Cloudflare/sign-in verification. The existing GitLab original and archive URLs still return SHA-256 HEAD `e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e`.
- 2026-07-03: Added opt-in remote object-format probe path: `uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli mirror-readiness --strict --probe-remotes` classifies 40-character SHA-1-compatible remote HEADs and blocks 64-character SHA-256 remote HEADs before push.
- 2026-07-04: Hardened mirror readiness reporting with first-class `mirror_targets`, `mirror_target_summary`, and `next_actions` fields. Live strict probe with the known mirror URLs reported `status: blocked`, blocker `remote_object_format`, `configured_count: 2`, `healthy_count: 1`, `blocked_count: 1`, providers `codeberg,gitlab`, GitLab `sha256` head `e3dcc84171382b1178636b36a160335af5d35be0fbc8274624bad048299fb50e`, and Codeberg `sha1` head `1895a0b7822dc0027393e83cb4c8cfc4a023c63e`.
- 2026-07-04: Focused validation passed after reporting hardening: `uv run --frozen --python 3.12 --extra dev ruff check src/corpus_cases_medilegal_nz/mirror.py scripts/mirror_readiness.py tests/test_mirror_workflow.py`, `uv run --frozen --python 3.12 --extra dev ruff format --check src/corpus_cases_medilegal_nz/mirror.py scripts/mirror_readiness.py tests/test_mirror_workflow.py`, and `uv run --frozen --python 3.12 --extra dev pytest -q tests/test_mirror_workflow.py` -> 9 passed.
- 2026-07-04: Created dedicated GitHub issue for the manual GitLab SHA-1 recreation proof and acceptance criteria: https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/9.
- 2026-07-04: Added scheduled `Mirror Probe Report` workflow to run strict remote readiness probes daily and on manual dispatch, upload `readiness.json` and `report.md`, write the report to the GitHub Actions summary, and post one idempotent marker comment to issue #9 when GitLab becomes SHA-1-compatible and strict readiness turns `ready`.
- 2026-07-04: Added release-readiness mirror gating. Monthly publication now writes `generated/mirror-probe/readiness.json` before strict `publication-readiness`; readiness treats healthy Codeberg SHA-1 coverage plus GitLab's known SHA-256 mismatch as `known_external_blocker` rather than a release blocker, and fails only when no healthy Codeberg mirror is present.
- 2026-07-04: Repaired the GitLab mirror by renaming the SHA-256 project to `corpus-cases-medilegal-nz-sha256-archive-20260703`, creating a replacement public project at `edithatogo/corpus-cases-medilegal-nz`, adding v3 writable deploy key `SHA256:HACEq+yiW+PnlES8HFBFnMK0ppUW4tXt1R4i/mIwIos`, and locally pushing/readback-verifying `30169f71adb73306f9245cee8112c85390effa5c`.
- 2026-07-04: Identified that GitLab and Codeberg require separate deploy keys because the GitHub fallback secret was rotated to GitLab v3 while Codeberg still trusts v2; provider-specific workflow secrets are now the canonical fix.
- 2026-07-04: Added and pushed provider-specific GitHub mirror key support in commit `9467106dc63469add0dc708b69dbbf4fcf7ed87d`. `GIT_MIRROR_SSH_PRIVATE_KEY_GITLAB` now uses GitLab v3, `GIT_MIRROR_SSH_PRIVATE_KEY_CODEBERG` uses Codeberg v2, and the generic fallback key was reset to Codeberg v2 for backward compatibility.
- 2026-07-04: Live verification complete: push-triggered Mirror Sync run `28704295813` succeeded, manual Mirror Sync run `28704324611` succeeded, and manual Mirror Probe Report run `28704325099` succeeded with strict readiness `ready`, two configured targets, two healthy targets, zero blockers, and both GitLab and Codeberg reporting SHA-1 `HEAD` `9467106dc63469add0dc708b69dbbf4fcf7ed87d`.
