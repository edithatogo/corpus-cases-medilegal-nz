# Track Specification: Integrate Privacy Commissioner
## 1. Goal
Add Privacy Commissioner decisions to the NZ medical-legal corpus.
## 2. Source
URL: https://www.privacy.org.nz/resources-and-learning/case-notes-and-court-decisions/
## 3. Data Format
Follows the standard format (Markdown+YAML, Text+JSON, JSONL, Parquet).
## 4. Pipeline Integration
Configured through `privacy_pipeline.yaml`, the `sources/privacy.py` adapter, and the multi-source pipeline framework.
