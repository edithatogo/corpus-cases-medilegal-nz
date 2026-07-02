from __future__ import annotations

import json
from pathlib import Path

from corpus_cases_medilegal_nz.archive import (
    build_attestation_verification,
    build_collection_quality_gates,
    build_legal_provenance,
    build_public_surface_audit,
    build_quality_report,
    build_source_collection_audit,
    build_source_coverage,
    write_metadata_packages,
)
from corpus_cases_medilegal_nz.archive_intelligence import (
    MATURITY_DIMENSIONS,
    build_archive_anomaly_report,
    build_archive_intelligence_from_artifact_dir,
    build_archive_intelligence_from_file,
    build_archive_maturity_report,
    build_federation_compatibility_report,
    build_privacy_rights_scoring,
    build_public_claims,
    build_source_observability_ledger,
    severity_for_score,
    validate_archive_intelligence_report,
    write_archive_intelligence_bundle,
    write_archive_intelligence_report,
)

ROOT = Path(__file__).resolve().parents[1]


def _complete_evidence(tmp_path: Path) -> dict:
    records = [
        {
            "id": f"{source}-1",
            "source": source,
            "text": "Example text.",
            "date": "2026-07-02",
            "url": "https://example.com/decision",
            "metadata": {
                "retrieved_at": "2026-07-02T00:00:00Z",
                "parsed_at": "2026-07-02T00:15:00Z",
                "document_class": "decision",
                "rights_review_status": "reviewed",
            },
        }
        for source in ("hdc", "hpdt", "moj_tribunals", "era", "teachers")
    ]
    evidence = {
        "release": {
            "archive_version": "2026.07.0",
            "github_release_tag": "dataset-v2026.07.0",
            "github_release_url": "",
            "coverage_statement": (
                "Monthly medilegal corpus archive. Current publication coverage is "
                "source-specific and evidence-backed by source_coverage.json."
            ),
        },
        "git": {"commit_sha": "abc123", "workflow_run_id": "123456"},
        "checksums": {
            "manifest_path": "manifests/checksum_manifest.json",
            "sha256sums_path": "SHA256SUMS",
            "manifest_sha256": "abc123",
            "artifact_count": 9,
        },
        "quality": build_quality_report(records),
        "source_coverage": build_source_coverage(root=ROOT, records=records),
        "source_collection_audit": build_source_collection_audit(root=ROOT, records=records),
        "collection_quality_gates": build_collection_quality_gates(records),
        "public_surface": build_public_surface_audit(
            archive_version="2026.07.0",
            hf_revision="",
            zenodo_record_url="",
        ),
        "legal_provenance": build_legal_provenance(),
        "attestation_verification": build_attestation_verification("2026.07.0"),
        "hugging_face": {
            "repo_id": "edithatogo/corpus-cases-medilegal-nz",
            "revision": "",
            "remote_manifest_verified": False,
        },
        "zenodo": {
            "draft_id": "",
            "record_url": "",
            "doi": "",
            "concept_doi": "",
            "publish_handoff_only": True,
        },
    }
    metadata_manifest = write_metadata_packages(tmp_path, evidence)
    evidence["metadata_packages"] = metadata_manifest
    return evidence


def _write_complete_artifact_dir(tmp_path: Path) -> Path:
    root_dir = tmp_path
    artifact_dir = root_dir / "monthly-publication"
    manifests_dir = artifact_dir / "manifests"
    metadata_dir = artifact_dir / "metadata"
    records_dir = root_dir / "data" / "processed" / "jsonl"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    records_dir.mkdir(parents=True, exist_ok=True)
    evidence = _complete_evidence(tmp_path)
    metadata_manifest = evidence.pop("metadata_packages")
    records = [
        {
            "id": f"{source}-1",
            "source": source,
            "text": "Example text.",
            "date": "2026-07-02",
            "url": "https://example.com/decision",
            "metadata": {
                "retrieved_at": "2026-07-02T00:00:00Z",
                "parsed_at": "2026-07-02T00:15:00Z",
                "document_class": "decision",
                "rights_review_status": "reviewed",
            },
        }
        for source in ("hdc", "hpdt", "moj_tribunals", "era", "teachers")
    ]
    (records_dir / "records.jsonl").write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )
    (manifests_dir / "release_evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
    (metadata_dir / "metadata_packages_manifest.json").write_text(
        json.dumps(metadata_manifest),
        encoding="utf-8",
    )
    (manifests_dir / "github_release_evidence.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "github_release_tag": "dataset-v2026.07.0",
                "github_release_url": "https://github.com/edithatogo/corpus-cases-medilegal-nz/releases/tag/dataset-v2026.07.0",
            }
        ),
        encoding="utf-8",
    )
    (manifests_dir / "huggingface_publish_evidence.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "repo_id": "edithatogo/corpus-cases-medilegal-nz",
                "revision": "abc123",
                "remote_manifest_verified": True,
                "path_in_repo": "releases/2026.07.0",
            }
        ),
        encoding="utf-8",
    )
    (manifests_dir / "zenodo_draft_evidence.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "archive_version": "2026.07.0",
                "deposition_id": "21119990",
                "record_url": "https://zenodo.org/deposit/21119990",
                "doi": "",
                "concept_doi": "",
                "publish_handoff_only": True,
            }
        ),
        encoding="utf-8",
    )
    return artifact_dir


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
    assert report["score"] >= 75
    assert report["severity"] in {"strong", "leading"}
    dimensions = {dimension["id"]: dimension for dimension in report["dimensions"]}
    assert dimensions["release_evidence_completeness"]["score"] == 100
    assert dimensions["metadata_package_completeness"]["score"] == 100
    assert dimensions["remote_publication_proof"]["score"] < 100


def test_archive_maturity_report_surfaces_missing_evidence() -> None:
    report = build_archive_maturity_report({"release": {}})

    assert report["severity"] == "blocked"
    assert "release_evidence_completeness" in report["blocking_dimensions"]
    dimensions = {dimension["id"]: dimension for dimension in report["dimensions"]}
    assert dimensions["metadata_package_completeness"]["severity"] == "blocked"
    assert dimensions["remote_publication_proof"]["evidence"]["failed_checks"]


def test_source_observability_ledger_captures_drift_and_review_state(tmp_path: Path) -> None:
    current_records = [
        {
            "id": "hdc-1",
            "source": "hdc",
            "text": "Example text.",
            "date": "2026-07-02",
            "url": "https://example.com/decision",
            "metadata": {
                "retrieved_at": "2026-07-02T00:00:00Z",
                "parsed_at": "2026-07-02T00:15:00Z",
                "document_class": "decision",
                "rights_review_status": "reviewed",
            },
        }
    ]
    previous_records = [
        *current_records,
        {
            "id": "hdc-2",
            "source": "hdc",
            "text": "Example text.",
            "date": "2026-07-01",
            "url": "https://example.com/decision-2",
            "metadata": {
                "retrieved_at": "2026-07-01T00:00:00Z",
                "parsed_at": "2026-07-01T00:15:00Z",
                "document_class": "decision",
                "rights_review_status": "reviewed",
            },
        },
    ]

    ledger = build_source_observability_ledger(
        root=ROOT,
        records=current_records,
        previous_records=previous_records,
    )
    by_source = {source["source_id"]: source for source in ledger["sources"]}

    assert ledger["summary"]["source_count"] == 13
    assert by_source["hdc"]["crawlability"]["status"] == "reachable"
    assert by_source["hdc"]["parser_completion"]["status"] == "validated_records"
    assert by_source["hdc"]["timestamps"]["last_fetch_at"] == "2026-07-02T00:00:00Z"
    assert by_source["hdc"]["drift"]["severity"] == "drop"
    assert by_source["hdc"]["rights"]["status"] == "reviewed"
    assert by_source["hdc"]["document_classes"] == ["decision"]


def test_archive_anomaly_report_detects_drift_and_manifest_problems(tmp_path: Path) -> None:
    evidence = _complete_evidence(tmp_path)
    source_observability = build_source_observability_ledger(
        root=ROOT,
        records=[
            {
                "id": "hdc-1",
                "source": "hdc",
                "text": "Example text.",
                "date": "2026-07-02",
                "url": "https://example.com/decision",
                "metadata": {
                    "retrieved_at": "2026-07-02T00:00:00Z",
                    "parsed_at": "2026-07-02T00:15:00Z",
                    "document_class": "decision",
                    "rights_review_status": "reviewed",
                },
            }
        ],
        previous_records=[
            {
                "id": "hdc-1",
                "source": "hdc",
                "text": "Example text.",
                "date": "2026-07-01",
                "url": "https://example.com/decision",
                "metadata": {
                    "retrieved_at": "2026-07-01T00:00:00Z",
                    "parsed_at": "2026-07-01T00:15:00Z",
                    "document_class": "decision",
                    "rights_review_status": "reviewed",
                },
            },
            {
                "id": "hdc-2",
                "source": "hdc",
                "text": "Example text.",
                "date": "2026-07-01",
                "url": "https://example.com/decision-2",
                "metadata": {
                    "retrieved_at": "2026-07-01T00:00:00Z",
                    "parsed_at": "2026-07-01T00:15:00Z",
                    "document_class": "decision",
                    "rights_review_status": "reviewed",
                },
            },
        ],
    )
    evidence["source_observability"] = source_observability
    evidence["schema"] = {"record_schema_version": "2.0.0"}
    evidence["hugging_face"]["remote_manifest_verified"] = False
    evidence["metadata_packages"]["packages"] = evidence["metadata_packages"]["packages"][:-1]
    previous_evidence = {
        "source_coverage": {
            "sources": [
                {"source_id": "hdc", "url": "https://old.example.test/decision"},
                {"source_id": "hpdt", "url": "https://www.hpdt.org.nz/Search-Decisions"},
            ]
        }
    }

    report = build_archive_anomaly_report(evidence, previous_evidence=previous_evidence)

    anomaly_types = {anomaly["type"] for anomaly in report["anomalies"]}
    assert report["status"] == "fail"
    assert "record_count_drop" in anomaly_types
    assert "source_url_drift" in anomaly_types
    assert "schema_drift" in anomaly_types
    assert "remote_manifest_verification" in anomaly_types
    assert "metadata_inconsistency" in anomaly_types


def test_public_claims_and_privacy_scoring_are_generated_from_ledgers(tmp_path: Path) -> None:
    evidence = _complete_evidence(tmp_path)
    evidence["source_observability"] = build_source_observability_ledger(
        root=ROOT,
        records=[
            {
                "id": f"{source}-1",
                "source": source,
                "text": "Example text.",
                "date": "2026-07-02",
                "url": "https://example.com/decision",
                "metadata": {
                    "retrieved_at": "2026-07-02T00:00:00Z",
                    "parsed_at": "2026-07-02T00:15:00Z",
                    "document_class": "decision",
                    "rights_review_status": "reviewed",
                },
            }
            for source in ("hdc", "hpdt", "moj_tribunals", "era", "teachers")
        ],
    )
    privacy = build_privacy_rights_scoring(evidence)
    claims = build_public_claims(evidence, maturity_report={"score": 100})

    assert privacy["status"] == "leading"
    assert privacy["score"] == 100
    assert "validated records across 5 active sources" in claims["markdown"]["README.md"]
    assert (
        "Privacy/rights status is summarized as leading." in claims["markdown"]["dataset-card.md"]
    )
    assert (
        "evidence-backed claims are generated from ledgers"
        in claims["markdown"]["release-notes.md"]
    )


def test_federation_compatibility_report_flags_missing_sections() -> None:
    report = build_federation_compatibility_report({"release": {}, "source_coverage": {}})

    assert report["status"] == "drift"
    assert "git" in report["missing_sections"]
    assert report["profile_version"] == "1.0.0"


def test_write_archive_intelligence_report(tmp_path: Path) -> None:
    evidence_path = tmp_path / "release_evidence.json"
    output_path = tmp_path / "archive_maturity.json"
    evidence_path.write_text(json.dumps(_complete_evidence(tmp_path)), encoding="utf-8")

    report = write_archive_intelligence_report(evidence_path, output_path)

    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8"))["score"] == report["score"]


def test_write_archive_intelligence_bundle_writes_claim_and_compatibility_artifacts(
    tmp_path: Path,
) -> None:
    artifact_dir = _write_complete_artifact_dir(tmp_path)
    output_dir = tmp_path / "generated" / "archive-intelligence"

    bundle = write_archive_intelligence_bundle(artifact_dir, output_dir, root=tmp_path)

    assert output_dir.joinpath("archive_maturity.json").is_file()
    assert output_dir.joinpath("source_observability.json").is_file()
    assert output_dir.joinpath("privacy_rights_score.json").is_file()
    assert output_dir.joinpath("anomaly_report.json").is_file()
    assert output_dir.joinpath("public_claims.json").is_file()
    assert output_dir.joinpath("federation_compatibility.json").is_file()
    assert output_dir.joinpath("README.claims.md").is_file()
    assert output_dir.joinpath("dataset-card.claims.md").is_file()
    assert output_dir.joinpath("release-notes.claims.md").is_file()
    assert output_dir.joinpath("github-project-summary.claims.md").is_file()
    assert bundle["public_claims"]["facts"]["record_count"] == 5


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


def test_archive_intelligence_from_artifact_dir_scores_100_when_publication_evidence_exists(
    tmp_path: Path,
) -> None:
    report = build_archive_intelligence_from_artifact_dir(
        _write_complete_artifact_dir(tmp_path),
    )

    assert report["score"] == 100
    assert report["severity"] == "leading"
    dimensions = {dimension["id"]: dimension for dimension in report["dimensions"]}
    assert dimensions["remote_publication_proof"]["score"] == 100


def test_archive_intelligence_strict_mode_rejects_partial_reports(tmp_path: Path) -> None:
    report = build_archive_intelligence_from_artifact_dir(_write_complete_artifact_dir(tmp_path))

    failures = validate_archive_intelligence_report(report, strict=True)

    assert failures == []
    partial_failures = validate_archive_intelligence_report(
        {"score": 88.0, "severity": "strong"},
        strict=True,
    )
    assert partial_failures
