# Implementation Plan: Additional Candidate Source Triage And Coverage Expansion

## Phase 1: Candidate Inventory And Scope Boundaries

- [ ] Task: Build a candidate inventory for additional medicolegal coverage.
    - [ ] ACC appeals/reviews and older ACCDCR decisions.
    - [ ] Social Security Appeal Authority and medical appeals.
    - [ ] Public professional-discipline mirror pages for Medical, Dental,
      Pharmacy, and Teaching councils.
    - [ ] Health-related Court of New Zealand filters and case-summary pages.
    - [ ] Mental Health Review Tribunal material if public.
- [ ] Task: Define canonical, candidate, validation-only, and excluded source
  classes.
    - [ ] Ensure the active registry stays unchanged until approval.
    - [ ] Record why adjacent sources are excluded or deferred.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Candidate Inventory And Scope Boundaries' (Protocol in workflow.md)

## Phase 2: Rights, Privacy, And Triage Decisions

- [ ] Task: Add rights and privacy notes for each candidate family.
    - [ ] Terms and attribution.
    - [ ] Redistribution posture.
    - [ ] Takedown contact.
    - [ ] Privacy caveats.
    - [ ] Citation guidance.
- [ ] Task: Classify each candidate family.
    - [ ] Approved.
    - [ ] Deferred.
    - [ ] Excluded.
- [ ] Task: Add tests for the candidate decision matrix and blocker reasons.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Rights, Privacy, And Triage Decisions' (Protocol in workflow.md)

## Phase 3: Approved Candidate Scaffolds

- [ ] Task: Add config and fixture contracts for approved candidates.
    - [ ] Include source identifiers and stable URLs.
    - [ ] Keep approved candidates separate from the active registry until
      promotion is explicitly triggered.
- [ ] Task: Add parser-risk and live-verification scaffolding for approved
  candidates.
    - [ ] Live fetch and hash archival.
    - [ ] Expected-record normalization.
    - [ ] Reconciliation summaries.
- [ ] Task: Add tests for approved-candidate promotion gating.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Approved Candidate Scaffolds' (Protocol in workflow.md)

## Phase 4: Coverage Reporting And Project Evidence

- [ ] Task: Add coverage reporting for candidate families.
    - [ ] Approved, deferred, and excluded counts.
    - [ ] Redundant-source availability for each family.
    - [ ] Remaining gaps and recommended next steps.
- [ ] Task: Add GitHub issue and project evidence for candidate decisions.
    - [ ] Parent issue.
    - [ ] Subissues per candidate family.
- [ ] Task: Add release-safe summaries for the candidate ledger.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Coverage Reporting And Project Evidence' (Protocol in workflow.md)
