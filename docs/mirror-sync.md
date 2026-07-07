# Mirror Sync

The repository keeps a secondary Git mirror workflow in
[`.github/workflows/mirror_sync.yml`](../.github/workflows/mirror_sync.yml).
It runs on pushes to `main` and `master`, and it is also manually dispatchable.

Local mirror values should stay in ignored `.env` or `.env.local` files, while
the workflow itself reads the corresponding GitHub secrets and variables at
runtime.

## Required Secrets

- `GIT_MIRROR_URL`
- `GIT_MIRROR_URL_GITLAB`
- `GIT_MIRROR_URL_CODEBERG`
- `GIT_MIRROR_SSH_PRIVATE_KEY`
- `GIT_MIRROR_SSH_PRIVATE_KEY_GITLAB`
- `GIT_MIRROR_SSH_PRIVATE_KEY_CODEBERG`

If no mirror URL is set, the workflow exits cleanly after logging that the
mirror step is skipped. If no SSH private key secret is set, the workflow also
exits cleanly. If at least one key exists but a configured target has no
provider-specific key and no fallback key, that target fails explicitly.

The repository currently uses GitLab and Codeberg as the public mirror
targets. The single `GIT_MIRROR_URL` secret remains as a backward-compatible
fallback, but the preferred configuration is to set the GitLab and Codeberg
URLs explicitly.

Provider-specific SSH key secrets are preferred. The generic
`GIT_MIRROR_SSH_PRIVATE_KEY` remains a fallback for unknown providers and older
single-key deployments. This lets GitLab and Codeberg use separate deploy keys
when one provider needs a key rotation but the other already has a working
deploy key.

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
- mirror SSH key coverage through either `GIT_MIRROR_SSH_PRIVATE_KEY` or the
  provider-specific `GIT_MIRROR_SSH_PRIVATE_KEY_GITLAB` and
  `GIT_MIRROR_SSH_PRIVATE_KEY_CODEBERG` secrets.

`--probe-remotes` additionally runs public `git ls-remote` readback against
configured mirror URLs and classifies remote HEAD object IDs. A 40-character
HEAD is treated as SHA-1-compatible. A 64-character HEAD is treated as a
SHA-256-format remote and blocks direct GitHub-to-provider mirroring because
GitHub repository history is SHA-1.

The readiness report includes:

- `mirror_targets`: one normalized row per unique configured target, including
  provider, HTTPS readback URL, probe status, object format, current HEAD when
  available, and the reason for the target state.
- `mirror_target_summary`: aggregate configured, healthy, blocked, and
  probe-failed counts for dashboards and issue/project evidence.
- `next_actions`: operator remediation steps generated from the observed
  blockers.

Or use the wrapper script:

```bash
python scripts/mirror_readiness.py
python scripts/mirror_readiness.py --strict --probe-remotes
```

## Scheduled Probe Reporting

[`Mirror Probe Report`](../.github/workflows/mirror_probe_report.yml) runs daily
and can also be manually dispatched. It does not push to any mirror. It only
runs strict readiness with remote probes, writes a GitHub Actions job summary,
and uploads `readiness.json` plus `report.md` as the `mirror-probe-report`
artifact.

The scheduled probe is intentionally non-spamming while GitLab remains blocked.
When the report first changes to `status: ready`, the workflow posts one
idempotent marker comment to issue
[#9](https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/9), making
the GitLab SHA-1 recreation visible without requiring operators to inspect
every scheduled run.

## Release Readiness Gate

Monthly publication builds mirror probe evidence before running strict
`publication-readiness`. Release readiness treats mirror coverage as acceptable
when Codeberg is healthy with a SHA-1 HEAD. If GitLab is the known SHA-256
remote-format mismatch, readiness records it in `known_external_blockers` with
issue #9 and keeps the release gate open because the repo still has a verified
public git mirror.

The gate fails only when mirror evidence exists but no healthy Codeberg mirror
is present. This prevents a repaired-or-broken mirror state from being hidden as
generic external-write debt while avoiding unnecessary release blockage for the
already-tracked GitLab recreation task.

## Manual Verification

```bash
gh workflow run "Mirror Sync" --repo edithatogo/corpus-cases-medilegal-nz --ref master
gh workflow run "Mirror Probe Report" --repo edithatogo/corpus-cases-medilegal-nz --ref master
gh run list --repo edithatogo/corpus-cases-medilegal-nz --workflow "Mirror Sync"
gh run list --repo edithatogo/corpus-cases-medilegal-nz --workflow "Mirror Probe Report"
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
- `mirror-readiness --strict --probe-remotes` shows Codeberg as healthy when it
  has a 40-character SHA-1 HEAD, and shows GitLab as blocked when it has the
  known 64-character SHA-256 HEAD.

## Current Provider Notes

- Codeberg is the verified public git mirror for `master`; SSH readback on
  2026-07-03 returned `b70b00f6642634d31299afba8976486328134a2a` for `HEAD`
  and `refs/heads/master`. It uses the v2 deploy key fingerprint
  `SHA256:8pVwLtOI8exwo3MLOJIQmEtwOrjwCof9eMRV94MBELE`.
- GitLab was recreated on 2026-07-04 as a blank public SHA-1-compatible project
  after the prior SHA-256 project was preserved under a dated archive path. It
  uses the v3 deploy key fingerprint
  `SHA256:HACEq+yiW+PnlES8HFBFnMK0ppUW4tXt1R4i/mIwIos`.

## GitLab SHA-1 Repair Checklist

Use this only when `mirror-readiness --strict --probe-remotes` reports a
64-character SHA-256 GitLab HEAD.

1. Preserve the existing SHA-256 GitLab project by renaming its path to a dated
   archive suffix such as `corpus-cases-medilegal-nz-sha256-archive-20260703`.
2. Create a new public blank GitLab project at
   `edithatogo/corpus-cases-medilegal-nz`.
3. Leave GitLab's `project[use_sha256_repository]` option unchecked when
   creating the replacement project.
4. Add a writable mirror deploy key to the replacement project. If the old key
   remains attached to the archived GitLab project or another mirror provider,
   generate a provider-specific replacement key and store it in
   `GIT_MIRROR_SSH_PRIVATE_KEY_GITLAB`.
5. Run `mirror-readiness --strict --probe-remotes`; the GitLab HEAD should be
   absent for an empty project or 40 characters after first push.
6. Dispatch Mirror Sync and verify both GitLab and Codeberg read back the
   canonical GitHub commit.
