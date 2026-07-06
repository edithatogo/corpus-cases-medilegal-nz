# Specification: Live Historical Corpus Completion And Rights Review

## Overview

Close the remaining gap between a complete archive pipeline and a substantively complete New Zealand medicolegal corpus. This track converts fixture-backed source proof into live, reproducible, source-by-source historical verification, rights review, parser replacement, candidate-source triage, and release/project evidence.

The track must not claim that all cases are archived until live source-index verification, rights review, parser proof, historical backfill, and release evidence all pass for the relevant source.

## Functional Requirements

- Create live source-index fetchers for all 13 active sources and archive the raw inputs where redistribution and technical access allow.
- Preserve offline replay by hash so live verification can be reproduced from archived evidence without network access.
- Normalize expected-record ledgers from live source-index evidence and reconcile them against processed records.
- Block public completeness claims for failed fetches, access barriers, unresolved rights review, unresolved parser risk, or unreconciled source gaps.
- Populate source terms, attribution, redistribution status, privacy caveats, citation guidance, known exclusions, and takedown contacts for every active source.
- Replace generic parsers for the seven high-risk sources: `moj_tribunals`, `royal_commissions`, `coronial`, `ombudsman`, `moj_courts`, `ipca`, and `law_commission`.
- Keep `hdc`, `hpdt`, `era`, `teachers`, `privacy`, and `human_rights` at review-level parser proof until live selector-drift checks pass.
- Triage the five candidate source groups into `approved`, `deferred`, or `excluded`: ACC appeals/reviews, other professional councils, Mental Health Review Tribunal, NZLII health/privacy/discipline subsets, and health appellate court filters.
- Give approved candidate sources source config, fixture contracts, live verification, rights ledger entries, and parser-risk status before canonical publication.
- Publish verified release evidence through the existing GitHub, Hugging Face, and Zenodo monthly archive surfaces.
- Mirror issue and project evidence into the repository roadmap project and Rare Insights on Open Policy from Aotearoa meta-project.

## Non-Functional Requirements

- No default CI job may depend on live network access for success.
- Live verification must be explicit, rate-limited, retry-safe, and blocker-aware.
- Large raw evidence belongs in release, Hugging Face, or Zenodo artifacts rather than Git.
- Public claims must be generated from evidence ledgers rather than hand-maintained prose.
- Rights and privacy posture must remain conservative until source evidence supports promotion.
- The implementation must remain compatible with existing monthly publication, source verification, maturity, mirror, and RIOPA sync workflows.

## Acceptance Criteria

- The track is registered in `conductor/tracks.md`.
- A parent GitHub issue and seven project-linked subissues exist with deterministic sync markers.
- Live source verification reports archived input evidence or explicit blockers for all active sources.
- Rights review no longer reports `needs-review` without a source-specific reason and next action.
- High-risk generic-parser sources have source-specific parser proof or remain explicit blockers.
- Candidate sources have durable `approved`, `deferred`, or `excluded` decisions with rationale.
- Historical backfill evidence reconciles expected live source records against processed records.
- Release evidence includes source-level completeness, rights, parser, candidate-source, and unresolved-gap status.
- Strict publication readiness prevents complete-corpus claims while any active source remains unresolved.

## Out Of Scope

- Circumventing authentication, paywalls, robots restrictions, anti-bot controls, or source terms.
- Treating fixture minima as historical completeness.
- Making OSF a canonical archive mirror.
- Claiming all NZ medicolegal cases are archived without live source-index evidence.
