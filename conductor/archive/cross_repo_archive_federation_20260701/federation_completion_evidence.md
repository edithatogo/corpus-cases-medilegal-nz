# Cross-Repo Archive Federation Completion Evidence

## Summary

The federation contract is implemented in the archive intelligence layer and
validated by the archive intelligence test suite.

## Implemented surfaces

- `src/corpus_cases_medilegal_nz/archive_intelligence.py`
  - `build_federation_compatibility_report`
  - federation compatibility output in the archive intelligence bundle
- `tests/test_archive_intelligence.py`
  - missing-section drift case
  - complete-evidence compatibility case
- `docs/riopa-project-synchronisation.md`
  - RIOPA and repository project alignment notes
- `scripts/sync_riopa_project.py`
  - issue/project evidence mirroring and marker conventions

## Contract

- Shared archive-family target repositories:
  - `corpus-cases-medilegal-nz`
  - `corpus-law-nz`
  - `corpus-nz-hansard`
  - `fyi-archive`
  - `hathi-nz`
- Compatibility reports are `compatible` only when the required release,
  coverage, provenance, metadata, and publication evidence sections are present.

## Validation

- Archive intelligence bundle tests exercise federation compatibility for both
  drift and complete-evidence states.
- The CLI already exposes `archive-intelligence`, which writes the bundled
  federation compatibility artifact alongside the other intelligence outputs.
