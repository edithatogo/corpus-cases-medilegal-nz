"""Check mirror workflow readiness."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from corpus_cases_medilegal_nz.mirror import mirror_sync_readiness  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run mirror readiness checks."""
    _ = argv
    report = mirror_sync_readiness(root=ROOT)
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
