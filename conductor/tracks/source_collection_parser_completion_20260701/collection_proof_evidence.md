# Phase 6 Collection Proof Evidence

Captured: 2026-07-02T10:34:06+10:00

## Non-Zero Collection Proof

Command:

```powershell
uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli collection-proof
```

Result:

- `record_count`: 5
- `collection_quality_gates.status`: `pass`
- Core parser-complete sources:
  - `hdc`: 1 record
  - `hpdt`: 1 record
  - `moj_tribunals`: 1 record
  - `era`: 1 record
  - `teachers`: 1 record

Generated local artifacts:

- `data/processed/jsonl/records.jsonl`
- `data/processed/jsonl/cases.jsonl`
- `data/processed/json/`
- `data/processed/markdown/`
- `data/processed/text/`
- `data/processed/parquet/`
- `data/processed/collection_proof.json`
- `data/processed/manifests/dataset_diff.json`
- `data/processed/manifests/collection_quality_gates.json`

## Source Audit Proof

Command:

```powershell
uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli source-audit
```

Result:

- `validated_records`: 5
- `planned`: 8
- HDC, HPDT, MoJ Tribunals, ERA, and Teachers are all classified as `validated_records`.

## Validation

Commands run for the Phase 5/6 implementation:

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_archive_release.py tests/test_collection_proof.py tests/test_source_adapter_parser_integration.py tests/test_medilegal_parser.py tests/test_parser_contract.py tests/test_malformed_source_fixtures.py tests/test_source_fixtures.py tests/test_sources/test_source_adapters.py tests/test_monthly_publication_workflow.py tests/test_publication_adapters.py -q
uv run --frozen --python 3.12 --extra dev ruff format --check src/corpus_cases_medilegal_nz/archive.py src/corpus_cases_medilegal_nz/collection_proof.py tests/test_archive_release.py tests/test_collection_proof.py
uv run --frozen --python 3.12 --extra dev ruff check src/corpus_cases_medilegal_nz/archive.py src/corpus_cases_medilegal_nz/collection_proof.py tests/test_archive_release.py tests/test_collection_proof.py
```

Result:

- `101 passed`
- Ruff format check passed.
- Ruff lint check passed.

## GitHub Issue And Project Evidence

Issue:

- `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1`
- `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861166064`

The issue remains the project-linked evidence anchor for this collection proof and monthly archive hardening work.
