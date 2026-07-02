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
from corpus_cases_medilegal_nz.sources import get_source_ids


def main(argv: Sequence[str] | None = None) -> int:
    """Run the repository command-line interface."""
    parser = argparse.ArgumentParser(description="Medilegal corpus CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sources", help="List configured source identifiers.")
    sub.add_parser("source-audit", help="Report source collection and parser completion state.")
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
        result = mirror_sync_readiness()
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
