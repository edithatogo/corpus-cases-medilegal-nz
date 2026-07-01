"""Validate public surface audit release evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    """Run public surface audit validation checks."""
    parser = argparse.ArgumentParser(description="Validate public surface audit evidence.")
    parser.add_argument(
        "--path",
        default="generated/monthly-publication/manifests/public_surface_audit.json",
    )
    parser.add_argument("--require-file", action="store_true")
    ns = parser.parse_args(argv)
    path = ROOT / ns.path
    failures: list[str] = []
    if not path.is_file():
        if ns.require_file:
            failures.append(f"{ns.path} is missing.")
    else:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        surfaces = payload.get("surfaces", {})
        for required in ("github", "hugging_face", "zenodo", "osf", "future_metadata"):
            if required not in surfaces:
                failures.append(f"Missing surface: {required}")
        osf = surfaces.get("osf", {})
        if isinstance(osf, dict) and osf.get("status") != "inactive":
            failures.append("OSF must stay inactive until a dedicated activation track.")
    if failures:
        for failure in failures:
            sys.stderr.write(f"PUBLIC-SURFACE: {failure}\n")
        return 1
    sys.stdout.write("Public surface audit checks passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
