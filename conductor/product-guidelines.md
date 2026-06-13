# Product Guidelines: New Zealand Medical-Legal Corpus

## 1. Directory & Data Structure
To align with the conventions of the `legal-nz` family, data should be organized systematically:
*   `data/raw/hdc/`, `data/raw/hpdt/`, etc.: Stores the raw, unaltered files (PDFs, HTML source) as fetched from the public sources.
*   `data/processed/`: Houses the clean, processed text in three export formats to support diverse NLP needs:
    1.  **Format A (Markdown + YAML):** Markdown files (`.md`) with a standardized YAML frontmatter block containing metadata fields (e.g., case ID, decision date, commissioner/judge, parties, citations).
    2.  **Format B (Plain Text + JSON):** Side-by-side plain text (`.txt`) for NLP ingestion and JSON (`.json`) files for metadata.
    3.  **Format C (JSON Lines):** A unified `records.jsonl` file containing one JSON object per document (containing both metadata fields and raw/clean text) for direct loading.
    4.  **Parquet:** Optimized Apache Parquet shards (`data/parquet/`) partitioned for high-performance querying (e.g., via DuckDB) and streaming on Hugging Face.

## 2. Ingestion & Sync Cadence
*   **Live Sync Mechanism:** A GitHub Actions workflow (e.g., `.github/workflows/hf_sync.yml`) will run on a daily scheduled cron.
*   **Workflow Behavior:**
    1.  Discover new/updated cases since the last execution.
    2.  Pull raw documents and save them to `data/raw/`.
    3.  Run processing scripts to update `data/processed/` formats and the Parquet shards.
    4.  Upload the updated files to the Hugging Face dataset (`edithatogo/corpus-cases-medilegal-nz`).
    5.  Trigger annual Zenodo archiving for long-term DOI-backed snapshots.

## 3. Shared Library Convention
*   All scraping, text extraction (OCR/PDF extraction), parsing, and data validation logic will be housed in the central shared repository `nlp-policy-nz`.
*   This repository (`corpus-cases-medilegal-nz`) will only contain configuration files, Github workflows, metadata manifests, and the data itself, keeping it lightweight and decoupled from the code.
