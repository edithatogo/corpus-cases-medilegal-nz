# Specification: Redundant Source Validation And Reconciliation Hardening

## Overview

Introduce a dedicated validation layer that uses redundant public sources to
confirm or falsify coverage claims made by the canonical corpus. The goal is to
separate "primary source ingestion" from "independent witness validation" so
the repo can show when a case family is covered twice and when it only has a
single public witness.

This track does not add new canonical sources first. It focuses on validation
mirrors, index pages, and alternate public listings that can be used to verify
the active registry and future candidate sources.

## Current State

- The repo already has live verification, replay, completeness reconciliation,
  and release-evidence generation.
- The active registry can be validated against several public witnesses:
  - NZLII decision subsets and search surfaces.
  - Court of New Zealand case summaries and judgment pages.
  - Council mirror pages for Medical, Dental, Pharmacy, and Teaching
    disciplinary decisions.
  - Older ACCDCR and ACC appeal surfaces.
  - Human Rights Review Tribunal and related Ministry of Justice indexes.
- The existing candidate queue already recognises that some sources should stay
  candidate-only until rights and scope are settled.

## Requirements

- Define validation-source classes separate from canonical sources.
  - `primary`
  - `redundant_witness`
  - `summary_index`
  - `mirror`
  - `candidate_only`
- Add source-equivalence and duplicate-detection rules for public witnesses.
- Add a redundant-source ledger that records which validation source confirms
  which canonical or candidate family.
- Use the redundant ledger to identify gaps where a family has only one public
  witness.
- Add tests that ensure the repo can distinguish canonical coverage from
  validation coverage.
- Add release-safe public claims that explicitly say when a claim is supported
  by a redundant source and when it is not.

## Non-Functional Requirements

- Validation evidence must be reproducible from archived public pages or
  snapshots.
- Mirror sources must never be mistaken for a new canonical source without an
  approval decision.
- Gaps and duplicate handling must remain source-scoped and diagnosable.
- The implementation should keep existing monthly archive publication
  compatibility intact.

## Acceptance Criteria

- The repo can produce a redundant-source ledger for active sources and
  approved candidates.
- Duplicate, mirror, and summary-index evidence is available for at least the
  major medicolegal families.
- Coverage reports can show when a source family lacks an independent witness.
- Public claims and release evidence can cite the redundant-source ledger.

## Out Of Scope

- Canonical promotion of validation mirrors without separate approval.
- Private, access-controlled, or non-public witness sources.
- Rewriting the current publication workflow beyond the evidence inputs needed
  for validation.
