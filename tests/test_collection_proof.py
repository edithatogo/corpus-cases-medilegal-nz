from __future__ import annotations

from pathlib import Path

from corpus_cases_medilegal_nz.archive import load_jsonl_records
from corpus_cases_medilegal_nz.collection_proof import (
    CORE_SOURCE_URLS,
    build_fixture_collection_records,
    write_collection_proof,
)


def test_build_fixture_collection_records_covers_all_core_sources() -> None:
    records = build_fixture_collection_records()

    assert len(records) == len(CORE_SOURCE_URLS)
    assert {record["source"] for record in records} == set(CORE_SOURCE_URLS)
    assert all(record["metadata"]["raw_sha256"] for record in records)


def test_write_collection_proof_exports_archive_compatible_records(tmp_path: Path) -> None:
    output_dir = tmp_path / "processed"

    evidence = write_collection_proof(output_dir=output_dir)
    records = load_jsonl_records(output_dir / "jsonl" / "records.jsonl")

    assert evidence["record_count"] == 5
    assert len(records) == 5
    assert evidence["source_collection_audit"]["stage_counts"]["validated_records"] == 5
    assert evidence["collection_quality_gates"]["status"] == "pass"
    assert evidence["dataset_diff"]["counts"]["added"] == 5
    assert evidence["dataset_diff"]["counts"]["current"] == 5
    assert (output_dir / "manifests" / "dataset_diff.json").is_file()
    assert (output_dir / "manifests" / "collection_quality_gates.json").is_file()
    assert (output_dir / "jsonl" / "cases.jsonl").is_file()
    assert (output_dir / "markdown").is_dir()
    assert (output_dir / "text").is_dir()
    assert (output_dir / "json").is_dir()
    assert (output_dir / "parquet").is_dir()


def test_write_collection_proof_reconciles_previous_records(tmp_path: Path) -> None:
    previous_records = tmp_path / "previous.jsonl"
    previous_records.write_text(
        '{"case_id":"HDC26HDC001","source":"hdc","title":"Old","date":"2026-06-15","text":"Old","metadata":{"url":"https://example.test","retrieved_at":"2026-07-01T00:00:00Z","parser_name":"fixture","parser_version":"1.0.0","raw_sha256":"0"}}\n'
        '{"case_id":"removed-record","source":"hdc","title":"Removed","date":"2026-01-01","text":"Removed","metadata":{"url":"https://example.test/removed","retrieved_at":"2026-07-01T00:00:00Z","parser_name":"fixture","parser_version":"1.0.0","raw_sha256":"0"}}\n',
        encoding="utf-8",
    )

    evidence = write_collection_proof(
        output_dir=tmp_path / "processed",
        previous_records_path=previous_records,
    )

    assert "HDC26HDC001" in evidence["dataset_diff"]["changed"]
    assert evidence["dataset_diff"]["removed"] == ["removed-record"]
    assert evidence["dataset_diff"]["tombstoned"] == ["removed-record"]
