# Phase 4 Claims, Privacy, And Federation Evidence

## Summary

This phase adds ledgers for public claims, privacy and rights scoring, and
cross-repo federation compatibility.

## Implementation

- Added `build_privacy_rights_scoring`.
- Added `build_public_claims`.
- Added `build_federation_compatibility_report`.
- Wired the bundle writer to emit markdown claim artifacts and compatibility
  JSON.
- Extended workflow publication assets to include the generated claims,
  privacy, and federation outputs.

## Verification

Commands:

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_intelligence.py tests/test_monthly_publication_workflow.py -q
uv run --frozen --python 3.12 --extra dev ruff check src\corpus_cases_medilegal_nz\archive_intelligence.py scripts\build_archive_intelligence_bundle.py tests\test_archive_intelligence.py tests\test_monthly_publication_workflow.py
```

Results:

- `pytest`: `16 passed`.
- `ruff check`: `All checks passed!`
