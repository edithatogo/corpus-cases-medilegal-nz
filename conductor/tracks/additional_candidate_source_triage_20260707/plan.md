# Implementation Plan: Additional Candidate Source Triage And Coverage Expansion

## Phase 1: Candidate Inventory And Scope Boundaries

- [x] Task: Build a candidate inventory for additional medicolegal coverage.
    - [x] ACC appeals/reviews and older ACCDCR decisions.
    - [x] Social Security Appeal Authority and medical appeals.
    - [x] Public professional-discipline mirror pages for Medical, Dental,
      Pharmacy, and Teaching councils.
    - [x] Health-related Court of New Zealand filters and case-summary pages.
    - [x] Mental Health Review Tribunal material if public.
- [x] Task: Define canonical, candidate, validation-only, and excluded source
  classes.
    - [x] Ensure the active registry stays unchanged until approval.
    - [x] Record why adjacent sources are excluded or deferred.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Candidate Inventory And Scope Boundaries' (Protocol in workflow.md)

## Phase 2: Rights, Privacy, And Triage Decisions

- [x] Task: Add rights and privacy notes for each candidate family.
    - [x] Terms and attribution.
    - [x] Redistribution posture.
    - [x] Takedown contact.
    - [x] Privacy caveats.
    - [x] Citation guidance.
- [x] Task: Classify each candidate family.
    - [x] Approved.
    - [x] Deferred.
    - [x] Excluded.
- [x] Task: Add tests for the candidate decision matrix and blocker reasons.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Rights, Privacy, And Triage Decisions' (Protocol in workflow.md)

## Phase 3: Approved Candidate Scaffolds

- [x] Task: Add config and fixture contracts for approved candidates.
    - [x] Include source identifiers and stable URLs.
    - [x] Keep approved candidates separate from the active registry until
      promotion is explicitly triggered.
- [x] Task: Add parser-risk and live-verification scaffolding for approved
  candidates.
    - [x] Live fetch and hash archival.
    - [x] Expected-record normalization.
    - [x] Reconciliation summaries.
- [x] Task: Add tests for approved-candidate promotion gating.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Approved Candidate Scaffolds' (Protocol in workflow.md)

## Phase 4: Coverage Reporting And Project Evidence

- [x] Task: Add coverage reporting for candidate families.
    - [x] Approved, deferred, and excluded counts.
    - [x] Redundant-source availability for each family.
    - [x] Remaining gaps and recommended next steps.
- [x] Task: Add GitHub issue and project evidence for candidate decisions.
    - [x] Parent issue.
    - [x] Subissues per candidate family.
- [x] Task: Add release-safe summaries for the candidate ledger.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Coverage Reporting And Project Evidence' (Protocol in workflow.md)
