from __future__ import annotations

import json
from pathlib import Path

from corpus_cases_medilegal_nz.archive import build_release_evidence, write_metadata_packages
from corpus_cases_medilegal_nz.archive_intelligence import (
    MATURITY_DIMENSIONS,
    build_archive_intelligence_from_file,
    build_archive_maturity_report,
    severity_for_score,
    write_archive_intelligence_report,
)

ROOT = Path(__file__).resolve().parents[1]


def _complete_evidence(tmp_path: Path) -> dict:
    evidence = build_release_evidence(
        root=ROOT,
        archive_version="2026.07.0",
        hf_revision="abc123",
        zenodo_draft_id="21119990",
        zenodo_record_url="https://zenodo.org/deposit/21119990",
        github_release_url="https://github.com/edithatogo/corpus-cases-medilegal-nz/releases/tag/dataset-v2026.07.0",
    )
    metadata_manifest = write_metadata_packages(tmp_path, evidence)
    evidence["metadata_packages"] = metadata_manifest
    return evidence


def test_maturity_dimensions_are_weighted_to_100() -> None:
    assert sum(dimension.weight for dimension in MATURITY_DIMENSIONS) == 100
    assert [dimension.dimension_id for dimension in MATURITY_DIMENSIONS] == [
        "release_evidence_completeness",
        "source_coverage_completeness",
        "collection_and_parsing_progress",
        "metadata_package_completeness",
        "public_surface_consistency",
        "security_and_provenance_posture",
        "remote_publication_proof",
    ]


def test_severity_for_score_boundaries() -> None:
    assert severity_for_score(95) == "leading"
    assert severity_for_score(80) == "strong"
    assert severity_for_score(65) == "developing"
    assert severity_for_score(50) == "fragile"
    assert severity_for_score(25) == "blocked"


def test_archive_maturity_report_scores_complete_evidence(tmp_path: Path) -> None:
    report = build_archive_maturity_report(_complete_evidence(tmp_path))

    assert report["schema_version"] == "1.0.0"
    assert report["score"] >= 90
    assert report["severity"] == "leading"
    assert report["blocking_dimensions"] == []
    dimensions = {dimension["id"]: dimension for dimension in report["dimensions"]}
    assert dimensions["metadata_package_completeness"]["score"] == 100
    assert dimensions["remote_publication_proof"]["score"] == 100


def test_archive_maturity_report_surfaces_missing_evidence() -> None:
    report = build_archive_maturity_report({"release": {}})

    assert report["severity"] == "blocked"
    assert "release_evidence_completeness" in report["blocking_dimensions"]
    dimensions = {dimension["id"]: dimension for dimension in report["dimensions"]}
    assert dimensions["metadata_package_completeness"]["severity"] == "blocked"
    assert dimensions["remote_publication_proof"]["evidence"]["failed_checks"]


def test_write_archive_intelligence_report(tmp_path: Path) -> None:
    evidence_path = tmp_path / "release_evidence.json"
    output_path = tmp_path / "archive_maturity.json"
    evidence_path.write_text(json.dumps(_complete_evidence(tmp_path)), encoding="utf-8")

    report = write_archive_intelligence_report(evidence_path, output_path)

    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8"))["score"] == report["score"]


def test_archive_intelligence_loads_sibling_metadata_manifest(tmp_path: Path) -> None:
    release_dir = tmp_path / "manifests"
    metadata_dir = tmp_path / "metadata"
    release_dir.mkdir()
    metadata_dir.mkdir()
    evidence = _complete_evidence(tmp_path)
    metadata_manifest = evidence.pop("metadata_packages")
    (release_dir / "release_evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
    (metadata_dir / "metadata_packages_manifest.json").write_text(
        json.dumps(metadata_manifest),
        encoding="utf-8",
    )

    report = build_archive_intelligence_from_file(release_dir / "release_evidence.json")

    dimensions = {dimension["id"]: dimension for dimension in report["dimensions"]}
    assert dimensions["metadata_package_completeness"]["score"] == 100
