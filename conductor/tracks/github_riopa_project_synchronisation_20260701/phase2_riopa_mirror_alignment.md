# Phase 2 RIOPA Mirror Alignment

Captured: 2026-07-02

## Mirror Source Decision

RIOPA project #4 has a `Mirror source` field:

- Field id: `PVTSSF_lAHOAOYc4M4BcJFFzhW0HKg`
- Current options:
  - `rulespec-nz`: `a3906499`
  - `nlp-policy-nz`: `f2dfa509`
  - `fyi-archive`: `bf110aaa`
  - `other`: `a77f89f8`

There is no dedicated `corpus-cases-medilegal-nz` option.

The installed GitHub CLI exposes `gh project field-create` for new fields, but not an option-add operation for an existing single-select field. Phase 2 therefore uses the API-safe fallback from Phase 1:

- Set RIOPA `Mirror source` to `other`.
- Use the item repository URL and hidden issue marker as the stable discriminator.
- Treat a dedicated `corpus-cases-medilegal-nz` single-select option as a manual project-admin follow-up or future GraphQL-backed sync enhancement.

## Applied RIOPA Item Updates

Issue:

- `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1`
- RIOPA item id: `PVTI_lAHOAOYc4M4BcJFFzgxZYg0`
- RIOPA project id: `PVT_kwHOAOYc4M4BcJFF`

Commands:

```powershell
gh project item-edit `
  --project-id PVT_kwHOAOYc4M4BcJFF `
  --id PVTI_lAHOAOYc4M4BcJFFzgxZYg0 `
  --field-id PVTSSF_lAHOAOYc4M4BcJFFzhW0HKg `
  --single-select-option-id a77f89f8

gh project item-edit `
  --project-id PVT_kwHOAOYc4M4BcJFF `
  --id PVTI_lAHOAOYc4M4BcJFFzgxZYg0 `
  --field-id PVTSSF_lAHOAOYc4M4BcJFFzhW0BX4 `
  --single-select-option-id 98236657
```

Applied values:

- `Mirror source`: `other`
- `Status`: `Done`

Repository is a built-in GitHub Projects field and readback reports:

- `repository`: `https://github.com/edithatogo/corpus-cases-medilegal-nz`

Conductor-track metadata is represented by the issue body marker:

```html
<!-- conductor-track-id: monthly_dynamic_archive_publication_20260701 -->
```

## Verification

Readback command:

```powershell
gh project item-list 4 --owner edithatogo --format json --limit 200
gh issue view 1 --json number,title,url,projectItems,body,subIssuesSummary
```

Observed:

- RIOPA item id: `PVTI_lAHOAOYc4M4BcJFFzgxZYg0`
- `mirror source`: `other`
- `status`: `Done`
- `repository`: `https://github.com/edithatogo/corpus-cases-medilegal-nz`
- issue marker present: `true`
- linked project item statuses:
  - `Rare Insights on Open Policy from Aotearoa`: `Done`
  - `corpus-cases-medilegal-nz Archive Roadmap`: `Done`

## Remaining Follow-Up

Phase 3 should create sub-issues under issue #1 and add those sub-issues to both projects. Once sub-issues exist, the RIOPA item can rely on `Parent issue` and `Sub-issues progress` for drill-down.

Phase 4 sync automation should:

- require the `Mirror source` field in RIOPA;
- prefer a dedicated `corpus-cases-medilegal-nz` option when present;
- otherwise set `other` and verify the repository URL plus hidden marker;
- fail loudly in apply mode if neither discriminator is available.
