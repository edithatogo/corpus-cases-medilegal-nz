# Track Specification: Integrate Ombudsman Reports
## 1. Goal
Add Ombudsman Reports to the NZ medical-legal corpus.
## 2. Source
URL: https://www.ombudsman.parliament.nz/resources
## 3. Data Format
Follows the standard format (Markdown+YAML, Text+JSON, JSONL, Parquet).
## 4. Pipeline Integration
Configured through `ombudsman_pipeline.yaml`, the `sources/ombudsman.py` adapter, and the multi-source pipeline framework.
