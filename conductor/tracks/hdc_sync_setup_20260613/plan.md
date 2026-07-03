- [x] Task: Oracle architectural analysis and mission review — Key finding: Use `uv` + `pyproject.toml` (not `pixi.toml`) per sibling convention
# Plan: Establish HDC Corpus Structure, Ingestion, and Live Sync

## Phase 1: Project Scaffolding & Shared Library Linkage

- [x] Task: Initialize `pixi.toml` and lock environment, referencing `nlp_policy_nz` as a path dependency.
- [x] Task: Create `config/hdc_pipeline.yaml` to specify HDC source URLs, endpoints, and scraping rules.
- [x] Task: Configure Ruff and `mypy` in `pyproject.toml` with strict rulesets.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Project Scaffolding & Shared Library Linkage' (Protocol in workflow.md)

## Phase 2: Ingestion Wrapper and Local Ingestion Tests

- [x] Task: Write unit tests for local configuration validation.
- [x] Task: Implement the pipeline configuration validation.
- [x] Task: Write unit tests for raw fetching wrapper delegating to `nlp_policy_nz`.
- [x] Task: Implement raw fetching wrapper delegating to `nlp_policy_nz`.
- [x] Task: Write unit tests for exporting processed data into formats A (Markdown+YAML), B (Text+JSON), C (JSONL), and Parquet.
- [x] Task: Implement format exporter for formats A, B, C, and Parquet.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Ingestion Wrapper and Local Ingestion Tests' (Protocol in workflow.md)

## Phase 3: GitHub Actions and Hugging Face Sync

- [x] Task: Write integration tests for Hugging Face upload and download wrapper functions.
- [x] Task: Implement Hugging Face upload and download wrapper functions.
- [x] Task: Create daily sync GitHub Actions workflow `.github/workflows/hf_sync.yml` to trigger the ingestion wrappers.
- [x] Task: Conductor - User Manual Verification 'Phase 3: GitHub Actions and Hugging Face Sync' (Protocol in workflow.md)
