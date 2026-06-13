# Plan: Establish HDC Corpus Structure, Ingestion, and Live Sync

## Phase 1: Project Scaffolding & Shared Library Linkage

- [ ] Task: Initialize `pixi.toml` and lock environment, referencing `nlp_policy_nz` as a path dependency.
- [ ] Task: Create `config/hdc_pipeline.yaml` to specify HDC source URLs, endpoints, and scraping rules.
- [ ] Task: Configure Ruff and `mypy` in `pyproject.toml` with strict rulesets.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Project Scaffolding & Shared Library Linkage' (Protocol in workflow.md)

## Phase 2: Ingestion Wrapper and Local Ingestion Tests

- [ ] Task: Write unit tests for local configuration validation.
- [ ] Task: Implement the pipeline configuration validation.
- [ ] Task: Write unit tests for raw fetching wrapper delegating to `nlp_policy_nz`.
- [ ] Task: Implement raw fetching wrapper delegating to `nlp_policy_nz`.
- [ ] Task: Write unit tests for exporting processed data into formats A (Markdown+YAML), B (Text+JSON), C (JSONL), and Parquet.
- [ ] Task: Implement format exporter for formats A, B, C, and Parquet.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Ingestion Wrapper and Local Ingestion Tests' (Protocol in workflow.md)

## Phase 3: GitHub Actions and Hugging Face Sync

- [ ] Task: Write integration tests for Hugging Face upload and download wrapper functions.
- [ ] Task: Implement Hugging Face upload and download wrapper functions.
- [ ] Task: Create daily sync GitHub Actions workflow `.github/workflows/hf_sync.yml` to trigger the ingestion wrappers.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: GitHub Actions and Hugging Face Sync' (Protocol in workflow.md)
