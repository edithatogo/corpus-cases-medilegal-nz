from __future__ import annotations

from corpus_cases_medilegal_nz import cli


def test_corpus_completion_readiness_cli_supports_live_mode(monkeypatch) -> None:
    calls: dict[str, object] = {}

    monkeypatch.setattr(cli, "load_jsonl_records", lambda _path: [])

    def fake_verification(**kwargs):
        calls.update(kwargs)
        return {
            "status": "verified_complete",
            "target_metadata": {"sources": {}},
            "reconciliation": {
                "summary": {
                    "missing_count": 0,
                    "extra_count": 0,
                    "duplicate_count": 0,
                    "ambiguous_count": 0,
                }
            },
        }

    monkeypatch.setattr(cli, "build_source_verification_bundle", fake_verification)
    monkeypatch.setattr(
        cli,
        "build_source_completeness_ledger",
        lambda **_kwargs: {"status": "pass"},
    )
    monkeypatch.setattr(
        cli,
        "build_source_rights_review_ledger",
        lambda: {"sources": []},
    )
    monkeypatch.setattr(cli, "build_parser_risk_ledger", lambda: {"sources": []})
    monkeypatch.setattr(cli, "build_source_discovery_queue", lambda: {"candidates": []})

    exit_code = cli.main(["corpus-completion-readiness", "--verification-mode", "live"])

    assert exit_code == 0
    assert calls["mode"] == "live"
    assert str(calls["output_dir"]).endswith("generated\\source-verification-live") or str(
        calls["output_dir"]
    ).endswith("generated/source-verification-live")


def test_live_backfill_proof_cli_reports_status(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "build_live_backfill_proof",
        lambda **_kwargs: {"status": "pass", "record_count": 1},
    )

    assert cli.main(["live-backfill-proof"]) == 0
