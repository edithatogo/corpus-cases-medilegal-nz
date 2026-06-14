# Task Plan (From Preset: fullstack)

Mission: Establish the HDC corpus data structure, ingestion pipeline configs, and daily Hugging Face/GitHub Actions sync

- [x] Review Mission

## Swarm Execution Summary — 2026-06-14 (Antigravity Orchestration)

### Final Status: ✅ MISSION COMPLETE — 80/80 tests pass

### Phase 1 — Scaffolding (All Complete ✅)
- [x] `pixi.toml` — Python 3.14, nlp_policy_nz path dependency
- [x] `config/hdc_pipeline.yaml` — HDC source URLs, endpoints, scraping rules
- [x] `pyproject.toml` — Ruff strict, mypy strict config
- [x] `data/raw/hdc/` directory
- [x] `data/processed/` subdirectories (markdown, text, json, jsonl, parquet)
- [x] `README.md` — Complete project documentation
- [x] `CONTRIBUTING.md` — Contribution guidelines
- [x] `data/README.md` — Hugging Face dataset card
- [x] `.pre-commit-config.yaml` — Pre-commit hooks
- [x] `.gitignore` — Git ignore rules

### Phase 2 — Ingestion (All Complete ✅)
- [x] `src/corpus_cases_medilegal_nz/config_models.py` — Pipeline config validation (Pydantic models + loader) — 28 tests
- [x] `src/corpus_cases_medilegal_nz/fetcher.py` — Raw fetching wrapper with retry logic — 20 tests
- [x] `src/corpus_cases_medilegal_nz/exporter.py` — Format exporter (A: Markdown+YAML, B: Text+JSON, C: JSONL, Parquet) — 32 tests

### Phase 3 — Sync (All Complete ✅)
- [x] `src/corpus_cases_medilegal_nz/hf_sync.py` — HF upload/download wrappers + orchestration pipeline
- [x] `.github/workflows/hf_sync.yml` — Daily cron workflow (14:17 UTC) + manual dispatch

- [x] Swarm Execution: 80 tests pass across 3 agents (Junior, Frontend, Quality_Validator)

## Quality_Validator Test Results — 2026-06-14

### ✅ Completed
- [x] **tests/test_config_models.py** — 28 tests created and passing
- [x] **tests/test_fetcher.py** — 20 tests created and passing
- [x] Full validation run: **48/48 tests passed**

### Verified Functionality
- `load_pipeline_config` — loads real YAML, validates values, handles FileNotFoundError, invalid YAML, missing fields
- `HdcPipelineConfig` — default construction with all nested models
- `FetchConfig` — defaults, custom values, all validation constraints
- `PathsConfig` — accepts Path objects and strings
- `ScrapingConfig` — validation of page_size, max_pages, timeout
- `PipelineDetails` — required fields with HttpUrl validation
- `FetchedCase` — dataclass construction, mutable default safety
- `HdcFetcher` — session build, retry adapter, headers, fetch_url, fetch_case, context manager
- `fetch_case` — convenience function with default/explicit config and case_id
