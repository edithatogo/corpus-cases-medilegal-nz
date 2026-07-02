# Phase 8 GitHub Actions Dry-Run Evidence

Captured: 2026-07-02

## Corrected Dry Run

- Run URL: `https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/runs/28557667012`
- GitHub issue evidence: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861228232`
- Head commit: `21968e692895c8d1e6de6463fbac8999903410db`
- Dispatch mode: `publication_mode=dry-run`
- Archive version: `2026.07.0`
- Result: success

Verified downloaded artifact evidence:

- `release.archive_version`: `2026.07.0`
- `quality.record_count`: 5
- `collection_quality_gates.status`: `pass`
- `source_collection_audit.stage_counts.validated_records`: 5
- `huggingface_publish_evidence.dry_run`: `true`
- `zenodo_draft_evidence.dry_run`: `true`
- `zenodo_draft_evidence.publish_handoff_only`: `true`

## Defect Found And Fixed

Initial dry-run run `28557593684` succeeded mechanically, but its downloaded
`release_evidence.json` reported `quality.record_count=0` and
`collection_quality_gates.status=blocked`.

Root cause: the GitHub Actions workflow built release evidence before creating
`data/processed/jsonl/records.jsonl`.

Fix: commit `21968e6` added a `Build deterministic collection proof` step before
`Build release evidence`, with a workflow ordering regression test.

## Local Validation

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_monthly_publication_workflow.py tests/test_archive_release.py tests/test_collection_proof.py -q
uv run --frozen --python 3.12 --extra dev ruff check tests/test_monthly_publication_workflow.py
```

Result:

- `15 passed`
- Ruff check passed.
