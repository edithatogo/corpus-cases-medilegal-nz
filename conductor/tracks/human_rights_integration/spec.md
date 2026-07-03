# Track Specification: Integrate Human Rights Commission/Tribunal
## 1. Goal
Add Human Rights Commission/Tribunal decisions to the NZ medical-legal corpus.
## 2. Source
URL: https://www.justice.govt.nz/tribunals/human-rights/hrrt-decisions/
## 3. Data Format
Follows the standard format (Markdown+YAML, Text+JSON, JSONL, Parquet).
## 4. Pipeline Integration
Configured through `human_rights_pipeline.yaml`, the `sources/human_rights.py` adapter, and the multi-source pipeline framework.
