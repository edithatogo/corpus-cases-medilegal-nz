# Specification: Live Source Verification And Reproducible Evidence Archiving

## Overview

Create a verification lane that proves whether the corpus has archived all available cases, findings, decisions, and reports for each configured source. The lane must begin with a feasibility phase that identifies what can be verified immediately from public source indexes or alternate datasets, what requires manual access or legal review, and what is technically blocked.

Where alternate verification datasets are used, the pipeline should download and archive those inputs as first-class evidence artifacts rather than relying on hand-maintained prose or transient external references. The result should be reproducible: another operator should be able to rerun the verification workflow and inspect the archived source-index evidence, comparison ledgers, blockers, and publication evidence.

## Sources In Scope

- Health and Disability Commissioner decisions.
- Health Practitioners Disciplinary Tribunal decisions.
- Ministry of Justice tribunals decisions.
- Employment Relations Authority determinations.
- Teachers Disciplinary Tribunal decisions.
- Privacy Commissioner decisions, case notes, investigations, and public determinations.
- Human Rights Commission and Human Rights Review Tribunal decisions.
- Ombudsman reports and findings.
- Independent Police Conduct Authority reports.
- Law Commission reports and statutory recommendations.
- Royal Commissions of Inquiry and Waitangi Tribunal reports.
- Coronial decisions and Coroners Court cases.
- Broader Ministry of Justice courts and judicial decisions.

## Functional Requirements

- Add a source-verification feasibility inventory for every configured source.
- Classify each verification input as immediately available, available with restrictions, blocked, deprecated, or excluded.
- Download and archive public source indexes, feeds, sitemaps, search exports, APIs, and alternate datasets where licensing and technical access allow.
- Preserve archived verification inputs with checksums, retrieval timestamps, canonical URLs, HTTP metadata, content type, byte count, and rights notes.
- Build source-specific verification adapters that normalize verification inputs into comparable expected-record ledgers.
- Reconcile expected-record ledgers against processed corpus records by stable identifiers, canonical URLs, dates, titles, and source-specific aliases.
- Emit completeness results per source: matched, missing, extra, duplicate, ambiguous, excluded, blocked, and manually-review-required.
- Promote source target confidence only from archived evidence-backed inputs such as official source indexes, source APIs, authoritative exported datasets, or independently archived source manifests.
- Keep baseline-minimum fixture targets separate from verified historical completeness.
- Generate public-safe verification reports for GitHub release assets, Hugging Face dataset cards, Zenodo metadata, README claims, and Conductor review evidence.
- Integrate the verification workflow with existing monthly publication, source maturity, release readiness, mirror readiness, and archive maturity evidence.

## Reproducible Evidence Archiving Requirements

- Store archived verification inputs under a deterministic evidence layout that is safe for Git, GitHub release artifacts, Hugging Face datasets, and Zenodo snapshots.
- Prefer small normalized ledgers in Git and large raw verification archives in release/Hugging Face/Zenodo artifacts.
- Include a verification-source manifest that records source URL, fetch method, license/terms status, redistribution status, content hash, normalized record count, and parser version.
- If an alternate data source is used to verify a public source, archive the alternate data source itself when permitted.
- If direct archiving is not permitted, archive only reproducible metadata: URL, citation, access instructions, checksum where available, retrieval proof, and exclusion reason.

## Feasibility Classification

Each source must receive:

- `verification_status`: `immediately_available`, `partially_available`, `blocked`, `manual_review_required`, or `excluded`.
- `evidence_type`: official index, official API, sitemap, static HTML, PDF index, CSV/export, third-party archive, web archive, manual sample, or unavailable.
- `archiving_policy`: archive raw, archive normalized only, metadata-only, no-archive legal blocker, or no-archive technical blocker.
- `blockers`: authentication, robots/terms, rate limiting, anti-bot, search-only pagination, dynamic JavaScript, missing historical index, unclear redistribution, privacy/redaction risk, or source outage.
- `next_action`: implement adapter, request permission, manual export, browser-assisted proof, official information request, or exclude with rationale.

## Non-Functional Requirements

- Verification must be deterministic where inputs are archived.
- Networked verification must be rate-limited, retry-safe, and resumable.
- Public claims must be generated from evidence ledgers, not manually edited prose.
- The workflow must avoid secrets in artifacts, logs, or archived pages.
- Verification should work offline against archived evidence bundles after the fetch phase has completed.
- CI should run no-network fixture tests by default and allow explicit manual/scheduled live verification jobs.
- Evidence must align with sibling archive patterns: GitHub for code and lightweight ledgers, Hugging Face for mutable operational datasets, Zenodo for immutable DOI snapshots, and Codeberg/GitLab for Git mirrors.

## Acceptance Criteria

- A feasibility report exists for every configured source and distinguishes immediately available verification inputs from blockers.
- Publicly reusable verification inputs are downloaded, checksummed, and archived into a reproducible evidence bundle.
- Verification adapters produce expected-record ledgers for all immediately available sources.
- Completeness reconciliation compares expected records with processed corpus records and emits per-source gaps.
- Source maturity target confidence is promoted only when backed by archived source-index evidence.
- Monthly publication artifacts include verification evidence and clear blockers.
- Release readiness can report: verified complete, verified incomplete, blocked by source access, or not yet verified.
- Tests cover feasibility classification, evidence downloading, manifest generation, archived-input replay, reconciliation, blocker handling, and public claim generation.

## Out Of Scope

- Claiming complete historical coverage without archived source-index evidence.
- Circumventing authentication, paywalls, robots restrictions, anti-bot controls, or source terms.
- Making OSF a canonical archive mirror.
- Replacing the existing monthly publication workflow rather than extending its evidence inputs.
