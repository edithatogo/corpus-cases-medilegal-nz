# Track Specification: Integrate MoJ Court Cases
## 1. Goal
Add Ministry of Justice (MoJ) Court Cases to the NZ medical-legal corpus.
## 2. Source
URL: https://www.justice.govt.nz/courts/decisions/jdo/
## 3. Data Format
Follows the standard format (Markdown+YAML, Text+JSON, JSONL, Parquet).
## 4. Pipeline Integration
Configured through `moj_courts_pipeline.yaml`, the `sources/moj_courts.py` adapter, and the multi-source pipeline framework.
