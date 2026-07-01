from __future__ import annotations

import json
from pathlib import Path

import pytest

from corpus_cases_medilegal_nz.medilegal_parser import parse_source_listing_html

FIXTURES_ROOT = Path(__file__).parent / "fixtures" / "sources"
LISTING_URLS = {
    "hdc": "https://www.hdc.org.nz/decisions/search-decisions/",
    "hpdt": "https://www.hpdt.org.nz/Search-Decisions",
    "moj_tribunals": "https://www.justice.govt.nz/tribunals/",
    "era": "https://www.era.govt.nz/",
    "teachers": "https://www.teachersdisciplinarytribunal.nz/",
}


@pytest.mark.parametrize("source_id", sorted(LISTING_URLS))
def test_parse_source_listing_html_emits_contract_valid_records(source_id: str) -> None:
    manifest = json.loads((FIXTURES_ROOT / "fixture_manifest.json").read_text(encoding="utf-8"))
    fixture = manifest["core_sources"][source_id]
    html = (FIXTURES_ROOT / fixture["html"]).read_text(encoding="utf-8")

    records = parse_source_listing_html(
        source_id=source_id,
        url=LISTING_URLS[source_id],
        html=html,
        retrieved_at="2026-07-01T00:00:00Z",
    )

    assert len(records) == 1
    record = records[0]
    expected = fixture["expected"]
    assert record["case_id"] == expected["identifier"]
    assert record["date"] == expected["date"]
    assert record["source"] == source_id
    assert record["title"] == expected["title"]
    assert record["text"] == expected["body_text"]
    assert record["metadata"]["decision_link"] == expected["decision_link"]
    assert record["metadata"]["retrieved_at"] == "2026-07-01T00:00:00Z"
    assert len(record["metadata"]["raw_sha256"]) == 64


def test_parse_source_listing_html_returns_empty_for_no_decision_candidates() -> None:
    html = (FIXTURES_ROOT / "malformed" / "empty.html").read_text(encoding="utf-8")

    records = parse_source_listing_html(
        source_id="hdc",
        url=LISTING_URLS["hdc"],
        html=html,
        retrieved_at="2026-07-01T00:00:00Z",
    )

    assert records == []
