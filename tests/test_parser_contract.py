from __future__ import annotations

import pytest

from corpus_cases_medilegal_nz.parser_contract import (
    PARSER_CONTRACT_VERSION,
    ParserContractError,
    build_parser_contract,
    validate_parser_input,
    validate_parser_record,
    validate_parser_records,
)


def test_parser_contract_documents_required_boundaries() -> None:
    contract = build_parser_contract()

    assert contract["schema_version"] == PARSER_CONTRACT_VERSION
    assert contract["provider"]["package"] == "nlp_policy_nz"
    assert contract["provider"]["minimum_version"] == "0.1.0"
    assert contract["input"]["required_fields"] == [
        "source_id",
        "url",
        "content",
        "content_type",
    ]
    assert contract["output"]["required_fields"] == [
        "case_id",
        "source",
        "title",
        "date",
        "text",
        "metadata",
    ]
    assert "recoverable" in contract["error_semantics"]
    assert "blocking" in contract["error_semantics"]


def test_validate_parser_input_accepts_supported_content() -> None:
    payload = {
        "source_id": "hdc",
        "url": "https://example.test/decision",
        "content": "<html>Decision</html>",
        "content_type": "text/html",
    }

    assert validate_parser_input(payload) == payload


def test_validate_parser_input_rejects_missing_fields() -> None:
    with pytest.raises(ParserContractError, match="missing required fields"):
        validate_parser_input({"source_id": "hdc", "content_type": "text/html"})


def test_validate_parser_input_rejects_unsupported_content_type() -> None:
    with pytest.raises(ParserContractError, match="Unsupported parser content_type"):
        validate_parser_input(
            {
                "source_id": "hdc",
                "url": "https://example.test/decision",
                "content": "Decision",
                "content_type": "application/octet-stream",
            }
        )


def test_validate_parser_record_accepts_exportable_case_shape() -> None:
    record = {
        "case_id": "hdc-001",
        "source": "hdc",
        "title": "Decision 001",
        "date": "2026-07-01",
        "text": "Decision body",
        "metadata": {
            "url": "https://example.test/decision",
            "retrieved_at": "2026-07-01T00:00:00Z",
            "parser_name": "fixture",
            "parser_version": "1.0.0",
            "raw_sha256": "0" * 64,
        },
    }

    assert validate_parser_record(record, source_id="hdc") == record


def test_validate_parser_record_rejects_source_mismatch() -> None:
    with pytest.raises(ParserContractError, match="source must be 'hdc'"):
        validate_parser_record(
            {
                "case_id": "hpdt-001",
                "source": "hpdt",
                "title": "Decision 001",
                "date": "2026-07-01",
                "text": "Decision body",
                "metadata": {},
            },
            source_id="hdc",
        )


def test_validate_parser_records_normalizes_all_records() -> None:
    records = [
        {
            "case_id": "hdc-001",
            "source": "hdc",
            "title": "Decision 001",
            "date": "2026-07-01",
            "text": "Decision body",
            "metadata": {},
        }
    ]

    assert validate_parser_records(records, source_id="hdc") == records
