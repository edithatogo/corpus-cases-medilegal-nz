from __future__ import annotations

from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

from corpus_cases_medilegal_nz.collection_proof import build_fixture_collection_records
from corpus_cases_medilegal_nz.source_verification import (
    build_live_backfill_proof,
    build_source_verification_bundle,
    build_source_verification_feasibility,
    build_verification_public_claims,
    fetch_verification_inputs,
    reconcile_expected_records,
    replay_verification_inputs,
    verification_target_metadata,
)

ROOT = Path(__file__).resolve().parents[1]


def test_source_verification_feasibility_covers_all_sources() -> None:
    report = build_source_verification_feasibility(root=ROOT)

    assert report["summary"]["source_count"] == 13
    assert report["summary"]["immediately_available_count"] == 13
    assert report["summary"]["blocked_count"] == 0
    assert {source["verification_status"] for source in report["sources"]} == {
        "immediately_available"
    }
    hdc = next(source for source in report["sources"] if source["source_id"] == "hdc")
    assert hdc["evidence_type"] == "official_static_fixture"
    assert hdc["archiving_policy"] == "archive_raw"
    assert hdc["rights"]["redistribution_status"] == "public-source-review-required"


def test_fetch_verification_inputs_archives_raw_fixtures_and_manifest(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "verification"

    manifest = fetch_verification_inputs(output_dir=evidence_dir, root=ROOT)

    assert manifest["summary"]["archived_input_count"] == 13
    assert manifest["summary"]["metadata_only_count"] == 0
    assert (evidence_dir / "manifests" / "verification_input_manifest.json").is_file()
    assert (evidence_dir / "raw" / "hdc" / "listing.html").is_file()
    hdc = next(item for item in manifest["inputs"] if item["source_id"] == "hdc")
    assert hdc["sha256"]
    assert hdc["byte_count"] > 0
    assert hdc["relative_path"] == "raw/hdc/listing.html"


def test_replay_verification_inputs_fails_on_hash_mismatch(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "verification"
    fetch_verification_inputs(output_dir=evidence_dir, root=ROOT)
    (evidence_dir / "raw" / "hdc" / "listing.html").write_text("tampered", encoding="utf-8")

    replay = replay_verification_inputs(evidence_dir)

    hdc = next(item for item in replay["inputs"] if item["source_id"] == "hdc")
    assert replay["status"] == "blocked"
    assert hdc["status"] == "hash_mismatch"


def test_source_verification_bundle_reconciles_expected_records(tmp_path: Path) -> None:
    records = build_fixture_collection_records()

    bundle = build_source_verification_bundle(
        output_dir=tmp_path / "verification",
        root=ROOT,
        processed_records=records,
    )

    assert bundle["status"] == "verified_complete"
    assert bundle["feasibility"]["summary"]["source_count"] == 13
    assert bundle["input_manifest"]["summary"]["archived_input_count"] == 13
    assert bundle["expected_records"]["summary"]["expected_record_count"] == 26
    assert bundle["reconciliation"]["summary"]["matched_count"] == 26
    assert bundle["reconciliation"]["summary"]["missing_count"] == 0
    assert bundle["replay"]["status"] == "pass"
    assert (tmp_path / "verification" / "manifests" / "source_expected_records.jsonl").is_file()
    assert (tmp_path / "verification" / "manifests" / "source_verification_summary.json").is_file()


def test_reconcile_expected_records_classifies_missing_and_extra() -> None:
    records = build_fixture_collection_records()
    hdc_records = [record for record in records if record["source"] == "hdc"]
    expected = [
        {
            "source": "hdc",
            "case_id": "HDC26HDC001",
            "title": "Care planning and informed consent",
            "date": "2026-06-15",
            "canonical_url": "https://www.hdc.org.nz/decisions/search-decisions/2026/hdc26hdc001/",
            "alternate_urls": [],
            "evidence_input": "raw/hdc/listing.html",
        },
        {
            "source": "hdc",
            "case_id": "missing",
            "title": "Missing decision",
            "date": "2026-01-01",
            "canonical_url": "https://example.test/missing",
            "alternate_urls": [],
            "evidence_input": "raw/hdc/listing.html",
        },
    ]

    reconciliation = reconcile_expected_records(
        expected_records=expected,
        processed_records=[*hdc_records[:1], {"source": "hdc", "case_id": "extra"}],
    )

    assert reconciliation["summary"]["matched_count"] == 1
    assert reconciliation["summary"]["missing_count"] == 1
    assert reconciliation["summary"]["extra_count"] == 1
    assert reconciliation["status"] == "verified_incomplete"


def test_reconcile_expected_records_can_report_ambiguity_without_failing_projection() -> None:
    expected = [
        {
            "source": "ombudsman",
            "case_id": "ombudsman-1",
            "title": "Annual report",
            "date": "",
        },
        {
            "source": "ombudsman",
            "case_id": "ombudsman-2",
            "title": "Annual report",
            "date": "",
        },
    ]

    strict = reconcile_expected_records(expected_records=expected, processed_records=expected)
    projected = reconcile_expected_records(
        expected_records=expected,
        processed_records=expected,
        fail_on_ambiguous=False,
    )

    assert strict["summary"]["ambiguous_count"] == 2
    assert strict["status"] == "verified_incomplete"
    assert projected["summary"]["ambiguous_count"] == 2
    assert projected["status"] == "verified_complete"


def test_verification_target_metadata_promotes_official_source_index_counts(
    tmp_path: Path,
) -> None:
    records = build_fixture_collection_records()
    bundle = build_source_verification_bundle(
        output_dir=tmp_path / "verification",
        root=ROOT,
        processed_records=records,
    )

    targets = verification_target_metadata(bundle["expected_records"])

    assert targets["sources"]["hdc"]["expected_count"] == 2
    assert targets["sources"]["hdc"]["expected_count_confidence"] == "source_index_count"


def test_verification_public_claims_are_evidence_backed(tmp_path: Path) -> None:
    records = build_fixture_collection_records()
    bundle = build_source_verification_bundle(
        output_dir=tmp_path / "verification",
        root=ROOT,
        processed_records=records,
    )

    claims = build_verification_public_claims(bundle)

    assert claims["status"] == "verified_complete"
    assert "26 expected records" in claims["coverage_statement"]
    assert claims["blocked_sources"] == []


def test_live_fetch_records_blocker_instead_of_silently_skipping(tmp_path: Path) -> None:
    class BrokenResponse:
        status_code = 503
        headers: ClassVar[dict[str, str]] = {"content-type": "text/html"}
        content = b"unavailable"

    with patch("corpus_cases_medilegal_nz.source_verification.requests.get") as get:
        get.return_value = BrokenResponse()
        manifest = fetch_verification_inputs(
            output_dir=tmp_path / "verification",
            root=ROOT,
            mode="live",
            source_ids=["hdc"],
        )

    hdc = manifest["inputs"][0]
    assert manifest["summary"]["blocked_input_count"] == 1
    assert hdc["status"] == "blocked"
    assert hdc["blockers"] == ["http_503"]


def test_live_fetch_success_replays_with_relative_paths(tmp_path: Path) -> None:
    class OkResponse:
        status_code = 200
        headers: ClassVar[dict[str, str]] = {"content-type": "text/html"}
        content = b"<html><body><article data-case-id='HDC-LIVE-1'><h2>Live HDC</h2><time datetime='2026-07-01'>1 July 2026</time><a href='https://example.test/live'>Decision</a><p>Live decision.</p></article></body></html>"

    with patch("corpus_cases_medilegal_nz.source_verification.requests.get") as get:
        get.return_value = OkResponse()
        manifest = fetch_verification_inputs(
            output_dir=tmp_path / "verification",
            root=ROOT,
            mode="live",
            source_ids=["hdc"],
        )

    replay = replay_verification_inputs(tmp_path / "verification")

    assert manifest["inputs"][0]["relative_path"] == "raw/hdc/listing.html"
    assert replay["status"] == "pass"
    assert replay["inputs"][0]["status"] == "replayed"


def test_live_backfill_proof_reconciles_generated_records(tmp_path: Path) -> None:
    class OkResponse:
        status_code = 200
        headers: ClassVar[dict[str, str]] = {"content-type": "text/html"}
        content = b"<html><body><article data-case-id='HDC-LIVE-1'><h2>Live HDC</h2><time datetime='2026-07-01'>1 July 2026</time><a href='https://example.test/live'>Decision</a><p>Live decision.</p></article></body></html>"

    with patch("corpus_cases_medilegal_nz.source_verification.requests.get") as get:
        get.return_value = OkResponse()
        proof = build_live_backfill_proof(
            output_dir=tmp_path / "live-backfill",
            root=ROOT,
            source_ids=["hdc"],
        )

    assert proof["status"] == "pass"
    assert proof["record_count"] == 1
    assert proof["reconciliation"]["status"] == "verified_complete"
    assert (tmp_path / "live-backfill" / "jsonl" / "records.jsonl").is_file()
