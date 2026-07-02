# Phase 1 Publication Evidence Overlay

## Summary

Phase 1 wires the archive maturity model to the monthly artifact directory so
the report can see live publication overlays instead of only the pre-publication
release evidence file.

## Implementation

- Added artifact-directory scoring helpers in `src/corpus_cases_medilegal_nz/archive_intelligence.py`.
- Added support for Hugging Face, Zenodo, GitHub release, and metadata-manifest overlays.
- Added strict-mode validation helpers for publication gating.
- Added `scripts/build_archive_intelligence.py` support for `--artifact-dir`.
- Added a CLI path for `archive-intelligence --artifact-dir`.

## Verification

Commands:

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_intelligence.py tests/test_monthly_publication_workflow.py -q
uv run --frozen --python 3.12 --extra dev ruff check src\corpus_cases_medilegal_nz\archive_intelligence.py src\corpus_cases_medilegal_nz\cli.py scripts\build_archive_intelligence.py tests\test_archive_intelligence.py tests\test_monthly_publication_workflow.py
uv run --frozen --python 3.12 --extra dev ruff format --check src\corpus_cases_medilegal_nz\archive_intelligence.py src\corpus_cases_medilegal_nz\cli.py scripts\build_archive_intelligence.py tests\test_archive_intelligence.py tests\test_monthly_publication_workflow.py
```

Results:

- `pytest`: `11 passed`.
- `ruff check`: passed.
- `ruff format --check`: passed.

Evidence from the unit tests confirms:

- A synthetic artifact directory with release, Hugging Face, Zenodo, and GitHub
  release overlays produces a `100`-score maturity report.
- Strict mode rejects partial reports.
- Sibling metadata-manifest fallback still works when the release evidence file
  does not embed metadata packages directly.
