# CLI-first entrypoints

Use `corpus-cases-medilegal-nz` before calling package modules directly.

## Commands

- `corpus-cases-medilegal-nz sources` lists configured source IDs.
- `corpus-cases-medilegal-nz sync [source]` runs the existing Hugging Face sync pipeline.

## Aliases

The package also exposes `nz-medilegal-corpus` for shorter local automation.

## Policy

The existing `corpus_cases_medilegal_nz.hf_sync` module remains the implementation source of truth. New automation, conductor tracks, and swarm prompts should call the package CLI first.
