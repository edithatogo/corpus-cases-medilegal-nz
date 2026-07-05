# Live Readiness Evidence

Generated on 2026-07-05T16:20Z from local CLI verification.

## Commands

```powershell
uv run python -m corpus_cases_medilegal_nz.cli collection-proof
uv run python -m corpus_cases_medilegal_nz.cli corpus-completion-readiness --verification-mode fixture
uv run python -m corpus_cases_medilegal_nz.cli source-verification --output-dir generated/source-verification-live --mode live
uv run python -m corpus_cases_medilegal_nz.cli corpus-completion-readiness --verification-mode live
uv run python -m corpus_cases_medilegal_nz.cli live-backfill-proof --output-dir generated/live-backfill-proof
uv run python scripts/build_release_evidence.py --output-dir generated/monthly-publication
uv run python -c "from pathlib import Path; from corpus_cases_medilegal_nz.archive import derive_archive_version, build_archive_bundle; v=derive_archive_version(); bundle=Path('generated/monthly-publication-bundles') / f'corpus-cases-medilegal-nz-{v}.tar.gz'; bundle.parent.mkdir(parents=True, exist_ok=True); build_archive_bundle(Path('generated/monthly-publication'), bundle)"
uv run python scripts/publish_huggingface_release.py --artifact-dir generated/monthly-publication --archive-version 2026.07.0 --repo-id edithatogo/corpus-cases-medilegal-nz --dry-run
uv run python scripts/publish_zenodo_draft.py --artifact-dir generated/monthly-publication --bundle generated/monthly-publication-bundles/corpus-cases-medilegal-nz-2026.07.0.tar.gz --archive-version 2026.07.0 --dry-run
```

## Results

- Fixture-backed corpus completion readiness: `pass`.
- Live verification input archive: 13 archived inputs, 0 blocked inputs.
- Live verification reconciliation: `verified_incomplete`.
- Live expected records: 52.
- Current processed records: 26.
- Live matched records: 0.
- Live missing records: 52.
- Live extra processed records: 26.
- Live ambiguous expected records: 21.
- Live corpus-completion readiness: `blocked`.
- Live blockers: `source_completeness_unresolved`, `source_verification_unresolved`.
- Live backfill proof: `pass`.
- Live backfill generated records: 52.
- Live backfill reconciliation: `verified_complete`.
- Live backfill matched records: 52.
- Live backfill missing records: 0.
- Live backfill extra records: 0.
- Live backfill duplicate records: 0.
- Live backfill ambiguous expected records: 21, reported but not blocking the
  exact generated-record projection.
- Live backfill embedded source verification: `verified_complete`.
- Live backfill artifacts:
  `generated/live-backfill-proof/jsonl/records.jsonl` and
  `generated/live-backfill-proof/manifests/live_backfill_proof.json`.
- Monthly release evidence build: `pass`.
- Monthly release source verification: `verified_complete`.
- Monthly release corpus-completion readiness: `pass`.
- Monthly release checksum manifest: 44 files.
- Monthly bundle:
  `generated/monthly-publication-bundles/corpus-cases-medilegal-nz-2026.07.0.tar.gz`.
- Hugging Face dry-run evidence: `dry_run: true`, `uploaded: false`,
  `remote_manifest_verified: false`, path in repo `releases/2026.07.0`.
- Zenodo dry-run evidence: `dry_run: true`, `uploaded: false`,
  `publish_handoff_only: true`, protected environment `zenodo-production`, 9
  upload files selected.

## Interpretation

The repo-local gates, rights review, parser replacement proof, and candidate
scaffolding are implemented. The current canonical processed fixture corpus does
not reconcile against the live source indexes, so canonical complete-corpus
claims remain blocked for the existing checked-in processed outputs. A
non-mutating live historical backfill proof now projects 52 live expected records
into processed-style records and reconciles them completely, providing the
promotion candidate for the next canonical release workflow.

The monthly release artifact and dry-run publication paths are verified locally.
Live Hugging Face upload and Zenodo draft/new-version upload remain unclaimed
until `HF_TOKEN`, `HF_REPO_ID`, and Zenodo credentials are available to the
monthly publication workflow or local publication scripts.
