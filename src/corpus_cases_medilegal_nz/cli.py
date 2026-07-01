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
from corpus_cases_medilegal_nz.collection_proof import write_collection_proof
from corpus_cases_medilegal_nz.hf_sync import main as hf_sync_main
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
    else:
        parser.error(f"Unhandled command: {ns.command}")
        exit_code = 2
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
