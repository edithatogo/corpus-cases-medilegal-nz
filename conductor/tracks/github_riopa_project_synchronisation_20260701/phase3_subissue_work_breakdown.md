# Phase 3 Sub-Issue Work Breakdown

Captured: 2026-07-02

## Parent Issue

- Parent: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1`
- Title: `Complete remote proof for monthly dynamic archive publication`
- Parent project statuses:
  - `Rare Insights on Open Policy from Aotearoa`: `Done`
  - `corpus-cases-medilegal-nz Archive Roadmap`: `Done`
- Sub-issues: `7`
- Completed sub-issues: `6`
- Completion: `85%`

## Created Sub-Issues

| Issue | Title | State | RIOPA status | Repo status | RIOPA mirror source |
| --- | --- | --- | --- | --- | --- |
| `#2` | `Hugging Face remote proof` | `CLOSED` | `Done` | `Done` | `other` |
| `#3` | `Zenodo draft and new-version proof` | `CLOSED` | `Done` | `Done` | `other` |
| `#4` | `Protected Zenodo production handoff` | `CLOSED` | `Done` | `Done` | `other` |
| `#5` | `GitHub release assets and attestations` | `CLOSED` | `Done` | `Done` | `other` |
| `#6` | `Public-surface and metadata evidence` | `CLOSED` | `Done` | `Done` | `other` |
| `#7` | `Collection and parser completion` | `CLOSED` | `Done` | `Done` | `other` |
| `#8` | `RIOPA and project sync automation` | `OPEN` | `In Progress` | `In Progress` | `other` |

## Markers

Each sub-issue body includes:

```html
<!-- parent-issue: 1 -->
<!-- riopa-subissue-id: <stable-id> -->
<!-- conductor-track-id: monthly_dynamic_archive_publication_20260701 -->
```

Stable sub-issue ids:

- `huggingface-remote-proof`
- `zenodo-draft-proof`
- `protected-zenodo-handoff`
- `github-release-assets-attestations`
- `public-surface-metadata-evidence`
- `collection-parser-completion`
- `riopa-project-sync-automation`

## Commands Used

Sub-issues were created with:

```powershell
gh issue create --parent 1 `
  --project "Rare Insights on Open Policy from Aotearoa" `
  --project "corpus-cases-medilegal-nz Archive Roadmap" `
  --title "<title>" `
  --body "<body with stable markers>"
```

Project fields were populated with:

```powershell
gh project item-edit --project-id PVT_kwHOAOYc4M4BcJFF `
  --id <riopa-item-id> `
  --field-id PVTSSF_lAHOAOYc4M4BcJFFzhW0HKg `
  --single-select-option-id a77f89f8

gh project item-edit --project-id <project-id> `
  --id <item-id> `
  --field-id <status-field-id> `
  --single-select-option-id <status-option-id>
```

Status option ids:

- `Done`: `98236657`
- `In Progress`: `47fc9ee4`
- RIOPA `Mirror source: other`: `a77f89f8`

## Verification

Readback commands:

```powershell
gh issue view 1 --json number,title,url,subIssues,subIssuesSummary,projectItems
gh issue list --state all --limit 20 --json number,title,state,url,parent,projectItems
gh project item-list 4 --owner edithatogo --format json --limit 200
gh project item-list 7 --owner edithatogo --format json --limit 100
```

Observed:

- Issue `#1` has seven sub-issues.
- Issues `#2`-`#7` are closed completed proof slices.
- Issue `#8` remains open and in progress for sync automation.
- All sub-issues are linked to both projects.
- All RIOPA items use `Mirror source: other`.
- RIOPA and repo roadmap project statuses match for every item.

## Boundary

Repo project #7 still has only default GitHub project fields. Phase 4 should add idempotent sync automation that can verify this default-field state, detect richer fields when they are later created, and fail loudly in apply mode when required configured fields are missing.
