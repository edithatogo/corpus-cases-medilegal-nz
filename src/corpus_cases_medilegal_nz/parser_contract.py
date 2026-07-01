"""Parser delegation contract for shared ``nlp-policy-nz`` integrations."""

from __future__ import annotations

from collections.abc import Mapping
from importlib import metadata
from typing import Any

PARSER_CONTRACT_VERSION = "1.0.0"
PARSER_PROVIDER_PACKAGE = "nlp_policy_nz"
PARSER_PROVIDER_DISTRIBUTION = "nlp-policy-nz"
REQUIRED_RECORD_FIELDS = ("case_id", "source", "title", "date", "text", "metadata")
REQUIRED_INPUT_FIELDS = ("source_id", "url", "content", "content_type")
REQUIRED_METADATA_FIELDS = ("url", "retrieved_at", "parser_name", "parser_version", "raw_sha256")

JsonObject = dict[str, Any]


class ParserContractError(ValueError):
    """Raised when parser input or output violates the medilegal contract."""


def provider_version() -> str:
    """Return the installed ``nlp-policy-nz`` version when available."""
    try:
        return metadata.version(PARSER_PROVIDER_DISTRIBUTION)
    except metadata.PackageNotFoundError:
        return "not-installed"


def build_parser_contract() -> JsonObject:
    """Return the source parser contract expected from ``nlp-policy-nz``."""
    return {
        "schema_version": PARSER_CONTRACT_VERSION,
        "provider": {
            "package": PARSER_PROVIDER_PACKAGE,
            "distribution": PARSER_PROVIDER_DISTRIBUTION,
            "installed_version": provider_version(),
            "minimum_version": "0.1.0",
        },
        "input": {
            "type": "mapping",
            "required_fields": list(REQUIRED_INPUT_FIELDS),
            "content_type_values": ["text/html", "application/pdf", "text/plain"],
            "description": (
                "Source adapters pass raw fetched content, source id, source URL, "
                "content type, and optional fetch/provenance metadata."
            ),
        },
        "output": {
            "type": "list[dict]",
            "required_fields": list(REQUIRED_RECORD_FIELDS),
            "metadata_required_fields": list(REQUIRED_METADATA_FIELDS),
            "description": (
                "Each record must be compatible with ExportableCase and release "
                "evidence JSONL records."
            ),
        },
        "error_semantics": {
            "recoverable": (
                "Parser returns zero records and records diagnostics when the source "
                "page is reachable but contains no supported decisions."
            ),
            "blocking": (
                "Parser raises a typed exception or returns diagnostics for malformed "
                "input, unsupported content types, missing required fields, or schema "
                "incompatibility."
            ),
        },
        "version_compatibility": {
            "contract": PARSER_CONTRACT_VERSION,
            "policy": "backwards-compatible until PARSER_CONTRACT_VERSION changes.",
        },
    }


def validate_parser_input(payload: Mapping[str, Any]) -> JsonObject:
    """Validate raw parser input passed from this repo to ``nlp-policy-nz``."""
    missing = [field for field in REQUIRED_INPUT_FIELDS if not str(payload.get(field, "")).strip()]
    if missing:
        raise ParserContractError(f"Parser input missing required fields: {missing}")
    content_type = str(payload["content_type"])
    allowed = set(build_parser_contract()["input"]["content_type_values"])
    if content_type not in allowed:
        raise ParserContractError(f"Unsupported parser content_type: {content_type}")
    return dict(payload)


def validate_parser_record(record: Mapping[str, Any], *, source_id: str) -> JsonObject:
    """Validate and normalize one parser output record."""
    missing = [field for field in REQUIRED_RECORD_FIELDS if field not in record]
    if missing:
        raise ParserContractError(f"Parser record missing required fields: {missing}")
    normalized = dict(record)
    if str(normalized.get("source")) != source_id:
        raise ParserContractError(
            f"Parser record source must be {source_id!r}, got {normalized.get('source')!r}"
        )
    for field in ("case_id", "title", "date", "text"):
        if not str(normalized.get(field, "")).strip():
            raise ParserContractError(f"Parser record field must be non-empty: {field}")
    metadata_value = normalized.get("metadata")
    if not isinstance(metadata_value, dict):
        raise ParserContractError("Parser record metadata must be a dict")
    missing_metadata = [
        field
        for field in REQUIRED_METADATA_FIELDS
        if not str(metadata_value.get(field, "")).strip()
    ]
    if missing_metadata:
        raise ParserContractError(
            f"Parser record metadata missing required fields: {missing_metadata}"
        )
    normalized["metadata"] = metadata_value
    return normalized


def validate_parser_records(
    records: list[Mapping[str, Any]],
    *,
    source_id: str,
) -> list[JsonObject]:
    """Validate and normalize parser output records for one source."""
    return [validate_parser_record(record, source_id=source_id) for record in records]
