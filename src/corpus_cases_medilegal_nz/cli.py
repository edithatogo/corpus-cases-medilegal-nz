"""CLI-first entrypoint for the medilegal corpus repository."""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence

from corpus_cases_medilegal_nz.hf_sync import main as hf_sync_main
from corpus_cases_medilegal_nz.sources import get_source_ids


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Medilegal corpus CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sources", help="List configured source identifiers.")
    sync = sub.add_parser("sync", help="Run the existing Hugging Face sync pipeline.")
    sync.add_argument("source", nargs="?", help="Optional source ID such as hdc, hpdt, or era.")
    ns = parser.parse_args(argv)
    if ns.command == "sources":
        for source_id in get_source_ids():
            print(source_id)
        return 0
    if ns.command == "sync":
        if ns.source:
            os.environ["SOURCE_ID"] = ns.source
        hf_sync_main()
        return 0
    parser.error(f"Unhandled command: {ns.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
