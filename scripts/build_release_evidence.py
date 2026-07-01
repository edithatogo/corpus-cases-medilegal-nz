"""Build monthly archive release evidence artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from corpus_cases_medilegal_nz.archive import build_release_artifacts  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run the release evidence artifact builder."""
    parser = argparse.ArgumentParser(description="Build monthly release evidence artifacts.")
    parser.add_argument("--output-dir", default="generated/monthly-publication")
    parser.add_argument("--archive-version", default="")
    parser.add_argument("--hf-repo-id", default="edithatogo/corpus-cases-medilegal-nz")
    parser.add_argument("--hf-revision", default="")
    parser.add_argument("--zenodo-draft-id", default="")
    parser.add_argument("--zenodo-record-url", default="")
    parser.add_argument("--zenodo-doi", default="")
    parser.add_argument("--zenodo-concept-doi", default="")
    ns = parser.parse_args(argv)
    summary = build_release_artifacts(
        output_dir=Path(ns.output_dir),
        root=ROOT,
        archive_version=ns.archive_version or None,
        hf_repo_id=ns.hf_repo_id,
        hf_revision=ns.hf_revision,
        zenodo_draft_id=ns.zenodo_draft_id,
        zenodo_record_url=ns.zenodo_record_url,
        zenodo_doi=ns.zenodo_doi,
        zenodo_concept_doi=ns.zenodo_concept_doi,
    )
    sys.stdout.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
