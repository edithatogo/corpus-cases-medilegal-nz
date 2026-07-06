# Specification: Additional Candidate Source Triage And Coverage Expansion

## Overview

Expand the corpus beyond the current active 13-source registry by triaging
additional public candidate families that materially improve medicolegal
coverage.

The current repo already has a candidate discovery queue, rights ledgers,
parser-risk tracking, and live verification. This track turns those discovery
notes into a controlled expansion program with explicit approve, defer, and
exclude outcomes. It also keeps candidate promotion separate from the current
canonical registry so that coverage gains do not silently mutate the active
source set.

## Current State

- The active registry already covers HDC, HPDT, MoJ Tribunals, ERA, Teachers,
  Royal Commissions/Waitangi Tribunal, Coronial, Privacy Commissioner, Human
  Rights Commission/Tribunal, Ombudsman, MoJ courts, IPCA, and Law Commission.
- The current candidate queue already includes ACC appeal/review material,
  other professional councils, Mental Health Review Tribunal material if
  public, NZLII health/privacy/discipline subsets, and health appellate court
  filters.
- Live research also shows adjacent public sources that are worth triage before
  promotion:
  - ACC appeals and older ACCDCR decisions.
  - Social Security Appeal Authority and medical appeals.
  - Public professional-discipline mirror pages for Medical, Dental, Pharmacy,
    and Teaching councils.
  - Health-related Court of New Zealand filters and case-summary pages.

## Requirements

- Define a single candidate taxonomy with the following outcomes:
  - `approved`
  - `deferred`
  - `excluded`
- Create explicit candidate records for each discovered source family and keep
  the current active registry unchanged until approval is granted.
- Add rights, terms, privacy, redistribution, takedown, and citation notes for
  every candidate family.
- For approved candidates, create source config, fixture contract, live
  verification, parser-risk evidence, and release-evidence hooks before
  promotion.
- For deferred candidates, record the blocker clearly and keep the source in a
  reviewable discovery ledger.
- For excluded candidates, record why the source is outside scope, redundant,
  non-public, or too uncertain to support canonical release claims.
- Add tests that verify classification, promotion gating, and the boundary
  between candidate and active sources.
- Keep a redundant-source requirement in the candidate review so a source can
  be validated against at least one independent witness when available.

## Non-Functional Requirements

- Candidate triage must be reproducible from archived source evidence.
- Public claims must never state that a candidate is canonical until its
  approval evidence exists.
- Scope boundaries must be explicit enough to keep adjacent but weakly related
  sources out of the canonical registry.
- The track should preserve compatibility with the existing monthly publication
  and GitHub project evidence pattern.

## Acceptance Criteria

- Every additional candidate family has an explicit approve, defer, or exclude
  decision.
- Approved candidates have config, fixtures, rights review, and parser-risk
  scaffolding ready for implementation.
- The repo can produce a coverage report showing which families remain open and
  why.
- The candidate ledger distinguishes canonical sources from validation-only
  mirrors and from out-of-scope sources.

## Out Of Scope

- Automatic promotion of candidate sources without review.
- Private or access-controlled source extraction.
- Changing the current active registry simply because a candidate exists.
- Publication workflow changes that are unrelated to source expansion.
