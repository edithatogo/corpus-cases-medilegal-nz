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

The workflow deduplicates repeated mirror URLs, attempts every configured
unique target, logs the remote HEAD for successful pushes, and fails at the end
if any configured mirror target failed. This keeps successful mirrors observable
even when one provider is temporarily incompatible.

## Readiness Checks

Use the local readiness command to confirm the workflow shape and secret
gating:

```bash
python -m corpus_cases_medilegal_nz.cli mirror-readiness
python -m corpus_cases_medilegal_nz.cli mirror-readiness --strict
python -m corpus_cases_medilegal_nz.cli mirror-readiness --strict --probe-remotes
```

`--strict` requires the full mirror target set to be configured:

- `GIT_MIRROR_URL`
- `GIT_MIRROR_URL_GITLAB`
- `GIT_MIRROR_URL_CODEBERG`
- `GIT_MIRROR_SSH_PRIVATE_KEY`

`--probe-remotes` additionally runs public `git ls-remote` readback against
configured mirror URLs and classifies remote HEAD object IDs. A 40-character
HEAD is treated as SHA-1-compatible. A 64-character HEAD is treated as a
SHA-256-format remote and blocks direct GitHub-to-provider mirroring because
GitHub repository history is SHA-1.

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
- The run completes successfully when all configured mirror targets accept the
  push.
- When the mirror secrets are absent, the job logs a guarded skip.
- If one configured mirror fails, the job still attempts later targets and logs
  per-target success or failure before exiting non-zero.

## Current Provider Notes

- Codeberg is the verified public git mirror for `master`; SSH readback on
  2026-07-03 returned `b70b00f6642634d31299afba8976486328134a2a` for `HEAD`
  and `refs/heads/master`.
- GitLab has writable deploy-key authentication configured, but the existing
  GitLab project was initialized with a SHA-256 object format and rejects this
  SHA-1 GitHub repository with `the receiving end does not support this
  repository's hash algorithm`. Recreate or reconfigure the GitLab mirror as a
  SHA-1-compatible repository before expecting direct git push mirroring to
  pass there.

## GitLab SHA-1 Repair Checklist

Use this only when `mirror-readiness --strict --probe-remotes` reports a
64-character SHA-256 GitLab HEAD.

1. Preserve the existing SHA-256 GitLab project by renaming its path to a dated
   archive suffix such as `corpus-cases-medilegal-nz-sha256-archive-20260703`.
2. Create a new public blank GitLab project at
   `edithatogo/corpus-cases-medilegal-nz`.
3. Leave GitLab's `project[use_sha256_repository]` option unchecked when
   creating the replacement project.
4. Add the existing writable mirror deploy key to the replacement project.
5. Run `mirror-readiness --strict --probe-remotes`; the GitLab HEAD should be
   absent for an empty project or 40 characters after first push.
6. Dispatch Mirror Sync and verify both GitLab and Codeberg read back the
   canonical GitHub commit.
