# Specification: Cross-Repo Archive Federation

## Overview

Create a shared archive-family federation contract so `corpus-cases-medilegal-nz` stays aligned with parallel archives across GitHub, Hugging Face, Zenodo, and project ledgers.

This track focuses on reusable conventions and compatibility across sibling repositories rather than this repo's local publication mechanics alone.

## Requirements

- Define a shared archive evidence schema profile across:
  - `corpus-cases-medilegal-nz`
  - `corpus-law-nz`
  - `corpus-nz-hansard`
  - `fyi-archive`
  - `hathi-nz`
  - other future Rare Insights corpus repos
- Standardize release evidence field names, status values, and mirror publication states.
- Standardize GitHub project fields and issue marker conventions.
- Define cross-repo source coverage and public-surface audit schema compatibility.
- Add compatibility tests using fixture ledgers from sibling patterns.
- Add docs for archive-family naming, versioning, secret names, protected environments, release assets, and evidence ledgers.
- Add a federation report that identifies drift between this repo and the archive-family contract.

## Non-Functional Requirements

- The federation contract must be additive and avoid breaking sibling repositories.
- This repo should be able to validate itself without cloning every sibling repository.
- Optional sibling-repo probes should degrade gracefully when paths or network access are unavailable.
- Schema changes must be versioned.

## Acceptance Criteria

- A documented archive-family contract exists.
- This repo can emit a federation compatibility report.
- Release evidence and project-sync artifacts identify their schema/profile version.
- Compatibility tests cover at least local sample ledgers for sibling archive patterns.
- Drift findings can be opened or mirrored into GitHub project items.

## Out Of Scope

- Refactoring sibling repositories directly.
- Replacing repo-specific Conductor tracks.
- Publishing a centralized hosted dashboard.
- Enforcing organization-wide policy outside the user's repositories.
