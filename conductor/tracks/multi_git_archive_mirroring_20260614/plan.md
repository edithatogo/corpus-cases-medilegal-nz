# Plan - Multi-Git and Multi-Archive Mirroring

## Phase 1: Git Remote Mirror Setup
- [x] Task: Write `.github/workflows/mirror_sync.yml` to support automated SSH mirroring to secondary Git remotes (GitLab/Codeberg).
- [x] Task: Locally harden `mirror_sync.yml` credential bypass behavior for missing mirror URL or missing SSH private key.
- [ ] Task: Configure repository secrets `GIT_MIRROR_URL` and `GIT_MIRROR_SSH_PRIVATE_KEY` on GitHub.
- [x] Task: Verify successful manual and push triggers for mirror sync.

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
