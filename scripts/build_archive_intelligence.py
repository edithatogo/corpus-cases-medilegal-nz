"""Build archive intelligence reports from monthly release evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from corpus_cases_medilegal_nz.archive_intelligence import (  # noqa: E402
    write_archive_intelligence_report,
)


def main() -> int:
    """Run archive intelligence report generation."""
    parser = argparse.ArgumentParser(description="Build archive intelligence report.")
    parser.add_argument(
        "--release-evidence",
        default="generated/monthly-publication/manifests/release_evidence.json",
    )
    parser.add_argument(
        "--output",
        default="generated/archive-intelligence/archive_maturity.json",
    )
    ns = parser.parse_args()
    report = write_archive_intelligence_report(
        release_evidence_path=ROOT / ns.release_evidence,
        output_path=ROOT / ns.output,
    )
    print(json.dumps(report, indent=2, sort_keys=True))  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
