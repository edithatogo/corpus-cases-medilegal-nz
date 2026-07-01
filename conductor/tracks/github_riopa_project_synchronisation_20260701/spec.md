# Specification: GitHub RIOPA Project Synchronisation

## Overview

Bring `corpus-cases-medilegal-nz` into full operational alignment with the Rare Insights on Open Policy from Aotearoa (RIOPA) meta-project and the sibling GitHub project conventions used by `rulespec-nz`, `nlp-policy-nz`, `fyi-archive`, `fyi-cli`, and archive-family repositories.

The track turns the current partial synchronisation into an auditable, automated, item-level project mirror with repo-specific project metadata, sub-issue hierarchy, and Conductor-linked issue records.

## Current State

- Repository project #7 exists: `corpus-cases-medilegal-nz Archive Roadmap`.
- RIOPA umbrella project #4 contains issue #1 from this repository.
- Issue #1 is linked to both projects and tracks `monthly_dynamic_archive_publication_20260701`.
- RIOPA has `Parent issue` and `Sub-issues progress` fields, but the current medilegal item does not use sub-issues.
- RIOPA `Mirror source` options do not include a dedicated `corpus-cases-medilegal-nz` value.
- Repo project #7 has only one item and no repo-specific operational fields beyond GitHub defaults.

## Requirements

- Add or configure a RIOPA `Mirror source` value for `corpus-cases-medilegal-nz`, or document the fallback if GitHub API access cannot create the option.
- Set the RIOPA item for issue #1 to the medilegal mirror source.
- Expand repo project #7 into a real operating board with fields aligned to sibling boards:
  - `Conductor track`
  - `Archive phase`
  - `Publication surface`
  - `Source status`
  - `Credential blocker`
  - `Remote proof`
  - `DOI state`
  - `Risk level`
- Split the flat issue #1 checklist into sub-issues for:
  - Hugging Face remote proof
  - Zenodo draft/new-version proof
  - Protected Zenodo production handoff
  - GitHub release assets and attestations
  - Public-surface and metadata evidence
  - Collection/parser completion
  - RIOPA/project sync automation
- Keep all sub-issues linked to repo project #7 and RIOPA.
- Preserve hidden `conductor-track-id` markers in issue bodies for idempotent syncing.
- Add project sync documentation and a repeatable script/workflow to reconcile Conductor tracks, GitHub issues, repo project fields, and RIOPA item fields.

## Non-Functional Requirements

- Sync must be idempotent and safe to rerun.
- Automation must not duplicate existing issues when a matching hidden marker exists.
- GitHub writes must be explicit, logged, and dry-run capable.
- Project field updates must fail loudly when required fields or options are missing.
- The design must remain compatible with sibling repo project conventions.

## Acceptance Criteria

- RIOPA item for issue #1 has a medilegal-specific mirror-source classification or a documented API limitation with a fallback.
- Issue #1 has sub-issues that represent the remote proof and governance work.
- Repo project #7 has meaningful custom fields and at least the issue/sub-issue work breakdown populated.
- A sync command or workflow can verify and reconcile Conductor track entries to GitHub issue/project state.
- Documentation states how repo project #7 mirrors into RIOPA and how to avoid duplicate items.

## Out Of Scope

- Implementing actual Hugging Face or Zenodo production publication.
- Replacing RIOPA with a new umbrella project.
- Moving sibling project items.
- Changing public dataset content or scraper/parser behavior.
