# Phase 8 Protected Zenodo Handoff Evidence

Captured: 2026-07-02

## Full Workflow Handoff Run

- Run URL: `https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/runs/28558066846`
- GitHub issue evidence: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861278867`
- Head commit: `6c6157a778742c0f63ed4d3a6e9eb7b2f3165d0e`
- Dispatch mode: `publication_mode=full`
- Archive version: `2026.07.0`
- Existing Zenodo deposition: `21119990`
- Result: success

Verified downloaded artifact evidence:

- `huggingface_publish_evidence.revision`: `154f2e06336b4a77839eb3ec23252d86cfa53e2b`
- `huggingface_publish_evidence.remote_manifest_verified`: `true`
- `zenodo_draft_evidence.uploaded`: `true`
- `zenodo_draft_evidence.deposition_id`: `21119990`
- `zenodo_draft_evidence.record_url`: `https://zenodo.org/deposit/21119990`
- `zenodo_draft_evidence.uploaded_files`: 9
- `zenodo_draft_evidence.publish_handoff_only`: `true`
- `zenodo_draft_evidence.doi`: empty; production DOI not published.
- `zenodo_draft_evidence.concept_doi`: empty; production DOI not published.
- `release_evidence.quality.record_count`: 5
- `release_evidence.collection_quality_gates.status`: `pass`

## Protected Handoff Job

Job: `Protected Zenodo Publish Handoff`

Verified log statements:

```text
Zenodo draft upload is complete.
Production DOI publication remains a human-approved protected-environment action.
Review zenodo_draft_evidence.json and publish from Zenodo only after approval.
```

The workflow exercised the production handoff boundary without publishing the
Zenodo DOI. Final DOI publication remains a manual Zenodo action after human
review of the draft evidence.
