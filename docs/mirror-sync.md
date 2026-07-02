# Mirror Sync

The repository keeps a secondary Git mirror workflow in
[`.github/workflows/mirror_sync.yml`](../.github/workflows/mirror_sync.yml).
It runs on pushes to `main` and `master`, and it is also manually dispatchable.

## Required Secrets

- `GIT_MIRROR_URL`
- `GIT_MIRROR_SSH_PRIVATE_KEY`

If either secret is missing, the workflow exits cleanly after logging that the
mirror step is skipped.

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
```

Expected outcome:

- The workflow dispatch is accepted by GitHub.
- The run completes successfully.
- When the mirror secrets are absent, the job logs a guarded skip.

