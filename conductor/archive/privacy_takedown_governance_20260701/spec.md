# Specification: Privacy, Takedown, And Redaction Governance

## Overview

Create an operational privacy and takedown governance layer for public medical-legal corpora, with evidence-backed rights, attribution, de-anonymisation, redaction, and removal workflows.

The archive publication track records legal/provenance ledgers, but this track turns those ledgers into repeatable operational governance.

## Requirements

- Create source-specific rights and redistribution decision records.
- Define a takedown contact, intake channel, triage process, and SLA.
- Add de-anonymisation and sensitive-health-information risk scoring.
- Add redaction and exclusion ledgers that preserve auditability without republishing removed sensitive content.
- Add public-facing takedown and correction documentation.
- Add release-blocking checks for unresolved high-risk privacy issues.
- Add citation and attribution guidance that avoids overclaiming legal status.
- Add rollback and reissue procedures for releases affected by takedown or correction.
- Align privacy governance with GitHub, Hugging Face, Zenodo, and any optional OSF surfaces.

## Non-Functional Requirements

- Governance records must be auditable without exposing sensitive takedown details.
- Public claims must be generated from ledgers where possible.
- Removal and correction workflows must preserve DOI immutability by issuing new versions rather than mutating published snapshots.
- The approach must be compatible with sibling corpus repositories.

## Acceptance Criteria

- A takedown policy and workflow exists in the repository.
- Legal/privacy ledgers include source terms, attribution, redistribution status, privacy notes, known exclusions, and takedown state.
- Publication readiness fails or warns on unresolved high-risk privacy blockers.
- Release evidence records whether a release contains known exclusions, corrections, or tombstones.
- A simulated takedown/correction test proves the workflow can produce a new evidence trail.

## Out Of Scope

- Providing legal advice.
- Removing already published third-party source material from its original host.
- Publishing private complainant/requester details.
- Making production removals without user approval.
