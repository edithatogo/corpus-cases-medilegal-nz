# OSF Mirror Convenience Policy — corpus-cases-medilegal-nz

## Overview

The Open Science Framework (OSF) provides an optional mirror target for corpus
snapshots. This policy defines the conditions, scope, and procedures for
maintaining an OSF mirror of the medilegal corpus dataset.

## When to Use OSF Mirroring

| Scenario | Recommend OSF? | Rationale |
|----------|----------------|-----------|
| Zenodo DOI already exists | Optional | Zenodo is preferred for archival |
| HF dataset is primary | Optional | HF Hub is the active distribution channel |
| User requests OSF backup | Yes | Accommodate user preference |
| Funders require OSF deposit | Yes | Compliance requirement |
| HF Hub is unavailable | Yes | Redundancy during outages |

## Policy Principles

1. **OSF is a convenience mirror, not a primary store.** The canonical dataset
   lives on Hugging Face Hub at `edithatogo/corpus-cases-medilegal-nz`.
2. **OSF mirrors are read-only snapshots.** No incremental sync.
3. **OSF mirrors are published under the same license** (MIT for code, CC-BY-4.0
   for data by default).
4. **OSF mirroring is triggered manually** (not on every push) to avoid API
   rate-limits and unnecessary overhead.

## Naming Convention

```
corpus-cases-medilegal-nz-{YYYY-MM-DD}-{format}
```

Examples:
- `corpus-cases-medilegal-nz-2026-12-01-parquet`
- `corpus-cases-medilegal-nz-2026-12-01-jsonl`

## OSF Project Structure (Recommended)

```
New Zealand Medical-Legal Corpus (parent project)
├── Data: corpus-cases-medilegal-nz (component)
│   ├── parquet/          # Apache Parquet shards
│   ├── jsonl/            # Unified records.jsonl
│   ├── markdown/         # Format A markdown files
│   ├── text/             # Format B plain text
│   └── json/             # Format B JSON metadata
├── Code (component)
│   └── mirror_snapshot.py
└── Documentation (component)
    ├── README.md
    └── data_dictionary.md
```

## Upload Procedure

### Prerequisites
- OSF account with project created
- OSF personal access token with `osf_files_write` scope

### Environment Variables

```bash
export OSF_TOKEN="your_osf_personal_access_token"
export OSF_PROJECT_ID="your_osf_project_id"
```

### CLI Tool (Planned)

```python
# Planned: src/corpus_cases_medilegal_nz/osf_mirror.py

"""
OSF Mirror CLI

Usage:
  osf-mirror upload <source_dir> --project <project_id>
  osf-mirror status --project <project_id>
  osf-mirror list-versions --project <project_id>
"""
```

### Manual Steps

1. Prepare a compressed archive of the processed data:
   ```bash
   tar czf corpus-cases-medilegal-nz-2026-12-01.tar.gz \
     data/processed/markdown/ \
     data/processed/json/ \
     data/processed/jsonl/records.jsonl \
     data/processed/parquet/
   ```
2. Upload via OSF web interface or osfclient CLI:
   ```bash
   pip install osfclient
   osf -p <project_id> upload \
     corpus-cases-medilegal-nz-2026-12-01.tar.gz \
     /corpus-cases-medilegal-nz-2026-12-01.tar.gz
   ```

## Frequency

| Action | Frequency | Notes |
|--------|-----------|-------|
| Full snapshot upload | Annually (aligned with Zenodo) | Coincide with annual DOI release |
| Ad-hoc snapshot | On request | User or maintainer request |

## Cost & Storage Considerations

- OSF provides 5 GB free storage per project.
- Estimated corpus size (all sources, all formats): ~250–500 MB (text-heavy).
- If corpus exceeds 5 GB, split into multiple OSF components or compress.

## Sister Repository Alignment

This policy follows conventions from:
- `../corpus-law-nz/conductor/tracks/osf_mirror_policy.md` (if present)
- `../corpus-nz-hansard/conductor/tracks/osf_mirror_policy.md` (if present)

## Decision Record

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-14 | OSF mirror is optional, manual-only | HF Hub is primary; reduce maintenance burden |
| 2026-06-14 | Annual snapshot aligned with Zenodo | Single preparation for both targets |
