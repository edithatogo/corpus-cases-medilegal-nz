# Phase 6 Collection Proof Evidence

Captured: 2026-07-03T19:32:30+10:00

## Non-Zero Collection Proof

Command:

```powershell
uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli collection-proof
```

Result:

- `record_count`: 13
- `collection_quality_gates.status`: `pass`
- Fixture-backed sources:
  - `hdc`: 1 record
  - `hpdt`: 1 record
  - `moj_tribunals`: 1 record
  - `era`: 1 record
  - `teachers`: 1 record
  - `privacy`: 1 record
  - `human_rights`: 1 record
  - `ombudsman`: 1 record
  - `ipca`: 1 record
  - `law_commission`: 1 record
  - `royal_commissions`: 1 record
  - `coronial`: 1 record
  - `moj_courts`: 1 record

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

- `validated_records`: 13
- HDC, HPDT, MoJ Tribunals, ERA, Teachers, Privacy Commissioner, Human Rights Commission/Tribunal, Ombudsman Reports, IPCA, Law Commission, Royal Commissions & Waitangi Tribunal, Coronial Decisions, and MoJ Court Cases are all classified as `validated_records`.

## Validation

Commands run for the Phase 5/6 implementation:

```powershell
uv run --frozen --python 3.12 --extra dev pytest tests/test_collection_proof.py tests/test_source_fixtures.py tests/test_medilegal_parser.py tests/test_source_adapter_parser_integration.py tests/test_extended_source_adapters.py tests/test_archive_release.py tests/test_archive_intelligence.py tests/test_sources/test_source_adapters.py tests/test_sources/test_sources_registry.py -q
uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli collection-proof
uv run --frozen --python 3.12 --extra dev python -m corpus_cases_medilegal_nz.cli source-audit
```

Result:

- `161 passed`
- `collection-proof` generated 13 fixture-backed records.
- `source-audit` reported 13 `validated_records` and 0 `planned`.

## GitHub Issue And Project Evidence

Issue:

- `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1`
- `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861166064`

The issue remains the project-linked evidence anchor for this collection proof and monthly archive hardening work.
