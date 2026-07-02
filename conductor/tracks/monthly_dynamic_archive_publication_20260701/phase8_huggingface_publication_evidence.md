# Phase 8 Hugging Face Publication Evidence

Captured: 2026-07-02

## Live Hugging Face Publication

- Run URL: `https://github.com/edithatogo/corpus-cases-medilegal-nz/actions/runs/28557778268`
- GitHub issue evidence: `https://github.com/edithatogo/corpus-cases-medilegal-nz/issues/1#issuecomment-4861246629`
- Head commit: `c8411faa348f5865100c39c4ec60abf7f5fbb2d7`
- Dispatch mode: `publication_mode=huggingface`
- Archive version: `2026.07.0`
- Result: success

Verified downloaded artifact evidence:

- `huggingface_publish_evidence.dry_run`: `false`
- `huggingface_publish_evidence.repo_id`: `edithatogo/corpus-cases-medilegal-nz`
- `huggingface_publish_evidence.revision`: `73b7b10889bc43ce013ffe1d5e3ba66a0cb352c2`
- `huggingface_publish_evidence.path_in_repo`: `releases/2026.07.0`
- `huggingface_publish_evidence.remote_manifest_verified`: `true`
- `release_evidence.quality.record_count`: 5
- `release_evidence.collection_quality_gates.status`: `pass`

GitHub release evidence:

- Release URL: `https://github.com/edithatogo/corpus-cases-medilegal-nz/releases/tag/dataset-v2026.07.0`
- Release tag: `dataset-v2026.07.0`
- Release state: published release, not draft, not prerelease.
- Attached assets include archive bundle, `SHA256SUMS`, release evidence,
  checksum manifest, source coverage, public surface audit, metadata package
  manifest, CycloneDX SBOM, and SPDX SBOM.

## Residual Notes

The workflow annotation reports that `actions/upload-artifact@v5` targets
Node.js 20 but is currently forced to Node.js 24 by GitHub Actions runner
compatibility behavior. This is informational and did not block the run.
