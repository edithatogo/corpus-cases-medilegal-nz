"""CLI-first entrypoint for the medilegal corpus repository."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence

from corpus_cases_medilegal_nz.archive import build_source_collection_audit, publication_readiness
from corpus_cases_medilegal_nz.hf_sync import main as hf_sync_main
from corpus_cases_medilegal_nz.sources import get_source_ids


def main(argv: Sequence[str] | None = None) -> int:
    """Run the repository command-line interface."""
    parser = argparse.ArgumentParser(description="Medilegal corpus CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sources", help="List configured source identifiers.")
    sub.add_parser("source-audit", help="Report source collection and parser completion state.")
    sync = sub.add_parser("sync", help="Run the existing Hugging Face sync pipeline.")
    sync.add_argument("source", nargs="?", help="Optional source ID such as hdc, hpdt, or era.")
    readiness = sub.add_parser(
        "publication-readiness",
        help="Check local monthly archive publication readiness.",
    )
    readiness.add_argument("--strict", action="store_true", help="Exit non-zero on blockers.")
    ns = parser.parse_args(argv)
    if ns.command == "sources":
        for source_id in get_source_ids():
            print(source_id)  # noqa: T201
        return 0
    if ns.command == "source-audit":
        result = build_source_collection_audit()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        return 0
    if ns.command == "sync":
        if ns.source:
            os.environ["SOURCE_ID"] = ns.source
        hf_sync_main()
        return 0
    if ns.command == "publication-readiness":
        result = publication_readiness()
        print(json.dumps(result, indent=2, sort_keys=True))  # noqa: T201
        if ns.strict and result["status"] != "ready":
            return 1
        return 0
    parser.error(f"Unhandled command: {ns.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
