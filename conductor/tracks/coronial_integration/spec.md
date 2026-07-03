# Track Specification: Integrate Coronial Decisions
## 1. Goal
Add Coronial Decisions to the NZ medical-legal corpus.
## 2. Source
URL: https://coronialservices.justice.govt.nz/
## 3. Data Format
Follows the standard format (Markdown+YAML, Text+JSON, JSONL, Parquet).
## 4. Pipeline Integration
Configured through `coronial_pipeline.yaml`, the `sources/coronial.py` adapter, and the multi-source pipeline framework.
