# Dataset Registry Readiness

Status: `repository_ready_external_gates_pending`

Roadmap: `dataset_registry_readiness_20260721`

- Parent issue: [#19](https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/19)
- Licensing and rights: [#20](https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/20)
- Zenodo/DataCite: [#21](https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/21)
- Hugging Face/Croissant: [#22](https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/22)

## Current contract

The repository separates code licensing from source-record redistribution rights. The repository is MIT-licensed, but source-specific rights and terms remain review gates before canonical publication. The archive pipeline produces source-rights, legal-provenance, public-surface, quality, and publication metadata manifests.

The operational publication surfaces are:

- Hugging Face for the mutable dataset surface.
- Zenodo for immutable DOI-backed snapshots.
- GitHub releases for versioned release assets and evidence.

## Required evidence

- Every source has a provenance URL, retrieval context, and rights review state.
- Unresolved rights states fail closed for canonical release claims.
- Zenodo metadata is generated from the archive evidence bundle and remains draft-first until the protected production handoff is completed.
- Hugging Face dataset metadata and the dataset card are generated and validated together.
- Any Croissant metadata publication must identify its schema version, source revision, and artifact digest.

## External boundary

This document does not claim a cleared licence for source records, a minted DOI, a public Zenodo record, or a completed Hugging Face publication. Those claims require authoritative evidence recorded in the linked issues and generated release manifests.
