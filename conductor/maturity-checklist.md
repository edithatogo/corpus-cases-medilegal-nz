# Maturity Dependency Checklist — corpus-cases-medilegal-nz

| Category | Status | Rationale |
|---|---|---|
| **Python environment manager (pixi)** | required | `pixi.toml` is the sole env manager; `pyproject.toml` uses hatchling for build only. No lock file committed — a CI reproducibility gap. |
| **Python lint/format (ruff)** | required | Fully configured in `pyproject.toml` with extensive rule selection, per-file-ignores, pre-commit hook, and CI task (`pixi run lint` / `format`). |
| **Python type checking (pyright)** | required | `pyright` configured with strict mode, dedicated CI task (`pixi run typecheck`). Tech-stack.md aspirationaly names `ty`/`mypy` but `pyright` is the actual implementation. |
| **Python logging (loguru)** | required | Listed in `pyproject.toml` deps, declared in `[tool.legal_nz] logging = "loguru"`. Actual code still uses `stdlib logging` — migration WIP. |
| **Python CLI UX (typer/rich)** | required | Both `typer` and `rich` in deps. Current CLI entrypoint uses `argparse` (pre-typer scaffold); migration expected post-MVP. |
| **Config/env loading (pydantic-settings)** | required | `pydantic-settings` in deps. Light usage currently; env integration planned as pipelines mature. |
| **Boundary validation (pydantic v2)** | required | Heavy use of Pydantic v2 `BaseModel` with `Field(gt=…)` constraints in `config_models.py`. Core to pipeline config integrity. |
| **Hot record serialization (msgspec)** | deferred | Not a dep for this subrepo. Used in sibling `nlp-policy-nz` for high-throughput serialization. Worth adopting when throughput requirements emerge (batch scraping). |
| **Dataframes (polars)** | required | Core dep, used in `exporter.py` for Parquet/Hive-partitioned export. Aligns with sibling subrepos. |
| **Query validation (duckdb)** | not_applicable | Not a dependency; no SQL querying needs in this ingestion-only pipeline. |
| **Columnar data (pyarrow/Parquet)** | required | Core dep; Parquet is a primary export format. `pyarrow` drives `polars` Parquet I/O. |
| **JSON schema (jsonschema)** | deferred | Not a dep; Pydantic models already provide schema validation. Pydantic can generate JSON Schema for interop, but no explicit usage yet. |
| **HTTP clients (httpx/requests)** | required | `requests` is a core dep used throughout `fetcher.py` with `urllib3.Retry` adapter. `httpx` not imported but available for future async needs. |
| **Retry/backoff (tenacity)** | deferred | Retry is done manually via `urllib3.util.retry.Retry` in `fetcher.py`. `tenacity` would simplify but not urgent. |
| **HTML parsing (beautifulsoup4/selectolax)** | required | `beautifulsoup4` and `defusedxml` are core deps; used for secure parsing of tribunal decision pages. |
| **Terminal UI (rich)** | required | Listed in deps, but not yet wired into CLI output (still using `print()` + `argparse`). Pending typer migration. |
| **Checksums/manifests** | deferred | Not implemented. Would be useful for data integrity verification in the HF sync pipeline. Planned post-MVP. |
| **Local vector store (lancedb)** | not_applicable | Not a dep; this is an ingestion pipeline, not a retrieval/embedding service. Sibling `nlp-policy-nz` uses lancedb for semantic search. |
| **Service vector DB (qdrant)** | not_applicable | Same rationale as lancedb — no retrieval workload in this subrepo. |
| **RAG orchestration (haystack)** | not_applicable | Out of scope. This subrepo produces datasets; downstream RAG is a separate concern. |
| **HF publication (huggingface_hub/datasets)** | required | `huggingface_hub` is a core dep used extensively in `hf_sync.py` for snapshot download/upload. Primary distribution channel. |
| **Archive/DOI (Zenodo/OSF)** | deferred | OSF mirror policy documented in `conductor/` tracks; no code implemented. Post-MVP once dataset has stable releases. |

## Blocking Dependency

This subrepo has an **editable path dependency** on `nlp-policy-nz`:

```toml
# pixi.toml
nlp-policy-nz = { path = "../nlp-policy-nz", editable = true }
```

This means any Python version migration (e.g. `>=3.11` → `>=3.14`) must be coordinated across both subrepos simultaneously. `nlp-policy-nz` carries heavier ML dependencies (`torch`, `spacy`, `transformers`, `bitsandbytes`) that may not have 3.14 wheels at the time of migration, making `corpus-cases-medilegal-nz` **blocked** on the sibling's readiness.

## Notes

- **Tech-stack.md aspirational drift**: The document names `Python 3.14`, `ty`, and `mypy` but actual implementation uses `3.11`, `pyright`, and `argparse`. The checklist reflects **current state**, not aspirational targets.
