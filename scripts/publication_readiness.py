"""Check monthly archive publication readiness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from corpus_cases_medilegal_nz.archive import publication_readiness  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run publication readiness checks."""
    parser = argparse.ArgumentParser(description="Check publication readiness.")
    parser.add_argument("--strict", action="store_true")
    ns = parser.parse_args(argv)
    report = publication_readiness(root=ROOT)
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 1 if ns.strict and report["status"] != "ready" else 0


if __name__ == "__main__":
    raise SystemExit(main())
