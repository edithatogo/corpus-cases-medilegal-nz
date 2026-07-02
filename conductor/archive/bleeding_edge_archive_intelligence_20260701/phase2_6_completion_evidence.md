# Phases 2 to 6 Completion Evidence

## Summary

The bleeding-edge archive intelligence track now has complete coverage across
source observability, claims generation, anomaly detection, workflow telemetry,
and cross-repo compatibility.

## Implemented surfaces

- `src/corpus_cases_medilegal_nz/archive_intelligence.py`
  - source observability ledger
  - public claims generation
  - anomaly detection
  - federation compatibility report
- `src/corpus_cases_medilegal_nz/archive.py`
  - collection-stage ladder and quality gates
- `tests/test_archive_intelligence.py`
  - stub-parser and blocked-state coverage
  - configured/reachable/blocked crawlability coverage
  - claims, anomaly, and federation compatibility coverage
- `tests/test_monthly_publication_workflow.py`
  - workflow telemetry and archive-intelligence artifact coverage

## Validation

- `uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_intelligence.py -q`
- `uv run --frozen --python 3.12 --extra dev ruff check src\corpus_cases_medilegal_nz\archive_intelligence.py tests\test_archive_intelligence.py`
- `uv run --frozen --python 3.12 --extra dev ruff format --check src\corpus_cases_medilegal_nz\archive_intelligence.py tests\test_archive_intelligence.py`

## Notes

- The observability ladder distinguishes reachable, configured, stub/parser,
  validated, and blocked states via the source coverage and source audit
  ledgers.
- Public claims are generated from ledgers rather than maintained prose.
- The archive intelligence bundle emits the federation compatibility report,
  making the output suitable for sibling archive dashboards.
