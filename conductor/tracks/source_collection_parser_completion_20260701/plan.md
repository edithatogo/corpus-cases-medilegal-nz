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

- [ ] Task: Complete or integrate HDC parser output.
- [ ] Task: Complete or integrate HPDT parser output.
- [ ] Task: Complete or integrate MoJ Tribunals parser output.
- [ ] Task: Complete or integrate ERA parser output.
- [ ] Task: Complete or integrate Teachers parser output.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Source Parser Implementation' (Protocol in workflow.md)

## Phase 4: Export And Reconciliation

- [ ] Task: Generate deterministic processed records.
    - [ ] JSONL.
    - [ ] JSON.
    - [ ] Markdown.
    - [ ] Text.
    - [ ] Parquet.
- [ ] Task: Add changed, removed, and tombstoned record reconciliation.
- [ ] Task: Add source-level checksums and provenance fields.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Export And Reconciliation' (Protocol in workflow.md)

## Phase 5: Quality Gates

- [ ] Task: Add parser-complete zero-record gates.
- [ ] Task: Add record-count drift warnings.
- [ ] Task: Add source-specific validation summaries.
- [ ] Task: Update release evidence to report parser and collection state.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Quality Gates' (Protocol in workflow.md)

## Phase 6: First Non-Zero Collection Proof

- [ ] Task: Run local collection for at least one source.
- [ ] Task: Validate generated artifacts and ledgers.
- [ ] Task: Attach collection proof to the GitHub issue/project.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: First Non-Zero Collection Proof' (Protocol in workflow.md)
