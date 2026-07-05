# Live Readiness Evidence

Generated on 2026-07-05T16:20Z from local CLI verification.

## Commands

```powershell
uv run python -m corpus_cases_medilegal_nz.cli collection-proof
uv run python -m corpus_cases_medilegal_nz.cli corpus-completion-readiness --verification-mode fixture
uv run python -m corpus_cases_medilegal_nz.cli source-verification --output-dir generated/source-verification-live --mode live
uv run python -m corpus_cases_medilegal_nz.cli corpus-completion-readiness --verification-mode live
uv run python -m corpus_cases_medilegal_nz.cli live-backfill-proof --output-dir generated/live-backfill-proof
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

## Interpretation

The repo-local gates, rights review, parser replacement proof, and candidate
scaffolding are implemented. The current canonical processed fixture corpus does
not reconcile against the live source indexes, so canonical complete-corpus
claims remain blocked for the existing checked-in processed outputs. A
non-mutating live historical backfill proof now projects 52 live expected records
into processed-style records and reconciles them completely, providing the
promotion candidate for the next canonical release workflow.
