from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from corpus_cases_medilegal_nz.archive import (
    build_archive_bundle,
    build_collection_quality_gates,
    build_dataset_diff,
    build_quality_report,
    build_release_artifacts,
    build_source_collection_audit,
    derive_archive_version,
    publication_readiness,
    release_tag,
    sha256_file,
    validate_release_evidence,
)

ROOT = Path(__file__).resolve().parents[1]


def test_archive_version_and_release_tag_are_monthly() -> None:
    version = derive_archive_version(date(2026, 7, 1))

    assert version == "2026.07.0"
    assert release_tag(version) == "dataset-v2026.07.0"


def test_dataset_diff_tracks_added_changed_removed_and_tombstoned() -> None:
    previous = [
        {"case_id": "a", "text": "same"},
        {"case_id": "b", "text": "old"},
        {"case_id": "removed", "text": "gone"},
    ]
    current = [
        {"case_id": "a", "text": "same"},
        {"case_id": "b", "text": "new"},
        {"case_id": "c", "text": "added"},
    ]

    diff = build_dataset_diff(current_records=current, previous_records=previous)

    assert diff["added"] == ["c"]
    assert diff["changed"] == ["b"]
    assert diff["removed"] == ["removed"]
    assert diff["tombstoned"] == ["removed"]


def test_quality_report_flags_blocking_record_regressions() -> None:
    quality = build_quality_report(
        [
            {"case_id": "a", "date": "2026-07-01", "url": "https://example.test/a", "text": ""},
            {"case_id": "a", "date": "bad-date", "url": "not-a-url", "text": "duplicate"},
        ]
    )

    assert quality["duplicate_ids"] == ["a"]
    assert quality["missing_text"] == ["a"]
    assert quality["invalid_dates"] == ["a"]
    assert quality["malformed_urls"] == ["a"]
    assert quality["blocking_issue_count"] == 3


def test_source_collection_audit_reports_current_parser_completion_state() -> None:
    audit = build_source_collection_audit(root=ROOT, records=[])
    by_source = {source["source_id"]: source for source in audit["sources"]}

    assert audit["stage_counts"]["fetch_scaffold_parser_stub"] == 5
    assert audit["stage_counts"]["planned"] == 8
    assert by_source["hdc"]["completion_stage"] == "fetch_scaffold_parser_stub"
    assert by_source["hdc"]["adapter_module_exists"] is True
    assert by_source["hdc"]["record_count"] == 0
    assert by_source["coronial"]["completion_stage"] == "planned"


def test_source_collection_audit_marks_sources_with_records_validated() -> None:
    audit = build_source_collection_audit(
        root=ROOT,
        records=[{"case_id": "hdc-1", "source": "hdc", "text": "Decision text"}],
    )
    by_source = {source["source_id"]: source for source in audit["sources"]}

    assert by_source["hdc"]["completion_stage"] == "validated_records"
    assert by_source["hdc"]["parser_contract"]["status"] == "satisfied"
    assert by_source["hdc"]["record_count"] == 1


def test_collection_quality_gates_block_parser_complete_zero_records() -> None:
    gates = build_collection_quality_gates(records=[])

    assert gates["status"] == "blocked"
    assert len(gates["blockers"]) == 5
    assert all(summary["status"] == "blocked" for summary in gates["source_validation_summaries"])


def test_collection_quality_gates_warn_on_record_count_drift() -> None:
    gates = build_collection_quality_gates(
        records=[{"case_id": "hdc-1", "source": "hdc"}],
        previous_records=[
            {"case_id": "hdc-1", "source": "hdc"},
            {"case_id": "hdc-2", "source": "hdc"},
            {"case_id": "hpdt-1", "source": "hpdt"},
        ],
    )

    assert gates["status"] == "blocked"
    assert any("hdc record count dropped" in warning for warning in gates["warnings"])


def test_build_release_artifacts_writes_required_ledgers(tmp_path: Path) -> None:
    output_dir = tmp_path / "monthly-publication"

    summary = build_release_artifacts(
        output_dir=output_dir,
        root=ROOT,
        archive_version="2026.07.0",
        hf_repo_id="edithatogo/corpus-cases-medilegal-nz",
    )

    evidence_path = output_dir / "manifests/release_evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert validate_release_evidence(evidence) == []
    assert evidence["release"]["archive_version"] == "2026.07.0"
    assert evidence["release"]["github_release_tag"] == "dataset-v2026.07.0"
    assert evidence["zenodo"]["publish_handoff_only"] is True
    assert evidence["parser_contract"]["provider"]["package"] == "nlp_policy_nz"
    assert evidence["source_collection_audit"]["stage_counts"]["planned"] == 8
    assert evidence["collection_quality_gates"]["status"] in {"pass", "blocked"}
    assert evidence["public_surface"]["surfaces"]["osf"]["status"] == "inactive"
    assert (output_dir / "SHA256SUMS").is_file()
    assert (output_dir / "manifests/parser_contract.json").is_file()
    assert (output_dir / "manifests/source_collection_audit.json").is_file()
    assert (output_dir / "manifests/collection_quality_gates.json").is_file()
    assert (output_dir / "metadata/croissant.jsonld").is_file()
    assert (output_dir / "metadata/ro-crate-metadata.json").is_file()
    assert (output_dir / "metadata/datapackage.json").is_file()
    assert (output_dir / "metadata/dcat.jsonld").is_file()
    assert (output_dir / "metadata/prov-o.jsonld").is_file()
    assert (output_dir / "metadata/datacite.json").is_file()
    assert (output_dir / "metadata/schema-org-dataset.jsonld").is_file()
    assert (output_dir / "metadata/huggingface-dataset-card-metadata.json").is_file()
    assert (output_dir / "sbom/sbom.cyclonedx.json").is_file()
    assert (output_dir / "sbom/sbom.spdx.json").is_file()
    assert summary["checksum_manifest"]["file_count"] > 0


def test_archive_bundle_is_reproducible(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()
    (artifact_dir / "a.txt").write_text("alpha\n", encoding="utf-8")
    (artifact_dir / "b.txt").write_text("beta\n", encoding="utf-8")
    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"

    build_archive_bundle(artifact_dir, first)
    build_archive_bundle(artifact_dir, second)

    assert sha256_file(first) == sha256_file(second)


def test_publication_readiness_reports_gated_secrets_not_local_blockers() -> None:
    readiness = publication_readiness(environment={}, root=ROOT)

    assert readiness["status"] == "ready"
    assert "HF_TOKEN" in readiness["gated_external_writes"]
    assert readiness["protected_environment"] == "zenodo-production"


def test_publication_readiness_accepts_zenodo_secret_aliases() -> None:
    readiness = publication_readiness(
        environment={
            "ZENODO_TOKEN": "legacy-production-token",
            "ZENODO_SANDBOX_TOKEN": "legacy-sandbox-token",
        },
        root=ROOT,
    )
    checks = {check["id"]: check for check in readiness["checks"]}

    assert checks["ZENODO_ACCESS_TOKEN"]["status"] == "configured"
    assert checks["ZENODO_ACCESS_TOKEN"]["configured_names"] == ["ZENODO_TOKEN"]
    assert checks["ZENODO_SANDBOX_ACCESS_TOKEN"]["status"] == "configured"
    assert checks["ZENODO_SANDBOX_ACCESS_TOKEN"]["configured_names"] == ["ZENODO_SANDBOX_TOKEN"]
