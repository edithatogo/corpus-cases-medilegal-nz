# Source Parser Delegation Contract

`corpus-cases-medilegal-nz` owns source configuration, raw fetch orchestration,
processed corpus exports, release evidence, and public archive publication.
`nlp-policy-nz` owns reusable parser logic when parser code should be shared
across legal NZ corpora.

The contract is machine-readable through:

```powershell
uv run python -m corpus_cases_medilegal_nz.cli parser-contract
```

Release builds also write:

```text
manifests/parser_contract.json
```

## Input Contract

Source adapters pass a mapping with these required fields:

- `source_id`: source identifier such as `hdc`, `hpdt`, `moj_tribunals`, `era`,
  or `teachers`.
- `url`: source URL for the fetched document or listing.
- `content`: raw fetched content as text, extracted text, or bytes decoded by
  the adapter before delegation.
- `content_type`: one of `text/html`, `application/pdf`, or `text/plain`.

Adapters may include optional fetch and provenance metadata, including
`retrieved_at`, `raw_sha256`, `http_status`, and `headers`.

## Output Contract

Parsers return `list[dict]`. Each record must contain:

- `case_id`
- `source`
- `title`
- `date`
- `text`
- `metadata`

The `metadata` object should include:

- `url`
- `retrieved_at`
- `parser_name`
- `parser_version`
- `raw_sha256`

Output records must be compatible with `ExportableCase` and the
`data/processed/jsonl/records.jsonl` release evidence path.

## Error Semantics

Recoverable parser outcomes:

- reachable page with no supported decisions
- empty listing page
- known source layout gap that should be reported but not crash the whole run

Blocking parser outcomes:

- unsupported content type
- malformed required input
- output records missing required fields
- source mismatch between adapter and parser record
- non-dict metadata

Blocking failures should be represented by a typed exception or diagnostic that
source-specific adapters can convert into source-scoped evidence.

## Version Compatibility

The contract version is `1.0.0`.

Changes are backwards-compatible until `PARSER_CONTRACT_VERSION` changes.
Any breaking change must update this document, `parser_contract.py`, release
evidence fixtures, and source adapter tests in the same track.
