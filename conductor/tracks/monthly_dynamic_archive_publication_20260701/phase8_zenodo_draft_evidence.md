# Phase 8 Zenodo Draft Evidence

Captured: 2026-07-02

## Live Zenodo Draft Upload

- Run URL: `https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/runs/28557891130`
- GitHub issue evidence: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861258383`
- Head commit: `5a767d63f90a886abca4691abf61593ac88aaa37`
- Dispatch mode: `publication_mode=zenodo-draft`
- Archive version: `2026.07.0`
- Result: success

Verified downloaded artifact evidence:

- `zenodo_draft_evidence.dry_run`: `false`
- `zenodo_draft_evidence.uploaded`: `true`
- `zenodo_draft_evidence.deposition_id`: `21119990`
- `zenodo_draft_evidence.record_url`: `https://zenodo.org/deposit/21119990`
- `zenodo_draft_evidence.doi`: empty draft DOI field; production DOI not published.
- `zenodo_draft_evidence.concept_doi`: empty draft concept DOI field; production DOI not published.
- `zenodo_draft_evidence.files`: 9
- `zenodo_draft_evidence.uploaded_files`: 9
- `zenodo_draft_evidence.publish_handoff_only`: `true`
- `release_evidence.quality.record_count`: 5
- `release_evidence.collection_quality_gates.status`: `pass`

## Publication Boundary

This step created/uploaded a Zenodo draft only. It did not publish a production
DOI record. Production publication remains a protected human-approved handoff.

## Compatibility Fix

Commit `5a767d6` keeps the canonical `ZENODO_ACCESS_TOKEN` path but also accepts
the existing repo secret alias `ZENODO_TOKEN` for compatibility with the
parallel archive setup.
