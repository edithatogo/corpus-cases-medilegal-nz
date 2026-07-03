# Track Specification: Integrate Law Commission Reports
## 1. Goal
Add Law Commission Reports to the NZ medical-legal corpus.
## 2. Source
URL: https://www.lawcom.govt.nz/our-work
## 3. Data Format
Follows the standard format (Markdown+YAML, Text+JSON, JSONL, Parquet).
## 4. Pipeline Integration
Configured through `law_commission_pipeline.yaml`, the `sources/law_commission.py` adapter, and the multi-source pipeline framework.
