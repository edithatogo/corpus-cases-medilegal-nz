# Privacy, Takedown, And Redaction Governance

This repository publishes public legal and medicolegal material with explicit
privacy and rights guardrails. The archive is evidence-backed, but it does not
claim to have anonymized, de-identified, or rights-cleared material beyond the
source publication.

## Intake

- Public takedown, correction, and redaction requests are opened through the
  GitHub issue/contact path used by the repository.
- The resulting request is normalized into a privacy event ledger for release
  evidence.
- Requester identity is not copied into release artifacts.

## Triage

- Acknowledge requests within 2 business days.
- Classify the request as one of:
  - `takedown`
  - `correction`
  - `redaction`
  - `exclusion`
  - `note`
- Mark the request as release-blocking when it could affect a canonical monthly
  publication.

## Redaction And Exclusion

- Prefer the minimum public-safe change required to preserve auditability.
- Use tombstones for removed records when a public trail is still needed.
- Exclude records when the source terms or privacy posture do not support
  publication.
- Keep corrections and tombstones in the redaction/exclusion ledger so the next
  monthly release can reconcile them deterministically.

## Publication Gate

- Canonical publication is blocked while any release-blocking privacy event is
  unresolved.
- Dry-run and local validation can still report the ledger, but they do not
  bypass unresolved blockers.

## Reissue

- Substantive corrections or takedowns that affect public outputs require a new
  monthly archive version.
- The release evidence must carry the privacy governance ledger, the
  redaction/exclusion ledger, and the legal provenance notes.

## Privacy Evidence Files

The monthly publication workflow writes these files into the release evidence
set:

- `manifests/privacy_governance.json`
- `manifests/redaction_exclusion_ledger.json`
- `manifests/legal_provenance.json`

