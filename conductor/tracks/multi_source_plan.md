# Multi-Source Integration Plan — All 13 Tracks

**Generated**: 2026-06-14
**Mission**: Implement all remaining corpus source tracks in parallel waves

## Overview
Add 13 new data source integrations to the corpus-cases-medilegal-nz repository, each following the HDC pattern: config YAML, source adapter, tests. Build a multi-source pipeline framework. Implement pipeline hardening (parallel GHA sync).

## Source Registry
| Source ID | Name | URL |
|-----------|------|-----|
| hdc | Health & Disability Commissioner | https://www.hdc.org.nz/decisions/search-decisions/ |
| hpdt | Health Practitioners Disciplinary Tribunal | https://www.hpdt.org.nz/Search-Decisions |
| moj_tribunals | Ministry of Justice Tribunals | https://www.justice.govt.nz/tribunals/ |
| era | Employment Relations Authority | https://www.era.govt.nz/ |
| teachers | Teachers Disciplinary Tribunal | https://www.teachersdisciplinarytribunal.nz/ |
| royal_commissions | Royal Commissions & Waitangi Tribunal | — |
| coronial | Coronial Decisions | — |
| privacy | Privacy Commissioner | — |
| human_rights | Human Rights Commission/Tribunal | — |
| ombudsman | Ombudsman Reports | — |
| moj_courts | Ministry of Justice Court Cases | — |
| ipca | Independent Police Conduct Authority | — |
| law_commission | Law Commission Reports | — |

## Dependency Graph
```
Wave 1 (Configs + Track Dirs) — 13 parallel tasks
  │
  ├──► Wave 2a (Source Adapters) — 13 parallel tasks
  │     │
  │     └──► Wave 3a (Tests) — 13 parallel tasks
  │
  └──► Wave 2b (Pipeline Hardening)
        │
        └──► Wave 3b (Validation + Finalize)
```

## Parallel Execution Waves

### Wave 1: Config YAMLs + Track Dirs (13 root tasks)
All independent — can run in full parallel.

### Wave 2a: Source Adapter Modules (depends on Wave 1)
Create `src/corpus_cases_medilegal_nz/sources/{source}.py` for each source.
Create `src/corpus_cases_medilegal_nz/sources/__init__.py` with registry.

### Wave 2b: Pipeline Hardening (depends on Wave 1)
- Update GHA workflow for multi-source parallel sync
- Update config_models.py for multi-source registry
- Update __init__.py

### Wave 3a: Tests (depends on Wave 2a)
Create `tests/test_sources/test_{source}.py` for each source.

### Wave 3b: Validation (depends on Wave 2b + 3a)
- Run all tests
- Update tracks.md
- Mark all tracks complete

---

## Wave 2 — Source Adapter Implementation + Pipeline Wiring

### Remaining Work After Wave 1
Wave 1 created config YAMLs, track directories, and the source registry. Now we need to:

1. **Create source-specific adapter subclasses** for 5 active sources (have URLs)
2. **Wire `hf_sync.py`** to use the multi-source adapter framework (replace stubs)
3. **Create tests** for adapters + wiring
4. **Update GHA workflow** to pass source_id

### Wave 2 Execution Plan

| Step | Agent | Task | Depends On |
|------|-------|------|------------|
| W2-A | Junior | Create `sources/hdc.py` — HdcAdapter wrapping existing HdcFetcher | None |
| W2-B | Junior | Create `sources/hpdt.py` — HpdtAdapter | None |
| W2-C | Junior | Create `sources/moj_tribunals.py` — MoJTribunalsAdapter | None |
| W2-D | Junior | Create `sources/era.py` — EraAdapter | None |
| W2-E | Junior | Create `sources/teachers.py` — TeachersAdapter | None |
| W2-F | Frontend | Wire `hf_sync.py` — replace stubs with adapter dispatch, update CLI | W2-A..E |
| W2-G | Quality_Validator | Create tests for adapters + wiring, validate all | W2-F |
