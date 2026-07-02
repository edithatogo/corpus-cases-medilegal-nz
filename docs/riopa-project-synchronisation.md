# RIOPA Project Synchronisation

This repository mirrors monthly archive publication evidence into the Rare
Insights on Open Policy from Aotearoa (RIOPA) GitHub Project and the local
repository roadmap project.

## Project Surfaces

| Surface | GitHub Project | Purpose |
| --- | --- | --- |
| RIOPA meta-project | `Rare Insights on Open Policy from Aotearoa` project `#4` | Cross-repository policy/archive evidence roll-up |
| Repository roadmap | `corpus-cases-medilegal-nz Archive Roadmap` project `#7` | Local operational tracking for this repository |
| Parent issue | `edithatogo/corpus-cases-medilegal-nz#1` | Stable archive-publication evidence anchor |

The parent issue carries the `monthly_dynamic_archive_publication_20260701`
Conductor marker. Subissues `#2` through `#8` decompose the archive proof into
Hugging Face, Zenodo, protected handoff, GitHub release/attestation,
public-surface metadata, parser completion, and sync-automation evidence.

## Synchronisation Contract

`scripts/sync_riopa_project.py` is the source of truth for desired GitHub issue
and project state. The script:

- Parses stable hidden HTML markers such as `riopa-subissue-id` and
  `conductor-track-id`.
- Detects duplicate subissue markers before planning writes.
- Verifies the expected seven subissues are present.
- Reconciles subissue open/closed state against the desired evidence status.
- Adds missing subissues to both GitHub Projects.
- Sets project status to `Done` for completed proof items and `In Progress` for
  active sync-automation work.
- Sets RIOPA `Mirror source` to `other` until a dedicated
  `corpus-cases-medilegal-nz` option is available on the RIOPA board.
- Writes JSON evidence to `generated/project-sync/riopa_project_sync_evidence.json`.

The current RIOPA single-select field exposes `rulespec-nz`, `nlp-policy-nz`,
`fyi-archive`, and `other`. Because this repo does not yet have a dedicated
option, `other` is the deterministic, API-safe value. If a project admin later
adds `corpus-cases-medilegal-nz`, update `RIOPA_MIRROR_OTHER_OPTION_ID` and the
field mapping tests in the same change.

## Running The Sync

Dry-run verification:

```powershell
uv run --frozen --python 3.12 --extra dev python scripts\sync_riopa_project.py --output generated\project-sync\riopa_project_sync_evidence.json
```

Apply drift repair:

```powershell
uv run --frozen --python 3.12 --extra dev python scripts\sync_riopa_project.py --apply --output generated\project-sync\riopa_project_sync_evidence.json
```

The expected clean dry-run result is:

```json
{
  "actions": [],
  "desired_subissue_count": 7,
  "duplicate_markers": {},
  "mode": "dry-run",
  "parent_issue": 1,
  "schema_version": "1.0.0",
  "status": "in_sync"
}
```

## Workflow Automation

`.github/workflows/riopa_project_sync.yml` runs the same sync weekly and on
manual dispatch. It uses least-privilege repository permissions and prefers
`RIOPA_PROJECT_TOKEN` when present because cross-project user boards can require
broader project access than the default `GITHUB_TOKEN`.

The workflow intentionally refuses publication-style writes for dependency
update actors such as Dependabot and Renovate. Each run uploads the
`riopa-project-sync-evidence` artifact so project drift can be audited without
re-running the job.

## Operating Notes

- Keep issue bodies deterministic and preserve the hidden marker comments.
- Do not manually duplicate a `riopa-subissue-id`; the sync script blocks on
  duplicate markers.
- Use issue `#1` for archive-family evidence roll-up and issue `#8` for sync
  automation follow-up.
- Treat `generated/project-sync/` as generated evidence, not a hand-maintained
  source file.
- Keep this repo aligned with sibling GitHub, Hugging Face, and Zenodo tracks by
  making GitHub Projects carry evidence pointers, while release artifacts and
  archive manifests remain the canonical publication proof.
