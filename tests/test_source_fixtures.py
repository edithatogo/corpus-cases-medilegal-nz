from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from corpus_cases_medilegal_nz.parser_contract import validate_parser_input, validate_parser_records

FIXTURES_ROOT = Path(__file__).parent / "fixtures" / "sources"
CORE_SOURCE_IDS = {"hdc", "hpdt", "moj_tribunals", "era", "teachers"}


def test_core_source_fixtures_manifest_covers_html_and_pdf() -> None:
    manifest = json.loads((FIXTURES_ROOT / "fixture_manifest.json").read_text(encoding="utf-8"))

    assert set(manifest["core_sources"]) == CORE_SOURCE_IDS
    for source_id, fixture_paths in manifest["core_sources"].items():
        html_path = FIXTURES_ROOT / fixture_paths["html"]
        pdf_path = FIXTURES_ROOT / fixture_paths["pdf"]

        assert html_path.is_file(), source_id
        assert pdf_path.is_file(), source_id
        assert "<!doctype html>" in html_path.read_text(encoding="utf-8").lower()
        assert pdf_path.read_bytes().startswith(b"%PDF-")


def test_hdc_listing_fixture_satisfies_parser_input_contract() -> None:
    html = (FIXTURES_ROOT / "hdc" / "listing.html").read_text(encoding="utf-8")

    payload = validate_parser_input(
        {
            "source_id": "hdc",
            "url": "https://www.hdc.org.nz/decisions/search-decisions/",
            "content": html,
            "content_type": "text/html",
        }
    )

    assert "HDC26HDC001" in payload["content"]
    assert "/decisions/search-decisions/2026/hdc26hdc001/" in payload["content"]
    assert "2026-06-15" in payload["content"]


def test_hdc_fixture_record_shape_matches_expected_parser_output() -> None:
    html_bytes = (FIXTURES_ROOT / "hdc" / "listing.html").read_bytes()
    record = {
        "case_id": "HDC26HDC001",
        "source": "hdc",
        "title": "Care planning and informed consent",
        "date": "2026-06-15",
        "text": "Synthetic fixture summary for parser tests.",
        "metadata": {
            "url": "https://www.hdc.org.nz/decisions/search-decisions/2026/hdc26hdc001/",
            "retrieved_at": "2026-07-01T00:00:00Z",
            "parser_name": "nlp_policy_nz.hdc.synthetic_fixture",
            "parser_version": "1.0.0",
            "raw_sha256": hashlib.sha256(html_bytes).hexdigest(),
            "decision_link": "/decisions/search-decisions/2026/hdc26hdc001/",
            "fixture": True,
        },
    }

    assert validate_parser_records([record], source_id="hdc") == [record]


@pytest.mark.parametrize("source_id", sorted(CORE_SOURCE_IDS))
def test_core_source_fixtures_encode_parser_metadata_expectations(source_id: str) -> None:
    manifest = json.loads((FIXTURES_ROOT / "fixture_manifest.json").read_text(encoding="utf-8"))
    source_fixture = manifest["core_sources"][source_id]
    html = (FIXTURES_ROOT / source_fixture["html"]).read_text(encoding="utf-8")

    for expected_value in source_fixture["expected"].values():
        assert expected_value in html, source_id
