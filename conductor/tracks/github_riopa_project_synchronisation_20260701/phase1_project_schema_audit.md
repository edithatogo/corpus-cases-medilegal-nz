# Phase 1 Project Schema Audit

Captured: 2026-07-02

## Projects

### RIOPA Umbrella

- Title: `Rare Insights on Open Policy from Aotearoa`
- Project number: `4`
- Project id: `PVT_kwHOAOYc4M4BcJFF`
- URL: `https://github.com/users/edithatogo/projects/4`
- Visibility: public
- Item count: `155`
- Field count: `14`

### Repo Roadmap

- Title: `corpus-cases-medilegal-nz Archive Roadmap`
- Project number: `7`
- Project id: `PVT_kwHOAOYc4M4BcLDo`
- URL: `https://github.com/users/edithatogo/projects/7`
- Visibility: public
- Item count: `1`
- Field count: `13`

## Current Issue Item IDs

Issue:

- Issue: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1`
- Issue node id: `I_kwDOS6HCd88AAAABHTPbzA`
- Hidden marker: `<!-- conductor-track-id: monthly_dynamic_archive_publication_20260701 -->`
- Sub-issues: `0`

Project item ids:

- RIOPA project #4 item id: `PVTI_lAHOAOYc4M4BcJFFzgxZYg0`
- Repo project #7 item id: `PVTI_lAHOAOYc4M4BcLDozgxZZz0`

Verified status after governance proof:

- RIOPA item status: `Done`
- Repo roadmap item status: `Done`

## RIOPA Field Schema

Command:

```powershell
gh project field-list 4 --owner edithatogo --format json
```

Fields:

| Field | Type | Field id / Options |
| --- | --- | --- |
| `Title` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BXw` |
| `Assignees` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BX0` |
| `Status` | `ProjectV2SingleSelectField` | `PVTSSF_lAHOAOYc4M4BcJFFzhW0BX4`: `Todo`=`f75ad846`, `In Progress`=`47fc9ee4`, `Done`=`98236657` |
| `Labels` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BX8` |
| `Linked pull requests` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYA` |
| `Milestone` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYE` |
| `Repository` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYI` |
| `Reviewers` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYM` |
| `Parent issue` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYQ` |
| `Sub-issues progress` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYU` |
| `Created` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYY` |
| `Updated` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYc` |
| `Closed` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcJFFzhW0BYg` |
| `Mirror source` | `ProjectV2SingleSelectField` | `PVTSSF_lAHOAOYc4M4BcJFFzhW0HKg`: `rulespec-nz`=`a3906499`, `nlp-policy-nz`=`f2dfa509`, `fyi-archive`=`bf110aaa`, `other`=`a77f89f8` |

Finding:

- RIOPA has a `Mirror source` field.
- RIOPA does not currently have a dedicated `corpus-cases-medilegal-nz` mirror-source option.
- Phase 2 should use `other` as the API-safe fallback unless a dedicated option is manually created through the GitHub project UI or a supported GraphQL mutation is added.

## Repo Project Field Schema

Command:

```powershell
gh project field-list 7 --owner edithatogo --format json
```

Fields:

| Field | Type | Field id / Options |
| --- | --- | --- |
| `Title` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yOg` |
| `Assignees` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yOk` |
| `Status` | `ProjectV2SingleSelectField` | `PVTSSF_lAHOAOYc4M4BcLDozhW1yOo`: `Todo`=`f75ad846`, `In Progress`=`47fc9ee4`, `Done`=`98236657` |
| `Labels` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yOs` |
| `Linked pull requests` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yOw` |
| `Milestone` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yO0` |
| `Repository` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yO4` |
| `Reviewers` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yO8` |
| `Parent issue` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yPA` |
| `Sub-issues progress` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yPE` |
| `Created` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yPI` |
| `Updated` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yPM` |
| `Closed` | `ProjectV2Field` | `PVTF_lAHOAOYc4M4BcLDozhW1yPQ` |

Finding:

- Repo project #7 currently has only GitHub default fields.
- Required medilegal operational fields from the specification are absent.
- The GitHub CLI exposes reliable field readback and item field mutation, but project field creation should be treated as a Phase 2/4 write operation with dry-run evidence or a documented manual fallback.

## Sibling Board Comparison

Compared live field schemas:

- `rulespec-nz coverage ledger` project #1.
- `nlp-policy-nz Conductor Roadmap` project #3.
- `sm-govt-nz Archive Roadmap` project #5.
- `fyi-cli Conductor Roadmap` project #6.

Patterns:

- Default fields are consistent across boards: `Status`, `Repository`, `Parent issue`, `Sub-issues progress`, timestamps, and linked PR metadata.
- RIOPA adds `Mirror source` for cross-repo filtering.
- `rulespec-nz` adds domain fields: `Policy family`, `Source status`, `Oracle status`, `Conductor track`, `Upstream issue`, and `Upstream PR`.
- `nlp-policy-nz` and `fyi-cli` add richer Conductor fields: `Conductor Track`, `Track Number`, `Conductor Status`, `Phase`, `Dependencies`, `Parallelization Node`, `Track Path`, `Workstream`, `Priority`, `Effort`, `Gate Type`, and `Issue Role`.
- `sm-govt-nz` currently has only default project fields, matching the current medilegal repo board baseline.

## Medilegal Project Field Contract

Recommended repo project #7 fields:

| Field | Type | Allowed values / Mapping |
| --- | --- | --- |
| `Conductor Track` | text | Conductor track id from hidden issue marker or local `conductor/tracks.md`. |
| `Archive Phase` | single select | `Collection`, `Validation`, `Publication`, `Governance`, `Federation`, `Maintenance`. |
| `Publication Surface` | single select | `GitHub`, `Hugging Face`, `Zenodo`, `OSF`, `Multi-surface`, `Internal`. |
| `Source Status` | single select | `planned`, `fetch scaffold`, `parser stub`, `validated records`, `blocked`, `not applicable`. |
| `Credential Blocker` | single select | `none`, `secret missing`, `environment approval`, `external account`, `manual review`. |
| `Remote Proof` | single select | `not started`, `dry-run`, `uploaded`, `verified`, `published`, `not applicable`. |
| `DOI State` | single select | `not applicable`, `draft`, `handoff pending`, `published`, `blocked`. |
| `Risk Level` | single select | `low`, `medium`, `high`, `critical`. |
| `Track Path` | text | Local track folder path. |
| `Issue Role` | single select | `Active Work`, `Roadmap`, `Evidence Anchor`, `Historical Record`. |

Fallback behavior:

- If field creation is unavailable through the installed GitHub CLI/API permissions, Phase 2 should document the manual field creation steps and keep automation in verification-only mode.
- If RIOPA lacks a dedicated `corpus-cases-medilegal-nz` mirror-source option, use `other` and record the repo URL plus hidden `conductor-track-id` marker as the stable discriminator.
- Sync automation must fail loudly when required fields are missing in apply mode, and must report missing fields as warnings in dry-run mode.

## Phase 1 Verification

Manual verification completed by readback from live GitHub Projects and issue APIs:

- Project metadata read with `gh project view`.
- Field schemas read with `gh project field-list`.
- Current project items read with `gh project item-list`.
- Issue linkage and sub-issue summary read with `gh issue view`.

No project or issue writes were made in Phase 1.
