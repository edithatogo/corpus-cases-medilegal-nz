"""Validate generated discovery metadata package manifests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    """Run metadata package validation checks."""
    parser = argparse.ArgumentParser(description="Validate generated metadata package manifest.")
    parser.add_argument(
        "--path",
        default="generated/monthly-publication/metadata/metadata_packages_manifest.json",
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
        packages = payload.get("packages", [])
        expected = {
            "croissant.jsonld",
            "ro-crate-metadata.json",
            "datapackage.json",
            "dcat.jsonld",
            "prov-o.jsonld",
            "datacite.json",
            "schema-org-dataset.jsonld",
            "huggingface-dataset-card-metadata.json",
        }
        seen = {Path(str(item.get("path", ""))).name for item in packages if isinstance(item, dict)}
        missing = sorted(expected - seen)
        if missing:
            failures.append("Missing metadata packages: " + ", ".join(missing))
    if failures:
        for failure in failures:
            sys.stderr.write(f"METADATA-PACKAGES: {failure}\n")
        return 1
    sys.stdout.write("Metadata package checks passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
