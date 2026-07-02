# Phase 1 Intelligence Model Evidence

## Summary

Phase 1 adds a deterministic archive maturity model that derives scores from
existing archive-family ledgers rather than hand-maintained claims.

## Implementation

- Added `src/corpus_cases_medilegal_nz/archive_intelligence.py`.
- Added `scripts/build_archive_intelligence.py`.
- Added `archive-intelligence` to the package CLI.
- Added `tests/test_archive_intelligence.py`.
- Updated release artifact generation so future `release_evidence.json` embeds
  the metadata package manifest.
- Added fallback loading of sibling `metadata/metadata_packages_manifest.json`
  so current monthly publication artifacts can be scored without regeneration.

## Scoring Dimensions

The model weights seven dimensions to 100 total points:

- Release evidence completeness: 15.
- Source coverage completeness: 15.
- Collection and parsing progress: 15.
- Metadata package completeness: 15.
- Public-surface consistency: 10.
- Security and provenance posture: 15.
- Remote publication proof: 15.

Severity thresholds:

- `leading`: 90-100.
- `strong`: 75-89.
- `developing`: 60-74.
- `fragile`: 40-59.
- `blocked`: 0-39.

## Local Report

Command:

```powershell
uv run --frozen --python 3.12 --extra dev python scripts\build_archive_intelligence.py --output generated\archive-intelligence\archive_maturity.json
```

Result summary:

- `score`: `88.0`.
- `severity`: `strong`.
- `blocking_dimensions`: `["remote_publication_proof"]`.
- All dimensions except `remote_publication_proof` scored `100`.

The remote publication proof gap is expected for the committed/generated local
release evidence snapshot because it does not contain the live Hugging Face
revision, GitHub release URL, or Zenodo draft/record identifiers captured in
the later live workflow evidence.

## Validation

Commands:

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_intelligence.py tests/test_archive_release.py -q
uv run --frozen --python 3.12 --extra dev ruff check src\corpus_cases_medilegal_nz\archive.py src\corpus_cases_medilegal_nz\archive_intelligence.py src\corpus_cases_medilegal_nz\cli.py scripts\build_archive_intelligence.py tests\test_archive_intelligence.py tests\test_archive_release.py
uv run --frozen --python 3.12 --extra dev ruff format --check src\corpus_cases_medilegal_nz\archive.py src\corpus_cases_medilegal_nz\archive_intelligence.py src\corpus_cases_medilegal_nz\cli.py scripts\build_archive_intelligence.py tests\test_archive_intelligence.py tests\test_archive_release.py
```

Results:

- `pytest`: `21 passed in 1.57s`.
- `ruff check`: `All checks passed!`.
- `ruff format --check`: `6 files already formatted`.
