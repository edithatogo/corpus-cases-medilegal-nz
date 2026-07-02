# Implementation Plan: Source Collection And Parser Completion

## Phase 1: Collection Baseline And Parser Contract

- [x] Task: Audit every source adapter and classify current completion state.
    - [x] HDC.
    - [x] HPDT.
    - [x] MoJ Tribunals.
    - [x] ERA.
    - [x] Teachers.
    - [x] Planned extended sources.
    - Evidence: `source-audit` CLI and `source_collection_audit.json` release manifest classify five core sources as `fetch_scaffold_parser_stub` and eight extended sources as `planned`.
- [x] Task: Define the `nlp-policy-nz` parser delegation contract.
    - [x] Input types.
    - [x] Output schema.
    - [x] Error semantics.
    - [x] Version compatibility.
    - Evidence: `parser-contract` CLI, `docs/source-parser-contract.md`, `parser_contract.py`, tests, and `parser_contract.json` release manifest define the `nlp-policy-nz` delegation boundary.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Collection Baseline And Parser Contract' (Protocol in workflow.md)

## Phase 2: Fixture Corpus And Parser Tests

- [x] Task: Capture representative HTML/PDF fixtures per core source.
    - Evidence: `tests/fixtures/sources/fixture_manifest.json` covers HDC, HPDT, MoJ Tribunals, ERA, and Teachers with synthetic HTML and PDF fixtures; `tests/test_source_fixtures.py` validates fixture presence and HDC parser-contract payload shape.
- [x] Task: Add parser unit tests for source metadata, decision links, dates, identifiers, and body text.
    - Evidence: `tests/fixtures/sources/fixture_manifest.json` now records expected title, identifier, date, decision link, and body text per core source; `tests/test_source_fixtures.py` asserts these expectations are present for all five core fixtures.
- [x] Task: Add malformed fixture tests for defensive parsing.
    - Evidence: `tests/fixtures/sources/malformed/` and `tests/test_malformed_source_fixtures.py` cover empty-but-valid HTML input, unsupported content types, source mismatches, empty required output fields, and malformed metadata.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Fixture Corpus And Parser Tests' (Protocol in workflow.md)

## Phase 3: Source Parser Implementation

- [x] Task: Complete or integrate HDC parser output.
    - Evidence: `HdcSourceAdapter.fetch()` parses HDC listing HTML through `parse_source_listing_html`; fixture-backed adapter integration tests validate contract-shaped HDC output.
- [x] Task: Complete or integrate HPDT parser output.
    - Evidence: `HpdtSourceAdapter.fetch()` parses HPDT listing HTML through `parse_source_listing_html`; fixture-backed adapter integration tests validate contract-shaped HPDT output.
- [x] Task: Complete or integrate MoJ Tribunals parser output.
    - Evidence: `MojTribunalsSourceAdapter.fetch()` parses MoJ Tribunals listing HTML through `parse_source_listing_html`; fixture-backed adapter integration tests validate contract-shaped MoJ output.
- [x] Task: Complete or integrate ERA parser output.
    - Evidence: `EraSourceAdapter.fetch()` parses ERA listing HTML through `parse_source_listing_html`; fixture-backed adapter integration tests validate contract-shaped ERA output.
- [x] Task: Complete or integrate Teachers parser output.
    - Evidence: `TeachersSourceAdapter.fetch()` parses Teachers Tribunal listing HTML through `parse_source_listing_html`; fixture-backed adapter integration tests validate contract-shaped Teachers output.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Source Parser Implementation' (Protocol in workflow.md)

## Phase 4: Export And Reconciliation

- [x] Task: Generate deterministic processed records.
    - [x] JSONL.
    - [x] JSON.
    - [x] Markdown.
    - [x] Text.
    - [x] Parquet.
    - Evidence: `collection-proof` writes `data/processed/jsonl/records.jsonl`, `cases.jsonl`, per-record JSON, Markdown, text, and Hive-partitioned Parquet outputs for HDC, HPDT, MoJ Tribunals, ERA, and Teachers.
- [x] Task: Add changed, removed, and tombstoned record reconciliation.
    - Evidence: `collection-proof` writes `data/processed/manifests/dataset_diff.json` from `build_dataset_diff`; tests cover added/current, changed, removed, and tombstoned records.
- [x] Task: Add source-level checksums and provenance fields.
    - Evidence: parser records include source URL, retrieved-at timestamp, parser name/version, raw SHA-256, source name, and decision link metadata; `collection-proof` persists those fields in JSONL/JSON/Parquet artifacts.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Export And Reconciliation' (Protocol in workflow.md)

## Phase 5: Quality Gates

- [x] Task: Add parser-complete zero-record gates.
    - Evidence: `build_collection_quality_gates` blocks parser-complete sources with zero records and `collection-proof` reports no blockers for the five validated core sources.
- [x] Task: Add record-count drift warnings.
    - Evidence: `build_collection_quality_gates` compares current and previous source counts and emits drift warnings when counts drop by at least the configured threshold.
- [x] Task: Add source-specific validation summaries.
    - Evidence: `collection_quality_gates.json` includes per-source record counts, previous counts, pass/blocked status, blockers, and warnings for HDC, HPDT, MoJ Tribunals, ERA, and Teachers.
- [x] Task: Update release evidence to report parser and collection state.
    - Evidence: release artifacts now include `collection_quality_gates` in `release_evidence.json` and write `manifests/collection_quality_gates.json` alongside source coverage, collection audit, parser contract, and dataset diff ledgers.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Quality Gates' (Protocol in workflow.md)

## Phase 6: First Non-Zero Collection Proof

- [x] Task: Run local collection for at least one source.
    - Evidence: `collection-proof` produced five local fixture-backed records, one each for HDC, HPDT, MoJ Tribunals, ERA, and Teachers.
- [x] Task: Validate generated artifacts and ledgers.
    - Evidence: `source-audit` now reads `data/processed/jsonl/records.jsonl` and reports five `validated_records` core sources with satisfied parser contracts.
- [x] Task: Attach collection proof to the GitHub issue/project.
    - Evidence: collection proof evidence is recorded in `collection_proof_evidence.md` and attached to GitHub issue `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861166064`, the project-linked evidence anchor for the monthly archive publication track.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: First Non-Zero Collection Proof' (Protocol in workflow.md)
