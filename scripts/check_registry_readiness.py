"""Validate the repository-side dataset registry readiness contract."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READINESS_DOC = ROOT / "docs" / "registry-readiness.md"
README = ROOT / "README.md"
ARCHIVE_DOC = ROOT / "docs" / "monthly-dynamic-archive-publication.md"
REQUIRED_FRAGMENTS = ("repository_ready_external_gates_pending", "source-specific rights", "Hugging Face", "Zenodo", "Croissant", "#20", "#21", "#22")


def check() -> None:
    if not READINESS_DOC.is_file():
        raise AssertionError(f"Missing {READINESS_DOC.relative_to(ROOT)}")
    text = READINESS_DOC.read_text(encoding="utf-8")
    missing = [fragment for fragment in REQUIRED_FRAGMENTS if fragment not in text]
    if missing:
        raise AssertionError("Registry readiness document missing: " + ", ".join(missing))
    if not (ROOT / "LICENSE").is_file():
        raise AssertionError("Missing repository code licence")
    for path, fragments in ((README, ("Hugging Face", "License")), (ARCHIVE_DOC, ("Zenodo", "Hugging Face", "rights", "metadata"))):
        source = path.read_text(encoding="utf-8")
        missing = [fragment for fragment in fragments if fragment.lower() not in source.lower()]
        if missing:
            raise AssertionError(f"{path.relative_to(ROOT)} missing: {', '.join(missing)}")


def main() -> int:
    argparse.ArgumentParser().parse_args()
    check()
    print("Dataset registry readiness contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
