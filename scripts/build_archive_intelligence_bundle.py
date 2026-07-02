"""Build the full archive intelligence bundle from monthly publication artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from corpus_cases_medilegal_nz.archive_intelligence import (  # noqa: E402
    write_archive_intelligence_bundle,
)


def main(argv: list[str] | None = None) -> int:
    """Run the archive intelligence bundle builder."""
    parser = argparse.ArgumentParser(description="Build archive intelligence bundle artifacts.")
    parser.add_argument("--artifact-dir", default="generated/monthly-publication")
    parser.add_argument("--output-dir", default="generated/archive-intelligence")
    ns = parser.parse_args(argv)
    bundle = write_archive_intelligence_bundle(
        artifact_dir=Path(ns.artifact_dir),
        output_dir=Path(ns.output_dir),
        root=ROOT,
    )
    sys.stdout.write(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
