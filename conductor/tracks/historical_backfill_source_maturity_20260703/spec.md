# Specification: Historical Backfill And Source Maturity

## Overview

Create a follow-on implementation track that moves the corpus from 13 fixture-backed, parser-validated sources to live historical collection completeness with source-by-source evidence.

The completed source parser work proves that every registered source can produce normalized records and release evidence. This track prevents that proof from being overstated as "all cases archived" until live source-depth backfill, reconciliation, rights review, and publication evidence show that claim is true.

## Current State

- `source-audit` reports 13 sources at `validated_records`.
- `data/processed/jsonl/records.jsonl` contains 13 deterministic proof records, one per registered source.
- Monthly publication, archive maturity, governance, GitHub project sync, and multi-mirror tracks exist.
- GitHub, Hugging Face, and Zenodo publication evidence exists for earlier monthly archive proof, but it must be rerun after the 13-source expansion.
- Remaining external governance items include GitHub mirror secret verification, OSF inactive policy, protected Zenodo production publication, and a documented RIOPA mirror-source option fallback.

## Requirements

- Add a stricter source maturity ladder that distinguishes parser proof from historical archive completion.
- Add a public-claims gate so README, dataset cards, release notes, and archive maturity reports cannot imply "all cases archived" unless historical completion evidence exists.
- Add per-source live backfill targets with expected count, fetched count, parsed count, excluded count, tombstoned count, latest source date, last successful crawl timestamp, source update cadence, and confidence level.
- Build a live completeness ledger that reconciles fetched, parsed, normalized, exported, excluded, tombstoned, and published records per source.
- Replace generic listing extraction with deeper source-specific parsers where live sites require it, prioritizing MoJ Tribunals, MoJ Courts/JDO, Ombudsman, IPCA, Law Commission, Royal Commissions/Waitangi Tribunal, and Coronial Decisions.
- Add a separate source-discovery queue for candidate sources so they are not treated as active registry sources until rights, availability, and parser scope are approved.
- Include initial candidate discovery entries for ACC appeal/review material, public professional council disciplinary material outside HPDT, public Mental Health Review Tribunal material if available, NZLII health/privacy/discipline subsets, and health-related Court of Appeal/Supreme Court filters.
- Rerun monthly archive publication after expanded source evidence is generated, capturing GitHub release assets, Hugging Face revision/readback, Zenodo draft evidence, archive maturity evidence, and source completeness reports.
- Close or explicitly gate governance gaps: mirror secrets, OSF activation policy, protected Zenodo DOI publication, and RIOPA mirror-source project field alignment.
- Add source-level legal, privacy, attribution, redistribution, takedown, de-identification, known-exclusion, and rights-review evidence.

## Additional Bleeding-Edge Scope

- Add resumable, idempotent backfill jobs with checkpoint cursors, batch manifests, retry/backoff, polite rate limiting, and site-specific crawl policies.
- Preserve raw HTTP provenance for each asset, including canonical URL, retrieval timestamp, HTTP status, content type, ETag, Last-Modified, raw SHA-256, parser version, and derived text hash.
- Add content-addressed raw storage and optional WARC-style capture metadata for future auditability.
- Add deduplication and canonicalization across sources where decisions or reports appear in more than one public surface.
- Add live smoke tests that verify source reachability and selector drift without depending on full historical crawls in CI.
- Add freshness and completeness SLOs per source, with alerts or issue/project evidence when a source falls behind.
- Generate public claim text from ledgers rather than hand-maintained prose.
- Add a release-blocking check for stale evidence, missing rights review, incomplete source maturity, or unverified remote manifest evidence.

## Non-Functional Requirements

- Live collection must be polite, resumable, deterministic, and diagnosable per source.
- CI must keep full historical crawls out of default tests while still validating fixtures, contracts, and lightweight live smoke checks.
- All public claims must be evidence-backed and conservative.
- New ledgers must align with sibling archive repositories and existing GitHub/Hugging Face/Zenodo release evidence formats.
- Source discovery must be review-gated before a candidate can become a registered active source.
- Rights and privacy posture must remain source-specific; the system must not infer redistribution clearance from public availability alone.

## Acceptance Criteria

- Source audit distinguishes `validated_records` from `historical_backfill_complete`.
- Every registered source has a backfill target row and live completeness summary.
- Public claims say "13 sources are parser validated" until historical completeness proof exists, and strict release mode fails if prose overclaims.
- Source-specific parser/live collection proof exists for high-risk sources that currently rely on generic listing extraction.
- Candidate sources are tracked in a separate discovery queue with review status, not silently added to the active registry.
- Monthly publication evidence is regenerated after expanded source maturity artifacts exist.
- GitHub release, Hugging Face, Zenodo, archive maturity, rights, and source completeness evidence all refer to the same manifest hash and source counts.
- Governance blockers are either closed with evidence or represented as intentional protected/manual gates.

## Out Of Scope

- Publishing a production Zenodo DOI without protected human approval.
- Activating OSF as a primary mirror.
- Making legal conclusions beyond source-specific evidence and conservative rights status.
- Guaranteeing historical completeness for a source whose public surface lacks enough evidence to establish a defensible target count.
