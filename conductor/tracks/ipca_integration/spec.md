# Track Specification: Integrate IPCA
## 1. Goal
Add Independent Police Conduct Authority (IPCA) decisions to the NZ medical-legal corpus.
## 2. Source
URL: https://www.ipca.govt.nz/Site/publications-and-media/Accountability/Archive.aspx
## 3. Data Format
Follows the standard format (Markdown+YAML, Text+JSON, JSONL, Parquet).
## 4. Pipeline Integration
Configured through `ipca_pipeline.yaml`, the `sources/ipca.py` adapter, and the multi-source pipeline framework.
