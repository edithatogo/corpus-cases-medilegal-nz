"""Check mirror workflow readiness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from corpus_cases_medilegal_nz.mirror import mirror_sync_readiness  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run mirror readiness checks."""
    parser = argparse.ArgumentParser(description="Check mirror workflow readiness.")
    parser.add_argument("--strict", action="store_true", help="Require the full mirror target set.")
    parser.add_argument(
        "--probe-remotes",
        action="store_true",
        help="Probe configured mirror HEADs and flag incompatible remote object formats.",
    )
    ns = parser.parse_args(argv)
    report = mirror_sync_readiness(
        root=ROOT,
        require_complete_mirror_set=ns.strict,
        probe_remotes=ns.probe_remotes,
    )
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
