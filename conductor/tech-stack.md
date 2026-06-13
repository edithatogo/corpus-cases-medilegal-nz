# Technology Stack: New Zealand Medical-Legal Corpus

This document outlines the bleeding-edge, strict technology stack and tools selected for the New Zealand Medical-Legal Corpus data management and ingestion pipeline.

## 1. Core Language & Runtime
*   **Language:** Python 3.14 (Bleeding-edge, utilizing the latest interpreter features, PEP enhancements, and speedups).
*   **Environment & Package Manager:** `pixi` (Conda-compatible package manager written in Rust, aligning with the environment management system in `nlp-policy-nz`).

## 2. Ingestion, Processing & Storage Libraries
To align with sibling repositories (specifically `corpus-law-nz` and `nlp-policy-nz`), the following library versions and equivalents are used:
*   **HTTP Clients:** `requests` / `httpx` (for REST API interactions and website indexing).
*   **HTML/XML Parsing:** `beautifulsoup4` and `defusedxml` (for secure parsing of tribunal decision pages).
*   **Data Analysis & Schemas:**
    *   `polars` (fast, multi-threaded DataFrame library for corpus indexing and metadata handling).
    *   `pyarrow` (for writing optimized, Hive-partitioned Parquet datasets).
    *   `pydantic` & `pydantic-settings` (v2+, for strict configuration management and metadata validation).
*   **Distribution Channels:**
    *   `huggingface_hub` (for datasets upload and dataset card sync).
    *   `zenodo-client` / `requests` (for automated archival uploads).

## 3. Strict Code Quality & Typing
*   **Linting & Formatting:** `ruff` (used strictly for linting, formatting, import sorting, and code upgrades, configured with maximum rulesets active).
*   **Static Type Checking:** `ty` / `mypy` (strict type checking enabled, ensuring type safety across the corpus workflows).
*   **Testing:** `pytest` (for integration and validation tests) and `hypothesis` (for property-based testing).
