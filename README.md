# New Zealand Medical-Legal Corpus

[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/edithatogo/corpus-cases-medilegal-nz/hf_sync.yml?style=flat-square&label=Daily%20Sync)](https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/workflows/hf_sync.yml)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-yellow?style=flat-square)](https://huggingface.co/datasets/edithatogo/corpus-cases-medilegal-nz)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue?style=flat-square)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000?style=flat-square)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&style=flat-square)](https://pre-commit.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

A bleeding-edge, open-source corpus of New Zealand medical-legal tribunal
decisions. This repository houses structured data for the **Health and
Disability Commissioner (HDC)** decisions, with planned expansion to HPDT,
MoJ Tribunals, ERA, Teachers Disciplinary Tribunal, and beyond.

**Data is stored here; processing logic lives in the shared library
[`nlp-policy-nz`](https://github.com/edithatogo/nlp-policy-nz).**

---

## Table of Contents

- [Data Sources](#data-sources)
- [Directory Structure](#directory-structure)
- [Data Formats](#data-formats)
- [Usage](#usage)
- [Pipeline & Sync](#pipeline--sync)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

---

## Data Sources

| Source                                              | Status     | URL                                                                   |
|-----------------------------------------------------|------------|-----------------------------------------------------------------------|
| Health and Disability Commissioner (HDC)            | ⚡ Active   | <https://www.hdc.org.nz/decisions/search-decisions/>                   |
| Health Practitioners Disciplinary Tribunal (HPDT)   | 📋 Planned | <https://www.hpdt.org.nz/Search-Decisions>                             |
| Ministry of Justice Tribunals                       | 📋 Planned | <https://www.justice.govt.nz/tribunals/>                               |
| Employment Relations Authority (ERA)                | 📋 Planned | <https://www.era.govt.nz/>                                             |
| Teachers Disciplinary Tribunal                      | 📋 Planned | <https://www.teachersdisciplinarytribunal.nz/>                         |
| Royal Commissions & Waitangi Tribunal               | 📋 Planned | —                                                                     |
| Coronial Decisions                                  | 📋 Planned | —                                                                     |
| Privacy Commissioner                                | 📋 Planned | —                                                                     |
| Human Rights Commission/Tribunal                    | 📋 Planned | —                                                                     |
| Ombudsman Reports                                   | 📋 Planned | —                                                                     |
| Independent Police Conduct Authority (IPCA)         | 📋 Planned | —                                                                     |
| Law Commission Reports                              | 📋 Planned | —                                                                     |

## Directory Structure

```
corpus-cases-medilegal-nz/
├── .github/
│   ├── workflows/
│   │   └── hf_sync.yml          # Daily sync to Hugging Face
│   └── styles/                  # Vale style rules for prose linting
├── config/
│   └── hdc_pipeline.yaml        # HDC source configuration
├── data/
│   ├── raw/
│   │   └── hdc/                 # Raw PDF/HTML files from HDC
│   └── processed/
│       ├── markdown/            # Format A: Markdown + YAML frontmatter
│       ├── text/                # Format B: Plain text files
│       ├── json/                # Format B: Side-by-side JSON metadata
│       ├── jsonl/               # Format C: Unified records.jsonl
│       └── parquet/             # Apache Parquet shards
├── conductor/                   # Project tracking and guidelines
├── .pre-commit-config.yaml      # Pre-commit hooks
├── .vale.ini                    # Vale prose linter configuration
├── pixi.toml                    # Environment and dependency management
├── pyproject.toml               # Python project configuration
├── README.md                    # This file
└── CONTRIBUTING.md              # Contribution guidelines
```

---

## Data Formats

All processed data is available in four standard formats to support diverse
NLP workflows.

### Format A: Markdown with YAML Frontmatter

Each document is a `.md` file with a structured YAML frontmatter block
containing metadata, followed by the clean markdown body.

```markdown
---
case_id: "HDC-2024-001"
source: "hdc"
title: "A Complainant v A Provider"
date: "2024-03-15"
commissioner: "Anthony Hill"
parties: ["Complainant", "Provider"]
outcome: "upheld"
---

# Decision

The Commissioner considered whether the Provider breached the Code of
Health and Disability Services Consumers' Rights...
```

*Location:* `data/processed/markdown/`

### Format B: Plain Text + JSON

Side-by-side files for direct NLP ingestion: a `.txt` file with the clean text
and a `.json` file carrying the metadata.

- `data/processed/text/HDC-2024-001.txt`
- `data/processed/json/HDC-2024-001.json`

### Format C: JSON Lines

A single `records.jsonl` file with one JSON object per line. Each object
contains both metadata and the full document text — ideal for streaming and
batch loading.

```jsonl
{"case_id": "HDC-2024-001", "source": "hdc", "text": "The Commissioner...", "metadata": {...}}
{"case_id": "HDC-2024-002", "source": "hdc", "text": "The Deputy Commissioner...", "metadata": {...}}
```

*Location:* `data/processed/jsonl/records.jsonl`

### Parquet

Apache Parquet shards partitioned for high-performance analytical queries
(via DuckDB, Polars, or PyArrow).

```
data/processed/parquet/
├── source=hdc/
│   ├── year=2024/
│   │   ├── data_0.parquet
│   │   └── data_1.parquet
│   └── year=2025/
│       └── data_0.parquet
└── _metadata
```

*Location:* `data/processed/parquet/`


---

## Usage

### Via Hugging Face Datasets

```python
from datasets import load_dataset

ds = load_dataset("edithatogo/corpus-cases-medilegal-nz", split="train")
print(ds[0]["text"])
```

### Via Local Clone

```bash
git clone https://github.com/edithatogo/corpus-cases-medilegal-nz.git
cd corpus-cases-medilegal-nz
pixi install
```

### Query with DuckDB (Parquet)

```python
import duckdb

con = duckdb.connect()
result = con.execute("""
    SELECT case_id, date, outcome
    FROM 'data/processed/parquet/*.parquet'
    WHERE outcome = 'upheld'
""").fetchdf()
```

---

## Pipeline & Sync

A daily GitHub Actions workflow (`hf_sync.yml`) performs the following steps:

1.  **Download** the previous snapshot from Hugging Face
2.  **Scrape** new/updated decisions from HDC via `nlp_policy_nz` library
3.  **Save** raw PDF/HTML to `data/raw/hdc/`
4.  **Process** into all four export formats under `data/processed/`
5.  **Validate** schema constraints and data integrity
6.  **Upload** updated dataset to Hugging Face

The shared `nlp-policy-nz` library handles all scraping, text extraction, and
processing logic — keeping this repository focused on data and configuration.

---

## Distribution Channels

| Platform    | URL                                                                     |
|-------------|-------------------------------------------------------------------------|
| GitHub      | [edithatogo/corpus-cases-medilegal-nz](https://github.com/edithatogo/corpus-cases-medilegal-nz) |
| Hugging Face| [edithatogo/corpus-cases-medilegal-nz](https://huggingface.co/datasets/edithatogo/corpus-cases-medilegal-nz) |
| Zenodo      | Coming soon — annual DOI-backed snapshots                              |

---

## Related Projects

| Repository | Description |
|------------|-------------|
| [nlp-policy-nz](https://github.com/edithatogo/nlp-policy-nz) | Shared NLP and extraction library |
| [corpus-legislation-nz](https://github.com/edithatogo/corpus-legislation-nz) | NZ legislation corpus |
| [corpus-nz-hansard](https://github.com/edithatogo/corpus-nz-hansard) | NZ Hansard parliamentary debates corpus |
| [Hugging Face Org](https://huggingface.co/edithatogo) | All datasets on Hugging Face |

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the code of
conduct and the process for submitting contributions.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
