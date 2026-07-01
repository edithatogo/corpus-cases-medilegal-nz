"""Deterministic local collection proof generation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import polars as pl

from corpus_cases_medilegal_nz.archive import (
    build_dataset_diff,
    build_source_collection_audit,
    load_jsonl_records,
    write_json,
)
from corpus_cases_medilegal_nz.medilegal_parser import parse_source_listing_html

CORE_SOURCE_URLS = {
    "hdc": "https://www.hdc.org.nz/decisions/search-decisions/",
    "hpdt": "https://www.hpdt.org.nz/Search-Decisions",
    "moj_tribunals": "https://www.justice.govt.nz/tribunals/",
    "era": "https://www.era.govt.nz/",
    "teachers": "https://www.teachersdisciplinarytribunal.nz/",
}

JsonObject = dict[str, Any]


def build_fixture_collection_records(
    fixture_root: Path = Path("tests/fixtures/sources"),
    *,
    retrieved_at: str = "2026-07-01T00:00:00Z",
) -> list[JsonObject]:
    """Build deterministic parser output records from core source fixtures."""
    manifest_path = fixture_root / "fixture_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records: list[JsonObject] = []
    for source_id in sorted(CORE_SOURCE_URLS):
        fixture = manifest["core_sources"][source_id]
        html = (fixture_root / fixture["html"]).read_text(encoding="utf-8")
        records.extend(
            parse_source_listing_html(
                source_id=source_id,
                url=CORE_SOURCE_URLS[source_id],
                html=html,
                retrieved_at=retrieved_at,
            )
        )
    return sorted(records, key=lambda record: (str(record["source"]), str(record["case_id"])))


def write_collection_proof(
    *,
    output_dir: Path = Path("data/processed"),
    fixture_root: Path = Path("tests/fixtures/sources"),
    previous_records_path: Path | None = None,
) -> JsonObject:
    """Write deterministic processed artifacts and return proof evidence."""
    records = build_fixture_collection_records(fixture_root=fixture_root)
    previous_records = load_jsonl_records(previous_records_path) if previous_records_path else []
    paths = _write_processed_artifacts(output_dir=output_dir, records=records)
    dataset_diff = build_dataset_diff(current_records=records, previous_records=previous_records)
    manifests_dir = output_dir / "manifests"
    dataset_diff_path = write_json(manifests_dir / "dataset_diff.json", dataset_diff)
    audit = build_source_collection_audit(records=records)
    evidence = {
        "schema_version": "1.0.0",
        "record_count": len(records),
        "source_counts": {
            source_id: sum(1 for record in records if record["source"] == source_id)
            for source_id in sorted(CORE_SOURCE_URLS)
        },
        "artifacts": {key: str(value) for key, value in paths.items()},
        "dataset_diff": dataset_diff,
        "source_collection_audit": audit,
    }
    evidence_path = output_dir / "collection_proof.json"
    write_json(evidence_path, evidence)
    evidence["artifacts"]["collection_proof"] = str(evidence_path)
    evidence["artifacts"]["dataset_diff"] = str(dataset_diff_path)
    return evidence


def _write_processed_artifacts(*, output_dir: Path, records: list[JsonObject]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir = output_dir / "markdown"
    text_dir = output_dir / "text"
    json_dir = output_dir / "json"
    jsonl_dir = output_dir / "jsonl"
    parquet_dir = output_dir / "parquet"
    for directory in (markdown_dir, text_dir, json_dir, jsonl_dir, parquet_dir):
        directory.mkdir(parents=True, exist_ok=True)

    for record in records:
        filename = _safe_filename(str(record["source"]), str(record["case_id"]))
        (markdown_dir / f"{filename}.md").write_text(_markdown_record(record), encoding="utf-8")
        (text_dir / f"{filename}.txt").write_text(str(record["text"]), encoding="utf-8")
        write_json(json_dir / f"{filename}.json", record)

    records_jsonl = jsonl_dir / "records.jsonl"
    records_jsonl.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records
        ),
        encoding="utf-8",
    )
    cases_jsonl = jsonl_dir / "cases.jsonl"
    cases_jsonl.write_text(records_jsonl.read_text(encoding="utf-8"), encoding="utf-8")

    if records:
        rows = [
            {
                **record,
                "metadata": json.dumps(record["metadata"], ensure_ascii=False, sort_keys=True),
            }
            for record in records
        ]
        pl.DataFrame(rows).write_parquet(parquet_dir, partition_by=["source"])

    return {
        "markdown": markdown_dir,
        "text": text_dir,
        "json": json_dir,
        "records_jsonl": records_jsonl,
        "cases_jsonl": cases_jsonl,
        "parquet": parquet_dir,
    }


def _markdown_record(record: JsonObject) -> str:
    frontmatter = {
        "case_id": record["case_id"],
        "source": record["source"],
        "title": record["title"],
        "date": record["date"],
        "url": record.get("url") or record["metadata"]["url"],
    }
    lines = ["---"]
    lines.extend(
        f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in frontmatter.items()
    )
    lines.extend(["---", "", str(record["text"]), ""])
    return "\n".join(lines)


def _safe_filename(source_id: str, case_id: str) -> str:
    safe_case_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", case_id).strip("-")
    return f"{source_id}-{safe_case_id}"
