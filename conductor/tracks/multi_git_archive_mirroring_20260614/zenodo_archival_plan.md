# Zenodo Archival Plan — corpus-cases-medilegal-nz

## Overview

This document defines the publication schema and script requirements for
archiving periodic snapshots of the medilegal corpus to Zenodo. Zenodo provides
DOI-backed immutable snapshots, satisfying the project's long-term preservation
and citation requirements.

## Deposition Schedule

| Cadence | Trigger | Retention |
|---------|---------|-----------|
| Annual (Q4) | Calendar year close | Permanent (DOI-assigned) |
| Major release | On new source integration | Permanent (DOI-assigned) |
| On-demand | User-initiated via CLI | Permanent (DOI-assigned) |

## Publication Schema

Each Zenodo deposition MUST contain the following artifacts:

```
corpus-cases-medilegal-nz-{YYYY}-{MM}/
├── metadata.json                # Top-level corpus metadata
├── manifest.sha256              # Checksum manifest for all files
├── README.md                    # Dataset description (auto-generated)
├── formats/
│   ├── markdown/                # Format A: Markdown + YAML frontmatter
│   ├── text/                    # Format B: Plain text
│   ├── json/                    # Format B: JSON metadata sidecars
│   ├── jsonl/                   # Format C: Unified JSONL records
│   └── parquet/                 # Apache Parquet shards
└── sources/
    ├── hdc/
    ├── hpdt/
    ├── moj_tribunals/
    ├── era/
    ├── teachers/
    ├── royal_commissions/
    ├── coronial/
    ├── privacy/
    ├── human_rights/
    ├── ombudsman/
    ├── moj_courts/
    ├── ipca/
    └── law_commission/
```

### metadata.json Structure

```json
{
  "corpus_name": "corpus-cases-medilegal-nz",
  "version": "0.1.0",
  "snapshot_date": "YYYY-MM-DD",
  "source_count": 13,
  "sources": {
    "hdc": {"name": "Health and Disability Commissioner", "case_count": 0},
    "hpdt": {"name": "Health Practitioners Disciplinary Tribunal", "case_count": 0},
    ...
  },
  "total_cases": 0,
  "format_summary": {
    "markdown_files": 0,
    "text_files": 0,
    "json_files": 0,
    "jsonl_records": 0,
    "parquet_bytes": 0
  },
  "checksums": {
    "manifest.sha256": "..."
  },
  "doi": null
}
```

## Script Requirements

### 1. `zenodo_archive.py` — CLI entry point

```
Usage: zenodo-archive [OPTIONS]

  Create and publish a Zenodo deposition for the medilegal corpus.

Options:
  --dry-run           Prepare archive bundle without uploading (default: True)
  --publish           Publish deposition to Zenodo (requires ZENODO_TOKEN)
  --sandbox           Use Zenodo Sandbox API for testing
  --year INTEGER      Publication year  [default: current year]
  --month INTEGER     Publication month  [default: current month]
  --verbose           Enable verbose logging
  --help              Show this message and exit.
```

### 2. Implementation sketch

```python
# zenodo_archive.py (planned location: src/corpus_cases_medilegal_nz/archive.py)

from pathlib import Path
from typing import Optional
import hashlib
import json
import shutil
import tempfile

import requests


ZENODO_API = "https://zenodo.org/api"
ZENODO_SANDBOX_API = "https://sandbox.zenodo.org/api"


def build_manifest(directory: Path) -> dict[str, str]:
    """Recursively compute SHA-256 hashes for all files in directory."""
    manifest = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            manifest[str(path.relative_to(directory))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return manifest


def build_metadata_json(
    source_dirs: dict[str, Path],
    total_cases: int,
    snapshot_date: str,
) -> dict:
    """Build the metadata.json for the deposition."""
    ...


def prepare_archive(
    processed_dir: Path,
    output_dir: Path,
    snapshot_date: str,
    sources: Optional[list[str]] = None,
) -> Path:
    """Prepare the archive bundle directory structure."""
    ...


def create_deposition(
    access_token: str,
    sandbox: bool = False,
) -> dict:
    """Create a new Zenodo deposition and return its metadata."""
    ...


def upload_deposition(
    access_token: str,
    deposition_id: str,
    archive_path: Path,
    sandbox: bool = False,
) -> None:
    """Upload prepared archive to an existing Zenodo deposition."""
    ...


def publish_deposition(
    access_token: str,
    deposition_id: str,
    sandbox: bool = False,
) -> dict:
    """Publish a Zenodo deposition (makes it public with DOI)."""
    ...
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ZENODO_TOKEN` | For publish | Zenodo API access token |
| `ZENODO_SANDBOX_TOKEN` | For sandbox | Zenodo Sandbox API token |

## GitHub Actions Integration

A reusable workflow fragment for annual archiving:

```yaml
# .github/workflows/zenodo_archive.yml (planned)
name: Zenodo Annual Archive

on:
  schedule:
    - cron: "0 0 1 12 *"   # Dec 1st annually
  workflow_dispatch:
    inputs:
      dry_run:
        description: "Dry run (prepare without upload)"
        type: boolean
        default: true

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: prefix-dev/setup-pixi@v0.8
        with:
          pixi-version: latest
      - run: pixi run python -m corpus_cases_medilegal_nz.archive
        env:
          ZENODO_TOKEN: ${{ secrets.ZENODO_TOKEN }}
```

## DOI Collection

DOIs obtained from Zenodo publications should be recorded in:

- `data/state/dois.json` — corpus-level DOI registry
- `README.md` — project-level citation badge
- `data/README.md` — dataset-level citation section

## Related Sibling Patterns

This plan follows conventions established in:
- `../corpus-law-nz/conductor/tracks/zenodo_archival/` (if present)
- `../corpus-nz-hansard/conductor/tracks/zenodo_archival/` (if present)
