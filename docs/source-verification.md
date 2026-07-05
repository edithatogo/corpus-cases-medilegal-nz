# Source Verification And Reproducible Evidence

This repository separates parser proof from historical completeness proof.

Parser proof shows that each configured source can emit normalized records. Source verification shows whether processed records reconcile against archived source-index evidence.

## Verification Modes

- `fixture`: deterministic no-network mode. It archives the checked-in fixture listings, replays them by hash, normalizes expected records, and reconciles them against processed records.
- `live`: manual/scheduled network mode. It downloads public source entry pages into an evidence archive. Failed fetches are recorded as blockers instead of silently skipped.

## Commands

Build feasibility only:

```bash
uv run python -m corpus_cases_medilegal_nz.cli source-verification-feasibility
```

Archive verification inputs:

```bash
uv run python -m corpus_cases_medilegal_nz.cli source-verification-fetch --output-dir generated/source-verification --mode fixture
```

Replay archived inputs and verify hashes:

```bash
uv run python -m corpus_cases_medilegal_nz.cli source-verification-replay --evidence-dir generated/source-verification
```

Build the full verification bundle:

```bash
uv run python -m corpus_cases_medilegal_nz.cli source-verification --output-dir generated/source-verification --mode fixture
```

Check whether complete-corpus claims are currently evidence-safe:

```bash
uv run python -m corpus_cases_medilegal_nz.cli corpus-completion-readiness
```

Use live verification inputs for the same gate:

```bash
uv run python -m corpus_cases_medilegal_nz.cli corpus-completion-readiness --verification-mode live
```

This command exits non-zero while source rights review, parser replacement,
candidate promotion, source verification, or completeness reconciliation gates
remain unresolved. A blocked result is expected until the live historical
backfill track has source-specific proof for every relevant source.

Live mode is explicit:

```bash
uv run python -m corpus_cases_medilegal_nz.cli source-verification --output-dir generated/source-verification-live --mode live
```

Build a non-mutating live historical backfill proof from archived live expected
records:

```bash
uv run python -m corpus_cases_medilegal_nz.cli live-backfill-proof --output-dir generated/live-backfill-proof
```

The live backfill proof writes generated processed-style records under
`generated/live-backfill-proof/jsonl/records.jsonl` and reconciles them against
the archived live expected-record ledger. It does not replace the canonical
processed corpus unless a release workflow explicitly promotes those artifacts.

## Evidence Layout

- `raw/<source_id>/listing.html`: archived source-index input.
- `manifests/source_verification_feasibility.json`: feasibility and blocker classification.
- `manifests/verification_input_manifest.json`: input checksums, retrieval metadata, and rights notes.
- `manifests/verification_replay.json`: offline replay and hash verification.
- `manifests/source_expected_records.jsonl`: normalized expected-record ledger.
- `manifests/source_verification_reconciliation.json`: expected-versus-processed gap ledger.
- `manifests/source_verification_public_claims.json`: public-safe generated claims.
- `manifests/source_verification_summary.json`: aggregate verification bundle.
- `manifests/corpus_completion_readiness.json`: complete-corpus claim gate covering
  verification, rights, parser, candidate-source, and reconciliation blockers.
- `generated/live-backfill-proof/`: non-mutating proof artifacts for a
  live-backed historical-record projection and reconciliation.

## Publication Integration

Monthly publication now includes source verification evidence in `release_evidence.json` and writes verification manifests alongside the other release ledgers. Hugging Face and Zenodo publication should treat these ledgers as reproducible evidence for completeness claims.

Large raw live evidence should be attached to release/Hugging Face/Zenodo artifacts rather than committed to Git. Small normalized manifests remain safe release assets.

## Blocker Policy

Blocked sources must remain explicit. Do not convert source access failures into zero-record success. Use:

- `blocked` for HTTP failures, anti-bot controls, inaccessible indexes, or missing reproducible inputs.
- `metadata_only` when raw archiving is not permitted but source metadata can be cited.
- `manual_review_required` when terms, privacy, or redistribution status is unclear.

Public claims must be generated from verification ledgers and must include caveats for blocked or partially verified sources.
Complete-corpus claims must additionally pass `corpus_completion_readiness`;
fixture-backed parser proof alone is not sufficient.
