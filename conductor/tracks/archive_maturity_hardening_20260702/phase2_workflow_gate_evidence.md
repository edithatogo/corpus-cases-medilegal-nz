# Phase 2 Workflow Attachment And Strict Gate Evidence

## Summary

Phase 2 attaches the maturity artifact to the monthly publication workflow and
adds a strict gate for canonical publication runs.

## Implementation

- Updated `.github/workflows/monthly_dynamic_archive_publication.yml`.
- Added a GitHub release evidence overlay file to the publication artifact set.
- Generated the archive maturity report after Hugging Face and Zenodo evidence
  exists.
- Included `generated/archive-intelligence/**` in workflow artifacts and release
  attestation subjects.
- Uploaded `generated/archive-intelligence/archive_maturity.json` as a GitHub
  release asset.
- Gated the GitHub release overlay step so dry-run runs do not fabricate live
  release proof.

## Verification

Commands:

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_intelligence.py tests/test_monthly_publication_workflow.py -q
uv run --frozen --python 3.12 --extra dev ruff check src\corpus_cases_medilegal_nz\archive_intelligence.py src\corpus_cases_medilegal_nz\cli.py scripts\build_archive_intelligence.py tests\test_archive_intelligence.py tests\test_monthly_publication_workflow.py
```

Results:

- `pytest`: `11 passed`.
- `ruff check`: passed.

Workflow assertions now cover:

- `Build GitHub release evidence overlay`
- `env.PUBLICATION_MODE != 'dry-run'`
- `Build archive maturity report`
- `--artifact-dir "$ARTIFACT_DIR"`
- `--strict`
- `generated/archive-intelligence/**`
- `archive_maturity.json`

The release step now has the full evidence bundle available before the GitHub
release upload occurs, so a full publication run can fail closed if maturity is
below `100`.
