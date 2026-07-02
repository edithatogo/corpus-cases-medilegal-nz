# Mirror Sync

The repository keeps a secondary Git mirror workflow in
[`.github/workflows/mirror_sync.yml`](../.github/workflows/mirror_sync.yml).
It runs on pushes to `main` and `master`, and it is also manually dispatchable.

## Required Secrets

- `GIT_MIRROR_URL`
- `GIT_MIRROR_URL_GITLAB`
- `GIT_MIRROR_URL_CODEBERG`
- `GIT_MIRROR_SSH_PRIVATE_KEY`

If no mirror URL is set, the workflow exits cleanly after logging that the
mirror step is skipped. If the SSH private key is missing, the workflow also
exits cleanly.

The repository currently uses GitLab and Codeberg as the public mirror
targets. The single `GIT_MIRROR_URL` secret remains as a backward-compatible
fallback, but the preferred configuration is to set the GitLab and Codeberg
URLs explicitly.

## Readiness Checks

Use the local readiness command to confirm the workflow shape and secret
gating:

```bash
python -m corpus_cases_medilegal_nz.cli mirror-readiness
python -m corpus_cases_medilegal_nz.cli mirror-readiness --strict
```

Or use the wrapper script:

```bash
python scripts/mirror_readiness.py
```

## Manual Verification

```bash
gh workflow run "Mirror Sync" --repo edithatogo/corpus-cases-medilegal-nz --ref master
gh run list --repo edithatogo/corpus-cases-medilegal-nz --workflow "Mirror Sync"
git ls-remote https://gitlab.com/edithatogo/corpus-cases-medilegal-nz.git HEAD
git ls-remote https://codeberg.org/edithatogo/corpus-cases-medilegal-nz.git HEAD
```

Expected outcome:

- The workflow dispatch is accepted by GitHub.
- The run completes successfully.
- When the mirror secrets are absent, the job logs a guarded skip.
