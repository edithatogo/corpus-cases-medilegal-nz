# Track Specification: Establish HDC Corpus Structure, Ingestion, and Live Sync

## 1. Goal
The objective of this track is to establish the core directories, configuration framework, and daily automated sync pipelines for the Health and Disability Commissioner (HDC) corpus. All scraping and text extraction logic will be imported from the shared core library `nlp_policy_nz`, keeping this repository data-centric and light.

## 2. Directory Structure
The repository will follow the standard `legal-nz` family convention:
```
corpus-cases-medilegal-nz/
├── .github/
│   └── workflows/
│       └── hf_sync.yml          # Daily GitHub Action to sync data to Hugging Face
├── conductor/                   # Conductor tracking and guidelines
├── config/
│   └── hdc_pipeline.yaml        # configuration file for HDC ingestion
├── data/
│   ├── raw/
│   │   └── hdc/                 # Raw PDF and HTML files fetched from HDC site
│   └── processed/
│       ├── markdown/            # Format A: Markdown with YAML frontmatter
│       ├── text/                # Format B: Plain text files
│       ├── json/                # Format B: Side-by-side JSON metadata files
│       ├── jsonl/               # Format C: Unified records.jsonl file
│       └── parquet/             # High-performance Parquet dataset shards
├── pixi.toml                    # Environment manager referencing shared nlp_policy_nz
└── README.md
```

## 3. Tech Stack Integration
*   **pixi.toml**: Configured to run Python 3.14 and reference `nlp_policy_nz` as a local path dependency:
    ```toml
    [dependencies]
    nlp_policy_nz = { path = "../nlp-policy-nz" }
    ```
*   **Linter & Formatter**: Ruff configured strictly in `pyproject.toml` or `pixi.toml`.
*   **Type Safety**: Strict `mypy` typing checks.

## 4. Pipeline Execution & Synchronization Flow
1.  **Retrieve Previous Snapshot**: The GitHub Actions runner downloads the current version of the dataset from Hugging Face (`edithatogo/corpus-cases-medilegal-nz`).
2.  **HDC Scraper Execution**: Execute a script imported from `nlp_policy_nz` to discover new or updated decisions from `https://www.hdc.org.nz/decisions/search-decisions/`.
3.  **Raw Preservation**: Save the raw PDF/HTML files into `data/raw/hdc/`.
4.  **Processing & Transformation**: Generate the four standard formats under `data/processed/`.
5.  **Validation Check**: Verify schema constraints, test coverage (>90% on ingestion scripts), and integrity of the manifests.
6.  **Hugging Face Sync**: Upload the updated `data/` directory to Hugging Face datasets.
