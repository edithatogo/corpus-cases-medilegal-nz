from __future__ import annotations

from pathlib import Path

import pytest

from corpus_cases_medilegal_nz.parser_contract import (
    ParserContractError,
    validate_parser_input,
    validate_parser_record,
)

FIXTURES_ROOT = Path(__file__).parent / "fixtures" / "sources" / "malformed"


def test_malformed_empty_html_still_has_valid_raw_input_contract() -> None:
    html = (FIXTURES_ROOT / "empty.html").read_text(encoding="utf-8")

    payload = validate_parser_input(
        {
            "source_id": "hdc",
            "url": "https://www.hdc.org.nz/decisions/search-decisions/",
            "content": html,
            "content_type": "text/html",
        }
    )

    assert "No decision records" in payload["content"]


def test_parser_input_rejects_unsupported_malformed_fixture_content_type() -> None:
    raw = (FIXTURES_ROOT / "unsupported.bin").read_text(encoding="utf-8")

    with pytest.raises(ParserContractError, match="Unsupported parser content_type"):
        validate_parser_input(
            {
                "source_id": "hdc",
                "url": "https://www.hdc.org.nz/decisions/search-decisions/",
                "content": raw,
                "content_type": "application/octet-stream",
            }
        )


@pytest.mark.parametrize(
    ("record", "match"),
    [
        (
            {
                "case_id": "HDC26HDC001",
                "source": "hpdt",
                "title": "Wrong source",
                "date": "2026-06-15",
                "text": "Wrong source fixture.",
                "metadata": {},
            },
            "source must be 'hdc'",
        ),
        (
            {
                "case_id": "HDC26HDC001",
                "source": "hdc",
                "title": "",
                "date": "2026-06-15",
                "text": "Empty title fixture.",
                "metadata": {},
            },
            "field must be non-empty: title",
        ),
        (
            {
                "case_id": "HDC26HDC001",
                "source": "hdc",
                "title": "Malformed metadata",
                "date": "2026-06-15",
                "text": "Metadata must be a mapping.",
                "metadata": "not-a-dict",
            },
            "metadata must be a dict",
        ),
    ],
)
def test_parser_record_rejects_malformed_output_shapes(
    record: dict[str, object],
    match: str,
) -> None:
    with pytest.raises(ParserContractError, match=match):
        validate_parser_record(record, source_id="hdc")
