"""CLI-first entrypoint for the medilegal corpus repository."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from pathlib import Path

from corpus_cases_medilegal_nz.archive import (
    build_source_collection_audit,
    load_jsonl_records,
    publication_readiness,
)
from corpus_cases_medilegal_nz.archive_intelligence import (
    validate_archive_intelligence_report,
    write_archive_intelligence_report,
    write_archive_intelligence_report_from_artifact_dir,
)
from corpus_cases_medilegal_nz.collection_proof import write_collection_proof
from corpus_cases_medilegal_nz.hf_sync import main as hf_sync_main
from corpus_cases_medilegal_nz.mirror import mirror_sync_readiness
from corpus_cases_medilegal_nz.parser_contract import build_parser_contract
from corpus_cases_medilegal_nz.source_maturity import (
    build_corpus_completion_readiness,
    build_candidate_coverage_report,
    build_parser_risk_ledger,
    build_publication_governance_ledger,
    build_redundant_source_validation_ledger,
    build_source_completeness_ledger,
    build_source_discovery_queue,
    build_source_maturity_ledger,
    build_source_rights_review_ledger,
)
from corpus_cases_medilegal_nz.source_verification import (
    build_live_backfill_proof,
    build_source_verification_bundle,
    build_source_verification_feasibility,
    fetch_verification_inputs,
    replay_verification_inputs,
)
from corpus_cases_medilegal_nz.sources import get_source_ids


def main(argv: Sequence[str] | None = None) -> int:
    """Run the repository command-line interface."""
    parser = argparse.ArgumentParser(description="Medilegal corpus CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sources", help="List configured source identifiers.")
    sub.add_parser("source-audit", help="Report source collection and parser completion state.")
    sub.add_parser(
        "source-maturity",
        help="Report source maturity beyond parser validation.",
    )
    sub.add_parser(
        "source-completeness",
        help="Report historical backfill completeness reconciliation.",
    )
    sub.add_parser("source-discovery", help="Report review-gated candidate source queue.")
    sub.add_parser("candidate-coverage", help="Report candidate promotion and witness coverage.")
    sub.add_parser(
        "redundant-validation",
        help="Report redundant public witness validation coverage.",
    )
    sub.add_parser("source-rights", help="Report source-level rights review ledger.")
    sub.add_parser("parser-risk", help="Report parser replacement and live-smoke priorities.")
    sub.add_parser("publication-governance", help="Report remaining publication governance gates.")
    completion_readiness = sub.add_parser(
        "corpus-completion-readiness",
        help="Report whether complete-corpus claims are currently evidence-safe.",
    )
    completion_readiness.add_argument(
        "--verification-mode",
        choices=("fixture", "live"),
        default="fixture",
        help="Source verification mode used for the readiness gate.",
    )
    sub.add_parser(
        "source-verification-feasibility",
        help="Report source verification input feasibility.",
    )
    verification_fetch = sub.add_parser(
        "source-verification-fetch",
        help="Archive source verification inputs.",
    )
    verification_fetch.add_argument("--output-dir", default="generated/source-verification")
    verification_fetch.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    verification_replay = sub.add_parser(
        "source-verification-replay",
        help="Replay archived source verification inputs and verify hashes.",
    )
    verification_replay.add_argument("--evidence-dir", default="generated/source-verification")
    verification = sub.add_parser(
        "source-verification",
        help="Build source verification feasibility, evidence archive, replay, and reconciliation.",
    )
    verification.add_argument("--output-dir", default="generated/source-verification")
    verification.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    live_backfill = sub.add_parser(
        "live-backfill-proof",
        help="Build generated live backfill proof without replacing canonical data.",
    )
    live_backfill.add_argument("--output-dir", default="generated/live-backfill-proof")
    proof = sub.add_parser("collection-proof", help="Build deterministic local collection proof.")
    proof.add_argument("--output-dir", default="data/processed")
    proof.add_argument("--fixture-root", default="tests/fixtures/sources")
    proof.add_argument("--previous-records", default=None)
    sub.add_parser("parser-contract", help="Print the nlp-policy-nz parser contract.")
    sync = sub.add_parser("sync", help="Run the existing Hugging Face sync pipeline.")
    sync.add_argument("source", nargs="?", help="Optional source ID such as hdc, hpdt, or era.")
    readiness = sub.add_parser(
        "publication-readiness",
        help="Check local monthly archive publication readiness.",
    )
    readiness.add_argument("--strict", action="store_true", help="Exit non-zero on blockers.")
    mirror = sub.add_parser(
        "mirror-readiness",
        help="Check mirror workflow readiness and secret gating.",
    )
    mirror.add_argument("--strict", action="store_true", help="Exit non-zero on blockers.")
    mirror.add_argument(
        "--probe-remotes",
        action="store_true",
        help="Probe configured mirror HEADs and flag incompatible remote object formats.",
    )
    intelligence = sub.add_parser(
        "archive-intelligence",
        help="Build archive maturity intelligence from monthly release evidence.",
    )
    scope = intelligence.add_mutually_exclusive_group()
    scope.add_argument(
        "--release-evidence",
        default="generated/monthly-publication/manifests/release_evidence.json",
    )
    scope.add_argument("--artifact-dir", default="")
    intelligence.add_argument(
        "--output",
        default="generated/archive-intelligence/archive_maturity.json",
    )
    intelligence.add_argument("--strict", action="store_true")
    ns = parser.parse_args(argv)
    exit_code = 0
    if ns.command == "sources":
        for source_id in get_source_ids():
            print(source_id)  # noqa: T201
    elif ns.command == "source-audit":
        records = load_jsonl_records(Path("data/processed/jsonl/records.jsonl"))
        result = build_source_collection_audit(records=records)
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "source-maturity":
        records = load_jsonl_records(Path("data/processed/jsonl/records.jsonl"))
        result = build_source_maturity_ledger(records=records)
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "source-completeness":
        records = load_jsonl_records(Path("data/processed/jsonl/records.jsonl"))
        result = build_source_completeness_ledger(records=records)
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "source-discovery":
        result = build_source_discovery_queue()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "candidate-coverage":
        result = build_candidate_coverage_report()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "redundant-validation":
        result = build_redundant_source_validation_ledger()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "source-rights":
        result = build_source_rights_review_ledger()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "parser-risk":
        result = build_parser_risk_ledger()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "publication-governance":
        result = build_publication_governance_ledger()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "corpus-completion-readiness":
        records = load_jsonl_records(Path("data/processed/jsonl/records.jsonl"))
        evidence_dir = (
            Path("generated/source-verification-live")
            if ns.verification_mode == "live"
            else Path("generated/source-verification")
        )
        verification = build_source_verification_bundle(
            output_dir=evidence_dir,
            processed_records=records,
            mode=ns.verification_mode,
        )
        result = build_corpus_completion_readiness(
            source_completeness=build_source_completeness_ledger(
                records=records,
                target_metadata=verification["target_metadata"],
            ),
            source_rights_review=build_source_rights_review_ledger(),
            parser_risk=build_parser_risk_ledger(),
            source_discovery_queue=build_source_discovery_queue(),
            source_verification=verification,
            strict=True,
        )
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        if result["status"] == "blocked":
            exit_code = 1
    elif ns.command == "source-verification-feasibility":
        result = build_source_verification_feasibility()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "source-verification-fetch":
        result = fetch_verification_inputs(output_dir=Path(ns.output_dir), mode=ns.mode)
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "source-verification-replay":
        result = replay_verification_inputs(Path(ns.evidence_dir))
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        if result["status"] != "pass":
            exit_code = 1
    elif ns.command == "source-verification":
        records = load_jsonl_records(Path("data/processed/jsonl/records.jsonl"))
        result = build_source_verification_bundle(
            output_dir=Path(ns.output_dir),
            processed_records=records,
            mode=ns.mode,
        )
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        if result["status"] == "blocked":
            exit_code = 1
    elif ns.command == "live-backfill-proof":
        result = build_live_backfill_proof(output_dir=Path(ns.output_dir))
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        if result["status"] != "pass":
            exit_code = 1
    elif ns.command == "collection-proof":
        result = write_collection_proof(
            output_dir=Path(ns.output_dir),
            fixture_root=Path(ns.fixture_root),
            previous_records_path=Path(ns.previous_records) if ns.previous_records else None,
        )
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "parser-contract":
        result = build_parser_contract()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
    elif ns.command == "sync":
        if ns.source:
            os.environ["SOURCE_ID"] = ns.source
        hf_sync_main()
    elif ns.command == "publication-readiness":
        result = publication_readiness()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        if ns.strict and result["status"] != "ready":
            exit_code = 1
    elif ns.command == "mirror-readiness":
        result = mirror_sync_readiness(
            require_complete_mirror_set=ns.strict,
            probe_remotes=ns.probe_remotes,
        )
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        if ns.strict and result["status"] != "ready":
            exit_code = 1
    elif ns.command == "archive-intelligence":
        if ns.artifact_dir:
            result = write_archive_intelligence_report_from_artifact_dir(
                artifact_dir=Path(ns.artifact_dir),
                output_path=Path(ns.output),
            )
        else:
            result = write_archive_intelligence_report(
                release_evidence_path=Path(ns.release_evidence),
                output_path=Path(ns.output),
            )
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        failures = validate_archive_intelligence_report(result, strict=ns.strict)
        if failures:
            for failure in failures:
                print(failure)  # noqa: T201
            exit_code = 1
    else:
        parser.error(f"Unhandled command: {ns.command}")
        exit_code = 2
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
