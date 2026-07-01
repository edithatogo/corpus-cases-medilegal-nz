# Verification Workflow - Monthly Dynamic Archive Publication

Use this protocol for each Conductor manual verification checkpoint.

## Local Evidence Build

1. Run `python scripts/build_release_evidence.py --output-dir generated/monthly-publication`.
2. Run `python scripts/check_release_evidence.py --require-file`.
3. Run `python scripts/check_metadata_packages.py --require-file`.
4. Run `python scripts/check_public_surface_audit.py --require-file`.
5. Run `python -m corpus_cases_medilegal_nz.cli publication-readiness`.

## Publication Dry Run

1. Build a deterministic bundle with
   `python -c "from pathlib import Path; from corpus_cases_medilegal_nz.archive import build_archive_bundle; build_archive_bundle(Path('generated/monthly-publication'), Path('generated/monthly-publication-bundles/corpus-cases-medilegal-nz-2026.07.0.tar.gz'))"`.
2. Run `python scripts/publish_huggingface_release.py --artifact-dir generated/monthly-publication --archive-version 2026.07.0 --dry-run`.
3. Run `python scripts/publish_zenodo_draft.py --artifact-dir generated/monthly-publication --bundle generated/monthly-publication-bundles/corpus-cases-medilegal-nz-2026.07.0.tar.gz --archive-version 2026.07.0 --dry-run`.

## Remote Publication Proof

1. Confirm `HF_TOKEN`, `HF_REPO_ID`, `ZENODO_ACCESS_TOKEN`,
   `ZENODO_API_URL`, and `ARCHIVE_CREATORS_JSON` are configured.
2. Run the monthly workflow in `huggingface` mode and verify
   `manifests/huggingface_publish_evidence.json`.
3. Run the monthly workflow in `zenodo-draft` mode and verify
   `manifests/zenodo_draft_evidence.json`.
4. Run `full` mode only after protected environment approval is configured.
5. Do not publish a production Zenodo DOI from automation until the draft
   evidence has been reviewed.

## Completion Criteria

- Focused tests pass.
- Release evidence validates.
- Hugging Face remote manifest readback passes.
- Zenodo draft evidence exists.
- GitHub release assets and attestations are attached.
- OSF remains inactive unless a later track activates it.
