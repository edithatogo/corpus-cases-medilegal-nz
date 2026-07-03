# Track Specification: Integrate Royal Commissions & Waitangi Tribunal
## 1. Goal
Add Royal Commissions & Waitangi Tribunal decisions to the NZ medical-legal corpus.
## 2. Source
URL: https://www.waitangitribunal.govt.nz/en/publications/tribunal-reports
## 3. Data Format
Follows the standard format (Markdown+YAML, Text+JSON, JSONL, Parquet).
## 4. Pipeline Integration
Configured through `royal_commissions_pipeline.yaml`, the `sources/royal_commissions.py` adapter, and the multi-source pipeline framework.
