# Phase 3 Source Observability And Anomaly Detection Evidence

## Summary

This phase adds the source-observability ledger, anomaly detection, and the
bundle writer that publishes archive-intelligence outputs alongside the monthly
release evidence.

## Implementation

- Added `build_source_observability_ledger`.
- Added `build_archive_anomaly_report`.
- Added `build_archive_intelligence_bundle` and
  `write_archive_intelligence_bundle`.
- Added the standalone bundle script at
  `scripts/build_archive_intelligence_bundle.py`.
- Updated the monthly publication workflow to generate and upload the new
  archive-intelligence bundle outputs.

## Verification

Commands:

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_intelligence.py tests/test_monthly_publication_workflow.py -q
uv run --frozen --python 3.12 --extra dev ruff check src\corpus_cases_medilegal_nz\archive_intelligence.py scripts\build_archive_intelligence_bundle.py tests\test_archive_intelligence.py tests\test_monthly_publication_workflow.py
uv run --frozen --python 3.12 --extra dev ruff format --check src\corpus_cases_medilegal_nz\archive_intelligence.py scripts\build_archive_intelligence_bundle.py tests\test_archive_intelligence.py tests\test_monthly_publication_workflow.py
```

Results:

- `pytest`: `16 passed`.
- `ruff check`: `All checks passed!`
- `ruff format --check`: `4 files already formatted`.
