"""Validate monthly release evidence artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from corpus_cases_medilegal_nz.archive import validate_release_evidence  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run release evidence validation checks."""
    parser = argparse.ArgumentParser(description="Validate release evidence artifacts.")
    parser.add_argument(
        "--path",
        default="generated/monthly-publication/manifests/release_evidence.json",
    )
    parser.add_argument("--require-file", action="store_true")
    ns = parser.parse_args(argv)
    evidence_path = ROOT / ns.path
    schema_path = ROOT / "schemas/release_evidence.schema.json"
    failures: list[str] = []
    if not schema_path.is_file():
        failures.append("schemas/release_evidence.schema.json is missing.")
    if evidence_path.is_file():
        payload = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
        failures.extend(validate_release_evidence(payload))
    elif ns.require_file:
        failures.append(f"{ns.path} is missing.")
    if failures:
        for failure in failures:
            sys.stderr.write(f"RELEASE-EVIDENCE: {failure}\n")
        return 1
    sys.stdout.write("Release evidence checks passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
