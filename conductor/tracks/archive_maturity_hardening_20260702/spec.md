# Specification: Archive Maturity Hardening

## Overview

Promote archive maturity from an internal diagnostic into a first-class release
artifact that is generated from the monthly publication artifact directory and
can reach a full `100` only after live GitHub, Hugging Face, and Zenodo proof
exists.

This track extends the existing archive intelligence work with the publication
overlay, strict release gating, and adjacent stretch hardening for observability,
claims generation, privacy scoring, and cross-repo compatibility.

## Requirements

- Generate a machine-readable archive maturity report from the monthly
  publication artifact directory, not only from the pre-publication release
  evidence file.
- Merge live publication evidence from the monthly workflow into the maturity
  report:
  - GitHub release URL proof.
  - Hugging Face revision and remote-manifest verification.
  - Zenodo draft or record proof.
  - Metadata-package evidence from the published artifact tree.
- Add a strict mode gate that fails canonical publication runs unless maturity
  reaches `100`.
- Attach the archive maturity report as a workflow artifact and release asset.
- Keep dry-run publication runs able to report partial maturity without failing
  the workflow.
- Add stretch hardening for:
  - source-level observability and drift warnings
  - anomaly detection
  - claims generation from ledgers
  - privacy/rights scoring
  - cross-repo compatibility with sibling archive repositories

## Non-Functional Requirements

- The report must be reproducible from committed code and workflow artifacts.
- Live publication proof must be read from the artifact directory, not from
  hand-maintained prose.
- Strict publication mode must fail closed when required live proof is missing.
- New outputs should remain compatible with the existing release evidence and
  project-sync ledgers.

## Acceptance Criteria

- The monthly publication workflow emits an archive maturity artifact.
- A full publication run can produce a maturity score of `100`.
- Dry-run runs still produce a report and can remain below `100`.
- Strict mode prevents canonical publication when live proof is incomplete.
- The maturity report can be consumed by GitHub release assets and future
  archive-intelligence consumers.

## Out Of Scope

- Building a hosted dashboard.
- Replacing the existing release evidence schema.
- Changing source redistribution policy without separate legal review.
